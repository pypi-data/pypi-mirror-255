import teradataml as tdml
import tdfs4ds
from teradataml.context.context import _get_database_username
from tdfs4ds.utils.visualization import display_table
from tdfs4ds.utils.query_management import execute_query

def prepare_feature_ingestion(df, entity_id, feature_names, feature_versions=None, **kwargs):
    """
    Transforms and prepares a DataFrame for feature ingestion into a feature store.

    This function takes a DataFrame and a set of feature names, and creates a new DataFrame where the features are unpivoted.
    It includes additional columns for entity IDs, feature names, feature values, and optionally, feature versions.
    The function also creates a volatile table in the database to store the transformed data.

    Parameters:
    - df (tdml.DataFrame): The input DataFrame containing the feature data.
    - entity_id (list/dict/other): A representation of the entity ID. If a dictionary, the keys are used as entity IDs.
                                   If a list or another data type, it is used directly as the entity ID.
    - feature_names (list): A list of feature names to be unpivoted from the DataFrame.
    - feature_versions (dict, optional): A dictionary specifying feature versions for given feature names.
                                         The keys are feature names and the values are their corresponding versions.
    - **kwargs: Additional keyword arguments that can be passed to the function.

    Returns:
    tuple: A tuple containing two elements:
           1. A tdml.DataFrame representing the transformed data suitable for feature ingestion.
           2. The name of the volatile table created in the database.

    Note:
    - The function creates a volatile table in the database and constructs a SQL query to transform the data.
    - The transformed DataFrame contains columns for each entity ID, 'FEATURE_NAME', 'FEATURE_VALUE', and 'FEATURE_VERSION'.
    - If 'feature_versions' is not provided, a default version is used for all features.
    - The function handles different data types for 'entity_id' and ensures proper SQL query formation.
    - Additional keyword arguments can be used to customize the behavior of the function.

    Example:
    >>> df = tdml.DataFrame(...)
    >>> entity_id = {'customer_id': 'INTEGER'}
    >>> feature_names = ['feature1', 'feature2']
    >>> transformed_df, volatile_table_name = prepare_feature_ingestion(df, entity_id, feature_names)
    """


    # Create the UNPIVOT clause for the specified feature columns
    unpivot_columns = ", \n".join(["(" + x + ") as '" + x + "'" for x in feature_names])

    if type(entity_id) == list:
        list_entity_id = entity_id
    elif type(entity_id) == dict:
        list_entity_id = list(entity_id.keys())
    else:
        list_entity_id = [entity_id]

    # Create the output column list including entity IDs, feature names, and feature values
    output_columns = ', \n'.join(list_entity_id + ['FEATURE_NAME', 'FEATURE_VALUE'])
    primary_index = ','.join(list_entity_id)

    # Create a dictionary to store feature versions, using the default version if not specified
    versions = {f: tdfs4ds.FEATURE_VERSION_DEFAULT for f in feature_names}
    if feature_versions is not None:
        for k, v in feature_versions.items():
            versions[k] = v

    # Create the CASE statement to assign feature versions based on feature names
    version_query = ["CASE"] + [f"WHEN FEATURE_NAME = '{k}' THEN '{v}' " for k, v in versions.items()] + [
        "END AS FEATURE_VERSION"]
    version_query = '\n'.join(version_query)

    # Create a volatile table name based on the original table's name, ensuring it is unique.
    volatile_table_name = df._table_name.split('.')[1].replace('"', '')
    volatile_table_name = f'temp_{volatile_table_name}'

    if type(entity_id) == list:
        list_entity_id = entity_id
    elif type(entity_id) == dict:
        list_entity_id = list(entity_id.keys())
    else:
        list_entity_id = [entity_id]

    # query casting in varchar everything
    nested_query = f"""
    CREATE VOLATILE TABLE {volatile_table_name} AS
    (
        SELECT 
        {','.join(list_entity_id)},
        {','.join([f'CAST({x} AS VARCHAR(2048)) AS {x}' for x in feature_names])}
        FROM {df._table_name}
    ) WITH DATA
    PRIMARY INDEX ({primary_index})
    ON COMMIT PRESERVE ROWS
    """

    # Execute the SQL query to create the volatile table.
    tdml.execute_sql(nested_query)

    # Construct the SQL query to create the volatile table with the transformed data.
    query = f"""
    SELECT 
    {output_columns},
    {version_query}
    FROM {tdml.in_schema(_get_database_username(), volatile_table_name)} 
    UNPIVOT ((FEATURE_VALUE )  FOR  FEATURE_NAME 
    IN ({unpivot_columns})) Tmp
    """

    # Optionally print the query if the display flag is set.
    if tdml.display.print_sqlmr_query:
        print(query)

    # Return the DataFrame representation of the volatile table and its name.
    return tdml.DataFrame.from_query(query), volatile_table_name


