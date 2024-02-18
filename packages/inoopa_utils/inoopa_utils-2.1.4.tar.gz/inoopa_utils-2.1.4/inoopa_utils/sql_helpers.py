from dotenv import load_dotenv
load_dotenv()
import os
from urllib.parse import quote_plus
from sqlalchemy import Engine, create_engine, text

from inoopa_utils.utils.exceptions import MissingEnvVariable
from inoopa_utils.inoopa_logging import create_logger
from pandas import DataFrame


_logger = create_logger("INOOPA.UTILS.SQL_HELPERS")

def get_env_name():
    return os.getenv("ENV", "dev").lower()


def create_sql_engine(mysql_ca_cert_path: str = "/tmp/mysql_ca_cert.cert") -> Engine:
    """
    Create a sqlalchemy engine to use to send SQL requests.

    :param mysql_database: A string with the name of the database to connect to. Default is 'master' the prod database.
    :param mysql_ca_certificate_path: Path where the sql ca certificate should be written to as a file.
    :return: A sqlalchemy engine.
    """
    connection_string = _get_sql_connection_string(mysql_ca_cert_path)
    return create_engine(connection_string, connect_args={'ssl_ca': mysql_ca_cert_path})

def _get_sql_connection_string(mysql_ca_certificate_path: str) -> str:
    """
    Create a connection string from env variables to connect to the MYSQL database.
    Also create a mysql ca certificate file at specified path.

    :param mysql_database: A string with the name of the database to connect to.
    :param mysql_ca_certificate_path: Path where the sql ca certificate should be written to as a file.
    :return: A formatted connection string for sql database
    """
    env_variables = {
        "mysql_host": os.getenv("MYSQL_HOST"),
        "mysql_username": os.getenv("MYSQL_USERNAME"),
        "mysql_password": os.getenv("MYSQL_PASSWORD"),
        "mysql_database_name": os.getenv(f"MYSQL_DATABASE_NAME"),
        "mysql_ca_certificate": os.getenv("MYSQL_CA_CERTIFICATE"),
    }

    missing_variables = []
    for key, value in env_variables.items():
        if value is None:
            _logger.error(f"MYSQL env variable missing: {key}")
            missing_variables.append(key)
    if len(missing_variables) > 0:
        raise MissingEnvVariable(f"Missing env variables: {missing_variables}")

    # Create a ca certificate file to use to create your sql engine
    # This is required with our DB security config
    with open(mysql_ca_certificate_path, "w") as file:
        # Convert the literal '\n' to the actual newline character
        env_variables["mysql_ca_certificate"] = env_variables["mysql_ca_certificate"].replace('\\n', '\n')
        file.write(env_variables["mysql_ca_certificate"])
    _logger.info(f"MYSQL_CA_CERTIFICATE written to: {mysql_ca_certificate_path}")

    return f"mysql+pymysql://{env_variables['mysql_username']}:{quote_plus(env_variables['mysql_password'])}@{env_variables['mysql_host']}/{env_variables['mysql_database_name']}"

def update_df_rows_in_db(df: DataFrame, table_name: str, engine: Engine, primary_key: str = "id") -> None:
    """
    !!! READ THE FULL DOCSTRING BEFORE USAGE !!!
    Update rows in a given SQL table based on the contents of a pandas DataFrame.

    This function will update rows in the specified table based on the DataFrame's 
    rows using the "id" column as the primary key. Only the columns present in 
    the DataFrame will be updated, leaving other columns in the database untouched.

    :param df: (pandas.DataFrame): The DataFrame containing the data to update. 
      It should have an "id" column which acts as the primary key.
    :param table_name: The name of the SQL table to update.

    Notes:
    - We only use this because we don't manipulate much the data in the Dataframe. we follows this pattern: 
        - Get the data from db pd.Dataframe.read_sql(query)
        - Update a few fields
        - Push back the data to DB
    - It is assumed that "id" is the primary key in both the DataFrame and the table.
    - Be cautious when using this function to ensure that the DataFrame's structure 
      matches the table's structure, especially in terms of column data types.
    """
    with engine.begin() as conn:
        for _, row in df.iterrows():
            # Construct an update statement
            update_query = f"UPDATE {table_name} SET "

            # Add each column to the update statement
            update_parts = [f"`{col}` = :{col}" for col in df.columns if col != primary_key]
            update_query += ", ".join(update_parts)
            update_query += f" WHERE {primary_key} = :{primary_key}"

            # Prepare the dictionary with the values from the row
            values = {col: row[col] for col in df.columns if col != primary_key}
            values[primary_key] = row[primary_key]

            prepared_query = text(update_query).bindparams(**values)
            _logger.debug(f"Update query: {prepared_query}")
            conn.execute(prepared_query)
