from flask_restx import Namespace, Resource, api

from mutalyzer.mutator import mutate

from .common import errors

ns = Namespace("/")


@ns.route("/mutate/<string:description>")
class Mutate(Resource):
    @errors
    def get(self, description):
        """Obtain the observed sequence from a description."""
        return mutate(description)
