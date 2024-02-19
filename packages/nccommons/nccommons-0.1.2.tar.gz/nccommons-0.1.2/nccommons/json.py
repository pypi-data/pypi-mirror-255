import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

def say_hello():
    print("Hello, World Broooo!")
    
#https://jsonpathfinder.com/
def modify_json(json_data, json_path, operation, value=None):
    path_parts = json_path.split('.')
    current_data = json_data
    for part in path_parts[:-1]:
        if '[' in part:
            part, index = part[:-1].split('[')
            index = int(index)
            current_data = current_data[part][index]
        else:
            if part not in current_data:
                current_data[part] = {} if path_parts[-1] != ']' else []
            current_data = current_data[part]

    final_part = path_parts[-1]
    if '[' in final_part:
        final_part, index = final_part[:-1].split('[')
        index = int(index)
    else:
        index = None
    
    if operation == 'add':
        if index is not None:
            while len(current_data.get(final_part, [])) <= index:
                current_data.setdefault(final_part, []).append(None)
            current_data[final_part][index] = value
        else:
            current_data[final_part] = value
    elif operation == 'remove':
        if index is not None:
            try:
                del current_data[final_part][index]
            except (KeyError, IndexError):
                pass 
        else:
            current_data.pop(final_part, None)
            print("hello")
    return json_data

def modify_json_bulk(json_data, modifications):
    """
    Modifies a JSON object based on a dictionary of modifications.
    Each key in the dictionary is a JSON path, and its value is a list containing [value, operation].

    :param json_data: The JSON data to modify.
    :param modifications: A dictionary of modifications.
    :return: The modified JSON data.
    """
    for json_path, (value, operation) in modifications.items():
        path_parts = json_path.split('.')
        current_data = json_data
        for part in path_parts[:-1]:
            if '[' in part:
                part, index = part[:-1].split('[')
                index = int(index)
                current_data = current_data[part][index]
            else:
                if part not in current_data:
                    current_data[part] = {} if path_parts[-1] != ']' else []
                current_data = current_data[part]

        final_part = path_parts[-1]
        if '[' in final_part:
            final_part, index = final_part[:-1].split('[')
            index = int(index)
        else:
            index = None

        if operation == 'add':
            if index is not None:
                while len(current_data.get(final_part, [])) <= index:
                    current_data.setdefault(final_part, []).append(None)
                current_data[final_part][index] = value
            else:
                current_data[final_part] = value
        elif operation == 'remove':
            if index is not None:
                try:
                    del current_data[final_part][index]
                except (KeyError, IndexError):
                    pass
            else:
                current_data.pop(final_part, None)
    return json_data


def schema_validator_wrapper(respons, schema):
    print("Validation successful.")
    response=json.loads(respons)
    if(validate(instance=response, schema=schema) is None):
        return "true"
    else:
        return "false"
