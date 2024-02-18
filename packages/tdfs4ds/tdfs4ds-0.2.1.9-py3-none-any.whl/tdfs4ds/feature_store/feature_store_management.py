import teradataml as tdml
import tdfs4ds
from tdfs4ds.utils.query_management import execute_query
from tdfs4ds.utils.info import get_column_types_simple
from tdfs4ds.feature_store.feature_query_retrieval import get_feature_store_table_name
import pandas as pd

def feature_store_catalog_creation(if_exists='replace', comment='this table is a feature catalog'):
    """
    Creates or replaces a feature store catalog table in a Teradata database. The catalog table stores metadata about
    features such as their names, associated tables and databases, validity periods, and more.

    Parameters:
    - if_exists (str, optional): Specifies the action to be taken if the catalog table already exists.
                                 Options are 'replace' (default) and 'fail'. 'replace' drops the existing table and creates a new one,
                                 while 'fail' will raise an exception if the table already exists.
    - comment (str, optional): A comment to be associated with the catalog table, describing its purpose or other information.
                               The default comment is 'this table is a feature catalog'.

    Returns:
    str: The name of the created or replaced catalog table.

    Note:
    - The function uses default values for the schema and table name from the tdfs4ds module.
    - It creates the catalog table with a primary index on 'FEATURE_ID' and a secondary index on 'FEATURE_NAME'.
    - The function also handles the creation of the table's comment.
    - In case of an existing table and 'if_exists' set to 'replace', it will drop the existing table before creating the new one.
    - The function assumes access to the database and appropriate permissions to create or modify tables.

    Example Usage:
    >>> catalog_table_name = feature_store_catalog_creation()
    >>> print(f"Feature catalog table {catalog_table_name} created successfully.")
    """


    # SQL query to create the catalog table
    query = f"""
    CREATE MULTISET TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME},
            FALLBACK,
            NO BEFORE JOURNAL,
            NO AFTER JOURNAL,
            CHECKSUM = DEFAULT,
            DEFAULT MERGEBLOCKRATIO,
            MAP = TD_MAP1
            (

                FEATURE_ID BIGINT,
                FEATURE_NAME VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
                FEATURE_TABLE VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
                FEATURE_DATABASE VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
                FEATURE_VIEW VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
                ENTITY_NAME VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
                DATA_DOMAIN VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
                ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
                ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
                PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME
            )
            PRIMARY INDEX (FEATURE_ID);
    """

    # SQL query to create a secondary index on the feature name
    query2 = f"CREATE INDEX (FEATURE_NAME) ON {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME};"

    # SQL query to comment the table
    query3 = f"COMMENT ON TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} IS '{comment}'"

    try:
        # Attempt to execute the create table query
        execute_query(query)
        if tdml.display.print_sqlmr_query:
            print(query)
        if tdfs4ds.DISPLAY_LOGS: print(f'TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} has been created')
        execute_query(query3)
    except Exception as e:
        # If the table already exists and if_exists is set to 'replace', drop the table and recreate it
        if tdfs4ds.DISPLAY_LOGS: print(str(e).split('\n')[0])
        if str(e).split('\n')[0].endswith('already exists.') and (if_exists == 'replace'):
            execute_query(f'DROP TABLE  {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}')
            print(f'TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} has been dropped')
            try:
                # Attempt to recreate the table after dropping it
                execute_query(query)
                if tdfs4ds.DISPLAY_LOGS: print(
                    f'TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} has been re-created')
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
        if tdfs4ds.DISPLAY_LOGS: print(
            f'SECONDARY INDEX ON TABLE {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} has been created')
    except Exception as e:
        print(str(e).split('\n')[0])

    return tdfs4ds.FEATURE_CATALOG_NAME


