from flask_restx import abort
from functools import wraps


def errors(endpoint):
    @wraps(endpoint)
    def dec(*args, **kwargs):
        output = endpoint(*args, **kwargs)
        if isinstance(output, dict) and output.get("errors"):
            abort(422, "Errors encountered. Check the 'custom' field.", custom=output)
        return output

    return dec
