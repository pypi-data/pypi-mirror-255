import jsonschema
def validate_data(data, schema):
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.exceptions.ValidationError as err:
            print(err)
            return False
        return True