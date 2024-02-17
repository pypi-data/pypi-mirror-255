import teradataml as tdml
import functools
from packaging import version
def is_version_greater_than(tested_version, base_version="17.20.00.03"):
    """
    Check if the tested version is greater than the base version.

    Args:
        tested_version (str): Version number to be tested.
        base_version (str, optional): Base version number to compare. Defaults to "17.20.00.03".

    Returns:
        bool: True if tested version is greater, False otherwise.
    """
    return version.parse(tested_version) > version.parse(base_version)
def execute_query_wrapper(f):
    """
    Decorator to execute a query. It wraps around the function and adds exception handling.

    Args:
        f (function): Function to be decorated.

    Returns:
        function: Decorated function.
    """
    @functools.wraps(f)
    def wrapped_f(*args, **kwargs):
        query = f(*args, **kwargs)
        if is_version_greater_than(tdml.__version__, base_version="17.20.00.03"):
            if type(query) == list:
                for q in query:
                    try:
                        tdml.execute_sql(q)
                    except Exception as e:
                        print(str(e).split('\n')[0])
                        print(q)
            else:
                try:
                    tdml.execute_sql(query)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(query)
        else:
            if type(query) == list:
                for q in query:
                    try:
                        tdml.get_context().execute(q)
                    except Exception as e:
                        print(str(e).split('\n')[0])
                        print(q)
            else:
                try:
                    tdml.get_context().execute(query)
                except Exception as e:
                    print(str(e).split('\n')[0])
                    print(query)
        return

    return wrapped_f


def execute_query(query):
    """
    Execute a SQL query or a list of queries using the tdml module.

    This function checks the version of the tdml module and executes the
    query or queries accordingly. For versions greater than 17.20.00.03,
    it uses `tdml.execute_sql`, otherwise it uses `tdml.get_context().execute`.

    Parameters:
    query (str or list): A single SQL query string or a list of SQL query strings.

    Returns:
    The result of the SQL execution if a single query is passed. None if a list of queries is passed or an exception occurs.
    """
    # Check if the version of tdml is greater than the specified base version
    if is_version_greater_than(tdml.__version__, base_version="17.20.00.03"):
        # If query is a list, iterate and execute each query
        if type(query) == list:
            for q in query:
                try:
                    tdml.execute_sql(q)  # Execute the query
                except Exception as e:
                    # Print the first line of the exception and the query that caused it
                    print(str(e).split('\n')[0])
                    print(q)
        else:
            # If query is not a list, execute it and return the result
            try:
                return tdml.execute_sql(query)
            except Exception as e:
                # Print the first line of the exception and the query
                print(str(e).split('\n')[0])
                print(query)
    else:
        # For tdml versions not greater than the specified version
        if type(query) == list:
            for q in query:
                try:
                    # Use the older execution method for the query
                    tdml.get_context().execute(q)
                except Exception as e:
                    # Print the first line of the exception and the query
                    print(str(e).split('\n')[0])
                    print(q)
        else:
            try:
                # Execute the single query using the older method and return the result
                return tdml.get_context().execute(query)
            except Exception as e:
                # Print the first line of the exception and the query
                print(str(e).split('\n')[0])
                print(query)

    # No return value if a list of queries is executed or if an exception occurs
    return