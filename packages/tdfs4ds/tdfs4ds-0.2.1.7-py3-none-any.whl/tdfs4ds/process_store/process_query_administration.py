import teradataml as tdml
import tdfs4ds
from tdfs4ds.utils.query_management import execute_query_wrapper

def list_processes():
    """
    Retrieves and returns a list of all processes from the feature store.
    The function fetches details like process ID, type, view name, entity ID,
    feature names, feature version, and metadata.

    Returns:
    DataFrame: A DataFrame containing the details of all processes in the feature store.
    """

    # Constructing the SQL query to fetch process details
    query = f"""
    CURRENT VALIDTIME
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

    Args:
    process_id (str): The unique identifier of the process to be removed.

    Returns:
    str: SQL query string that deletes the specified process from the process catalog.
    """

    # Constructing SQL query to delete a process by its ID
    query = f"DELETE FROM {tdfs4ds.SCHEMA}.{tdfs4ds.PROCESS_CATALOG_NAME} WHERE process_id = '{process_id}'"

    # Returning the SQL query string
    return query

def get_process_id(view_name):
    """
    Retrieves the process ID associated with a given view name in a database.

    This function first formats the `view_name` to match the database's naming conventions.
    It then queries a list of processes and returns the process ID that corresponds to the specified view name.

    Parameters:
    view_name (str): The name of the view for which the process ID is to be retrieved.
                     This can be either just the view name or a combination of database name and view name.

    Returns:
    int: The process ID associated with the given view name.
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
