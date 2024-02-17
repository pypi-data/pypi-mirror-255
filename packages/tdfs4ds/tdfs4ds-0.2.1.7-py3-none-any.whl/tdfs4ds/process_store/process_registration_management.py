import teradataml as tdml
import tdfs4ds
from tdfs4ds.utils.query_management import execute_query_wrapper
import uuid
import json

@execute_query_wrapper
def register_process_view(view_name, entity_id, feature_names, metadata={}, **kwargs):
    """
    Registers a process view with the specified details in the feature store. The function
    handles both the creation of new views and the updating of existing views.

    Parameters:
    view_name (str or DataFrame): The name of the view or a DataFrame object representing the view.
    entity_id (str): The identifier of the entity associated with the view.
    feature_names (list): A list of feature names included in the view.
    metadata (dict, optional): Additional metadata related to the view. Defaults to an empty dictionary.

    Returns:
    str: A query string to insert or update the view details in the feature store.
    """

    # Handling the case where the view name is provided as a DataFrame
    if type(view_name) == tdml.dataframe.dataframe.DataFrame:
        try:
            view_name = view_name._table_name
        except:
            print('create your teradata dataframe using tdml.DataFrame(<view name>). Crystallize your view if needed')
            return []

    # Generating a unique process identifier
    process_id = str(uuid.uuid4())

    # Joining the feature names into a comma-separated string
    feature_names = ','.join(feature_names)

    # Setting the end period for the view
    if tdfs4ds.END_PERIOD == 'UNTIL_CHANGED':
        end_period_ = '9999-01-01 00:00:00'
    else:
        end_period_ = tdfs4ds.END_PERIOD

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME PERIOD '({tdfs4ds.FEATURE_STORE_TIME},{end_period_})'"

    # Handling cases based on whether the date is in the past or not
    if tdfs4ds.FEATURE_STORE_TIME == None:

        # Checking if the view already exists in the feature store
        query_ = f"CURRENT VALIDTIME SEL * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} WHERE view_name = '{view_name}'"
        df = tdml.DataFrame.from_query(query_)

        # Constructing the query for new views
        if df.shape[0] == 0:
            query_insert = f"""
                CURRENT VALIDTIME INSERT INTO {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} (PROCESS_ID, PROCESS_TYPE, VIEW_NAME, ENTITY_ID, FEATURE_NAMES, FEATURE_VERSION, METADATA, DATA_DOMAIN)
                    VALUES ('{process_id}',
                    'denormalized view',
                    '{view_name}',
                    '{json.dumps(entity_id).replace("'", '"')}',
                    '{feature_names}',
                    '1',
                    '{json.dumps(metadata).replace("'", '"')}',
                    '{tdfs4ds.DATA_DOMAIN}'
                    )
                """
        # Constructing the query for updating existing views
        else:
            query_insert = f"""
                            CURRENT VALIDTIME UPDATE {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} 
                            SET 
                                PROCESS_TYPE = 'denormalized view'
                            ,   ENTITY_ID = '{json.dumps(entity_id).replace("'", '"')}'
                            ,   FEATURE_NAMES = '{feature_names}'
                            ,   FEATURE_VERSION = CAST((CAST(FEATURE_VERSION AS INTEGER) +1) AS VARCHAR(4))
                            ,   METADATA = '{json.dumps(metadata).replace("'", '"')}'
                            ,   DATA_DOMAIN = '{tdfs4ds.DATA_DOMAIN}'
                            WHERE VIEW_NAME = '{view_name}'
                            """
            process_id = tdml.DataFrame.from_query(f"CURRENT VALIDTIME SEL PROCESS_ID FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} WHERE VIEW_NAME = '{view_name}'").to_pandas().PROCESS_ID.values[0]

    else:
        # Handling the case when the date is in the past
        df = tdml.DataFrame.from_query(f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}' SEL * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} WHERE view_name = '{view_name}'")



        # Constructing the query for new views with a past date
        if df.shape[0] == 0:
            query_insert = f"""
            INSERT INTO {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} (PROCESS_ID, PROCESS_TYPE, VIEW_NAME,  ENTITY_ID, FEATURE_NAMES, FEATURE_VERSION, METADATA, DATA_DOMAIN,ValidStart, ValidEnd)
                VALUES ('{process_id}',
                'denormalized view',
                '{view_name}',
                '{json.dumps(entity_id).replace("'", '"')}'
                ,'{feature_names}',
                '1',
                '{json.dumps(metadata).replace("'", '"')}',
                '{tdfs4ds.DATA_DOMAIN}',
                TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}',
                TIMESTAMP '{end_period_}'
                )
            """
        # Constructing the query for updating existing views with a past date
        else:
            query_insert = f"""{validtime_statement}
                            UPDATE {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} 
                            SET 
                                PROCESS_TYPE = 'denormalized view'
                            ,   ENTITY_ID = '{json.dumps(entity_id).replace("'", '"')}'
                            ,   FEATURE_NAMES = '{feature_names}'
                            ,   FEATURE_VERSION = CAST((CAST(FEATURE_VERSION AS INTEGER) +1) AS VARCHAR(4))
                            ,   METADATA = '{json.dumps(metadata).replace("'", '"')}'
                            ,   DATA_DOMAIN = '{tdfs4ds.DATA_DOMAIN}'
                            WHERE VIEW_NAME = '{view_name}'
                            """
            process_id = tdml.DataFrame.from_query(
                f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}' SEL PROCESS_ID FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} WHERE VIEW_NAME = '{view_name}'").to_pandas().PROCESS_ID.values[
                0]
    # Logging the process registration
    print(f'register process with id : {process_id}')
    print(f'to run the process again just type : run(process_id={process_id})')
    print(f'to update your dataset : dataset = run(process_id={process_id},return_dataset=True)')

    if kwargs.get('with_process_id'):
        return query_insert, process_id
    else:
        return query_insert

