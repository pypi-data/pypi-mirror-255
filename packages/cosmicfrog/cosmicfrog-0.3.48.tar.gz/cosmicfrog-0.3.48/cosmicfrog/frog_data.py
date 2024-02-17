"""
    Helper functions for working with Cosmic Frog models
"""

import os
import sys
import json
import time
import uuid
from typing import Dict, List, Type, Optional
from contextlib import contextmanager
from io import StringIO
from collections.abc import Iterable
from contextlib import contextmanager
from pandas import DataFrame
import pkg_resources
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError
from psycopg2 import sql
from .frog_platform import OptilogicClient
from .frog_log import get_logger
from .frog_activity import ModelActivity, ActivityStatus

# TODO:
# Will need extensions for custom tables in a model
# Profile parallel write for xlsx
# Add batching to standard table writing

# Define chunk size (number of rows to write per chunk)
CHUNK_SIZE = 1000000

MASTERLIST_STABLE = "anura27/anuraMasterTableList.json"
TABLES_STABLE = "anura27/table_definitions"
SCHEMA_STABLE = "anura_2_7"

# TODO: Not currently supported, pending 2.8
MASTERLIST_PREVIEW = "anura27/anuraMasterTableList.json"
TABLES_PREVIEW = "anura27/table_definitions"
SCHEMA_PREVIEW = "anura_2_7"

MASTERLIST_PATH = MASTERLIST_STABLE
TABLES_PATH = TABLES_STABLE
DEFAULT_SCHEMA = SCHEMA_STABLE

# For key columns, replace Null with placeholder
# For matching on key columns only, will not be written to final table!
PLACEHOLDER_VALUE = ""  # replace with a value that does not appear in your data

CFLIB_STATEMENT_TIMEOUT = (
    os.getenv("CFLIB_STATEMENT_TIMEOUT") or 1800000
)  # Statement timeout in milliseconds = 30 minutes
CFLIB_IDLE_TRANSACTION_TIMEOUT = os.getenv("CFLIB_IDLE_TRANSACTION_TIMEOUT") or 1800
CFLIB_CONNECT_TIMEOUT = (
    os.getenv("CFLIB_CONNECT_TIMEOUT") or 15
)  # Connection timeout in seconds
CFLIB_DEFAULT_MAX_RETRIES = os.getenv("CFLIB_DEFAULT_MAX_RETRIES") or 5
CFLIB_DEFAULT_RETRY_DELAY = os.getenv("CFLIB_DEFAULT_RETRY_DELAY") or 5


def create_engine_with_retry(
    logger,
    connection_string: str,
    application_name: str,
    max_retries: int = CFLIB_DEFAULT_MAX_RETRIES,
    retry_delay: int = CFLIB_DEFAULT_RETRY_DELAY,
) -> sqlalchemy.Engine:
    """
    Wrapper for sqlalchemy.create_engine - adds ping with retries, to ensure connection is valid for use
    """

    connection_string = f"{connection_string}&application_name={application_name}"

    engine = sqlalchemy.create_engine(
        connection_string,
        connect_args={"connect_timeout": CFLIB_CONNECT_TIMEOUT},
        execution_options={"statement_timeout": CFLIB_STATEMENT_TIMEOUT},
    )

    for attempt in range(max_retries):
        try:
            # Attempt to establish a connection and successful ping
            with engine.connect() as connection:
                connection.execute(
                    text(
                        f"SET idle_in_transaction_session_timeout = '{CFLIB_IDLE_TRANSACTION_TIMEOUT}s';"
                    )  # Idle transaction timeout in seconds
                )
                return engine

        except OperationalError:
            logger.warning("create_engine_with_retry: Database not ready, retrying")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise  # Re-raise the exception if all retries fail