def feature_store_table_creation(entity_id, feature_type, if_exists='fail'):
    """
    Creates a feature store table and a corresponding view in a Teradata database schema. This function is based on the provided entity ID,
    feature type, and an existing feature catalog. It allows for the creation of a table specifically designed for storing feature data.

    Parameters:
    - entity_id (dict): A dictionary mapping column names to their respective entity ID types.
                        These are used for constructing the table and view names.
    - feature_type (str): The type of the feature (e.g., 'FLOAT', 'BIGINT', 'VARCHAR').
    - if_exists (str, optional): Specifies the action to be taken if the table already exists.
                                 Options are 'fail' (default) and 'replace'. 'fail' raises an exception if the table exists,
                                 while 'replace' drops the existing table and creates a new one.

    Returns:
    str: The name of the created feature store table.

    Note:
    - The function uses the default values for the schema and feature catalog name from the tdfs4ds module.
    - It creates the feature store table with a primary index on entity ID, feature ID, and feature version.
    - A secondary index on the feature ID is also created for the table.
    - The corresponding view provides a current valid time snapshot of the features.
    - In the case of an existing table and 'if_exists' set to 'replace', the existing table will be dropped and a new one will be created.
    - The function assumes access to the database and appropriate permissions to create or modify tables.

    Example Usage:
    >>> entity_id_dict = {'customer_id': 'INTEGER'}
    >>> table_name = feature_store_table_creation(entity_id_dict, 'FLOAT')
    >>> print(f"Feature store table {table_name} created successfully.")
    """

    table_name, view_name = get_feature_store_table_name(entity_id, feature_type)
    if tdml.db_list_tables(schema_name=tdfs4ds.SCHEMA, object_name=table_name + '%').shape[0] > 0:
        if tdfs4ds.DISPLAY_LOGS:
            print(f'table {table_name} in the {tdfs4ds.SCHEMA} database already exists. No need to create it.')
        return
    else:
        if tdfs4ds.DISPLAY_LOGS:
            print(f'table {table_name} in the {tdfs4ds.SCHEMA} database does not exists. Need to create it.')

    query_feature_value = {
        'FLOAT': 'FEATURE_VALUE FLOAT',
        'BIGINT': 'FEATURE_VALUE BIGINT',
        'VARCHAR': 'FEATURE_VALUE VARCHAR(2048) CHARACTER SET LATIN'
    }

    # Construct the column definitions for the table based on the entity ID
    ENTITY_ID = ', \n'.join([k + ' ' + v for k, v in entity_id.items()])
    ENTITY_ID_ = ', \n'.join(['B.' + k for k, v in entity_id.items()])
    ENTITY_ID__ = ','.join([k for k, v in entity_id.items()])

    # SQL query to create the feature store table
    query = f"""
    CREATE MULTISET TABLE {tdfs4ds.SCHEMA}.{table_name},
            FALLBACK,
            NO BEFORE JOURNAL,
            NO AFTER JOURNAL,
            CHECKSUM = DEFAULT,
            DEFAULT MERGEBLOCKRATIO,
            MAP = TD_MAP1
            (

                {ENTITY_ID},
                FEATURE_ID BIGINT,
                {query_feature_value[feature_type]},
                FEATURE_VERSION VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
                ValidStart TIMESTAMP(0) WITH TIME ZONE NOT NULL,
                ValidEnd TIMESTAMP(0) WITH TIME ZONE NOT NULL,
                PERIOD FOR ValidPeriod  (ValidStart, ValidEnd) AS VALIDTIME
            )
            PRIMARY INDEX ({ENTITY_ID__},FEATURE_ID,FEATURE_VERSION);
    """

    # SQL query to create a secondary index on the feature ID
    query2 = f"CREATE INDEX (FEATURE_ID) ON {tdfs4ds.SCHEMA}.{table_name};"

    # SQL query to create the view
    query_view = f"""
    REPLACE VIEW {tdfs4ds.SCHEMA}.{view_name} AS
    CURRENT VALIDTIME
    SELECT
        A.FEATURE_NAME,
        {ENTITY_ID_},
        B.FEATURE_VALUE,
        B.FEATURE_VERSION
    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} A
    , {tdfs4ds.SCHEMA}.{table_name} B
    WHERE A.FEATURE_ID = B.FEATURE_ID
    """

    try:
        # Attempt to execute the create table query
        execute_query(query)
        if tdml.display.print_sqlmr_query:
            print(query)
        if tdfs4ds.DISPLAY_LOGS: print(f'TABLE {tdfs4ds.SCHEMA}.{table_name} has been created')
        execute_query(query2)
    except Exception as e:
        # If the table already exists and if_exists is set to 'replace', drop the table and recreate it
        print(str(e).split('\n')[0])
        if str(e).split('\n')[0].endswith('already exists.') and (if_exists == 'replace'):
            execute_query(f'DROP TABLE  {tdfs4ds.SCHEMA}.{table_name}')
            if tdfs4ds.DISPLAY_LOGS: print(f'TABLE {tdfs4ds.SCHEMA}.{table_name} has been dropped')
            try:
                # Attempt to recreate the table after dropping it
                execute_query(query)
                if tdfs4ds.DISPLAY_LOGS: print(f'TABLE {tdfs4ds.SCHEMA}.{table_name} has been re-created')
                if tdml.display.print_sqlmr_query:
                    print(query)
            except Exception as e:
                print(str(e).split('\n')[0])

    try:
        # Attempt to create the view
        execute_query(query_view)
        if tdml.display.print_sqlmr_query:
            print(query)
        if tdfs4ds.DISPLAY_LOGS: print(f'VIEW {tdfs4ds.SCHEMA}.{view_name} has been created')
    except Exception as e:
        print(str(e).split('\n')[0])

    return table_name


