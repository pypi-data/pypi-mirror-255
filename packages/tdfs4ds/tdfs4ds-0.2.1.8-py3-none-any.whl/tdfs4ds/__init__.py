__version__ = '0.2.1.8'

DATA_DOMAIN             = None
SCHEMA                  = None
FEATURE_CATALOG_NAME    = 'FS_FEATURE_CATALOG'
PROCESS_CATALOG_NAME    = 'FS_PROCESS_CATALOG'

END_PERIOD              = 'UNTIL_CHANGED' #'9999-01-01 00:00:00'
FEATURE_STORE_TIME      = None
FEATURE_VERSION_DEFAULT = 'dev.0.0'
DISPLAY_LOGS            = True
DEBUG_MODE              = False

import warnings
warnings.filterwarnings('ignore')

import teradataml as tdml
from teradataml.context.context import _get_current_databasename
from tdfs4ds.utils.info import get_column_types
from tdfs4ds.utils.query_management import execute_query
from tdfs4ds.feature_store.feature_store_management import feature_store_catalog_creation
from tdfs4ds.process_store.process_store_catalog_management import process_store_catalog_creation
from tdfs4ds.feature_store.entity_management import register_entity, tdstone2_entity_id
from tdfs4ds.feature_store.feature_store_management import Gettdtypes,register_features, tdstone2_Gettdtypes
from tdfs4ds.feature_store.feature_data_processing import prepare_feature_ingestion,store_feature, prepare_feature_ingestion_tdstone2
from tdfs4ds.utils.info import get_column_types
from tdfs4ds.utils.query_management import execute_query
from tdfs4ds.process_store.process_registration_management import register_process_view
import inspect
import tqdm

try:
    SCHEMA = _get_current_databasename()
    if SCHEMA is None:
        print('Please specify the database which is hosting the feature store.')
        print('tdfs4ds.feature_store.schema = "<feature store database>"')
    else:
        print('The default database is used for the feature store.')
        print(f"tdfs4ds.feature_store.schema = '{SCHEMA}'")
        if DATA_DOMAIN is None:
            DATA_DOMAIN = SCHEMA
            print(f"the data domain for the current work is :{DATA_DOMAIN}")
            print("Please update it as you wish with tdfs4ds.DATA_DOMAIN=<your data domain>")

except Exception as e:
    print('Please specify the database which is hosting the feature store.')
    print('tdfs4ds.feature_store.schema = "<feature store database>"')


def setup(database, if_exists='fail'):
    """
    Set up the database environment by configuring schema names and optionally dropping existing tables.

    This function sets the database schema for feature and process catalogs. If specified, it also handles
    the replacement of existing catalog tables. It reports the status of these operations, including any
    encountered exceptions.

    Parameters:
    database (str): The name of the database schema to be used.
    if_exists (str, optional): Determines the behavior if catalog tables already exist in the database.
                               'fail' (default) - Do nothing if the tables exist.
                               'replace' - Drop the tables if they exist before creating new ones.

    Steps performed:
    1. Sets the schema to the provided database name.
    2. If 'if_exists' is 'replace', attempts to drop 'FS_FEATURE_CATALOG' and 'FS_PROCESS_CATALOG' tables.
    3. Creates new feature and process catalog tables and sets their names in the tdfs4ds module.
    4. Prints the names of the newly created tables along with the database name.
    5. Captures and prints the first line of any exceptions that occur during these operations.

    Returns:
    None
    """

    global SCHEMA
    global FEATURE_CATALOG_NAME
    global PROCESS_CATALOG_NAME

    SCHEMA = database
    if if_exists == 'replace':
        try:
            tdml.db_drop_table(table_name = 'FS_FEATURE_CATALOG', schema_name=database)
        except Exception as e:
            print(str(e).split('\n')[0])
        try:
            tdml.db_drop_table(table_name = 'FS_PROCESS_CATALOG', schema_name=database)
        except Exception as e:
            print(str(e).split('\n')[0])
    try:
        FEATURE_CATALOG_NAME = feature_store_catalog_creation()
        print('feature catalog table: ', FEATURE_CATALOG_NAME, ' in database ', database)
    except Exception as e:
        print(str(e).split('\n')[0])

    try:
        PROCESS_CATALOG_NAME = process_store_catalog_creation()
        print('process catalog table: ', PROCESS_CATALOG_NAME, ' in database ', database)
    except Exception as e:
        print(str(e).split('\n')[0])

    return

