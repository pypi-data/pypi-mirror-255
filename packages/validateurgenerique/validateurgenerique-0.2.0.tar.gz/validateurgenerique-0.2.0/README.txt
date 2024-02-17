Package Name: validateurgenerique
Overview
This package provides utilities for data validation and transformation. It includes modules for schema validation, form validation, and various data transformations.

Installation
You can install the package using pip from PyPI or directly from GitLab.

From PyPI:
pip install validateurgenerique
From GitLab:
pip install validateurgenerique --index-url https://gitlab.com/api/v4/projects/54359493/packages/pypi/simple
Modules
schemavalidator.py
This module includes a SchemaValidator class for validating data against JSON schemas.

Example usage:
from validateurgenerique import SchemaValidator

# Create a schema validator instance
validator = SchemaValidator(schema=my_schema)

# Validate data against the provided schema
is_valid, errors = validator.validate_schema(data=my_data)
transformation.py
This module contains a Transformations class with various data transformation methods.

Example usage:
from validateurgenerique import Transformations

# Create a transformations instance
transformer = Transformations(date_formats=["%Y-%m-%d"])

# Transform date to a different format
transformed_date = transformer.transform_date(date_str="2024-02-05")
formvalidator.py
This module provides a FormValidator class for validating data against a specified form schema.

Example usage:
from validateurgenerique import FormValidator

# Create a form validator instance
validator = FormValidator(schema=my_form_schema)

# Validate data against the provided form schema
validation_errors = validator.validate_schema(data=my_form_data)
Example Use Cases
Schema Validation:
from validateurgenerique import SchemaValidator

# Create a schema validator instance
validator = SchemaValidator(schema=my_schema)

# Validate data against the provided schema
is_valid, errors = validator.validate_schema(data=my_data)
Data Transformation:
from validateurgenerique import Transformations

# Create a transformations instance
transformer = Transformations(date_formats=["%Y-%m-%d"])

# Transform date to a different format
transformed_date = transformer.transform_date(date_str="2024-02-05")
Form Validation:
from validateurgenerique import FormValidator

# Create a form validator instance
validator = FormValidator(schema=my_form_schema)

# Validate data against the provided form schema
validation_errors = validator.validate_schema(data=my_form_data)
Contributors
Gharbi Youssef 
License
This package is distributed under the MIT license.
