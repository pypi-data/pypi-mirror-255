"""
    Helper functions for working with Cosmic Frog models
"""

import os
import sys
import time
import uuid
from typing import Dict, List, Optional
from contextlib import contextmanager
from io import StringIO
from collections.abc import Iterable
from pandas import DataFrame
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import text, inspect
from psycopg2 import sql
from psycopg2.errors import LockNotAvailable, DeadlockDetected
from .frog_platform import OptilogicClient
from .frog_log import get_logger
from .frog_activity import ModelActivity, ActivityStatus
from .db_helpers import create_engine_with_retry
from .frog_utils import FrogUtils
from .frog_anura import AnuraSchema

# pylint: disable=logging-fstring-interpolation

# TODO:
# Will need extensions for custom tables in a model
# Profile parallel write for xlsx
# Add batching to standard table writing

# Define chunk size (number of rows to write per chunk)
CHUNK_SIZE = 1000000

# For key columns, replace Null with placeholder
# For matching on key columns only, will not be written to final table!
PLACEHOLDER_VALUE = ""  # replace with a value that does not appear in your data

CFLIB_IDLE_TRANSACTION_TIMEOUT = os.getenv("CFLIB_IDLE_TRANSACTION_TIMEOUT") or 1800


class FrogModel:
    """
    FrogModel class with helper functions for accessing Cosmic Frog models
    """

    # This allows app key to be set once for all instances, makes utilities easier to write
    class_app_key = None

    def __init__(
        self,
        model_name: Optional[str] = None,
        connection_string: Optional[str] = None,
        engine: Optional[sqlalchemy.engine.Engine] = None,
        application_name: str = "CosmicFrog User Library",
        app_key: str = None,
    ) -> None:
        self.model_name = None
        self.engine = None
        self.connection = None
        self.transactions = []
        self.log = get_logger()
        self.default_schema = None

        # App key can be supplied in 4 ways:
        # 1) Passed in argument when opening a model e.g. FrogModel(app_key="my_app_key")
        # 2) Set via class variable (used for all instances of FrogModel, used in utilities)
        # 3) Via Enviroment var, in Andromeda
        # 4) Via app.key file (when running locally, place file in folder with your script)

        # Store an app key if supplied (it may not be if initialising via engine or connection string)
        if app_key:
            found_app_key = app_key
        elif FrogModel.class_app_key:
            found_app_key = FrogModel.class_app_key
        else:
            found_app_key = os.environ.get("OPTILOGIC_JOB_APPKEY")

        if not found_app_key:
            initial_script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
            file_path = os.path.join(initial_script_dir, "app.key")

            # If local file 'app.key' exists then assume it contains a valid app key
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    found_app_key = file.read().strip()

        self._app_key = found_app_key

        # Model connection can happen in 3 ways:
        # 1) A model name is supplied (required app key) - connection string will be fetched
        # 2) A pre-connected engine is supplied
        # 3) A model connection string is supplied

        if model_name and not (connection_string or engine):

            oc = OptilogicClient(appkey=self._app_key)

            success, connection_string = oc.get_connection_string(model_name)

            if not success:
                raise ValueError(f"Cannot get connection string for frog model: {model_name}")

            self.engine = create_engine_with_retry(self.log, connection_string, application_name)

        # Initialise connection
        elif engine:
            self.engine = engine
        elif connection_string:
            self.engine = create_engine_with_retry(self.log, connection_string, application_name)

        # Identify Anura version
        self.anura_version = self.get_anura_version()

    def __enter__(self):
        self.start_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # No exceptions occurred, so commit the transaction
            self.commit_transaction()
        else:
            # An exception occurred, so roll back the transaction
            self.rollback_transaction()

    # Note: The following are for user managed transactions (do not use for library internal transactions)
    def start_transaction(self) -> None:
        """Start a new transaction."""
        if self.connection is None:
            self.connection = self.engine.connect()

        if self.transactions:
            self.transactions.append(self.connection.begin_nested())
        else:
            self.transactions.append(self.connection.begin())

    def commit_transaction(self) -> None:
        """Commit the outermost transaction."""
        if self.transactions:
            transaction = self.transactions.pop()
            transaction.commit()

            if not self.transactions:
                self.connection.close()
                self.connection = None

    def rollback_transaction(self) -> None:
        """Rollback the outermost transaction."""
        if self.transactions:
            transaction = self.transactions.pop()
            transaction.rollback()

            if not self.transactions:
                self.connection.close()
                self.connection = None

    @contextmanager
    def begin(self):
        """
        Context manager for model connections, used to manage both user and system transactions
        """
        connection = None
        try:
            # Decide the context based on the transaction state
            if self.transactions:  # If user has opened a transaction, then nest one
                connection = self.transactions[-1].connection
                transaction = connection.begin_nested()
            else:  # else start a new one
                connection = self.engine.connect()
                transaction = connection.begin()

            # IMPORTANT DETAIL -> yields the connection, not the transaction
            yield connection

            transaction.commit()  # commit the transaction if everything goes well

        except LockNotAvailable:
            self.log.warning("Rolling back, unable to execute due to existing locks on model")
            transaction.rollback()

        except DeadlockDetected:
            self.log.warning("Rolling back, DEADLOCK was detected during operation on model")
            transaction.rollback()

        except Exception:
            self.log.exception(
                "Error, rolling back transaction due to exception", exc_info=True, stack_info=True
            )
            transaction.rollback()
            raise
        finally:
            # If the connection was created in this method, close it.
            if not self.transactions:
                connection.close()

    def get_anura_version(self):
        """
        Returns the current Anura schema version
        """
        df = self.read_sql("SELECT current_schema()")
        return df.iloc[0, 0]

    def get_tablelist(
        self,
        input_only: bool = False,
        output_only: bool = False,
        technology_filter: str = None,
        original_names: bool = False,
    ) -> List[str]:
        """Get a list of commonly used Anura tables, with various filtering options.

        input_only:         Return only input tables
        output_only:        Return only output tables
        technology_filter:  Return tables matching technology (e.g. "NEO")
        original_names:     Return original (UI) names (e.g. "CustomerDemand" rather than "customerdemand")
        """
        assert not (input_only and output_only), "input_only and output_only cannot both be True"

        if technology_filter:
            filtered_data = [
                field
                for field in AnuraSchema.get_anura_masterlist(self.anura_version)
                if (
                    (technology_filter.upper() in field["Technology"].upper())
                    and (
                        (input_only and not field["Category"].startswith("Output"))
                        or (output_only and field["Category"].startswith("Output"))
                        or (not input_only and not output_only)
                    )
                )
            ]

            return [
                field["Table"].lower() if not original_names else field["Table"]
                for field in filtered_data
            ]

        lower_case = not original_names

        # Common un filtered cases
        if input_only:
            return AnuraSchema.get_anura_input_table_names(self.anura_version, lower_case)

        if output_only:
            return AnuraSchema.get_anura_output_table_names(self.anura_version, lower_case)

        return AnuraSchema.get_anura_table_names(self.anura_version, lower_case)

    def get_columns(self, table_name: str) -> List[str]:
        """
        Get a list of Anura columns for the given table

        Parameters:
        table_name: The target table to fetch columns for
        """

        lower_name = table_name.lower()

        return AnuraSchema.get_anura_columns(self.anura_version, lower_name)

    def get_key_columns(self, table_name: str) -> List[str]:
        """
        Get a list of Anura 'key' columns for the given table

        Parameters:
        table_name: The target table to fetch keys for
        """

        lower_name = table_name.lower()

        return AnuraSchema.get_anura_keys(self.anura_version, lower_name)

    # Dump data to a model table
    def write_table(
        self, table_name: str, data: pd.DataFrame | Iterable, overwrite: bool = False
    ) -> None:
        """
        This pushes data into a model table from a data frame or iterable object

        Parameters:
        table_name: The target table
        data:       The data to be written
        overwrite:  Set to true to overwrite current table contents
        """

        table_name = table_name.lower().strip()

        self.log.info("write_table, writing to: %s", table_name)

        # TODO: Should be under same transaction as the write
        if overwrite:
            self.clear_table(table_name)

        if isinstance(data, pd.DataFrame) is False:
            data = pd.DataFrame(data)

        data.columns = data.columns.str.lower().map(str.strip)

        # Initial implementation - pull everything into a df and dump with to_sql
        with self.begin() as connection:
            data.to_sql(
                table_name,
                con=connection,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=CHUNK_SIZE,
            )

        # Note: tried a couple of ways to dump the generator rows directly, but didn't
        # give significant performance over dataframe (though may be better for memory)
        # Decided to leave as is for now

    def read_table(self, table_name: str, id_col: bool = False) -> DataFrame:
        """
        Read a single model table and return as a DataFrame

        Args:
            table_name: Table name to be read (supporting custom tables)
            id_col: Indicates whether the table id column should be returned

        Returns:
            Single dataframe holding table contents
        """

        table_name = table_name.lower().strip()

        with self.begin() as connection:
            result = pd.read_sql(table_name, con=connection)
            if not id_col:
                result.drop(columns=["id"], inplace=True)
            return result

    # Read all, or multiple Anura tables
    def read_tables(
        self, table_list: List[str] = None, id_col: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Read multiple Anura tables and return as a dictionary, indexed by table name

        Args:
            table_list: List of table names to be read (supporting custom tables)
            id_col: Indicates whether the table id column should be returned

        Returns:
            Dictionary of tables, where key is table name and value is dataframe of contents
        """

        result = {}

        for t in table_list:
            result[t] = self.read_table(t, id_col=id_col)

        return result

    def clear_table(self, table_name: str):
        """
        Clear table of all content

        Args:
            table_name: Name of table to be cleared

        Returns:
            None
        """

        table_name = table_name.lower().strip()

        # delete any existing data data from the table
        self.exec_sql(f"DELETE FROM {table_name}")

        return True

    def geocode_table(
        self,
        table_name: str,
        geoprovider: str = "MapBox",
        geoapikey: str = None,
        ignore_low_confidence: bool = True,
    ):
        """
        Geocode a geocodable entity table (Customers, Facilities, Suppliers) in model
        """

        # TODO: This may fail if FrogModel initialised with no app key - i.e. from connection string or engine

        return FrogUtils.geocode_table(
            self.model_name,
            table_name,
            self._app_key,
            geoprovider=geoprovider,
            geoapikey=geoapikey,
            ignore_low_confidence=ignore_low_confidence,
        )

    # Read from model using raw sql query
    def read_sql(self, query: str) -> DataFrame:
        """
        Executes a sql query on the model and returns the results in a dataframe

        Args:
            query: SQL query to be run

        Returns:
            Dataframe containing results of query
        """
        with self.begin() as connection:
            return pd.read_sql_query(query, connection)

    # Execute raw sql on model
    def exec_sql(self, query: str | sql.Composed) -> None:
        with self.begin() as connection:
            connection.execute(text(query))

    # Upsert from a csv file to a model table
    def upsert_csv(self, table_name: str, filename: str, _correlation_id: str = "") -> (int, int):
        """
        Upsert a csv file to a Cosmic Frog model table

        Args:
            table_name: Name of the target Anura table
            filename: Name of csv file to be imported

        Returns:
            updated_rows, inserted_rows
        """
        total_updated = 0
        total_inserted = 0

        for chunk in pd.read_csv(filename, chunksize=CHUNK_SIZE, dtype=str, skipinitialspace=True):
            chunk.replace("", np.nan, inplace=True)
            updated, inserted = self.upsert(table_name, chunk, _correlation_id=_correlation_id)

            total_updated += updated
            total_inserted += inserted

        return total_updated, total_inserted

    # Upsert from an xls file to a model table
    def upsert_excel(
        self, filename: str, activity: ModelActivity = None, _correlation_id: str = ""
    ) -> (int, int):
        """
        Upsert an xlsx file to a Cosmic Frog model table

        Args:
            table_name: Name of the target Anura table
            filename: Name of xlsx file to be imported

        Returns:
            updated_rows, inserted_rows
        """

        # TODO: If an issue could consider another way to load/stream from xlsx maybe?

        with pd.ExcelFile(filename) as xls:
            file_name_without_extension = (
                os.path.basename(filename).replace(".xlsx", "").replace(".xls", "")
            )

            total_sheets = len(xls.sheet_names)

            if total_sheets == 0:
                self.log.warning("Excel file has no sheets")
                return 0, 0

            # For each sheet in the file
            for count, sheet_name in enumerate(xls.sheet_names):
                if activity:
                    # TODO: Support async here
                    activity.update_activity(
                        ActivityStatus.STARTED,
                        last_message=f"Uploading {sheet_name}",
                        progress=int(count / total_sheets),
                    )

                table_to_upload = (
                    file_name_without_extension if sheet_name[:5].lower() == "sheet" else sheet_name
                )

                # Read the entire sheet into a DataFrame
                # Note: For xlsx there is an upper limit of ~1million rows per sheet, so not chunking here

                # TODO: Consider parallelism
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)

                df.columns = df.columns.str.lower().map(str.strip)

                df.replace("", np.nan, inplace=True)

                updated, inserted = self.upsert(
                    table_to_upload, df, _correlation_id=_correlation_id
                )

        # TODO: For xlsx need to handle per table - pending implementation of 'signals'
        return updated, inserted

    def get_table_columns_from_model(self, table_name: str, id_col: bool = False) -> List[str]:
        """
        Fetches all columns direct from database (including custom)

        This gets all actual columns in the model table, including user custom columns
        """
        table_name = table_name.lower().strip()

        # Create an Inspector object
        inspector = inspect(self.engine)

        # Get the column names for a specific table
        column_names = inspector.get_columns(table_name)

        column_names = [column["name"] for column in column_names]

        if not id_col:
            column_names.remove("id")

        return [name.lower().strip() for name in column_names]

    def _get_combined_key_columns_for_upsert(self, table_name: str):

        anura_keys = AnuraSchema.get_anura_keys(self.anura_version, table_name)

        # TODO: Call platform custom columns apis here
        custom_key_columns = ["notes"]

        return anura_keys + custom_key_columns

    def __generate_index_sql(self, index_name, table_name, key_column_list) -> str:
        """
        Creates an appropriate index for Anura tables.
        Coalesce is used to support
        """
        coalesced_columns = ", ".join(
            [f"COALESCE({column}, '{PLACEHOLDER_VALUE}')" for column in key_column_list]
        )

        return f"CREATE INDEX {index_name} ON {table_name}({coalesced_columns});"

    def _create_upsert_index_for_table(
        self, table_name: str, cursor, combined_key_columns=None
    ) -> str:
        """
        Creates an index to aid update/insert performance for upsert
        """

        if combined_key_columns is None:
            combined_key_columns = self._get_combined_key_columns_for_upsert(table_name)

        upsert_index_name = "cf_upsert_index_" + str(uuid.uuid4()).replace("-", "")
        index_sql = self.__generate_index_sql(upsert_index_name, table_name, combined_key_columns)

        start_time = time.time()
        cursor.execute(index_sql)
        end_time = time.time()
        self.log.info(
            f"Index creation took {end_time - start_time} seconds for {table_name}",
        )

        return upsert_index_name

    def upsert(
        self,
        table_name: str,
        data: pd.DataFrame,
        _correlation_id: str = "",  # Optional: correlation id for logging / tracing (for internal use)
    ) -> (int, int):
        """
        Upsert a pandas dataframe to a Cosmic Frog model table

        Args:
            table_name: Name of the target Anura table
            data: A Pandas dataframe containing the data to upsert

        Returns:
            updated_rows, inserted_rows
        """

        table_name = table_name.strip().lower()

        data.columns = data.columns.str.lower().map(str.strip)

        anura_tables = AnuraSchema.get_anura_table_names(self.anura_version)

        table_exists = any(s.lower() == table_name for s in anura_tables)

        if not table_exists:
            # Skip it
            self.log.warning(
                "Table name not recognised as an Anura table (skipping): %s", table_name
            )
            return 0, 0

        self.log.info("Importing to table: %s", table_name)
        self.log.info("Source data has %s rows", len(data))

        # Behavior rules:
        # Key columns - get used to match (Note: possible future requirement, some custom columns may also be key columns)
        # Other Anura columns - get updated
        # Other Custom columns - get updated
        # Other columns (neither Anura or Custom) - get ignored

        all_column_names = self.get_table_columns_from_model(table_name)
        if "id" in all_column_names:
            all_column_names.remove("id")

        # 1) Anura key cols - defined in Anura
        # 2) Custom key cols - TBD CF Meta
        # 3) Update cols - The rest

        combined_key_columns = self._get_combined_key_columns_for_upsert(table_name)

        update_columns = [col for col in all_column_names if col not in combined_key_columns]

        # Skipping unrecognised columns (Do not trust column names from user data)
        cols_to_drop = [col for col in data.columns if col not in all_column_names]

        for col in cols_to_drop:
            self.log.info("Skipping unknown column in %s: %s", table_name, col)

        data = data.drop(cols_to_drop, axis=1)

        # Sometimes no columns match up (including for malformed
        # xlsx files saved in 3rd party tools)
        if len(data.columns) == 0:
            self.log.warning("No columns to import")
            return 0, 0

        updated_rows = 0
        inserted_rows = 0

        # Want to either make a transaction, or a nested transaction depending on the
        # presence or absence of a user transaction (if one exists then nest another,
        # else create a root)
        with self.begin() as connection:

            # Create temporary table
            temp_table_name = "temp_table_" + str(uuid.uuid4()).replace("-", "")
            self.log.info("Moving data to temporary table: %s", temp_table_name)

            # Note: this will also clone custom columns
            create_temp_table_sql = f"""
                /* {_correlation_id} cflib.upsert */
                CREATE TEMPORARY TABLE {temp_table_name} AS
                SELECT *
                FROM {table_name}
                WITH NO DATA;
                """

            connection.execute(text(create_temp_table_sql))

            # Copy data from df to temporary table
            copy_sql = sql.SQL(
                "COPY {table} ({fields}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
            ).format(
                table=sql.Identifier(temp_table_name),
                fields=sql.SQL(", ").join(map(sql.Identifier, data.columns)),
            )

            for column in combined_key_columns:
                if column in data.columns:
                    data[column].fillna(PLACEHOLDER_VALUE, inplace=True)

            with connection.connection.cursor() as cursor:
                start_time = time.time()
                cursor.copy_expert(copy_sql, StringIO(data.to_csv(index=False)))
                self.log.info(
                    f"Copy data to temporary table took {time.time() - start_time} seconds for {table_name}"
                )
                del data

                # Now upsert from temporary table to final table

                # Note: Looked at ON CONFLICT for upsert here, but not possible without
                # defining constraints on target table so doing insert and update separately

                all_columns_list = ", ".join([f'"{col_name}"' for col_name in all_column_names])

                if combined_key_columns:
                    update_column_list = ", ".join(
                        [
                            f'"{col_name}" = "{temp_table_name}"."{col_name}"'
                            for col_name in update_columns
                        ]
                    )
                    key_condition = " AND ".join(
                        [
                            f'COALESCE("{table_name}"."{key_col}", \'{PLACEHOLDER_VALUE}\') = COALESCE("{temp_table_name}"."{key_col}", \'{PLACEHOLDER_VALUE}\')'
                            for key_col in combined_key_columns
                        ]
                    )

                    cursor.execute(
                        f"SET idle_in_transaction_session_timeout = '{CFLIB_IDLE_TRANSACTION_TIMEOUT}s';"
                    )  # Idle transaction timeout in seconds

                    # Pre-locking allows order of rows to be specified, so deadlocks less likely
                    lock_query = f"""
                        /* {_correlation_id} cflib.upsert.lock */
                        SELECT 1
                        FROM {table_name}
                        ORDER BY {table_name}.id
                        FOR UPDATE NOWAIT;
                    """
                    start_time = time.time()
                    cursor.execute(lock_query)
                    updated_rows = cursor.rowcount
                    self.log.info(
                        f"Locking query took {time.time() - start_time} seconds for {table_name}"
                    )

                    # TODO: Indexing is based on the key columns required - this varies per upsert in some cases, due to
                    # allowing custom columns to be part of the index
                    _upsert_index_name = self._create_upsert_index_for_table(
                        table_name, cursor, combined_key_columns
                    )

                    update_query = f"""
                        /* {_correlation_id} cflib.upsert.update */
                        UPDATE {table_name}
                        SET {update_column_list}
                        FROM {temp_table_name}
                        WHERE {key_condition};
                    """
                    start_time = time.time()
                    cursor.execute(update_query)
                    updated_rows = cursor.rowcount
                    self.log.info(
                        f"Update query took {time.time() - start_time} seconds for {table_name}"
                    )

                    start_time = time.time()
                    cursor.execute(update_query)
                    updated_rows = cursor.rowcount
                    self.log.info(
                        f"Update query took {time.time() - start_time} seconds for {table_name}"
                    )

                    temp_columns_list = ", ".join(
                        [f'"{temp_table_name}"."{col_name}"' for col_name in all_column_names]
                    )
                    null_conditions = [
                        f"{table_name}.{col} IS NULL" for col in combined_key_columns
                    ]
                    null_conditions_clause = " AND ".join(null_conditions)

                    insert_query = f"""
                        /* {_correlation_id} cflib.upsert.insert */
                        INSERT INTO {table_name} ({all_columns_list})
                        SELECT {temp_columns_list}
                        FROM {temp_table_name}
                        LEFT JOIN {table_name}
                        ON {key_condition}
                        WHERE {null_conditions_clause}
                    """

                    start_time = time.time()
                    cursor.execute(insert_query)
                    inserted_rows = cursor.rowcount
                    self.log.info(
                        f"Insert query took {time.time() - start_time} seconds for {table_name}"
                    )

                    # Finally remove the index created for upsert
                    cursor.execute(f"DROP INDEX IF EXISTS {_upsert_index_name};")

                # If no key columns, then just insert
                else:
                    insert_query = f"""
                        /* {_correlation_id} cflib.upsert.insert_only */
                        INSERT INTO {table_name} ({all_columns_list})
                        SELECT {all_columns_list}
                        FROM {temp_table_name}
                    """

                    updated_rows = 0
                    self.log.info(f"Running insert query for {table_name}")
                    cursor.execute(insert_query)
                    inserted_rows = cursor.rowcount

                self.log.info("Updated rows  = %s for %s", updated_rows, table_name)
                self.log.info("Inserted rows = %s for %s", inserted_rows, table_name)

        return updated_rows, inserted_rows
