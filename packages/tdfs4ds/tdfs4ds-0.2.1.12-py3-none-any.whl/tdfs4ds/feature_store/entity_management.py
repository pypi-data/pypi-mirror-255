import inspect
from tdfs4ds.feature_store.feature_store_management import feature_store_table_creation
def register_entity(entity_id):
    """
    Registers an entity in the feature store by creating three types of feature store tables.

    This function calls the `feature_store_table_creation` function for three different
    feature types: 'FLOAT', 'BIGINT', and 'VARCHAR'. Each call creates a feature store table
    for the specified entity and feature type.

    Parameters:
    entity_id (str): The identifier of the entity for which feature store tables are created.

    Returns:
    tuple: A tuple containing the names of the created feature store tables. The tuple includes
           the names of the float feature table, the bigint feature table, and the varchar feature
           table, in that order.

    Example:
    >>> register_entity("entity123")
    ("float_table_name", "bigint_table_name", "varchar_table_name")
    """
    feature_store_table_name_float = feature_store_table_creation(entity_id, feature_type='FLOAT')
    feature_store_table_name_integer = feature_store_table_creation(entity_id, feature_type='BIGINT')
    feature_store_table_name_varchar = feature_store_table_creation(entity_id, feature_type='VARCHAR')

    return feature_store_table_name_float,feature_store_table_name_integer,feature_store_table_name_varchar

def tdstone2_entity_id(existing_model):
    """
    Generate a dictionary mapping entity IDs to their respective data types in a given tdstone2 model.

    This function analyzes the provided tdstone2 model object to determine the type of the model ('model scoring' or 'feature engineering').
    Depending on the model type, it retrieves the list of entity IDs from the appropriate mapper attribute ('mapper_scoring' or 'mapper').
    It then constructs a dictionary where each key is an entity ID, and its corresponding value is the data type of that entity ID,
    as specified in the model's mapper attributes ('types').

    Args:
        existing_model (object): A model object created using the tdstone2 package.
                                 This object should contain the necessary mapper attributes ('mapper_scoring' or 'mapper') with 'id_row', 'id_partition', and 'types'.

    Returns:
        dict: A dictionary mapping entity IDs to their data types.
              Keys are entity IDs, and values are data types (e.g., 'BIGINT').

    Raises:
        TypeError: If the relevant ID attribute ('id_row' or 'id_partition') in the model is neither a list nor a single value.

    Note:
        - The function dynamically determines the type of the model (scoring or feature engineering) based on the presence of specific attributes.
        - 'id_row' or 'id_partition' is converted to a list if it is not already one.
        - This function assumes the model is correctly instantiated and the necessary attributes are properly defined.

    Example:
        model = <instance of tdstone2 model>
        entity_id_types = tdstone2_entity_id(model)
        # entity_id_types might look like {'ID': 'BIGINT'}
    """

    # Initialize an empty dictionary to store entity IDs and their data types.
    entity_id = {}

    # Retrieve the list of IDs from the 'id_row' attribute of 'mapper_scoring' in the model.
    if 'score' in [x[0] for x in inspect.getmembers(type(existing_model))]:
        ids = existing_model.mapper_scoring.id_row
        model_type = 'model scoring'
    elif existing_model.feature_engineering_type == 'feature engineering reducer':
        ids = existing_model.mapper.id_partition
        model_type = 'feature engineering'
    else:
        ids = existing_model.mapper.id_row
        model_type = 'feature engineering'

    # Ensure 'ids' is a list. If not, convert it into a list.
    if type(ids) != list:
        ids = [ids]

    # Iterate over each ID in 'ids' and map it to its corresponding data type in the dictionary.
    if model_type == 'model scoring':
        for k in ids:
            entity_id[k] = existing_model.mapper_scoring.types[k]
    else:
        for k in ids:
            entity_id[k] = existing_model.mapper.types[k]

    # Return the dictionary containing mappings of entity IDs to data types.
    return entity_id