def store_feature(entity_id, prepared_features, **kwargs):
    """
    Stores prepared feature data in specific feature tables within a Teradata database. This function performs updates and inserts
    on the feature tables based on the provided entity IDs and prepared feature data.

    Parameters:
    - entity_id (dict): A dictionary representing the entity ID, where keys are used to identify the entity.
    - prepared_features (tdml.DataFrame): A DataFrame containing the prepared feature data for ingestion.
    - **kwargs: Additional keyword arguments that can include:
        - schema (str): The schema name where the feature tables are located.
        - feature_catalog_name (str, optional): The name of the feature catalog table, defaulting to 'FS_FEATURE_CATALOG'.

    Returns:
    None: This function does not return any value but performs database operations.

    Note:
    - The function uses the Teradata temporal feature (VALIDTIME) for handling the valid time of the records.
    - It constructs SQL queries to update existing feature values and insert new ones based on the entity ID.
    - The function handles the entity ID, feature IDs, and versions for inserting and updating records.
    - It utilizes additional settings from the tdfs4ds module for configuring the feature store time and display logs.
    - This function assumes that the necessary database tables and schema are correctly set up and accessible.

    Example Usage:
    >>> entity_id_dict = {'customer_id': 'INTEGER'}
    >>> prepared_features = tdml.DataFrame(...)
    >>> store_feature(entity_id_dict, prepared_features)
    """

    #feature_catalog = tdml.DataFrame(tdml.in_schema(tdfs4ds.SCHEMA, tdfs4ds.FEATURE_CATALOG_NAME))

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
        validtime_statement2 = validtime_statement
    else:
        validtime_statement = f"VALIDTIME PERIOD '({tdfs4ds.FEATURE_STORE_TIME},{tdfs4ds.END_PERIOD})'"
        validtime_statement2 = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # SQL query to select feature data and corresponding feature metadata from the prepared features and feature catalog
    query = f"""
    {validtime_statement2}
    SELECT
        A.*
    ,   B.FEATURE_ID
    ,   B.FEATURE_TABLE
    ,   B.FEATURE_DATABASE
    FROM {prepared_features._table_name} A,
    {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} B
    WHERE A.FEATURE_NAME = B.FEATURE_NAME
    AND B.DATA_DOMAIN = '{tdfs4ds.DATA_DOMAIN}'
    """

    df = tdml.DataFrame.from_query(query)

    # Group the target tables by feature table and feature database and count the number of occurrences
    target_tables = df[['FEATURE_TABLE', 'FEATURE_DATABASE', 'FEATURE_ID']].groupby(
        ['FEATURE_TABLE', 'FEATURE_DATABASE']).count().to_pandas()
    if tdfs4ds.DISPLAY_LOGS:
        display_table(target_tables[['FEATURE_DATABASE', 'FEATURE_TABLE', 'count_FEATURE_ID']])

    ENTITY_ID = ', \n'.join([k for k, v in entity_id.items()])
    ENTITY_ID_ON = ' AND '.join([f'NEW_FEATURES.{k} = EXISTING_FEATURES.{k}' for k, v in entity_id.items()])
    ENTITY_ID_WHERE_INS = ' OR '.join([f'EXISTING_FEATURES.{k} IS NOT NULL' for k, v in entity_id.items()])
    ENTITY_ID_WHERE_UP = ' OR '.join([f'EXISTING_FEATURES.{k} IS NULL' for k, v in entity_id.items()])

    ENTITY_ID_SELECT = ', \n'.join(['NEW_FEATURES.' + k for k, v in entity_id.items()])
    # Iterate over target tables and perform update and insert operations
    for i, row in target_tables.iterrows():

        ENTITY_ID_WHERE_ = ' AND '.join([f'{row.iloc[0]}.{k}   = UPDATED_FEATURES.{k}' for k, v in entity_id.items()])
        # SQL query to update existing feature values
        query_update = f"""
        {validtime_statement} 
        UPDATE {row.iloc[1]}.{row.iloc[0]}
        FROM (
            {validtime_statement2} 
            SELECT
                {ENTITY_ID_SELECT},
                NEW_FEATURES.FEATURE_ID,
                NEW_FEATURES.FEATURE_VALUE,
                NEW_FEATURES.FEATURE_VERSION
            FROM {df._table_name} NEW_FEATURES
            LEFT JOIN {row.iloc[1]}.{row.iloc[0]} EXISTING_FEATURES
            ON {ENTITY_ID_ON}
            AND NEW_FEATURES.FEATURE_ID = EXISTING_FEATURES.FEATURE_ID
            AND NEW_FEATURES.FEATURE_VERSION = EXISTING_FEATURES.FEATURE_VERSION
            WHERE ({ENTITY_ID_WHERE_INS})
            AND NEW_FEATURES.FEATURE_DATABASE = '{row.iloc[1]}'
            AND NEW_FEATURES.FEATURE_TABLE = '{row.iloc[0]}'
        ) UPDATED_FEATURES
        SET
            FEATURE_VALUE = UPDATED_FEATURES.FEATURE_VALUE
        WHERE     {ENTITY_ID_WHERE_}
        AND {row.iloc[0]}.FEATURE_ID          = UPDATED_FEATURES.FEATURE_ID
            AND {row.iloc[0]}.FEATURE_VERSION = UPDATED_FEATURES.FEATURE_VERSION;
        """

        # SQL query to insert new feature values
        if validtime_statement == 'CURRENT VALIDTIME':
            query_insert = f"""
            {validtime_statement} 
            INSERT INTO {row.iloc[1]}.{row.iloc[0]} ({ENTITY_ID}, FEATURE_ID, FEATURE_VALUE, FEATURE_VERSION)
                SELECT
                    {ENTITY_ID_SELECT},
                    NEW_FEATURES.FEATURE_ID,
                    NEW_FEATURES.FEATURE_VALUE,
                    NEW_FEATURES.FEATURE_VERSION
                FROM {df._table_name} NEW_FEATURES
                LEFT JOIN {row.iloc[1]}.{row.iloc[0]} EXISTING_FEATURES
                ON {ENTITY_ID_ON}
                AND NEW_FEATURES.FEATURE_ID = EXISTING_FEATURES.FEATURE_ID
                AND NEW_FEATURES.FEATURE_VERSION = EXISTING_FEATURES.FEATURE_VERSION
                WHERE ({ENTITY_ID_WHERE_UP})
                AND NEW_FEATURES.FEATURE_DATABASE = '{row.iloc[1]}'
                AND NEW_FEATURES.FEATURE_TABLE = '{row.iloc[0]}'
            """
        elif tdfs4ds.FEATURE_STORE_TIME is not None:
            if tdfs4ds.END_PERIOD == 'UNTIL_CHANGED':
                end_period_ = '9999-01-01 00:00:00'
            else:
                end_period_ = tdfs4ds.END_PERIOD
            query_insert = f"""
            INSERT INTO {row.iloc[1]}.{row.iloc[0]} ({ENTITY_ID}, FEATURE_ID, FEATURE_VALUE, FEATURE_VERSION, ValidStart, ValidEnd)
                SELECT
                    {ENTITY_ID_SELECT},
                    NEW_FEATURES.FEATURE_ID,
                    NEW_FEATURES.FEATURE_VALUE,
                    NEW_FEATURES.FEATURE_VERSION,
                    TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}',
                    TIMESTAMP '{end_period_}'
                FROM {df._table_name} NEW_FEATURES
                LEFT JOIN {row.iloc[1]}.{row.iloc[0]} EXISTING_FEATURES
                ON {ENTITY_ID_ON}
                AND NEW_FEATURES.FEATURE_ID = EXISTING_FEATURES.FEATURE_ID
                AND NEW_FEATURES.FEATURE_VERSION = EXISTING_FEATURES.FEATURE_VERSION
                WHERE ({ENTITY_ID_WHERE_UP})
                AND NEW_FEATURES.FEATURE_DATABASE = '{row.iloc[1]}'
                AND NEW_FEATURES.FEATURE_TABLE = '{row.iloc[0]}'
            """
        entity_id_str = ', \n'.join([k for k, v in entity_id.items()])
        if tdfs4ds.DISPLAY_LOGS: print(
            f'insert feature values of new {entity_id_str} combinations in {row.iloc[1]}.{row.iloc[0]}')
        if tdml.display.print_sqlmr_query:
            print(query_insert)
        execute_query(query_insert)
        if tdfs4ds.DISPLAY_LOGS: print(
            f'update feature values of existing {entity_id_str} combinations in {row.iloc[1]}.{row.iloc[0]}')
        if tdml.display.print_sqlmr_query:
            print(query_update)
        execute_query(query_update)


    return

