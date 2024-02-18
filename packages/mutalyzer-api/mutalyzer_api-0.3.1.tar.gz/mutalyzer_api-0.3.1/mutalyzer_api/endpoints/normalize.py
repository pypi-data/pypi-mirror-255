from flask_restx import Namespace, Resource, inputs, reqparse

from mutalyzer.normalizer import normalize

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


@ns.route("/normalize/<string:description>")
class Normalizer(Resource):
    @ns.expect(_args)
    @errors
    def get(self, description):
        """Normalize a variant description."""
        return normalize(description, **_args.parse_args())
