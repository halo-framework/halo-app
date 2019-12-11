# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask import Flask
from flask_restful import Api


def create_app(config_object='settings'):
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    with app.app_context():
        from halo_flask.apis import load_api_config
        from halo_flask.flask.viewsx import PerfLinkX
        if app.config['SSM_TYPE'] != 'NONE':
            load_api_config(app.config['ENV_TYPE'], app.config['SSM_TYPE'], app.config['FUNC_NAME'], app.config['API_CONFIG'])
        # @TODO add test endpoint?
        #app.add_url_rule("/", view_func=TestLinkX.as_view("member"))
        app.add_url_rule("/perf", view_func=PerfLinkX.as_view("perf"))

    api = Api(app, catch_all_404s=True)

    return app


app = create_app()
