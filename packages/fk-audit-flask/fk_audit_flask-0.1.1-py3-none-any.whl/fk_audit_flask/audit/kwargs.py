
from fk_audit_flask import SETTINGS


def create_kwargs(kwargs: dict):
    if SETTINGS.HEADERS is True:
        from fk_audit_flask.utils.flask import KwargsFlask
        return kwargs | KwargsFlask.get_kwargs(SETTINGS)
    return kwargs
