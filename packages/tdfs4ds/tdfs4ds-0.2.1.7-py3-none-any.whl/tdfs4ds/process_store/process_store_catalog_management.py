import teradataml as tdml
import tdfs4ds
from tdfs4ds.utils.query_management import execute_query

def process_store_catalog_creation(if_exists='replace', comment='this table is a process catalog'):
    """
    This function creates a feature store catalog table in Teradata database.
    The catalog table stores information about features such as their names, associated tables, databases, validity periods, etc.

    Parameters:
    - schema: The schema name in which the catalog table will be created.
    - if_exists (optional): Specifies the behavior if the catalog table already exists. The default is 'replace', which means the existing table will be replaced.
    - table_name (optional): The name of the catalog table. The default is 'FS_FEATURE_CATALOG'.

    Returns:
    The name of the created or replaced catalog table.

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