def run(process_id, return_dataset = False):
    """
    Executes a specific process from the feature store identified by the process ID.
    The function handles different process types and performs appropriate actions.

    Args:
    process_id (str): The unique identifier of the process to run.
    as_date_of (str, optional): Date parameter for the process execution. Defaults to None.

    Returns:
    None: The function returns None, but performs operations based on process type.
    """

    global FEATURE_STORE_TIME
    global SCHEMA
    global PROCESS_CATALOG_NAME
    global DATA_DOMAIN

    if FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{FEATURE_STORE_TIME}'"

    # Construct SQL query to retrieve process details by process ID
    query = f"""
    {validtime_statement}
    SEL * FROM {SCHEMA}.{PROCESS_CATALOG_NAME}
    WHERE PROCESS_ID = '{process_id}'
    """

    # Executing the query and converting the result to Pandas DataFrame
    df = tdml.DataFrame.from_query(query).to_pandas()

    # Check if exactly one record is returned, else print an error
    if df.shape[0] != 1:
        print('error - there is ', df.shape[0], f' records. Check table {SCHEMA}.{PROCESS_CATALOG_NAME}')
        return

    # Fetching the process type from the query result
    process_type = df['PROCESS_TYPE'].values[0]

    # Fetching the data domain from the query result
    DATA_DOMAIN = df['DATA_DOMAIN'].values[0]

    # Handling 'denormalized view' process type
    if process_type == 'denormalized view':
        # Extracting necessary details for this process type
        view_name = df['VIEW_NAME'].values[0]
        entity_id = eval(df['ENTITY_ID'].values[0])
        feature_names = df['FEATURE_NAMES'].values[0].split(',')

        # Fetching data and uploading features to the feature store
        df_data = tdml.DataFrame(tdml.in_schema(view_name.split('.')[0], view_name.split('.')[1]))

        dataset = _upload_features(
            df_data,
            entity_id,
            feature_names,
            feature_versions = process_id)

    # Handling 'tdstone2 view' process type
    elif process_type == 'tdstone2 view':
        print('not implemented yet')

    if return_dataset:
        return dataset
    else:
        return

def upload_features(df, entity_id, feature_names, metadata={}):
    """
    Uploads features from a dataframe to a specified entity, registering the process and returning the resulting dataset.

    Args:
        df (DataFrame): The dataframe containing the features to be uploaded.
        entity_id (dict or compatible type): The entity identifier. If not a dictionary, it will be converted using `get_column_types`.
        feature_names (list): The list of feature names to be uploaded.
        metadata (dict, optional): Additional metadata to associate with the upload. Defaults to an empty dictionary.

    Returns:
        DataFrame: The dataset resulting from the upload process.
    """

    # Convert entity_id to a dictionary if it's not already one
    if type(entity_id) != dict:
        entity_id = get_column_types(df, entity_id)
        print('entity_id has been converted to a proper dictionary : ', entity_id)

    # Register the process and retrieve the SQL query to insert the features, and the process ID
    query_insert, process_id = register_process_view.__wrapped__(
        view_name=df,
        entity_id=entity_id,
        feature_names=feature_names,
        metadata=metadata,
        with_process_id=True
    )

    # Execute the SQL query to insert the features into the database
    execute_query(query_insert)

    # Run the registered process and return the resulting dataset
    dataset = run(process_id=process_id, return_dataset=True)

    return dataset

