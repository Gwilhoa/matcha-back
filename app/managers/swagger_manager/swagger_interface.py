import re
from dataclasses import dataclass

from apispec import APISpec
from apispec.exceptions import DuplicateComponentNameError
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Blueprint, Flask
from flask_swagger_ui import get_swaggerui_blueprint


@dataclass
class SwaggerParams:
    title: str
    version: str
    openapi_version: str
    plugins: list = None
    swagger_ui: bool = True
    components: dict = None
    security_definitions: dict = None
    security: list = None
    info: dict = None
    url_prefix: str = '/doc'


class SwaggerInterface:
    PATH_RE = re.compile(r'<(?:[^:<>]+:)?([^<>]+)>')

    def __init__(
        self,
        params: SwaggerParams,
    ):
        if params.plugins is None:
            params.plugins = []
        self.title = params.title
        self.version = params.version
        self.openapi_version = params.openapi_version
        self.plugins = params.plugins
        self.plugins.append(FlaskPlugin())
        self.plugins.append(MarshmallowPlugin())
        self.swagger_ui = params.swagger_ui
        self.components = params.components
        self.security_definitions = params.security_definitions
        self.security = params.security
        self.info = params.info
        self.url = params.url_prefix
        self.app = None
        self.docs: APISpec = APISpec(
            title=self.title,
            version=self.version,
            openapi_version=self.openapi_version,
            plugins=self.plugins,
            swagger_ui=self.swagger_ui,
            components=self.components,
            securityDefinitions=self.security_definitions,
            security=self.security,
            info=self.info,
        )
        self.functions = []

    def init_app(self, app: Flask):
        self.app = app
        swaggerui_blueprint = get_swaggerui_blueprint(
            self.url,
            f'{self.url}/swagger',
            config={
                'app_name': self.title,
            },
        )
        swagger_blueprint = Blueprint(f'{self.title}_blueprint', __name__)
        swagger_blueprint.add_url_rule(
            f'{self.url}/swagger',
            view_func=lambda: self.docs.to_dict(),
        )

        app.register_blueprint(swaggerui_blueprint)
        app.register_blueprint(swagger_blueprint)

        for function in self.functions:
            rules = self.app.url_map._rules_by_endpoint[function['endpoint']]
            with app.app_context():
                for rule in rules:
                    method = rule.methods - {'HEAD', 'OPTIONS'}
                    method = list(method)[0].lower()
                    swagger_info = getattr(function['target_function'], '_swagger_info', {})
                    info = {
                        'summary': function['target_function'].__name__,
                        'tags': [function['blueprint'].name.replace('_blueprint', '')],
                        'parameters': [],
                    }
                    if response := swagger_info.get('responses', None):
                        info['responses'] = response
                    if body := swagger_info.get('requestBody', None):
                        info['requestBody'] = body
                    if header := swagger_info.get('headers', None):
                        info['parameters'] = header
                    for param in re.findall(r'<([^>]+)>', rule.rule):
                        param_name = param.split(':')[-1]
                        param_type = param.split(':')[0]
                        info['parameters'].append(
                            {
                                'name': param_name,
                                'in': 'path',
                                'required': True,
                                'schema': {'type': param_type},
                                'description': f'{param_name} parameter',
                            }
                        )
                    self.docs.path(
                        view=function['target_function'],
                        path=self._rule_to_path(rule),
                        operations={method: info},
                        consumes=['multipart/form-data'],
                    )

    def _rule_to_path(self, rule):
        return self.PATH_RE.sub(r'{\1}', rule.rule)

    def register_function(self, target_function, target_blueprint):
        endpoint = f'{target_blueprint.name}.{target_function.__name__.lower()}'
        target_function.__doc__ = None
        self.functions.append({'endpoint': endpoint, 'target_function': target_function, 'blueprint': target_blueprint})

    def register_schema(self, schema):
        try:
            self.docs.components.schema(schema.__class__.__name__, schema=schema)
        except DuplicateComponentNameError:
            pass