def register_features(entity_id, feature_names_types):
    """
    Registers features in the feature catalog table of a Teradata database. This function is used to create or update
    entries in the catalog based on the provided entity ID and feature names and types.

    Parameters:
    - entity_id (dict): A dictionary representing the entity ID, where keys are used to identify the entity.
    - feature_names_types (dict): A dictionary containing feature names and their corresponding types.
                                  The keys are feature names and values are dictionaries with 'type' and 'id' keys.

    Returns:
    pd.DataFrame: A DataFrame containing the registered features and their metadata including feature names, types,
                  IDs, and the details of the corresponding feature store table and view.

    Note:
    - The function updates existing entries in the feature catalog and inserts new entries as needed.
    - It constructs SQL queries to handle the insertion and updating of feature catalog entries.
    - The function uses valid time statements based on the configuration in the tdfs4ds module.
    - It assumes that the feature catalog table already exists in the specified schema.
    - The function is designed to work with Teradata databases and assumes that database access is properly configured.

    Example Usage:
    >>> entity_id_dict = {'customer_id': 'INTEGER'}
    >>> feature_names_types = {'age': {'type': 'BIGINT', 'id': 1}, 'gender': {'type': 'VARCHAR', 'id': 2}}
    >>> registered_features = register_features(entity_id_dict, feature_names_types)
    >>> print(registered_features)
    """

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME PERIOD '({tdfs4ds.FEATURE_STORE_TIME},{tdfs4ds.END_PERIOD})'"

    if len(list(feature_names_types.keys())) == 0:
        if tdfs4ds.DISPLAY_LOGS: print('no new feature to register')
        return

    # Create a comma-separated string of entity IDs
    ENTITY_ID__ = ','.join([k for k, v in entity_id.items()])

    # Create a DataFrame from the feature_names_types dictionary
    if len(feature_names_types.keys()) > 1:
        df = pd.DataFrame(feature_names_types).transpose().reset_index()
        df.columns = ['FEATURE_NAME', 'TYPE', 'FEATURE_ID']
    else:
        df = pd.DataFrame(columns=['FEATURE_NAME', 'TYPE', 'FEATURE_ID'])
        k = list(feature_names_types.keys())[0]
        df['FEATURE_NAME'] = [k]
        df['TYPE'] = [feature_names_types[k]['type']]
        df['FEATURE_ID'] = [feature_names_types[k]['id']]

    # Generate the feature table and view names based on the entity ID and feature type
    df['FEATURE_TABLE'] = df.apply(lambda row: get_feature_store_table_name(entity_id, row.iloc[1])[0], axis=1)
    df['FEATURE_VIEW'] = df.apply(lambda row: get_feature_store_table_name(entity_id, row.iloc[1])[1], axis=1)

    # Add additional columns to the DataFrame
    df['ENTITY_NAME'] = ENTITY_ID__
    df['FEATURE_DATABASE'] = tdfs4ds.SCHEMA
    df['DATA_DOMAIN'] = tdfs4ds.DATA_DOMAIN

    # Copy the DataFrame to a temporary table in Teradata
    tdml.copy_to_sql(df, table_name='temp', schema_name=tdfs4ds.SCHEMA, if_exists='replace', primary_index='FEATURE_ID',
                     types={'FEATURE_ID': tdml.BIGINT})

    # SQL query to update existing entries in the feature catalog
    query_update = f"""
    {validtime_statement} 
    UPDATE {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}
    FROM (
        CURRENT VALIDTIME
        SELECT
            NEW_FEATURES.FEATURE_ID
        ,   NEW_FEATURES.FEATURE_NAME
        ,   NEW_FEATURES.FEATURE_TABLE
        ,   NEW_FEATURES.FEATURE_DATABASE
        ,   NEW_FEATURES.FEATURE_VIEW
        ,   NEW_FEATURES.ENTITY_NAME
        ,   NEW_FEATURES.DATA_DOMAIN
        FROM {tdfs4ds.SCHEMA}.temp NEW_FEATURES
        LEFT JOIN {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} EXISTING_FEATURES
        ON NEW_FEATURES.FEATURE_ID = EXISTING_FEATURES.FEATURE_ID
        AND NEW_FEATURES.DATA_DOMAIN = EXISTING_FEATURES.DATA_DOMAIN
        WHERE EXISTING_FEATURES.FEATURE_NAME IS NOT NULL
    ) UPDATED_FEATURES
    SET
        FEATURE_NAME     = UPDATED_FEATURES.FEATURE_NAME,
        FEATURE_TABLE    = UPDATED_FEATURES.FEATURE_TABLE,
        FEATURE_DATABASE = UPDATED_FEATURES.FEATURE_DATABASE,
        FEATURE_VIEW     = UPDATED_FEATURES.FEATURE_VIEW,
        ENTITY_NAME      = UPDATED_FEATURES.ENTITY_NAME
    WHERE     {tdfs4ds.FEATURE_CATALOG_NAME}.FEATURE_ID = UPDATED_FEATURES.FEATURE_ID
    AND {tdfs4ds.FEATURE_CATALOG_NAME}.DATA_DOMAIN = UPDATED_FEATURES.DATA_DOMAIN;
    """

    # SQL query to insert new entries into the feature catalog
    if validtime_statement == 'CURRENT VALIDTIME':
        query_insert = f"""
        {validtime_statement} 
        INSERT INTO {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} (FEATURE_ID, FEATURE_NAME, FEATURE_TABLE, FEATURE_DATABASE, FEATURE_VIEW, ENTITY_NAME,DATA_DOMAIN)
            SELECT
                NEW_FEATURES.FEATURE_ID
            ,   NEW_FEATURES.FEATURE_NAME
            ,   NEW_FEATURES.FEATURE_TABLE
            ,   NEW_FEATURES.FEATURE_DATABASE
            ,   NEW_FEATURES.FEATURE_VIEW
            ,   NEW_FEATURES.ENTITY_NAME
            ,   NEW_FEATURES.DATA_DOMAIN
            FROM {tdfs4ds.SCHEMA}.temp NEW_FEATURES
            LEFT JOIN {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} EXISTING_FEATURES
            ON NEW_FEATURES.FEATURE_ID = EXISTING_FEATURES.FEATURE_ID
            AND NEW_FEATURES.DATA_DOMAIN = EXISTING_FEATURES.DATA_DOMAIN
            WHERE EXISTING_FEATURES.FEATURE_NAME IS NULL;
        """
    elif tdfs4ds.FEATURE_STORE_TIME is not None:
        if tdfs4ds.END_PERIOD == 'UNTIL_CHANGED':
            end_period_ = '9999-01-01 00:00:00'
        else:
            end_period_ = tdfs4ds.END_PERIOD
        query_insert = f"""
        INSERT INTO {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} (FEATURE_ID, FEATURE_NAME, FEATURE_TABLE, FEATURE_DATABASE, FEATURE_VIEW, ENTITY_NAME,DATA_DOMAIN,ValidStart,ValidEnd)
            SELECT
                NEW_FEATURES.FEATURE_ID
            ,   NEW_FEATURES.FEATURE_NAME
            ,   NEW_FEATURES.FEATURE_TABLE
            ,   NEW_FEATURES.FEATURE_DATABASE
            ,   NEW_FEATURES.FEATURE_VIEW
            ,   NEW_FEATURES.ENTITY_NAME
            ,   NEW_FEATURES.DATA_DOMAIN
            ,   TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'
            ,   TIMESTAMP '{end_period_}'
            FROM {tdfs4ds.SCHEMA}.temp NEW_FEATURES
            LEFT JOIN {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} EXISTING_FEATURES
            ON NEW_FEATURES.FEATURE_ID = EXISTING_FEATURES.FEATURE_ID
            AND NEW_FEATURES.DATA_DOMAIN = EXISTING_FEATURES.DATA_DOMAIN
            WHERE EXISTING_FEATURES.FEATURE_NAME IS NULL;
        """

    # Execute the update and insert queries
    execute_query(query_insert)
    execute_query(query_update)

    return df

