# -*- coding: utf-8 -*-
"""Create an application instance."""
import os
from flask import Flask
from halo_app.apis import load_api_config
from halo_app.ssm import set_app_param_config,set_host_param_config,get_app_param_config
from halo_app.app.viewsx import load_global_data
from halo_app.base_util import BaseUtil

#@todo remove aws from code
#@todo enable reflection for major functionality: saga,cache



def create_app(config_object='settings'):
    """
    An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    with app.app_context():
        stage = '/' + app.config['ENV_NAME']
        if app.config['SSM_TYPE'] and app.config['SSM_TYPE'] != 'NONE':
            load_api_config(app.config['ENV_TYPE'], app.config['SSM_TYPE'], app.config['FUNC_NAME'], app.config['API_CONFIG'])
            HALO_HOST = BaseUtil.get_host_name()
            params = {}
            params["url"] = set_host_param_config(HALO_HOST)
            set_app_param_config(app.config['SSM_TYPE'], params )
            val = get_app_param_config(app.config['SSM_TYPE'], app.config['FUNC_NAME'], "url")
            print("get_app_param_config=" + str(val))
        from tests.test_viewsx import TestLinkX
        app.add_url_rule(stage, view_func=TestLinkX.as_view("member"))

        if 'INIT_DATA_MAP' in app.config and 'INIT_CLASS_NAME' in app.config:
            data_map = app.config['INIT_DATA_MAP']
            class_name = app.config['INIT_CLASS_NAME']
            load_global_data(class_name,data_map)

    site_map(app)

    return app

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def site_map(app):
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = rule.rule
            links.append((url, rule.endpoint))
            print(str(url))

app = create_app()

