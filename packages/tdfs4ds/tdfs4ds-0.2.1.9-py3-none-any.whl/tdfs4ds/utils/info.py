
def get_column_types(df, columns):
    """
    Retrieve the column types for specified columns from a TeradataML DataFrame.

    This function retrieves the data types of specified columns in a TeradataML DataFrame. It is tailored to work with
    DataFrames that have specific attributes like `_td_column_names_and_types` and `_td_column_names_and_sqlalchemy_types`,
    which are not standard in typical pandas DataFrames.

    Parameters:
    - df (DataFrame): The TeradataML DataFrame from which to get the column types.
    - columns (list or str): A list of column names or a single column name whose types are to be retrieved.

    Returns:
    dict: A dictionary where keys are column names and values are their types, including character set for VARCHAR columns.

    Notes:
    - This function is designed to work with TeradataML DataFrames, which may have extended column type information.
    - For VARCHAR columns, it retrieves the detailed type information, including the character set.

    Dependencies:
    - TeradataML DataFrame containing attributes '_td_column_names_and_types' and '_td_column_names_and_sqlalchemy_types'.
    """

    # Convert columns to a list if it's not already a list
    if type(columns) != list:
        columns = [columns]

    # Build a dictionary of column types for the specified columns
    col_type = {x[0]: x[1] for x in df._td_column_names_and_types if x[0] in columns}

    # Iterate over the column types
    for k, v in col_type.items():
        # Special handling for columns of type VARCHAR
        if v == 'VARCHAR':
            # Retrieve detailed type information, including character set
            temp = df._td_column_names_and_sqlalchemy_types[k.lower()]
            col_type[k] = f"{temp.compile()} CHARACTER SET {temp.charset}"

    return col_type



def get_column_types_simple(df, columns):
    """
    Retrieve simplified column types for specified columns from a DataFrame.

    This function simplifies the data types of the specified columns in a DataFrame, translating database-specific data types
    (such as INTEGER, BYTEINT, etc.) into more generalized Python data types (e.g., int, float). It assumes the DataFrame has
    a specific attribute '_td_column_names_and_types' that stores column names and their types.

    Parameters:
    - df (DataFrame): The DataFrame from which to get the column types.
    - columns (list or str): A list of column names or a single column name whose types are to be retrieved.

    Returns:
    dict: A dictionary where keys are column names and values are simplified Python data types.

    Notes:
    - This function is designed to work with DataFrames that have a specific attribute '_td_column_names_and_types'.
    - It uses a mapping from specific database column types to simplified Python data types for simplification.

    Dependencies:
    - DataFrame containing the '_td_column_names_and_types' attribute.
    """

    # Ensure that the columns parameter is in list format
    if type(columns) != list:
        columns = [columns]

    # Extract the column types for the specified columns
    col_type = {x[0]: x[1] for x in df._td_column_names_and_types if x[0] in columns}

    # Define a mapping from specific database column types to simplified Python data types
    mapping = {'INTEGER': 'int',
               'BYTEINT': 'int',
               'BIGINT': 'int',
               'FLOAT': 'float'
               }

    # Update the column types in the dictionary using the mapping
    for k, v in col_type.items():
        if v in mapping:
            col_type[k] = mapping[v]

    return col_type