def GetTheLargestFeatureID():
    """
    Retrieves the highest feature ID currently in use from the feature catalog table of a Teradata database.

    This function queries the feature catalog table to find the maximum value of the FEATURE_ID column. It is useful for
    identifying the next available feature ID in scenarios where a new feature needs to be added to the catalog.

    Parameters:
    - schema (str): The schema name where the feature catalog table is located.
    - table_name (str, optional): The name of the feature catalog table. Defaults to 'FS_FEATURE_CATALOG'.

    Returns:
    int: The maximum feature ID found in the feature catalog table. If the table is empty, returns 0.

    Note:
    - The function assumes that the feature catalog table exists and is accessible in the specified schema.
    - If the feature catalog table has no entries, the function returns 0, indicating no feature IDs are currently in use.
    - The function is designed for use with Teradata databases and assumes appropriate database access.

    Example Usage:
    >>> max_feature_id = GetTheLargestFeatureID()
    >>> print(f"The largest feature ID is: {max_feature_id}")
    """
    # Execute a SQL query to get the maximum feature ID from the feature catalog table.
    feature_id = execute_query(f'SEL MAX(FEATURE_ID) AS MAX_FEATURE_ID FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}').fetchall()[0][0]

    # If the result of the query is None (which means the table is empty), return 0.
    if feature_id == None:
        return 0
    # If the result of the query is not None, return the maximum feature ID.
    else:
        return feature_id


