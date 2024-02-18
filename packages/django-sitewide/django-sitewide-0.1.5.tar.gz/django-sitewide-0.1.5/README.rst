========
sitewide
========

Sitewide is a Django app for creating and maintaining a consistent look across a django websie

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "sitewide" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "sitewide",
    ]

2. Include the sitewide URLconf in your project urls.py like this::

    path("", include("sitewide.urls")),

3. Run ``python manage.py migrate`` to create the model for sitewide settings.

4. To use sitewide, import it into the relevant views.py module and assign it to a variable within a view. Make the variable available to the template of choice via view-render contexts
