"""
Indicate Django application directory. Allows zut to be added in INSTALLED_APP with simple name:

    INSTALLED_APP = [
        ...
        'zut',
        ...
    ]
"""
from __future__ import annotations
from django.apps import AppConfig

class ZutAppConfig(AppConfig):
    name = "zut.django"
    label = "zut"
