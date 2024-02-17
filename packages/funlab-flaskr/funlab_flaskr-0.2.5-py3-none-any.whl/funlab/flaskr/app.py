from __future__ import annotations
import argparse

import logging
from cryptography.fernet import Fernet
from flask import (Blueprint, Flask, g, redirect, render_template, request, url_for)
from flask_login import AnonymousUserMixin, LoginManager, current_user, login_required

from funlab.flaskr.menu import AbstractMenu, Menu, MenuBar, MenuItem, MenuDivider
from funlab.flaskr.plugin import SecurityPlugin, ViewPlugin
from funlab.core import _Configuable
from funlab.utils import log
from funlab.core.config2 import Config
from funlab.core.dbmgr2 import DbMgr
from funlab.utils.plugin import load_plugins
from sqlalchemy.orm import registry
# 在table, entity間有相關性時, 例user, manager, account, 必需使用同一個registry去宣告entity
# 否則sqlalchemy會因registry資訊不足而有錯誤,
# 例: Foreign key associated with column 'account.manager_id' could not find table 'user' with which to generate a foreign key to target column 'id'
# 並此 registry 可用初如化時create db table
APP_ENTITIES_REGISTRY = registry()

class FunlabFlask(_Configuable, Flask):
    def __init__(self, configfile:str, env_file:str, *args, **kwargs):
        self.mylogger = log.get_logger(self.__class__.__name__, level=logging.INFO)
        self.mylogger.info('Funlab Flask create started ...')
        super().__init__(*args, **kwargs)
        self.mylogger.info('Funlab Flask setup configuration ...')
        self.login_manager = None
        self.myconfig:Config = None
        self._setup_config(configfile, env_file)
        self.dbmgr: DbMgr = DbMgr(self.config['DATABASE'])

        if not (app_logo:=self.config.get('APP_LOGO')):
            app_logo = '/static/logo.svg'
            self.config.update({'APP_LOGO': app_logo})
        self._mainmenu:MenuBar = MenuBar(title='FunLab', icon=f"{ self.config['APP_LOGO'] }", href='/')
        self._usermenu:Menu = Menu(title="", dummy=True, collapsible=True, expand=False)
        self._adminmenu = Menu(title="Admin"
                        ,icon='<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-tool" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"></path><path d="M7 10h3v-3l-3.5 -3.5a6 6 0 0 1 8 8l6 6a2 2 0 0 1 -3 3l-6 -6a6 6 0 0 1 -8 -8l3.5 3.5"></path></svg>'
                        ,admin_only=True, collapsible=False)
        self.plugins = {}
        self._register_root_routes()
        self._register_plugins()
        if self.login_manager is None:
            self.login_manager = LoginManager()
            self.login_manager.init_app(self)
            self.login_manager.login_view = 'root_bp.blank'
            @self.login_manager.user_loader
            def user_loader(user_id):
                return AnonymousUserMixin()

        self._register_request_handler()
        # self._register_exception_handler()
        self._register_jinja_filters()
        self.dbmgr.create_registry_tables(APP_ENTITIES_REGISTRY)
        # make as last one, after plugins created
        self.add_usermenu([MenuDivider(),
                        MenuItem(title='Configuration',
                            icon='<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-info-octagon-filled" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M14.897 1a4 4 0 0 1 2.664 1.016l.165 .156l4.1 4.1a4 4 0 0 1 1.168 2.605l.006 .227v5.794a4 4 0 0 1 -1.016 2.664l-.156 .165l-4.1 4.1a4 4 0 0 1 -2.603 1.168l-.227 .006h-5.795a3.999 3.999 0 0 1 -2.664 -1.017l-.165 -.156l-4.1 -4.1a4 4 0 0 1 -1.168 -2.604l-.006 -.227v-5.794a4 4 0 0 1 1.016 -2.664l.156 -.165l4.1 -4.1a4 4 0 0 1 2.605 -1.168l.227 -.006h5.793zm-2.897 10h-1l-.117 .007a1 1 0 0 0 0 1.986l.117 .007v3l.007 .117a1 1 0 0 0 .876 .876l.117 .007h1l.117 -.007a1 1 0 0 0 .876 -.876l.007 -.117l-.007 -.117a1 1 0 0 0 -.764 -.857l-.112 -.02l-.117 -.006v-3l-.007 -.117a1 1 0 0 0 -.876 -.876l-.117 -.007zm.01 -3l-.127 .007a1 1 0 0 0 0 1.986l.117 .007l.127 -.007a1 1 0 0 0 0 -1.986l-.117 -.007z" stroke-width="0" fill="currentColor" /></svg>',
                            href='/conf_data', admin_only=True),
                        MenuItem(title='about',
                            icon='<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-info-square-rounded" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 9h.01" /><path d="M11 12h1v4h1" /><path d="M12 3c7.2 0 9 1.8 9 9s-1.8 9 -9 9s-9 -1.8 -9 -9s1.8 -9 9 -9z" /></svg>',
                            href='/about'),
                        ])
        self.mylogger.info('Funlab Flask created.')

    def get_section_config(self, section:str, default=None, case_insensitive=False):
        return self.myconfig.get_section_config(section=section, default=default, case_insensitive=case_insensitive)

    @property
    def env_vars(self):
        return self.myconfig._env_vars

    @property
    def mainmenu(self):
        return self._mainmenu.html(layout=request.args.get('layout', 'vertical'), user=current_user)

    @property
    def usermenu(self):
        return self._usermenu.html(layout='vertical', user=current_user)

    def add_mainmenu(self, menus:list[AbstractMenu]|AbstractMenu)->Menu:
        self._mainmenu.append(menus)

    def add_adminmenu(self, menus:list[AbstractMenu]|AbstractMenu)->Menu:
        self._adminmenu.append(menus)

    def add_usermenu(self, menus:list[AbstractMenu]|AbstractMenu)->Menu:
        self._usermenu.append(menus)

    def _setup_config(self, configfile, env_file:str=None):
        def setup_flask_env():
            env_config = flask_config.get('ENV')
            for key, value in env_config.items():
                flask_config.update({key:value})
            flask_config.pop('ENV')
            if not 'SECRET_KEY' in flask_config:
                flask_config.update({'SECRET_KEY': Fernet.generate_key().decode(),})
            # try to automate get version infomation from metadata, failed
            # flask_config.update({'VERSION': importlib.metadata.version(flask_config.get('PROJ_NAME'))})

            # self.config is Flask's config
            self.config.from_mapping(flask_config)

        if configfile:
            self.myconfig: Config = Config(configfile, env_file_or_values=env_file)
        else:
            self.myconfig : Config = Config({})

        # self.myconfig.join(app_default_config)
        flask_config = self.get_config('config.toml', section='FLASK', ext_config=self.myconfig).as_dict()
        setup_flask_env()

    def _register_root_routes(self):
        self.blueprint = Blueprint(
            'root_bp',
            import_name='funlab.flaskr',
            static_folder='static',
            template_folder='templates',
        )
        # set route for blueprint
        @self.blueprint.route('/')
        def index():
            if current_user.is_authenticated:
                return redirect(url_for('root_bp.home'))
            else:
                return redirect(url_for(self.login_manager.login_view))

        @self.blueprint.route('/blank')
        def blank():
            return render_template('blank.html')

        @self.blueprint.route('/home')
        @login_required
        def home():
            home_entry:str=None
            if home_entry:=self.config.get("HOME_ENTRY", None):
                if home_entry.endswith(('.html', '.htm',)):
                    return render_template(home_entry)
                else:
                    return redirect(url_for(home_entry))
            else:
                return render_template('blank.html')

        @self.blueprint.route('/conf_data')
        @login_required
        def conf_data():
            return render_template('conf-data.html', config=self.myconfig.as_dict())

        @self.blueprint.route('/about')
        def about():
            about_entry:str=None
            if about_entry:=self.config.get("ABOUT_ENTRY", None):
                if about_entry.endswith(('.html', '.htm',)):
                    return render_template(about_entry)
                else:
                    return redirect(url_for(about_entry))
            else:
                return render_template('about.html')

        # Need to call flask's register_blueprint for all route, after route defined
        self.register_blueprint(self.blueprint)

    def _register_plugins(self):
        def init_plugin_object(plugin_cls:type[ViewPlugin]):
            plugin: ViewPlugin = plugin_cls(self)
            self.plugins[plugin.name] = plugin
            # self.mylogger.info(f"Loaded: {plugin.name}:{plugin.__class__.__name__}")
            if blueprint:=plugin.blueprint:
                self.register_blueprint(blueprint)

            # create sqlalchemy registry db table for each plugin
            if plugin.entities_registry:
                self.dbmgr.create_registry_tables(plugin.entities_registry)

            return plugin


        self.mylogger.info('Funlab Flask searching plugins ...')
        plugin_classes:dict = load_plugins(group='funlab_plugin')
        ordered_plugins:list = []
        # add priority plugins first, this for preventing dependency issue
        priority_plugins = self.config.get('PRIORITY_PLUGINS', [])
        for plugin_classname in priority_plugins:
            if plugin_cls:=plugin_classes.pop(plugin_classname, None):
                ordered_plugins.append(plugin_cls)
        # add rest of plugins
        for plugin_cls in plugin_classes.values() :
            ordered_plugins.append(plugin_cls)

        installed_security_plugin = None
        for plugin_cls in ordered_plugins :
            self.mylogger.info(f"Loading plugin: {plugin_cls.__name__}")
            plugin = init_plugin_object(plugin_cls)
            if isinstance(plugin, SecurityPlugin):
                if installed_security_plugin:
                    msg = f"There is SecurityPlugin, named '{installed_security_plugin}' had been installed for login_manager. {plugin_cls} skipped."
                    self.mylogger.warning(msg)
                    continue
                else:
                    installed_security_plugin = plugin
        if installed_security_plugin:
            self.login_manager = installed_security_plugin.login_manager
            self.login_manager.init_app(self)
            # set login_view for each plugin
            if installed_security_plugin.login_view:
                self.login_manager.blueprint_login_views[installed_security_plugin.bp_name] = installed_security_plugin.login_view

        self._mainmenu.append(self._adminmenu)
        # append adminmenu to last, and useless
        del self._adminmenu

    def _register_request_handler(self):
        @self.teardown_request
        def shutdown_session(exception=None):
            self.dbmgr.remove_all_sessions()

        @self.before_request
        def set_global_variables():
            g.mainmenu = self.mainmenu
            g.usermenu = self.usermenu

    def _register_jinja_filters(self):
        from funlab.flaskr import jinja_filters
        for module in jinja_filters.__all__:
            filter_func = getattr(jinja_filters, module)
            if callable(filter_func):
                self.add_template_filter(filter_func)