def _upload_features(df, entity_id, feature_names,
                   feature_versions=FEATURE_VERSION_DEFAULT):
    """
    This function uploads features from a Teradata DataFrame to the feature store.

    Parameters:
    - df: The input Teradata DataFrame.
    - entity_id: The ID of the entity that the features belong to.
    - feature_names: A list of feature names.
    - schema_name: The name of the schema where the feature store resides.
    - feature_catalog_name (optional): The name of the feature catalog table. Default is 'FS_FEATURE_CATALOG'.
    - feature_versions (optional): The versions of the features. Can be a string or a list. If it's a string, it's used as the version for all features. If it's a list, it should have the same length as feature_names. Default is 'dev.0.0'.

    Returns:
    A DataFrame representing the dataset view created in the feature store.
    """


    register_entity(entity_id)

    # If feature_versions is a list, create a dictionary mapping each feature name to its corresponding version.
    # If feature_versions is a string, create a dictionary mapping each feature name to this string.
    if type(feature_versions) == list:
        selected_features = {k: v for k, v in zip(feature_names, feature_versions)}
    else:
        selected_features = {k: feature_versions for k in feature_names}

    # Get the Teradata types of the features in df.
    feature_names_types = Gettdtypes(
        df,
        features_columns=feature_names,
        entity_id=entity_id
    )

    # Register the features in the feature catalog.
    register_features(
        entity_id,
        feature_names_types
    )

    # Prepare the features for ingestion.
    prepared_features, volatile_table_name = prepare_feature_ingestion(
        df,
        entity_id,
        feature_names,
        feature_versions=selected_features
    )

    # Store the prepared features in the feature store.
    store_feature(
        entity_id,
        prepared_features
    )

    # Clean up by dropping the temporary volatile table.
    tdml.execute_sql(f'DROP TABLE {volatile_table_name}')

    # Build a dataset view in the feature store.
    dataset = build_dataset(
        entity_id,
        selected_features,
        view_name=None
    )

    # Return the dataset view.
    return dataset