@execute_query_wrapper
def register_process_tdstone(model, metadata={}):
    """
    Registers a 'tdstone2 view' process in the feature store with specified model details and metadata.
    It handles both the scenarios where the feature store date is current or in the past.

    Parameters:
    model (Model Object): The model object containing necessary details for the registration.
    metadata (dict, optional): Additional metadata related to the process. Defaults to an empty dictionary.

    Returns:
    str: A query string to insert the process details into the feature store.
    """

    # Generating a unique process identifier
    process_id = str(uuid.uuid4())

    # Handling the current date scenario
    if tdfs4ds.FEATURE_STORE_TIME is None:
        # Constructing the query for insertion with current valid time
        query_insert = f"""
            CURRENT VALIDTIME INSERT INTO {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} (PROCESS_ID, PROCESS_TYPE, ENTITY_ID, FEATURE_VERSION, METADATA, DATA_DOMAIN)
                VALUES ('{process_id}',
                'tdstone2 view',
                '{model.mapper_scoring.id_row}',
                '{model.id}',
                '{json.dumps(metadata).replace("'", '"')}',
                '{tdfs4ds.DATA_DOMAIN}'
                )
            """
    else:
        # Determining the end period based on feature store configuration
        end_period_ = '9999-01-01 00:00:00' if tdfs4ds.END_PERIOD == 'UNTIL_CHANGED' else tdfs4ds.END_PERIOD

        # Constructing the query for insertion with a specified past date
        query_insert = f"""
        INSERT INTO {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} (PROCESS_ID, PROCESS_TYPE, ENTITY_ID, FEATURE_VERSION, METADATA, DATA_DOMAIN, ValidStart, ValidEnd)
            VALUES ('{process_id}',
            'tdstone2 view',
            '{model.mapper_scoring.id_row}',
            '{model.id}',
            '{json.dumps(metadata).replace("'", '"')}',
            '{tdfs4ds.DATA_DOMAIN}',
            TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}',
            TIMESTAMP '{end_period_}')
        """

    # Logging the process registration
    print(f'register process with id : {process_id}')

    return query_insert