def GetAlreadyExistingFeatureNames(feature_name, entity_id):
    """
    Retrieves a list of already existing feature names from the feature catalog table in a Teradata database.
    The function checks against a specific feature name and entity ID to determine if similar features already exist in the catalog.

    Parameters:
    - feature_name (str/list): The name(s) of the feature(s) to check. Can be a single feature name or a list of names.
    - entity_id (dict): A dictionary representing the entity ID, where keys are used to identify the entity.
    - schema (str): The schema name where the feature catalog table is located.
    - table_name (str, optional): The name of the feature catalog table. Defaults to 'FS_FEATURE_CATALOG'.

    Returns:
    list: A list of feature names that already exist in the feature catalog table and match the given feature name and entity ID.

    Note:
    - The function creates a temporary table in the database to facilitate the comparison.
    - It assumes that the feature catalog table exists and is accessible in the specified schema.
    - The function is designed for use with Teradata databases and assumes appropriate database access.

    Example Usage:
    >>> entity_id_dict = {'customer_id': 'INTEGER'}
    >>> existing_features = GetAlreadyExistingFeatureNames('age', entity_id_dict)
    >>> print(f"Existing features: {existing_features}")
    """

    # Create a temporary DataFrame with the feature name.
    df = pd.DataFrame({'FEATURE_NAME': feature_name, 'DATA_DOMAIN': tdfs4ds.DATA_DOMAIN, 'ENTITY_NAME': ','.join([k for k,v in entity_id.items()])})

    # Define a temporary table name.
    tmp_name = 'tdfs__fgjnojnsmdoignmosnig'

    # Copy the temporary DataFrame to a temporary table in the Teradata database.
    tdml.copy_to_sql(df, schema_name=tdfs4ds.SCHEMA, table_name=tmp_name, if_exists='replace',
                     types={'FEATURE_NAME': tdml.VARCHAR(length=255, charset='LATIN')})

    # Execute a SQL query to get the feature names that exist in both the temporary table and the feature catalog table.
    existing_features = list(tdml.DataFrame.from_query(f"""
        SEL A.FEATURE_NAME
        FROM {tdfs4ds.SCHEMA}.{tmp_name} A
        INNER JOIN {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} B
        ON A.FEATURE_NAME = B.FEATURE_NAME
        AND A.ENTITY_NAME = B.ENTITY_NAME
        AND A.DATA_DOMAIN = B.DATA_DOMAIN
        """).to_pandas().FEATURE_NAME.values)

    # Return the list of existing features.
    return existing_features