def prepare_feature_ingestion_tdstone2(df, entity_id):
    """
    Prepares a DataFrame for feature ingestion into a tdstone2 feature store by transforming the data structure.
    This function unpivots the DataFrame and adds necessary columns for entity IDs, feature names, feature values,
    and a predefined feature version. It creates a volatile table in the database to facilitate this transformation.

    Parameters:
    - df (tdml.DataFrame): The input DataFrame containing the feature data. The DataFrame should be structured
      in a way that is compatible with tdstone2 feature store requirements.
    - entity_id (list/dict/other): A representation of the entity ID. If a dictionary, the keys are used as entity IDs.
                                   If a list or another data type, it is used directly as the entity ID.

    Returns:
    - tdml.DataFrame: A transformed DataFrame suitable for feature store ingestion.
    - str: The name of the volatile table created in the database for storing the transformed data.

    Note:
    - The function requires that the input DataFrame 'df' has a valid table name and is compatible with tdml operations.
    - It automatically handles the creation and management of a volatile table in the database.
    - 'ID_PROCESS' is used as the default feature version identifier.
    - The transformed DataFrame includes columns for each entity ID, 'FEATURE_NAME', 'FEATURE_VALUE', and 'FEATURE_VERSION'.

    Example Usage:
    >>> input_df = tdml.DataFrame(...)
    >>> entity_id_dict = {'customer_id': 'INTEGER'}
    >>> transformed_df, table_name = prepare_feature_ingestion_tdstone2(input_df, entity_id_dict)
    """

    # Ensure the internal table name of the DataFrame is set, necessary for further processing.
    df._DataFrame__execute_node_and_set_table_name(df._nodeid, df._metaexpr)

    if type(entity_id) == list:
        list_entity_id = entity_id
    elif type(entity_id) == dict:
        list_entity_id = list(entity_id.keys())
    else:
        list_entity_id = [entity_id]

    # Combine entity ID columns with feature name and value columns to form the output column list.
    output_columns = ', \n'.join(list_entity_id + ['FEATURE_NAME', 'FEATURE_VALUE'])
    primary_index = ','.join(list_entity_id)

    # Define a query segment to assign feature versions.
    version_query = "ID_PROCESS AS FEATURE_VERSION"

    # Create a volatile table name based on the original table's name, ensuring it is unique.
    if tdfs4ds.USE_VOLATILE_TABLE:
        volatile_table_name = df._table_name.split('.')[1].replace('"', '')
        volatile_table_name = f'temp_{volatile_table_name}'
        volatile_verb = 'VOLATILE'
        volatile_expression = 'ON COMMIT PRESERVE ROWS'
    else:
        volatile_table_name = df._table_name.split('.')[1].replace('"', '')
        volatile_table_name = f'"{tdfs4ds.SCHEMA}"."temp_{volatile_table_name}"'
        volatile_verb = ''
        volatile_expression = ''

    # Construct the SQL query to create the volatile table with the transformed data.
    query = f"""
    CREATE {volatile_verb} TABLE {volatile_table_name} AS
    (
    SELECT 
    {output_columns},
    {version_query}
    FROM {df._table_name}
    ) WITH DATA
    PRIMARY INDEX ({primary_index})
    {volatile_expression}
    """
    # Execute the SQL query to create the volatile table.
    tdml.execute_sql(query)

    # Optionally print the query if the display flag is set.
    if tdml.display.print_sqlmr_query:
        print(query)

    # Return the DataFrame representation of the volatile table and its name.
    if tdfs4ds.USE_VOLATILE_TABLE:
        return tdml.DataFrame(tdml.in_schema(_get_database_username(), volatile_table_name)), volatile_table_name
    else:
        return tdml.DataFrame(volatile_table_name), volatile_table_name


