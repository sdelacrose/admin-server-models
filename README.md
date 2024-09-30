# Shared Userinfo Package

This Django app provides a custom `User` model and integrates with Django's groups and permissions system.

## Installation

1. Install the package:

    ```bash
    pip install models
    ```

2. Add `'models'` to your `INSTALLED_APPS` in your Django settings.

3. Run the migrations:

    ```bash
    python manage.py migrate
    ```

## Usage

Import the `User` model from the package:

```python
from models.models import User
