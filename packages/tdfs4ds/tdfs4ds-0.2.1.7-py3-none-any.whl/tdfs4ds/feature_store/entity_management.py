import inspect
from tdfs4ds.feature_store.feature_store_management import feature_store_table_creation
def register_entity(entity_id):
    feature_store_table_name_float = feature_store_table_creation(entity_id, feature_type='FLOAT')
    feature_store_table_name_integer = feature_store_table_creation(entity_id, feature_type='BIGINT')
    feature_store_table_name_varchar = feature_store_table_creation(entity_id, feature_type='VARCHAR')

    return feature_store_table_name_float,feature_store_table_name_integer,feature_store_table_name_varchar

def tdstone2_entity_id(existing_model):
    """
    Generate a dictionary mapping entity IDs to their respective data types in a given model.

    This function iterates over the 'id_row' attribute of the 'mapper_scoring' object in the provided model.
    It then creates a dictionary where each key is an entity ID and its corresponding value is the data type of that entity ID,
    as defined in the 'types' attribute of the 'mapper_scoring' object.

    Args:
        existing_model (object): The model object that contains the 'mapper_scoring' attribute with necessary information.
                                 It is expected to have 'id_row' and 'types' attributes.

    Returns:
        dict: A dictionary where keys are entity IDs and values are their respective data types.

    Raises:
        TypeError: If the 'id_row' attribute in the model is not a list or a single value.

    Note:
        - If 'id_row' is a single value (not a list), it is converted into a list with that single value.
        - The function assumes 'mapper_scoring' and its attributes ('id_row' and 'types') are properly defined in the model.

    Example:
        entity_id = tdstone2_entity_id(model)
        # entity_id might look like {'ID': 'BIGINT'}
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