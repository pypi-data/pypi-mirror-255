
def get_column_types(df, columns):
    """
    Retrieve the column types for specified columns from a DataFrame.

    This function gets the types of specified columns in a DataFrame. For columns of type VARCHAR,
    it further specifies the character set. It is tailored to work with DataFrames that have
    specific attributes like `_td_column_names_and_types` and `_td_column_names_and_sqlalchemy_types`,
    which are not standard in typical pandas DataFrames.

    Parameters:
    df (DataFrame): The DataFrame from which to get the column types.
    columns (list or str): A list of column names or a single column name whose types are to be retrieved.

    Returns:
    dict: A dictionary where keys are column names and values are their types.
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

    This function simplifies the column types of the specified columns in a DataFrame.
    It translates database-specific data types (like INTEGER, BYTEINT, etc.) to more
    generalized Python data types (like int, float). It assumes the DataFrame has a
    specific attribute `_td_column_names_and_types` which stores column names and their types.

    Parameters:
    df (DataFrame): The DataFrame from which to get the column types.
    columns (list or str): A list of column names or a single column name whose types are to be retrieved.

    Returns:
    dict: A dictionary where keys are column names and values are simplified data types.
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