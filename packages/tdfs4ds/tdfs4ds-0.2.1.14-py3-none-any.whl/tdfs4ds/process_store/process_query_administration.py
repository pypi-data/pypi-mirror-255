import teradataml as tdml
import tdfs4ds
from tdfs4ds.utils.query_management import execute_query_wrapper

def list_processes():
    """
    Retrieves and returns a list of all processes from the feature store.

    This function constructs and executes a SQL query to fetch details of all processes
    stored in the feature store. The details include process ID, process type, view name,
    entity ID, feature names, feature version, data domain, and metadata. The function
    handles different states of the feature store time, choosing either the current valid time
    or a specific timestamp based on the configuration. It also optionally prints the constructed
    SQL query, depending on the configuration. If the query execution fails, the function
    catches the exception, prints the error message, and the query for debugging purposes.

    Returns:
        DataFrame: A pandas DataFrame containing the details of all processes in the feature store.
                  The columns of the DataFrame correspond to the process ID, process type, view name,
                  entity ID, feature names, feature version, data domain, and metadata.

    Raises:
        Exception: If the query execution fails, the function prints the exception message and the query.
    """

    if tdfs4ds.FEATURE_STORE_TIME == None:
        validtime_statement = 'CURRENT VALIDTIME'
    else:
        validtime_statement = f"VALIDTIME AS OF TIMESTAMP '{tdfs4ds.FEATURE_STORE_TIME}'"

    # Constructing the SQL query to fetch process details
    query = f"""
    {validtime_statement}
    SELECT 
        PROCESS_ID ,
        PROCESS_TYPE ,
        VIEW_NAME ,
        ENTITY_ID ,
        FEATURE_NAMES ,
        FEATURE_VERSION AS PROCESS_VERSION,
        DATA_DOMAIN,
        METADATA
    FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME}
    """

    # Optionally printing the query if configured to do so
    if tdml.display.print_sqlmr_query:
        print(query)

    # Executing the query and returning the result as a DataFrame
    try:
        return tdml.DataFrame.from_query(query)
    except Exception as e:
        print(str(e))
        print(query)




@execute_query_wrapper
def remove_process(process_id):
    """
    Deletes a process from the feature store's process catalog based on the given process ID.

    This function constructs an SQL query to delete a process from the feature store's process
    catalog, using the provided process ID. It utilizes a decorator, `execute_query_wrapper`,
    which likely handles the execution and potential error handling of the SQL query. The
    function itself constructs the delete query and returns it as a string. This functionality is
    particularly useful for maintaining or updating the state of the feature store by removing
    outdated or unnecessary processes.

    Args:
    process_id (str): The unique identifier of the process to be removed. This ID is used to
                      specify which process should be deleted from the process catalog.

    Returns:
    str: A SQL query string that, when executed, deletes the specified process from the
         process catalog. This query identifies the process to be removed based on its unique ID.

    Note:
    The actual execution of the SQL query is handled by the `execute_query_wrapper` decorator,
    which is not detailed in this docstring.
    """

    # Constructing SQL query to delete a process by its ID
    query = f"DELETE FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} WHERE process_id = '{process_id}'"

    # Returning the SQL query string
    return query

def get_process_id(view_name):
    """
    Retrieves the process ID associated with a given view name in a database.

    This function is designed to obtain the process ID for a specified view within a database.
    Initially, it formats the provided `view_name` to conform to the database's naming conventions,
    including handling scenarios where the view name is prefixed with a database name. After formatting
    the view name, the function queries a list of processes using an assumedly predefined function
    `list_processes`. It then filters this list to find the process corresponding to the formatted view name
    and returns the associated process ID. The function assumes specific column names ('VIEW_NAME' and
    'PROCESS_ID') in the data structure returned by `list_processes` and that these columns are in a
    specific format (e.g., uppercase for view names).

    Parameters:
    view_name (str): The name of the view for which the process ID is to be retrieved.
                     This can be either just the view name or a combination of database name and view name,
                     formatted as 'database.view'.

    Returns:
    int: The process ID associated with the given view name. This ID is retrieved from a list of
         processes, where it is associated with the view name that matches the input.

    Raises:
    IndexError: If no process is found with the given view name.
    """

    # Remove any double quotes from the input view name
    view_name = view_name.replace('"', '')

    # Check if the view name includes a database name (i.e., it contains a dot)
    if len(view_name.split('.')) > 1:
        # Format the view name as "database"."view_name" with quotes
        view_name = '.'.join(['"'+x+'"' for x in view_name.split('.')])
    else:
        # Format the view name as "default_schema"."view_name" with quotes
        # Note: 'tdfs4ds.SCHEMA' refers to a default schema name
        view_name = '"'+tdfs4ds.SCHEMA+'"."'+view_name+'"'

    # Retrieve a list of processes (assumes list_processes is a function defined elsewhere)
    list_processes_ = list_processes()

    # Filter the list to find the process with the matching view name and return its ID
    # Assumes VIEW_NAME is a column in the list_processes and is in uppercase
    # Also assumes PROCESS_ID is a column containing the process IDs
    return list_processes_[list_processes_.VIEW_NAME == view_name.upper()].to_pandas().PROCESS_ID.values[0]
