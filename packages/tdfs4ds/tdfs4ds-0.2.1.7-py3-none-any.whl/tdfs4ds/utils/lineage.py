import re
import pandas as pd
import teradataml as tdml
import tdfs4ds
import tqdm

def _analyze_sql_query(sql_query):
    """
    Analyze a SQL query to extract the source tables, target tables, and views.

    The function uses regular expressions to search for patterns indicative
    of source tables, target tables, and views in the given SQL query.

    :param sql_query: str
        A string containing a SQL query to be analyzed.

    :return: dict
        A dictionary containing lists of source tables, target tables, and views.
        Format: {
            'source': [source_tables],
            'target': [target_tables]
        }
    """

    def find_in_with_statement(sql_text):
        """
        Extracts terms from a SQL text that are followed by 'AS ('.

        Args:
            sql_text (str): The SQL text to be searched.

        Returns:
            list: A list of terms that are followed by 'AS ('
        """
        # Regex pattern to find ', term AS ('
        # It looks for a comma, optional whitespace, captures a word (term), followed by optional whitespace, 'AS', whitespace, and an opening parenthesis
        pattern = r'WITH\s*(\w+)\s+AS\s+\('

        # Find all occurrences of the pattern
        terms = re.findall(pattern, sql_text, re.IGNORECASE)

        pattern = r',\s*(\w+)\s+AS\s+\('

        # Find all occurrences of the pattern
        terms = terms + re.findall(pattern, sql_text, re.IGNORECASE)

        terms = [t.split(' ')[0] for t in terms]
        return terms

    def remove_sql_comments(sql_query):
        # Remove single line comments
        sql_query = re.sub(r'--.*', '', sql_query)

        # Remove multi-line comments
        sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)

        return sql_query

    # we remove the comments from the query
    sql_query = remove_sql_comments(sql_query)

    # Regular expression patterns for different SQL components
    create_table_pattern = r'CREATE\s+TABLE\s+([\w\s\.\"]+?)\s+AS'
    insert_into_pattern = r'INSERT\s+INTO\s+([\w\s\.\"]+?)'
    create_view_pattern = r'(CREATE|REPLACE)\s+VIEW\s+([\w\s\.\"]+?)\s+AS'
    #select_pattern = r'(FROM|JOIN|LEFT\sJOIN|RIGHT\sJOIN)\s+([\w\s\.\"]+?)(?=\s*(,|\s+GROUP|$|WHERE|PIVOT|UNPIVOT|UNION|ON|\)|\s+AS))'
    select_pattern = r'(\bFROM\b|LEFT\s+JOIN|RIGHT\s+JOIN|\bJOIN\b)\s+([\w\s\.\"]+?)(?=\s*(,|\bUNION\b|\bFULL\b|\bJOIN\b|\bLEFT\b|\bRIGHT\b|\bGROUP\b|\bQUALIFY\b|\bQUALIFY\b|\bWHERE\b|\bPIVOT\b|\bUNPIVOT\b|\bUNION\b|\bON\b|\bAS\b|$|\)))'
    select_pattern = r'(\bFROM\b|CROSS\s+JOIN|FULL\sOUTER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|\bJOIN\b)\s+([\w\s\.\"]+?)(?=\s*(,|\bUNION\b|\bFULL\b|\bJOIN\b|\bLEFT\b|\bRIGHT\b|\bGROUP\s+BY\b|\bQUALIFY\b|\bHAVING\b|\bWHERE\b|\bPIVOT\b|\bUNPIVOT\b|\bUNION\b|\bUNION\s+ALL\b|\bINTERSECT\b|\bMINUS\b|\bEXCEPT\b|\bON\b|\bAS\b|$|\)))'

    # select_pattern2 =  r'(FROM|JOIN)\s+([\w\s\.\"]+?)(?=\s*(,|group|$|where|pivot|unpivot|\)|AS))'



    # Find all matches in the SQL query for each pattern
    create_table_matches = re.findall(create_table_pattern, sql_query, re.IGNORECASE)
    insert_into_matches = re.findall(insert_into_pattern, sql_query, re.IGNORECASE)
    create_view_matches = re.findall(create_view_pattern, sql_query, re.IGNORECASE)
    select_matches = re.findall(select_pattern, sql_query, re.IGNORECASE)

    # select_matches2 = re.findall(select_pattern2, sql_query, re.IGNORECASE)

    # Extract the actual table or view name from the match tuples
    create_table_matches = [match[0] if match[0] else match[1] for match in create_table_matches]
    insert_into_matches = [match[0] if match[0] else match[1] for match in insert_into_matches]
    create_view_matches = [match[1] if match[0] else match[1] for match in create_view_matches]
    if tdfs4ds.DEBUG_MODE:
        print('select matches :', select_matches)
    with_matches = [x.lower() for x in find_in_with_statement(sql_query)]
    select_matches = [match[1] for match in select_matches]
    if tdfs4ds.DEBUG_MODE:
        print('select matches :', select_matches)
    # select_matches2 = [match[0] for match in select_matches2]

    table_names = {
        'source': [],
        'target': []
    }

    # Categorize the matched tables and views into 'source' or 'target'
    table_names['target'].extend(create_table_matches)
    table_names['target'].extend(insert_into_matches)
    table_names['target'].extend(create_view_matches)
    table_names['source'].extend(select_matches)
    # table_names['source'].extend(select_matches2)

    # Remove duplicate table and view names
    table_names['source'] = list(set(table_names['source']))
    table_names['target'] = list(set(table_names['target']))

    correct_source = []
    for target in table_names['source']:
        if '"' not in target:
            if ' ' in target:
                target = target.split(' ')[0]
            if target.lower() not in with_matches:
                correct_source.append('.'.join(['"' + t + '"' for t in target.split('.')]))
        else:
            if target.lower() not in with_matches:
                correct_source.append(target)

    correct_target = []
    for target in table_names['target']:
        if '"' not in target:
            if ' ' in target:
                target = target.split(' ')[0]
            if target.lower() not in with_matches:
                correct_target.append('.'.join(['"' + t + '"' for t in target.split('.')]))
        else:
            if target.lower() not in with_matches:
                correct_target.append(target)

    table_names['source'] = correct_source
    table_names['target'] = correct_target

    return table_names