def Gettdtypes(tddf, features_columns, entity_id):
    """
    Retrieves the data types of columns in the provided DataFrame and assigns new feature IDs for columns that are not
    already registered in the feature catalog table of a Teradata database. This function is useful for preparing a
    DataFrame for feature ingestion by ensuring each feature has a unique ID and a recognized data type.

    Parameters:
    - tddf (tdml.DataFrame): The input DataFrame containing the features.
    - features_columns (list): A list of column names in the DataFrame to be considered as features.
    - entity_id (dict): A dictionary representing the entity ID, where keys are used to identify the entity.
    - schema (str): The schema name where the feature catalog table is located.
    - table_name (str, optional): The name of the feature catalog table. Defaults to 'FS_FEATURE_CATALOG'.

    Returns:
    dict: A dictionary where keys are column names from the input DataFrame and values are dictionaries containing
          the type and ID of the feature. The type is determined based on the column's data type in the DataFrame,
          and the ID is either retrieved from the feature catalog (for existing features) or newly assigned.

    Note:
    - The function checks each column in the DataFrame against the feature catalog table to determine if it already exists.
    - New feature IDs are sequentially assigned starting from the highest existing feature ID in the catalog.
    - Currently managed data types include integers (mapped to 'BIGINT') and floats (mapped to 'FLOAT').
      Other data types are mapped to 'VARCHAR'.
    - The function assumes that the feature catalog table exists and is accessible in the specified schema.

    Example Usage:
    >>> input_df = tdml.DataFrame(...)
    >>> feature_columns = ['age', 'income', 'gender']
    >>> entity_id_dict = {'customer_id': 'INTEGER'}
    >>> feature_types = Gettdtypes(input_df, feature_columns, entity_id_dict)
    >>> print(feature_types)
    """
    # Get the data types of the columns in the DataFrame.
    types = get_column_types_simple(tddf, tddf.columns) #dict(tddf.to_pandas(num_rows=10).dtypes)

    # Get the names of the features that already exist in the feature catalog table.
    existing_features = GetAlreadyExistingFeatureNames(tddf.columns, entity_id)

    # Get the maximum feature ID from the feature catalog table.
    feature_id = GetTheLargestFeatureID()

    # Increment the maximum feature ID to create a new feature ID.
    feature_id = feature_id + 1

    # Initialize a dictionary to store the result.
    res = {}

    # Iterate over the data types of the columns in the DataFrame.
    for k, v in types.items():
        # If the column name does not exist in the feature catalog table and is in the list of feature column names...
        if k.upper() not in [n.upper() for n in existing_features] and k.upper() in [n.upper() for n in features_columns]:
            # If the data type of the column is integer...
            if 'int' in str(v):
                # Add an entry to the result dictionary for the column name with its data type and new feature ID.
                res[k] = {'type': 'BIGINT', 'id': feature_id}
            # If the data type of the column is float...
            elif 'float' in str(v):
                # Add an entry to the result dictionary for the column name with its data type and new feature ID.
                res[k] = {'type': 'FLOAT', 'id': feature_id}
            # If the data type of the column is neither integer nor float...
            else:
                res[k] = {'type': 'VARCHAR', 'id': feature_id}
                # Print a message that the data type is not yet managed.
                #if tdfs4ds.DISPLAY_LOGS: print(f'{k} has a type that is not yet managed')

            # Increment the feature ID for the next iteration.
            feature_id += 1

    # Return the result dictionary.
    return res