def build_dataset(entity_id, selected_features, view_name,
                  comment='dataset', no_temporal=False, time_manager=None, query_only=False):
    """
    This function builds a dataset view in a Teradata database. It is designed to pivot and format data from the feature catalog and feature tables based on the specified parameters.

    Parameters:
    - entity_id (dict or list or other): A dictionary, list, or other format representing the entity ID. The keys of the dictionary are used to identify the entity. Lists and other formats are converted to a list of keys.
    - selected_features (dict): A dictionary specifying the selected features and their corresponding feature versions.
    - view_name (str): The name of the dataset view to be created.
    - comment (str, optional): A comment to associate with the dataset view. Defaults to 'dataset'.
    - no_temporal (bool, optional): Flag to determine if temporal aspects should be ignored. Defaults to False.
    - time_manager (object, optional): An object to manage time aspects. Defaults to None.
    - query_only (bool, optional): Flag to determine if we want only the generated query without the execution

    Returns:
    tdml.DataFrame: A DataFrame representing the dataset view.
    """

    global FEATURE_STORE_TIME
    global SCHEMA
    global FEATURE_CATALOG_NAME
    global DATA_DOMAIN
    global DISPLAY_LOGS

    # Retrieve feature data from the feature catalog table
    feature_catalog = tdml.DataFrame.from_query(f'CURRENT VALIDTIME SELECT * FROM {SCHEMA}.{FEATURE_CATALOG_NAME}')

    # Determine the valid time statement based on the presence of a specific date in the past
    if FEATURE_STORE_TIME is None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{FEATURE_STORE_TIME}'"

    # Adjust valid time statement based on the presence of time_manager and no_temporal flag
    if no_temporal:
        validtime_statement = ''

    # Convert entity_id to a list format for processing
    if isinstance(entity_id, list):
        list_entity_id = entity_id
    elif isinstance(entity_id, dict):
        list_entity_id = list(entity_id.keys())
    else:
        list_entity_id = [entity_id]

    # Compose the entity names and retrieve the corresponding feature locations
    ENTITY_NAMES = ','.join([k for k in list_entity_id])
    ENTITY_ID = ', \n'.join([k for k in list_entity_id])
    if len(selected_features) > 1:
        ENTITY_ID_ = ','.join([','.join(['COALESCE('+','.join(['AA'+str(i+1)+'.'+k for i,c in enumerate(selected_features)])+') as '+k]) for k in list_entity_id])
    else:
        ENTITY_ID_ = ','.join([','.join(['' + ','.join(['AA' + str(i + 1) + '.' + k for i, c in enumerate(selected_features)]) + ' as ' + k]) for k in list_entity_id])


    feature_location = feature_catalog[(feature_catalog.FEATURE_NAME.isin(list(selected_features.keys()))) & \
                                        (feature_catalog.ENTITY_NAME == ENTITY_NAMES) & \
                                        (feature_catalog.DATA_DOMAIN == DATA_DOMAIN) \
                                       ].to_pandas()

    # manage the case sensitivity
    feature_location['FEATURE_NAME_UPPER'] = [x.upper() for x in feature_location['FEATURE_NAME']]
    feature_location['FEATURE_VERSION'] = feature_location['FEATURE_NAME_UPPER'].map({k.upper():v for k,v in selected_features.items()})


    # Build the query to retrieve the selected features from the feature tables
    query = []
    counter = 1
    feature_names = []
    for g,df in feature_location.groupby(['FEATURE_DATABASE','FEATURE_TABLE']):
        for i,row in df.iterrows():
            condition = ' \n '+f"(FEATURE_ID = {row['FEATURE_ID']} AND FEATURE_VERSION = '{row['FEATURE_VERSION']}')"
            if time_manager is not None:
                if 'date' in time_manager.data_type.lower():
                    if DISPLAY_LOGS:
                        print(f'Time Manager {time_manager.schema_name}.{time_manager.table_name} has a {time_manager.data_type} data type')
                    query_ = f"""
                    SELECT  A{counter}.* FROM (
                    SELECT * FROM {g[0]}.{g[1]}
                    WHERE  {condition} AND PERIOD(CAST(ValidStart AS DATE), CAST(ValidEnd AS DATE)) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.table_name})
                    ) A{counter}
                    """
                else:
                    if DISPLAY_LOGS:
                        print(
                        f'Time Manager {time_manager.schema_name}.{time_manager.table_name} has a {time_manager.data_type} data type')
                    query_ = f"""
                    SELECT  A{counter}.* FROM (
                    SELECT * FROM {g[0]}.{g[1]}
                    WHERE  {condition} AND PERIOD(ValidStart, ValidEnd) CONTAINS (SEL BUSINESS_DATE FROM {time_manager.schema_name}.{time_manager.table_name})
                    ) A{counter}
                    """
            else:
                if DISPLAY_LOGS:
                    print(f'no time manager used.')
                query_ = f"""
                SELECT  A{counter}.* FROM (
                {validtime_statement} SELECT * FROM {g[0]}.{g[1]}
                WHERE  {condition}
                ) A{counter}
                """
            query.append(query_)
            feature_names.append(row['FEATURE_NAME'])
            counter+=1



    query_select  = [f"SELECT {ENTITY_ID_}"]
    query_select  = query_select + ['AA'+str(i+1)+'.FEATURE_VALUE AS '+c for i,c in enumerate(feature_names)]
    if no_temporal:
        query_select = query_select + ['AA'+str(i+1)+'.ValidStart AS ValidStart_'+ c + ',AA'+str(i+1)+'.ValidEnd AS ValidEnd_'+ c for i,c in enumerate(feature_names)]
    query_select  = ', \n'.join(query_select)

    query_from    = [' FROM ('+query[0]+') AA1 ']
    query_from    = query_from + [' FULL OUTER JOIN ('+q+') AA'+str(i+1)+' \n ON '+' \n AND '.join([f'AA1.{c}=AA{i+1}.{c}' for c in list_entity_id]) for i,q in enumerate(query) if i>0]
    query_from    = '\n'.join(query_from)

    query_dataset = query_select + '\n' + query_from

    # Build the query to create the dataset view by pivoting the feature data
    query_create_view = f'REPLACE VIEW {SCHEMA}.{view_name} AS'
    query_pivot = f"""
    {query_dataset} 
    """

    if tdml.display.print_sqlmr_query:
        print(query_create_view+'\n'+query_pivot)
    if query_only:
        return query_pivot
    else:
        if view_name != None:
            execute_query(query_create_view+'\n'+query_pivot)
            execute_query(f"COMMENT ON VIEW {SCHEMA}.{view_name} IS '{comment}'")
            if DISPLAY_LOGS: print(f'the dataset view {SCHEMA}.{view_name} has been created')

            return tdml.DataFrame(tdml.in_schema(SCHEMA, view_name))
        else:
            return tdml.DataFrame.from_query(query_pivot)