def analyze_sql_query(sql_query, df=None, target=None, root_name='ml__', node_info=None):
    """
    Analyzes the provided SQL query to determine source and target tables/views relationships.
    It then captures these relationships in a pandas DataFrame.

    :param sql_query: str
        A string containing the SQL query to be analyzed.
    :param df: pd.DataFrame, optional
        An existing DataFrame to append the relationships to. If not provided, a new DataFrame is created.
    :param target: str, optional
        Name of the target table/view. If not provided, it's deduced from the SQL query.

    :return: pd.DataFrame
        A DataFrame with two columns: 'source' and 'target', representing the relationships.

    :Note: This function is specifically tailored for Teradata and makes use of teradataml (tdml) for certain operations.
    """

    # Extract source and potential target tables/views from the provided SQL query
    table_name = _analyze_sql_query(sql_query)


    # Extract node informations
    if node_info is None and target is None:
        node_info = [{'target': target, 'columns': tdml.DataFrame.from_query(sql_query).columns, 'query': sql_query}]
    elif node_info is None:
        if '"' not in target:
            target = '.'.join(['"' + t + '"' for t in target.split('.')])

        node_info = [{'target': target, 'columns': tdml.DataFrame(target).columns, 'query': sql_query}]
    else:
        if '"' not in target:
            target = '.'.join(['"' + t + '"' for t in target.split('.')])

        node_info = node_info + [{'target': target, 'columns': tdml.DataFrame(target).columns, 'query': sql_query}]

    # If df is not provided, initialize it; else append to the existing df
    table_name['target'] = [target] * len(table_name['source'])
    if df is None:
        df = pd.DataFrame(table_name)
    else:
        df = pd.concat([df, pd.DataFrame(table_name)], ignore_index=True)

    # Check for teradataml views in the source and recursively analyze them
    for obj in table_name['source']:
        if root_name == None or root_name.lower() in obj.lower():

            # It's a teradataml view. Fetch its definition.
            try:
                sql_query_ = tdml.execute_sql(f"SHOW VIEW {obj}").fetchall()[0][0].replace('\r', '\n').replace('\t', '\n')
            except Exception as e:
                if tdfs4ds.DISPLAY_LOGS:
                    print(str(e).split("\n")[0])
            try:
                # Recursively analyze the view definition to get its relationships
                df, node_info = analyze_sql_query(
                    sql_query_,
                    df,
                    target    = obj,
                    node_info = node_info,
                    root_name = root_name
                )

                if tdfs4ds.DEBUG_MODE:
                    print('-------------------------------------------')
                    print('source     : ', obj)
                    print('-------------------------------------------')
                    print('source DDL : ')
                    print(sql_query_)
                    print('-------------------------------------------')
                    print(node_info)

            except:
                if tdfs4ds.DISPLAY_LOGS:
                    print(f"{obj} is a root, outside of the current database or a view directly connected to a table")

        else:
            if tdfs4ds.DISPLAY_LOGS:
                print(root_name.lower(), ' not in ', obj.lower(), 'then excluded')

    return df, node_info
