import logging

from flask import Blueprint, url_for
from flask_restx import Api, apidoc, Namespace, Resource

from mutalyzer.util import log_dir
from .back_translate import ns as ns_back_translate
from .compare import ns as ns_compare
from .description_extract import ns as ns_description_extract
from .description_to_model import ns as ns_description_to_model
from .get_selectors import ns as ns_get_selectors
from .map import ns as ns_map
from .mutate import ns as ns_mutate
from .normalize import ns as ns_normalize
from .delins_model import ns as ns_delins_model
from .position_convert import ns as ns_position_convert
from .reference_model import ns as ns_reference_model
from .related_references import ns as ns_related_references
from .spdi_converter import ns as ns_spdi_converter
from .view_variants import ns as ns_view_variants

from pkg_resources import get_distribution


logging.basicConfig(level=logging.INFO, filename=log_dir())

API_VERSION = "2.1"


# Trick to make the swagger files available under "/api".
class PatchedApi(Api):
    def _register_apidoc(self, app):
        patched_api = apidoc.Apidoc(
            "restx_doc",
            "flask_restx.apidoc",
            template_folder="templates",
            static_folder="static",
            static_url_path="/api",
        )

        @patched_api.add_app_template_global
        def swagger_static(filename):
            return url_for("restx_doc.static", filename=filename)

        app.register_blueprint(patched_api)


blueprint = Blueprint("api", __name__)

api = PatchedApi(blueprint, version=API_VERSION, title="Mutalyzer3 API")

ns_version = Namespace("/")


@ns_version.route("/version")
class Version(Resource):
    def get(self):
        """Get versions."""
        return {"mutalyzer": get_distribution("mutalyzer").version, "api": API_VERSION}


api.add_namespace(ns_compare)
api.add_namespace(ns_map)
api.add_namespace(ns_mutate)
api.add_namespace(ns_normalize)
api.add_namespace(ns_delins_model)
api.add_namespace(ns_description_to_model)
api.add_namespace(ns_reference_model)
api.add_namespace(ns_related_references)
api.add_namespace(ns_position_convert)
api.add_namespace(ns_description_extract)
api.add_namespace(ns_get_selectors)
api.add_namespace(ns_view_variants)
api.add_namespace(ns_spdi_converter)
api.add_namespace(ns_back_translate)
api.add_namespace(ns_version)
