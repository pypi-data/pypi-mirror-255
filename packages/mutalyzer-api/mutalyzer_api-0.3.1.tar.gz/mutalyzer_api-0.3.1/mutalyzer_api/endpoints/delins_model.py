from flask_restx import Namespace, Resource, inputs, reqparse

from mutalyzer.normalizer import delins_model

from .common import errors

ns = Namespace("/")


_args = reqparse.RequestParser()

_args.add_argument(
    "sequence",
    type=str,
    help="Reference sequence.",
    required=False,
)

_args.add_argument(
    "only_variants",
    type=inputs.boolean,
    help="The description consists only of variants.",
    default=False,
    required=False,
)


@ns.route("/delins_model/<string:description>")
class DelinsModel(Resource):
    @ns.expect(_args)
    @errors
    def get(self, description):
        """Obtain the delins model of a variant description (zero-based half-open locations)."""
        return delins_model(description, **_args.parse_args())