def _build_time_series(entity_id, selected_feature, query_only=False):
    """
    Constructs a time series dataset for a given entity and feature.
    Optionally returns only the query used for dataset construction.

    This is a wrapper around the `build_dataset` function, tailored specifically for time series data by setting temporal parameters to null.

    Args:
        entity_id (dict): The identifier for the entity for which the dataset is being built.
        selected_feature (str or list): The feature(s) to be included in the dataset.
        query_only (bool, optional): If True, returns only the SQL query used for building the dataset, not the dataset itself. Defaults to False.

    Returns:
        DataFrame or str: The constructed time series dataset as a DataFrame, or the SQL query as a string if query_only is True.
    """

    # Call the build_dataset function with specific parameters set for time series dataset construction
    return build_dataset(
        entity_id=entity_id,  # The identifier for the entity
        selected_features=selected_feature,  # The feature(s) to be included in the dataset
        no_temporal=True,  # Indicates that the dataset should not have a temporal component
        query_only=query_only,  # Determines whether to return just the query or the constructed dataset
        time_manager=None,  # No time management for the dataset construction
        view_name=None  # No specific view name provided
    )


def build_dataset_time_series(df, time_column, entity_id, selected_features, query_only=False, time_manager=None):
    """
    Constructs a time series dataset based on the specified features and entity_id from the provided dataframe.

    Args:
        df (DataFrame): The source dataframe.
        time_column (str): The name of the column in df that represents time.
        entity_id (dict): A dictionary representing the entity identifier.
        selected_features (dict): A dictionary with keys as feature names and values as conditions or specifications for those features.
        query_only (bool, optional): If True, only the SQL query for the dataset is returned. Defaults to False.
        time_manager (TimeManager, optional): An instance of TimeManager to manage time-related operations. Defaults to None.

    Returns:
        DataFrame or str: The constructed time series dataset as a DataFrame, or the SQL query as a string if query_only is True.
    """

    # Convert column names to lowercase for case-insensitive matching
    col = [c.lower() for c in df.columns]

    # Check if the entity_id keys are present in the dataframe columns
    for e in entity_id:
        if e.lower() not in col:
            print(f' {e} is not present in your dataframe')
            print('Here are the columns of your dataframe:')
            print(str(col))
            return  # Exit if any entity_id key is not found

    # Check if the time_column is present in the dataframe columns
    if time_column.lower() not in col:
        print(f' {time_column} is not present in your dataframe')
        print('Here are the columns of your dataframe:')
        print(str(col))
        return  # Exit if the time_column is not found

    # Extract and check the data type of the time_column
    d_ = {x[0]: x[1] for x in df._td_column_names_and_types}
    time_column_data_type = d_[time_column]
    print('time column data type :', time_column_data_type)
    if 'date' not in time_column_data_type.lower() and 'time' not in time_column_data_type.lower():
        print('the time column of your data frame is neither a date nor a timestamp')
        return  # Exit if the time_column data type is not date or timestamp

    # Initialize the select query
    select_query = 'SELECT \n' + ', \n'.join(['A.' + c for c in col]) + '\n'

    # If a time_manager is provided, extract its details
    if time_manager is not None:
        tm_datatype = time_manager.data_type.lower()
        tm_schema = time_manager.schema_name
        tm_table = time_manager.table_name

    sub_queries_list = []
    # For each selected feature, build its part of the query
    for i, (k, v) in enumerate(selected_features.items()):
        select_query += ', BB' + str(i + 1) + '.' + k + '\n'

        nested_query = _build_time_series(entity_id, {k: v}, query_only=True)

        sub_queries = 'SELECT \n' + '\n ,'.join(entity_id) + '\n ,' + k + '\n'

        # Build the sub_queries based on the presence of a time_manager and the data types of time_column and time_manager
        if time_manager is None:
            # there is a time manager
            if 'date' in tm_datatype:
                # the data type of the time column is DATE
                sub_queries += f',	CAST(ValidStart_{k} AS DATE) AS ValidStart \n'
                sub_queries += f',	CAST(ValidEnd_{k} AS DATE) AS ValidEnd \n'
            else:
                # the data type of the time column is timestamp
                sub_queries += f',	CAST(ValidStart_{k} AS TIMESTAMP(0)) AS ValidStart \n'
                sub_queries += f',	CAST(ValidEnd_{k} AS TIMESTAMP(0)) AS ValidEnd \n'
        else:
            # there is a time manager
            if 'date' in time_column_data_type.lower():
                # the data type of the time column is DATE
                if 'date' in tm_datatype:
                    # the data type of the time manager is DATE
                    sub_queries += f',	CAST(ValidStart_{k} AS DATE) AS ValidStart \n'
                    sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS DATE) > BUS_DATE.BUSINESS_DATE THEN BUS_DATE.BUSINESS_DATE ELSE CAST(ValidEnd_{k} AS DATE) END AS ValidEnd \n'
                else:
                    # the data type of the time manager is timestamp
                    sub_queries += f',	CAST(ValidStart_{k} AS DATE) AS ValidStart \n'
                    sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS DATE) > BUS_DATE.BUSINESS_DATE THEN BUS_DATE.BUSINESS_DATE ELSE CAST(ValidEnd_{k} AS DATE) END AS ValidEnd \n'
            else:
                # the data type of the time column is TIMESTAMP
                if 'date' in tm_datatype:
                    sub_queries += f',	CAST(ValidStart_{k} AS TIMESTAMP(0)) AS ValidStart \n'
                    sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS TIMESTAMP(0)) > CAST(BUS_DATE.BUSINESS_DATE AS TIMESTAMP(0)) THEN BUS_DATE.BUSINESS_DATE ELSE CAST(ValidEnd_{k} AS TIMESTAMP(0)) END AS ValidEnd \n'
                else:
                    sub_queries += f',	CAST(ValidStart_{k} AS TIMESTAMP(0)) AS ValidStart \n'
                    sub_queries += f',	CASE WHEN CAST(ValidEnd_{k} AS TIMESTAMP(0)) > CAST(BUS_DATE.BUSINESS_DATE AS TIMESTAMP(0)) THEN BUS_DATE.BUSINESS_DATE ELSE CAST(ValidEnd_{k} AS TIMESTAMP(0)) END AS ValidEnd \n'

        sub_queries += f'FROM ({nested_query}) tmp{i + 1} \n'
        if time_manager is not None:
            sub_queries += f',{tm_schema}.{tm_table} BUS_DATE \n'

        sub_queries += 'WHERE ValidStart < ValidEnd \n'

        sub_queries = 'LEFT JOIN ( \n' + sub_queries + ') BB' + str(i + 1) + '\n ON '

        sub_queries += '\n  AND '.join(['A.' + c + '=BB' + str(i + 1) + '.' + c for c in entity_id])

        sub_queries += f'\n AND PERIOD(BB{i + 1}.ValidStart, BB{i + 1}.ValidEnd) CONTAINS A.{time_column} \n'

        sub_queries_list.append(sub_queries)

    # Combine all parts of the query
    query = select_query + f'FROM ({df.show_query()}) A \n' + '\n --------------- \n'.join(sub_queries_list)

    # If only the query is requested, return it; otherwise, execute the query and return the resulting DataFrame
    if query_only:
        return query
    else:
        return tdml.DataFrame.from_query(query)