def tdstone2_Gettdtypes(existing_model, entity_id, display_logs=False):
    """
    Generates a dictionary mapping feature names to their data types and unique feature IDs for a given tdstone2 model.
    The function filters out features that already exist in the feature catalog and includes new features with 'BIGINT'
    or 'FLOAT' data types.

    Args:
        existing_model (object): The tdstone2 model object containing necessary schema and scoring information.
        entity_id (dict): A dictionary representing the entity ID, where keys are used to identify the entity.
        display_logs (bool, optional): Flag to indicate whether to display logs. Defaults to False.

    Returns:
        dict: A dictionary with feature names as keys. Each key's value is a dictionary containing 'type' (either 'BIGINT' or 'FLOAT') and 'id' (unique feature ID).

    Raises:
        ValueError: If the data types encountered in the model are neither integer ('int') nor float ('float').

    Note:
        - This function is specifically designed for tdstone2 model objects.
        - It assumes that the feature catalog already exists and is accessible.
        - Unique IDs for new features are automatically generated, starting from the largest existing feature ID in the catalog.
        - Existing features in the catalog are not included in the output dictionary.

    Example Usage:
        model = <instance of tdstone2 model>
        entity_id_dict = {'customer_id': 'INTEGER'}
        feature_types = tdstone2_Gettdtypes(model, entity_id_dict)
        # feature_types might look like {'feature1': {'type': 'BIGINT', 'id': 101}, 'feature2': {'type': 'FLOAT', 'id': 102}}
    """

    # Initialize an empty dictionary to store feature names and their types.
    types = {}

    # Create a DataFrame based on the model's schema and scores repository.
    if 'score' in [x[0] for x in inspect.getmembers(type(existing_model))]:
        df = existing_model.get_model_predictions()
    else:
        #if existing_model.feature_engineering_type == 'feature engineering reducer':
        df = existing_model.get_computed_features()

    # Group and count the DataFrame by feature name and type, converting it to a pandas DataFrame.
    df_ = df[['FEATURE_NAME', 'FEATURE_TYPE', 'FEATURE_VALUE']].groupby(['FEATURE_NAME', 'FEATURE_TYPE']).count()[
        ['FEATURE_NAME', 'FEATURE_TYPE']].to_pandas()

    # Iterate through the DataFrame to filter and assign types.
    for i, row in df_.iterrows():
        if 'float' in row['FEATURE_TYPE'] or 'int' in row['FEATURE_TYPE']:
            types[row['FEATURE_NAME']] = row['FEATURE_TYPE']

    # Retrieve existing feature names to filter out already cataloged features.
    existing_features = GetAlreadyExistingFeatureNames(types.keys(),entity_id)

    # Get the current maximum feature ID to ensure uniqueness for new features.
    feature_id = GetTheLargestFeatureID() + 1

    # Initialize a dictionary to store the result.
    res = {}

    # Process each feature type and assign a corresponding data type and unique ID.
    for k, v in types.items():
        if k not in existing_features and k in types.keys():
            if 'int' in str(v):
                res[k] = {'type': 'BIGINT', 'id': feature_id}
            elif 'float' in str(v):
                res[k] = {'type': 'FLOAT', 'id': feature_id}
            else:
                if tdfs4ds.DISPLAY_LOGS:
                    print(f'{k} has a type that is not yet managed')
                continue  # Skip this iteration for unmanaged types.
            feature_id += 1

    # Return the dictionary containing feature names, types, and IDs.
    return res