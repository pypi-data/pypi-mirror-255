from __future__ import annotations

from typing import TYPE_CHECKING

from abc import ABC, abstractmethod
from flask_login import LoginManager
from flask import Blueprint, render_template
from .menu import Menu
from funlab.core.config2 import Config
from funlab.core import _Configuable
from pathlib import Path
import inspect
from flask_login import current_user

if TYPE_CHECKING:  # direct import will cause circle import error, and we just use for parameter type checking
    from funlab.flaskr.app import FunlabFlask

class ViewPlugin(_Configuable, ABC):
    def __init__(self, app:FunlabFlask, url_prefix:str=None):
        """_summary_
        Args:
            app (FunlabFlask): The FunlabFlask app that have this plugin
            url_prefix (str, optional): The blueprint's url_prefix that represet plugin's view.
            Defaults to self.__class__.__name__.removesuffix('View').removesuffix('Security').removesuffix('Service').removesuffix('Plugin').lower().
        """
        self.app:FunlabFlask = app
        self.name = self.__class__.__name__.removesuffix('View').removesuffix('Security').removesuffix('Service').removesuffix('Plugin').lower()  #
        ext_config = self.app.myconfig.get_section_config(section=self.__class__.__name__,
                                                            default=Config({self.__class__.__name__:{}}, env_file_or_values=self.app.env_vars), keep_section=True)
        self.plugin_config = self.get_config(file_name='plugin.toml', ext_config=ext_config)
        self.bp_name = self.name+'_bp'
        self._blueprint=Blueprint(self.bp_name,
                            self.__class__.__module__,
                            static_folder='static',
                            template_folder='templates', # + ('/'+self.name if url_prefix=='' else ''),  # to still use sub-folder
                            url_prefix='/' + (self.name if url_prefix is None else url_prefix)
                    )
        self._mainmenu = Menu(title=self.name, dummy=True)
        self._usermenu = Menu(title=self.name, dummy=True, collapsible=True)  # usermenu added below user icon

    @property
    def blueprint(self):
        return self._blueprint

    @property
    def userhome(self)->Path:
        """Inside static folder for plugin to store/manage user data files."""
        root = Path(inspect.getmodule(self).__file__).parent
        userhome = root.joinpath(f'./{self.blueprint.static_url_path}', current_user.username.lower().replace(' ', ''))
        if not userhome.exists():
            userhome.mkdir(parents=True, exist_ok=True)
        return userhome

    @property
    def login_view(self):
        """ Use to create blueprint_login_views of flask-login for the view if not None"""
        return None

    @property
    def menu(self)->Menu:
        return self._mainmenu

    @property
    def usermenu(self)->Menu:
        return self._usermenu

    @property
    def needDivider(self)-> bool:  # todo use config.toml setting
        """ subclass implement to let app decide if create usermenu with divider or not"""
        return True

    @property
    def entities_registry(self):
        """ FunlabFlask use to table creation by sqlalchemy in __init__ for application initiation """
        return None

    # def register_errorhandler_routes(self):
    #     @self.blueprint.errorhandler(403)
    #     def access_forbidden(error):
    #         return render_template('error-403.html'), 403

    #     @self.blueprint.errorhandler(404)
    #     def not_found_error(error):
    #         return render_template('error-404.html'), 404

    #     @self.blueprint.errorhandler(500)
    #     def internal_error(error):
    #         return render_template('error-500.html'), 500

class SecurityPlugin(ViewPlugin):
    def __init__(self, app:FunlabFlask, url_prefix:str=None):
        super().__init__(app, url_prefix)
        self._login_manager = LoginManager()  # LoginManager(app), not pass app, use init_app in
        self._login_manager.login_view = self.bp_name+".login"
        self._login_manager.login_message = "Please log in to access this page."
        self._login_manager.login_message_category = "warning"
        # self.login_manager.refresh_view = "reauth"
        # self.login_manager.needs_refresh_message = "Session timed out, please re-authenticate."
        self._login_manager.needs_refresh_message_category = "info"

    @property
    def login_manager(self):
        return self._login_manager

class ServicePlugin(ViewPlugin):
    def __init__(self, app:FunlabFlask):
        super().__init__(app)

    @abstractmethod
    def start_service(self):
        pass

    @abstractmethod
    def stop_service(self):
        pass

    def restart_service(self):
        self.stop_service()
        self.start_service()

    @abstractmethod
    def reload_service(self):
        pass
