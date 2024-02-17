import jsonschema
from jsonschema import ValidationError

class SchemaValidator:
    def __init__(self, schema=None):
        self.schema = schema

    def validate_schema(self, data, schema=None):
        schema_to_use = schema or self.schema
        if not schema_to_use:
            raise ValueError("No schema provided for validation.")

        try:
            jsonschema.validate(instance=data, schema=schema_to_use)
            return True, None
        except ValidationError as e:
            error_messages = [f"Schema validation failed: {error.message}" for error in e.context]
            return False, error_messages