def upload_tdstone2_scores(model):
    """
    Uploads features from a model's predictions to the Teradata feature store. This function handles the entire
    workflow from extracting feature names and types, registering them in the feature catalog, preparing features for ingestion,
    storing them in the feature store, and finally creating a dataset view in the feature store.

    Parameters:
    - model: The model object whose predictions contain features to be uploaded. This model should have methods
      to extract predictions and feature information.

    Returns:
    - DataFrame: A DataFrame representing the dataset view created in the feature store, which includes
      features from the model's predictions.

    Note:
    - The function assumes that the model provides a method `get_model_predictions` which returns a Teradata DataFrame.
    - Entity ID for the model is extracted and registered in the data domain.
    - The function cleans up by dropping the volatile table created during the process.
    - The feature names and their types are extracted from the model's predictions and are registered in the feature catalog.
    """

    # Extract the entity ID from the existing model.
    entity_id = tdstone2_entity_id(model)

    # Register the entity ID in the data domain.
    register_entity(entity_id)

    # Get the Teradata types of the features from the model's predictions.
    feature_names_types = tdstone2_Gettdtypes(model,entity_id)

    # Register these features in the feature catalog.
    register_features(entity_id, feature_names_types)

    # Prepare the features for ingestion into the feature store.
    if 'score' in [x[0] for x in inspect.getmembers(type(model))]:
        prepared_features, volatile_table_name = prepare_feature_ingestion_tdstone2(
            model.get_model_predictions(),
            entity_id
        )
    else:
        prepared_features, volatile_table_name = prepare_feature_ingestion_tdstone2(
            model.get_computed_features(),
            entity_id
        )

    # Store the prepared features in the feature store.
    store_feature(entity_id, prepared_features)

    # Clean up by dropping the temporary volatile table.
    tdml.execute_sql(f'DROP TABLE {volatile_table_name}')

    # Get the list of selected features for building the dataset view.
    if 'score' in [x[0] for x in inspect.getmembers(type(model))]:
        selected_features = model.get_model_predictions().groupby(['FEATURE_NAME', 'ID_PROCESS']).count().to_pandas()[
            ['FEATURE_NAME', 'ID_PROCESS']].set_index('FEATURE_NAME').to_dict()['ID_PROCESS']
    else:
        selected_features = model.get_computed_features().groupby(['FEATURE_NAME', 'ID_PROCESS']).count().to_pandas()[
            ['FEATURE_NAME', 'ID_PROCESS']].set_index('FEATURE_NAME').to_dict()['ID_PROCESS']

    # Build and return the dataset view in the feature store.
    dataset = build_dataset(entity_id, selected_features, view_name=None)
    return dataset


