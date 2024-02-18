# django-willing-zg
A Django app to hold common utilities for Zygoat-managed applications


## What it does
`willing_zg` provides a means to define frontend configuration in the django settings and an API endpoint to make that configuration accessible.

## Usage
1. Add "willing_zg" to `INSTALLED_APPS` in the django settings

2. Define `ZYGOAT_FRONTEND_META_CONFIG` in the django settings

    ZYGOAT_FRONTEND_META_CONFIG = { "example_frontend_config": "example_value" }

3. Include the willing_zg URLconf in your project's urls.py:

    path('api/zygoat/', include('willing_zg.urls')),

4. Import willing-zg settings into the django settings

   from willing_zg.settings import * # noqa


## Running locally for development
1. checkout the directory into the `backend` directory of the app you're developing in

2. modify your Dockerfile.local and add `ADD /django-willing-zg /django-willing-zg` above `WORKDIR /code` and add ` RUN poetry add --editable /django-willing-zg` after poetry install