def crystallize_view(tddf, view_name, schema_name):
    """
    Materializes a given teradataml DataFrame as a view in the database with sub-views, if needed. This function
    helps in creating nested views, where complex views are broken down into simpler sub-views to simplify debugging
    and optimization. Each sub-view is named based on the main view's name with an additional suffix.

    Parameters:
    :param tddf: teradataml.DataFrame
        The teradataml dataframe whose view needs to be materialized.
    :param view_name: str
        The name of the main view to be created.
    :param schema_name: str
        The schema in which the view should be created.

    Returns:
    :return: teradataml.DataFrame
        A teradataml DataFrame representation of the created view.

    Notes:
    This function is specific to the teradataml library, and assumes the existence of certain attributes in the input DataFrame.
    """

    # Create the _table_name attribute for the teradataml DataFrame if it doesn't exist
    tddf._DataFrame__execute_node_and_set_table_name(tddf._nodeid, tddf._metaexpr)

    # Generate the dependency graph for the input DataFrame's SQL representation
    tddf_graph, _ = analyze_sql_query(tddf.show_query(), target=tddf._table_name)

    # Generate new names for sub-views based on the main view's name and store in a mapping dictionary
    if len(tddf_graph['target'].values)>1:
        mapping = {n: schema_name + '.' + view_name + '_sub_' + str(i) for i, n in enumerate(tddf_graph['target'].values)}
    else:
        mapping = {tddf_graph['target'].values[0] : schema_name + '.' + view_name}

    # Replace or create the sub-views with their new names in the database
    for old_name, new_name in reversed(mapping.items()):
        query = tdml.execute_sql(f"SHOW VIEW {old_name}").fetchall()[0][0].replace('\r','\n').lower()
        query = query.replace('create', 'replace')
        for old_sub_name, new_sub_name in mapping.items():
            query = query.upper().replace(old_sub_name.upper(), new_sub_name)
        if tdfs4ds.DISPLAY_LOGS:
            print('REPLACE VIEW ', new_name)
        tdml.execute_sql(query)

    # Construct the final view by replacing the old names with new ones in the SQL representation
    mapping[new_name] = view_name

    #query = tdml.execute_sql(f"SHOW VIEW {tddf._table_name}").fetchall()[0][0].replace('\r','\n').lower()
    #query = f'replace view {schema_name}.{view_name} AS \n' + query
    for old_name, new_name in mapping.items():
        query = query.upper().replace(old_name.upper(), new_name)

    # Execute the final query to create the main view
    if tdfs4ds.DISPLAY_LOGS:
        print('REPLACE VIEW '+ schema_name+'.'+view_name)
    tdml.execute_sql(query)


    # Return a teradataml DataFrame representation of the created view
    return tdml.DataFrame(tdml.in_schema(schema_name, view_name))