def create_app(configfile, env_file:str=None):
    return FunlabFlask(configfile=configfile, env_file=env_file, import_name=__name__, template_folder="")

def start_server(app:Flask):
    config:Config = app.config
    wsgi = config.get('WSGI', 'flask')
    supported_wsgi = ('waitress', 'gunicorn', 'flask')
    if wsgi not in supported_wsgi:
        raise Exception(f'Not supported WSGI. Only {supported_wsgi} is supported.')
    if wsgi == 'waitress':
        try:
            from waitress import serve
            from funlab.flaskr.conf import waitress_conf
        except ImportError as e:
            raise Exception("If use waitress as WSGI server, please install needed packages: pip install waitress") from e
        kwargs = {name: getattr(waitress_conf, name) for name in dir(waitress_conf) if not name.startswith('__')}
        kwargs.pop('multiprocessing', None)  # dummy for import multiprocessing statement
        serve(app, **kwargs)
    elif wsgi == 'gunicorn':
        try:
            # https://stackoverflow.com/questions/70396641/how-to-run-gunicorn-inside-python-not-as-a-command-line
            try:
                from gevent import monkey
                monkey.patch_all() # thread=False, select=False)  # for issue: https://github.com/gevent/gevent/issues/1016
            # import gunicorn
                from gunicorn.app.wsgiapp import WSGIApplication
            except ImportError as e:
                raise Exception("If use gunicorn as WSGI server, please install needed packages: pip install gunicorn gevent") from e
            from funlab.flaskr.conf import gunicorn_conf
        except ImportError as e:
            raise Exception("Use gunicorn as WSGI server, but not found package, please install: pip install gunicorn") from e
        class GunicornApplication(WSGIApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                gunicorn_logger = logging.getLogger('gunicorn.error')
                app.logger.handlers = gunicorn_logger.handlers
                app.logger.setLevel(gunicorn_logger.level)
                super().__init__()

            def load_config(self):
                config = {key: value for key, value in self.options.items()
                        if key in self.cfg.settings and value is not None}
                for key, value in config.items():
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application
        kwargs = {name: getattr(gunicorn_conf, name) for name in dir(gunicorn_conf) if not name.startswith('__')}
        kwargs.pop('multiprocessing', None)  # dummy for import multiprocessing statement
        GunicornApplication(app, kwargs).run()
    else:  # development, use flask embeded server
        import logging
        log_file = './finfun.log'
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)
        app.logger.addHandler(handler)
        app.run(port=config['PORT'], use_reloader=False)

def main(args=None):
    if not args:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Programing by 013 ...")

    parser.add_argument("-c", "--configfile", dest="configfile", help="specify config.toml name and path")
    parser.add_argument("-e", "--envfile", dest="envfile", help="specify .env file name and path")
    # parser.add_argument("-k", "--keyname", dest="keyname", default='', help="specify the keyname and use it to save the key into environment varable.")
    args = parser.parse_args(args)
    configfile=args.configfile
    envfile=args.envfile
    # if envfile:
    #     # env.setup_envvar(envfile)
    #     keyname = vars2env.encode_envfile_vars(envfile)
    start_server(create_app(configfile=configfile, env_file=envfile))

import sys
if __name__ == "__main__":
    args = None
    args= ['-e', '.env', '-c', 'config.toml']
    sys.exit(main(args))