class ValidationError(Exception):
    """Exception raised for validation errors.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


class AnuraTableData:
    anura_all_tablelist_orig: List[str] = []
    anura_input_tablelist_orig: List[str] = []
    anura_output_tablelist_orig: List[str] = []
    anura_all_tablelist: List[str] = []
    anura_input_tablelist: List[str] = []
    anura_output_tablelist: List[str] = []

    anura_keys: Dict[str, List[str]] = {}
    anura_cols: Dict[str, List[str]] = {}


class FrogModel:
    """
    FrogModel class with helper functions for accessing Cosmic Frog models
    """

    _app_key = None

    # Do not use directly, use get_tablelist()
    __anura_masterlist = None
    __anura_tabledata = None

    @classmethod
    def __get_anura_masterlist(cls: Type["FrogModel"]) -> List:
        # Lazy initializer for masterlist
        if cls.__anura_masterlist is None:
            cls.__anura_masterlist = cls.__read_anura_masterlist()
        return cls.__anura_masterlist

    @staticmethod
    def __read_anura_masterlist():
        file_path = pkg_resources.resource_filename(__name__, MASTERLIST_PATH)

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def __get_anura_tablelists(cls: Type["FrogModel"]):
        # Lazy initialiser for table data
        if cls.__anura_tabledata is None:
            cls.__anura_tabledata = cls.__read_anura_tabledata()
        return cls.__anura_tabledata

    @staticmethod
    def __read_anura_tabledata():
        tabledata = AnuraTableData()

        # Pre-calculate some commonly used table lists
        for field in FrogModel.__get_anura_masterlist():
            table_name = field["Table"]

            tabledata.anura_all_tablelist_orig.append(table_name)
            tabledata.anura_all_tablelist.append(table_name.lower())

            # Table names where the Category does not begin with "Output"
            if field["Category"].startswith("Output"):
                tabledata.anura_output_tablelist_orig.append(table_name)
                tabledata.anura_output_tablelist.append(table_name.lower())
            else:
                tabledata.anura_input_tablelist_orig.append(table_name)
                tabledata.anura_input_tablelist.append(table_name.lower())

            # TODO: This takes a moment, could potentially be initialised separately to table data above
            FrogModel.__read_pk_columns(tabledata)

        return tabledata

    @staticmethod
    def __read_pk_columns(target: AnuraTableData) -> None:
        file_path = pkg_resources.resource_filename(__name__, TABLES_PATH)

        # Iterate over each file in the directory
        for filename in os.listdir(file_path):
            filepath = os.path.join(file_path, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            table_name = data.get("TableName").lower()

            # Extract the column names where "PK" is "Yes"
            target.anura_cols[table_name] = [
                field["Column Name"].lower() for field in data.get("fields", [])
            ]
            target.anura_keys[table_name] = [
                field["Column Name"].lower()
                for field in data.get("fields", [])
                if field.get("PK") == "Yes"
            ]

    @classmethod
    def get_tablelist(
        cls: Type["FrogModel"],
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
        assert not (
            input_only and output_only
        ), "input_only and output_only cannot both be True"

        if technology_filter:
            filtered_data = [
                field
                for field in cls.__get_anura_masterlist()
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

        # Common un filtered cases are pre-calculated
        if input_only:
            if original_names:
                return cls.__get_anura_tablelists().anura_input_tablelist_orig

            return cls.__get_anura_tablelists().anura_input_tablelist

        if output_only:
            if original_names:
                return cls.__get_anura_tablelists().anura_output_tablelist_orig

            return cls.__get_anura_tablelists().anura_output_tablelist

        if original_names:
            return cls.__get_anura_tablelists().anura_all_tablelist_orig

        return cls.__get_anura_tablelists().anura_all_tablelist

    @classmethod
    def get_columns(cls: Type["FrogModel"], table_name: str) -> List[str]:
        """Get a list of Anura columns for the given table"""

        lower_name = table_name.lower()

        return FrogModel.__get_anura_tablelists().anura_cols[lower_name]

    @classmethod
    def get_key_columns(cls: Type["FrogModel"], table_name: str) -> List[str]:
        """Get a list of Anura 'key' columns for the given table"""

        lower_name = table_name.lower()

        return FrogModel.__get_anura_tablelists().anura_keys[lower_name]

    def __init__(
        self,
        model_name: Optional[str] = None,
        connection_string: Optional[str] = None,
        engine: Optional[sqlalchemy.engine.Engine] = None,
        application_name: str = "CosmicFrog User Library",
    ) -> None:
        self.model_name = None
        self.engine = None
        self.connection = None
        self.transactions = []
        self.log = get_logger()
        self.default_schema = None
        # If running in Atlas, then we just need a model name
        # or on desktop read in 'app.key'
        if model_name and not (connection_string or engine):
            # App key can be got from multiple places
            # 1) Via utility command line (stored in class var during load, see frog_launcher.py)
            # 2) Via Enviroment var, in Andromeda
            # 3) Via app.key file, when running locally

            if FrogModel._app_key:
                job_app_key = FrogModel._app_key
            else:
                job_app_key = os.environ.get("OPTILOGIC_JOB_APPKEY")

            if not job_app_key:
                initial_script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
                file_path = os.path.join(initial_script_dir, "app.key")

                # If local file 'app.key' exists then assume it contains a valid app key
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as file:
                        job_app_key = file.read().strip()

            oc = OptilogicClient(appkey=job_app_key)

            success, connection_string = oc.get_connection_string(model_name)

            if not success:
                raise ValueError(
                    f"Cannot get connection string for frog model: {model_name}"
                )

            self.engine = create_engine_with_retry(
                self.log, connection_string, application_name
            )

        # Initialise connection
        elif engine:
            self.engine = engine
        elif connection_string:
            self.engine = create_engine_with_retry(
                self.log, connection_string, application_name
            )

        # Validate schema
        with self.engine.connect() as connection:
            result = connection.execute(text("SELECT current_schema()"))
            row = result.fetchone()
            self.default_schema = row[0]

        # Temporary: Tie library to a single Anura version per instance
        assert (
            self.default_schema == DEFAULT_SCHEMA
        ), f"Unrecognised Anura version for this model: {self.default_schema}"

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
        connection = None
        try:
            # Decide the context based on the transaction state
            if self.transactions:  # If user has opened a transaction, then nest one
                connection = self.transactions[-1].connection
                transaction = connection.begin_nested()
            else:  # else start a new one
                connection = self.engine.connect()
                transaction = connection.begin()

            yield connection  # yield the connection, not the transaction

            transaction.commit()  # commit the transaction if everything goes well

        except Exception:
            transaction.rollback()
            raise
        finally:
            # If the connection was created in this method, close it.
            if not self.transactions:
                connection.close()

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

    def geocode_table(self, table_name: str):
        """
        Geocode a geocodable entity table (Customers, Facilities, Suppliers) in model
        """

        table_name = table_name.lower().strip()

        if table_name not in ["customers", "facilities", "suppliers"]:
            raise ValidationError("Table must be customers, facilities or suppliers")

        # Geocode a table
        HYPNO_URL = ""  # Pending new API Production

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
    def upsert_csv(
        self, table_name: str, filename: str, _correlation_id: str = ""
    ) -> (int, int):
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

        for chunk in pd.read_csv(
            filename, chunksize=CHUNK_SIZE, dtype=str, skipinitialspace=True
        ):
            chunk.replace("", np.nan, inplace=True)
            updated, inserted = self.upsert(
                table_name, chunk, _correlation_id=_correlation_id
            )

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
                    file_name_without_extension
                    if sheet_name[:5].lower() == "sheet"
                    else sheet_name
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

    def get_table_columns_from_model(
        self, table_name: str, id_col: bool = False
    ) -> List[str]:
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

    @contextmanager
    def _optional_connection(self, external_connection=None):
        """
        Helper to allow upsert to be called with/without a given connection
        """
        if external_connection is None:
            with self.begin() as connection:
                yield connection
        else:
            yield external_connection

    def _get_combined_key_columns_for_upsert(self, table_name: str):
        anura_key_columns = FrogModel.__get_anura_tablelists().anura_keys[table_name]

        # TODO: Call platform custom columns apis here
        custom_key_columns = ["notes"]

        return anura_key_columns + custom_key_columns

    def __generate_index_sql(self, index_name, table_name, key_column_list) -> str:
        """
        Creates an appropriate index for Anura tables.
        Coalesce is used to support
        """
        coalesced_columns = ", ".join(
            [f"COALESCE({column}, '{PLACEHOLDER_VALUE}')" for column in key_column_list]
        )

        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({coalesced_columns});"

        return sql

    def _create_upsert_index_for_table(
        self, table_name: str, cursor, combined_key_columns=None
    ) -> str:
        """
        Creates an index to aid update/insert performance for upsert
        """

        if combined_key_columns is None:
            combined_key_columns = self._get_combined_key_columns_for_upsert(table_name)

        upsert_index_name = "cf_upsert_index_" + str(uuid.uuid4()).replace("-", "")
        index_sql = self.__generate_index_sql(
            upsert_index_name, table_name, combined_key_columns
        )

        start_time = time.time()
        cursor.execute(index_sql)
        end_time = time.time()
        self.log.info(
            "Index creation took %s seconds for %s",
            end_time - start_time,
            table_name,
        )

        return upsert_index_name

    def upsert(
        self,
        table_name: str,
        data: pd.DataFrame,
        _correlation_id: str = "",  # Optional: correlation id for logging / tracing (for internal use)
        _external_connection=None,  # Optional: pre-existing connection (for internal use)
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

        anura_tables = FrogModel.get_tablelist()

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

        update_columns = [
            col for col in all_column_names if col not in combined_key_columns
        ]

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

        # Want to either make a transaction, or a nested transaction depending on the
        # presence or absence of a user transaction (if one exists then nest another,
        # else create a root)
        with self._optional_connection(_external_connection) as connection:
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
                end_time = time.time()
                self.log.info(
                    "Copy data from %s to temporary table took %s seconds",
                    table_name,
                    end_time - start_time,
                )
                del data

                _upsert_index_name = self._create_upsert_index_for_table(
                    table_name, cursor, combined_key_columns
                )

                # Now upsert from temporary table to final table

                # Note: Looked at ON CONFLICT for upsert here, but not possible without
                # defining constraints on target table so doing insert and update separately

                all_columns_list = ", ".join(
                    [f'"{col_name}"' for col_name in all_column_names]
                )

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

                    update_query = f"""
                        /* {_correlation_id} cflib.upsert */
                        UPDATE {table_name}
                        SET {update_column_list}
                        FROM {temp_table_name}
                        WHERE {key_condition};
                    """

                    start_time = time.time()
                    cursor.execute(update_query)
                    updated_rows = cursor.rowcount
                    end_time = time.time()
                    self.log.info(
                        "Update query took %s seconds for %s",
                        end_time - start_time,
                        table_name,
                    )

                    temp_columns_list = ", ".join(
                        [
                            f'"{temp_table_name}"."{col_name}"'
                            for col_name in all_column_names
                        ]
                    )
                    null_conditions = [
                        f"{table_name}.{col} IS NULL" for col in combined_key_columns
                    ]
                    null_conditions_clause = " AND ".join(null_conditions)

                    insert_query = f"""
                        /* {_correlation_id} cflib.upsert */
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
                    end_time = time.time()
                    self.log.info(
                        "Insert query took %s seconds for %s",
                        end_time - start_time,
                        table_name,
                    )

                    # Finally remove the index created for upsert
                    cursor.execute(f"DROP INDEX IF EXISTS {_upsert_index_name};")

                # If no key columns, then just insert
                else:
                    insert_query = f"""
                        /* {_correlation_id} cflib.upsert */
                        INSERT INTO {table_name} ({all_columns_list})
                        SELECT {all_columns_list}
                        FROM {temp_table_name}
                    """

                    updated_rows = 0
                    self.log.info("Running insert query for %s", table_name)
                    cursor.execute(insert_query)
                    inserted_rows = cursor.rowcount

        self.log.info("Updated rows  = %s for %s", updated_rows, table_name)
        self.log.info("Inserted rows = %s for %s", inserted_rows, table_name)

        return updated_rows, inserted_rows
