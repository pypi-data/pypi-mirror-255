import teradataml as tdml
import tdfs4ds


def list_features():

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    query = f"{validtime_statement} SEL * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}"

    return tdml.DataFrame.from_query(query)


def get_feature_store_table_name(entity_id, feature_type):
    """

    This function generates the table and view names for a feature store table based on the provided entity ID and feature type.

    Parameters:
    - entity_id: A dictionary representing the entity ID. The keys of the dictionary are used to construct the table and view names.
    - feature_type: The type of the feature.

    Returns:
    A tuple containing the generated table name and view name.

    """

    if type(entity_id) == list:
        list_entity_id = entity_id
    elif type(entity_id) == dict:
        list_entity_id = list(entity_id.keys())
    else:
        list_entity_id = [entity_id]

    # Construct the table name by concatenating the elements 'FS', 'T', the keys of entity_id, and feature_type
    table_name = ['FS', 'T'] + [tdfs4ds.DATA_DOMAIN] + list_entity_id + [feature_type]
    table_name = '_'.join(table_name)

    # Construct the view name by concatenating the elements 'FS', 'V', the keys of entity_id, and feature_type
    view_name = ['FS', 'V'] + [tdfs4ds.DATA_DOMAIN] + list_entity_id + [feature_type]
    view_name = '_'.join(view_name)

    return table_name, view_name

def get_available_features(entity_id, display_details=False):
    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    if type(entity_id) == dict:
        ENTITY_ID__ = ','.join([k.lower() for k, v in entity_id.items()])
    elif type(entity_id) == list:
        ENTITY_ID__ = ','.join([k.lower() for k in entity_id])
    else:
        ENTITY_ID__ = entity_id.lower()

    query = f"""
    {validtime_statement}
    SELECT 
          FEATURE_NAME
    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}
    WHERE LOWER(ENTITY_NAME) = '{ENTITY_ID__}'
    AND DATA_DOMAIN = '{tdfs4ds.DATA_DOMAIN}'
    """

    if tdfs4ds.DEBUG_MODE:
        print(query)

    if display_details:
        print(tdml.DataFrame.from_query(f'{validtime_statement} SELECT * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}'))

    return list(tdml.DataFrame.from_query(query).to_pandas().FEATURE_NAME.values)

def get_list_entity(domain=None):
    """
    Retrieve a list of unique entity names from a specified data domain.

    This function executes a database query to extract distinct entity names from
    a feature catalog, filtered by the provided data domain. If no domain is
    specified, it defaults to a predefined data domain.

    Parameters:
    domain (str, optional): The data domain to filter the entity names.
                            Defaults to None, in which case a predefined domain is used.

    Returns:
    DataFrame: A pandas-like DataFrame containing the unique entity names.
    """

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Use the default data domain if none is specified
    if domain is None:
        domain = tdfs4ds.DATA_DOMAIN

    # Constructing the SQL query to fetch distinct entity names from the specified domain
    query = f"{validtime_statement} SEL DISTINCT ENTITY_NAME FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} where DATA_DOMAIN = '{domain}'"

    # Executing the query and returning the result as a DataFrame
    return tdml.DataFrame.from_query(query)


def get_list_features(entity_name, domain=None):
    """
    Retrieve a list of feature names associated with a specific entity or entities
    from a given data domain.

    This function constructs and executes a database query to extract feature names
    for the specified entity or entities from a feature catalog, filtered by the
    provided data domain. If no domain is specified, it defaults to a predefined
    data domain.

    Parameters:
    entity_name (str or list): The name of the entity or a list of entity names
                               to fetch features for.
    domain (str, optional): The data domain to filter the feature names.
                            Defaults to None, where a predefined domain is used.

    Returns:
    DataFrame: A pandas-like DataFrame containing the feature names associated with the given entity or entities.
    """

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Default to a predefined data domain if none is provided
    if domain is None:
        domain = tdfs4ds.DATA_DOMAIN

    # Convert the entity_name to a string if it is a list
    if type(entity_name) == list:
        entity_name = ','.join(entity_name)

    # Constructing the SQL query to fetch feature names for the specified entity or entities
    query = f"{validtime_statement} SEL FEATURE_NAME FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} where entity_name = '{entity_name}' AND DATA_DOMAIN = '{domain}'"

    # Executing the query and returning the result as a DataFrame
    return tdml.DataFrame.from_query(query)


def get_feature_versions(entity_name, features, domain=None, latest_version_only=True, version_lag=0):
    """
    Retrieve feature versions for specified features associated with certain entities
    from a given data domain. This function allows fetching either all versions or
    just the latest versions of the features.

    Parameters:
    entity_name (str or list): The name of the entity or a list of entity names
                               for which feature versions are to be fetched.
    features (list): A list of features for which versions are required.
    domain (str, optional): The data domain to filter the feature versions.
                            Defaults to None, where a predefined domain is used.
    latest_version_only (bool, optional): Flag to fetch only the latest version
                                          of each feature. Defaults to True.
    version_lag (int, optional): The number of versions to lag behind the latest.
                                 Only effective if latest_version_only is True. Defaults to 0.

    Returns:
    dict: A dictionary with feature names as keys and their corresponding versions as values.
    """

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Default to a predefined data domain if none is provided
    if domain is None:
        domain = tdfs4ds.DATA_DOMAIN

    # Convert the entity_name to a string if it is a list
    if type(entity_name) == list:
        entity_name = ','.join(entity_name)

    # Preparing the feature names for inclusion in the SQL query
    features = ["'" + f + "'" for f in features]

    # Constructing the SQL query to fetch basic feature data for the specified entities and features
    query = f"""{validtime_statement}
    SEL FEATURE_ID, FEATURE_NAME, FEATURE_TABLE, FEATURE_DATABASE
    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME} where entity_name = '{entity_name}' AND DATA_DOMAIN = '{domain}' 
    AND FEATURE_NAME in ({','.join(features)})"""

    # Executing the first query and converting the results to a pandas DataFrame
    df = tdml.DataFrame.from_query(query).to_pandas()

    # Building the second query to fetch feature versions
    query = []
    for i, row in df.iterrows():
        query_ = f"""
        SEL DISTINCT A{i}.FEATURE_NAME, A{i}.FEATURE_VERSION
        FROM (
        {validtime_statement}
        SELECT CAST('{row['FEATURE_NAME']}' AS VARCHAR(255)) AS FEATURE_NAME, FEATURE_VERSION FROM {row['FEATURE_DATABASE']}.{row['FEATURE_TABLE']}
        WHERE FEATURE_ID = {row['FEATURE_ID']})
        A{i}
        """
        query.append(query_)

    # Combining the individual queries with UNION ALL
    query = '\n UNION ALL \n'.join(query)

    # Modifying the query to fetch only the latest versions, if specified
    if latest_version_only:
        query = 'SELECT * FROM (' + query + ') A \n' + f'QUALIFY ROW_NUMBER() OVER(PARTITION BY FEATURE_NAME ORDER BY FEATURE_VERSION DESC) = 1+{version_lag}'

    # Executing the final query and converting the results to a pandas DataFrame
    df = tdml.DataFrame.from_query(query).to_pandas()

    # Returning the results as a dictionary with feature names as keys and their versions as values
    return {row['FEATURE_NAME']:row['FEATURE_VERSION'] for i,row in df.iterrows()}