def roll_out(date_list, process_list, time_manager):
    """
    Executes a series of processes for each date in a given list, managing the time and logging settings.

    This function iterates over a list of dates, updating a TimeManager object with each date, and then
    executes a list of processes for that date. It also manages the synchronization of time for a feature store
    and disables display logs during its execution.

    Parameters:
    date_list (list): A list of dates for which the processes need to be executed.
    process_list (list): A list of process IDs that need to be executed for each date.
    time_manager (TimeManager object): An object that manages time-related operations, like updating or retrieving time.

    Side Effects:
    - Sets global variables DISPLAY_LOGS and FEATURE_STORE_TIME.
    - Catches and prints exceptions along with the date on which they occurred.
    """

    global DISPLAY_LOGS
    global FEATURE_STORE_TIME

    # Disable display logs
    temp_DISPLAY_LOGS = DISPLAY_LOGS
    DISPLAY_LOGS = False

    try:

        pbar = tqdm.tqdm(date_list, desc="Starting")
        # Iterate over each date in the provided list
        for date_ in pbar:
            pbar.set_description(f"Processing {date_}")
            # Update the time manager with the new date
            time_manager.update(new_time=date_)
            # Synchronize the time for the feature store with the current date
            FEATURE_STORE_TIME = time_manager.get_date_in_the_past()
            # Execute each process in the process list for the current date
            for proc_id in process_list:
                pbar.set_description(f"Processing {date_} process {proc_id}")
                run(process_id=proc_id)
        DISPLAY_LOGS = temp_DISPLAY_LOGS
    except Exception as e:
        DISPLAY_LOGS = temp_DISPLAY_LOGS
        # If an exception occurs, print the date and the first line of the exception message
        print(date_)
        print(str(e).split('\n')[0])
