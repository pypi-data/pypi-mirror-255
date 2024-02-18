# Pydantic DbModel Core

## Overview

The `pydantic-dbmodel-core` library presents the `DbModelCore` class, an augmentation of the `BaseModel` class from Pydantic. This enhancement is achieved through a change in the `ModelMetaclass` meta-class, enabling the coexistence of class variables and instance variables with identical names. This feature, available in Pydantic V1 but absent in Pydantic V2, has been reintroduced with this small yet crucial modification.

## Installation

To install `pydantic-dbmodel-core`, run the following command:

```bash
pip install pydantic-dbmodel-core
```

## Usage

Import the `DbModelCore` class from the library and use it as you would use Pydantic's `BaseModel`.

```python
from pydantic_dbmodel_core import DbModelCore

class YourModel(DbModelCore):
    # Define your fields here
    pass
```

## Features

- Allows the definition of class variables with the same name as instance variables.
- Fully compatible with Pydantic's field definitions and validators.