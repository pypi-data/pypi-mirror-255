import teradataml as tdml
import tdfs4ds
from tdfs4ds.utils.query_management import execute_query

def process_store_catalog_creation(if_exists='replace', comment='this table is a process catalog'):
    """
    Create or replace a feature store catalog table in Teradata database.

    This function creates a catalog table in the specified schema of the Teradata database.
    The catalog table is used to store information about features, including their names, associated tables, databases, validity periods, etc.

    Parameters:
    - if_exists (str, optional): Specifies the behavior if the catalog table already exists.
      Default is 'replace', which means the existing table will be replaced.
    - comment (str, optional): A comment to describe the catalog table. Default is 'this table is a process catalog'.

    Returns:
    str: The name of the created or replaced catalog table.

    Notes:
    - The schema in which the catalog table will be created should be specified separately.
    - If the catalog table already exists and if_exists is set to 'replace', the existing table will be dropped and recreated.
    - This function also creates a secondary index on the 'PROCESS_TYPE' column for faster querying.
    - The catalog table structure includes columns for process ID, process type, view name, entity ID, feature names,
      feature version, data domain, metadata, and validity period.
    - This function relies on external global variables and configurations like 'tdfs4ds' and 'tdml' which should be set
      in the environment.
    - It also depends on an 'execute_query' function for executing SQL queries.

    Dependencies:
    - 'tdfs4ds' global variables for schema and table name.
    - 'tdml' for displaying SQL queries (if configured).
    - 'execute_query' for executing SQL queries.
    """

    # SQL query to create the catalog table
    query = f"""
    CREATE MULTISET TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME},
            FALLBACK,
            NO BEFORE JOURNAL,
            NO AFTER JOURNAL,
            CHECKSUM = DEFAULT,
            DEFAULT MERGEBLOCKRATIO,
            MAP = TD_MAP1
            (

                PROCESS_ID VARCHAR(36) NOT NULL,
                PROCESS_TYPE VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
                VIEW_NAME   VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
                ENTITY_ID JSON(32000),
                FEATURE_NAMES VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
                FEATURE_VERSION VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
                DATA_DOMAIN VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
                METADATA JSON(32000),
                ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
                ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
                PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME
            )
            PRIMARY INDEX (PROCESS_ID);
    """

    # SQL query to create a secondary index on the feature name
    query2 = f"CREATE INDEX (PROCESS_TYPE) ON {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME};"

    # SQL query to comment the table
    query3 = f"COMMENT ON TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} IS '{comment}'"

    try:
        # Attempt to execute the create table query
        execute_query(query)
        if tdml.display.print_sqlmr_query:
            print(query)
        if tdfs4ds.DISPLAY_LOGS: print(f'TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} has been created')
        execute_query(query3)
    except Exception as e:
        # If the table already exists and if_exists is set to 'replace', drop the table and recreate it
        if tdfs4ds.DISPLAY_LOGS: print(str(e).split('\n')[0])
        if str(e).split('\n')[0].endswith('already exists.') and (if_exists == 'replace'):
            execute_query(f'DROP TABLE  {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME}')
            print(f'TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} has been dropped')
            try:
                # Attempt to recreate the table after dropping it
                execute_query(query)
                if tdfs4ds.DISPLAY_LOGS: print(f'TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} has been re-created')
                if tdml.display.print_sqlmr_query:
                    print(query)
                execute_query(query3)
            except Exception as e:
                print(str(e).split('\n')[0])

    try:
        # Attempt to create the secondary index
        execute_query(query2)
        if tdml.display.print_sqlmr_query:
            print(query)
        if tdfs4ds.DISPLAY_LOGS: print(f'SECONDARY INDEX ON TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} has been created')
    except Exception as e:
        print(str(e).split('\n')[0])

    return tdfs4ds.PROCESS_CATALOG_NAME