def generate_view_dependency_network(schema_name):
    """
    Generates a network of view dependencies for a given database schema.

    This function lists all views within the specified schema and analyzes each one to
    construct a network of view interdependencies. It returns a DataFrame that
    represents these dependencies.

    Parameters:
    schema_name (str): The name of the database schema for which to generate the view dependency network.

    Returns:
    pd.DataFrame: A DataFrame representing the dependencies between the views in the specified schema.
    """

    # Temporarily disable logging to prevent clutter during the process
    display_logs = tdfs4ds.DISPLAY_LOGS
    tdfs4ds.DISPLAY_LOGS = False

    try:
        # List all views in the given schema
        views = tdml.db_list_tables(schema_name=schema_name, object_type='view').TableName.tolist()

        # Initialize an empty list to store dataframes representing individual view dependencies
        df_list = []

        # Initialize a progress bar for processing views
        pbar = tqdm.tqdm(views, desc="Starting")
        for v in pbar:
            pbar.set_description(f"Processing view {v}")

            # Analyze the SQL query for the current view and retrieve a dataframe representing its dependencies
            df, node_info = analyze_sql_query(get_ddl(view_name=v, schema_name=schema_name), target=f"{schema_name}.{v}", root_name=None)

            # Append the resulting dataframe to the list
            df_list.append(df)

        # Concatenate all individual view dependency dataframes and remove duplicates
        combined_df = pd.concat(df_list).drop_duplicates()

        # Restore the original logging setting
        tdfs4ds.DISPLAY_LOGS = display_logs

        return combined_df

    except Exception as e:
        # In case of an exception, restore logging settings and print the error
        tdfs4ds.DISPLAY_LOGS = display_logs
        print(str(e))
        return None


def generate_view_dependency_network_fs(schema_name):
    """
    Generates a network of feature store view dependencies for a given database schema.

    This function constructs a SQL query to identify dependencies between views and features
    in the specified schema. It returns a DataFrame that represents these dependencies,
    where each row contains a source view and its target dependency.

    Parameters:
    schema_name (str): The name of the database schema for which to generate the view dependency network.

    Returns:
    pd.DataFrame: A DataFrame representing the dependencies between views and features in the specified schema.
    """

    try:
        # Construct the pattern for matching view names in the schema
        pattern = '"' + schema_name + '".%'

        # SQL query to find dependencies between views and features
        query = f"""
        WITH SELECTED_PROCESS AS (
            SELECT * FROM NGramSplitter(
                ON (
                    CURRENT VALIDTIME
                    SELECT 
                        VIEW_NAME,
                        FEATURE_NAMES,
                        DATA_DOMAIN
                    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME}
                    WHERE VIEW_NAME LIKE '{pattern}'
                ) AS "input"
                PARTITION BY ANY
                USING
                TextColumn('FEATURE_NAMES')
                Grams('1')
                Delimiter(',')
                NGramColName('FEATURE_NAME')
            ) as sqlmr
        )
        SELECT DISTINCT
            A.VIEW_NAME AS source,
            '"'||B.FEATURE_DATABASE||'"."'||B.FEATURE_TABLE||'"' AS target
        FROM SELECTED_PROCESS AS A
        INNER JOIN (CURRENT VALIDTIME SEL * FROM {tdfs4ds.SCHEMA}.{tdfs4ds.FEATURE_CATALOG_NAME}) AS B
        ON A.DATA_DOMAIN = B.DATA_DOMAIN AND A.FEATURE_NAME = B.FEATURE_NAME"""

        # Execute the query and convert the result to a pandas DataFrame
        graph = tdml.DataFrame.from_query(query).to_pandas()

        return graph

    except Exception as e:
        # Print the first line of the exception message and return None
        print(str(e).split('\n')[0])
        return None



def get_ddl(view_name, schema_name, object_type='view'):
    """
    Retrieves the Data Definition Language (DDL) statement for a specified view or table in a database schema.

    This function executes a SQL query to obtain the DDL statement for a given view or table. It returns
    the DDL as a string, with line breaks appropriately formatted.

    Parameters:
    view_name (str): The name of the view or table for which to retrieve the DDL.
    schema_name (str): The name of the schema in which the view or table is located.
    object_type (str, optional): The type of object to retrieve the DDL for, either 'view' or 'table'.
                                  Defaults to 'view'.

    Returns:
    str: The DDL statement for the specified view or table.

    Raises:
    ValueError: If an invalid object_type is provided.
    """

    # Execute the appropriate SQL command based on the object type
    if object_type == 'view':
        # Retrieve DDL for a view
        ddl = tdml.execute_sql(f'SHOW VIEW {schema_name}.{view_name}').fetchall()[0][0]
    elif object_type == 'table':
        # Retrieve DDL for a table
        ddl = tdml.execute_sql(f'SHOW TABLE {schema_name}.{view_name}').fetchall()[0][0]
    else:
        # Raise an error if the object_type is not recognized
        raise ValueError("Invalid object_type. Authorized values are 'view' and 'table'")

    # Replace carriage returns with newlines for consistent formatting
    return ddl.replace('\r', '\n')

