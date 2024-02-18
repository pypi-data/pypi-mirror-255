from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Setting
from django.conf import settings

import os
import tomllib


class SWElement:
    """A Sitewide element of a Header, Sidebar, or Footer"""

    def __init__(self, **kwargs):
        """initialize"""

        self.__se = {
            "allow": ["is_staff"],
            "show": True,  # show element by default
        }
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def allow(self):
        """return an allow list element"""

        return self.__se.get("allow")

    @allow.setter
    def allow(self, value):
        """set a textual element"""

        if isinstance(value, str) and value not in self.__se.get("allow"):
            self.__se["allow"].append(value)

    @property
    def icon(self):
        """return a icon element"""

        return self.__se.get("icon")

    @icon.setter
    def icon(self, code):
        """set a textual element"""

        if isinstance(code, str):
            self.__se["icon"] = code

    @property
    def name(self):
        """return a name element"""

        return self.__se.get("name")

    @name.setter
    def name(self, value):
        """set a name element"""

        if isinstance(value, str):
            self.__se["name"] = value

    @property
    def text(self):
        """return a textual element"""

        return self.__se.get("text")

    @text.setter
    def text(self, value):
        """set a textual element"""

        if isinstance(value, str):
            self.__se["text"] = value

    @property
    def show(self):
        """return visibility state of this element"""

        return self.__se.get("show")

    @show.setter
    def show(self, value):
        """set the visibility state of this element"""

        if isinstance(value, bool):
            self.__se["show"] = value

    @property
    def url(self):
        """return a url element"""

        return self.__se.get("url")

    @url.setter
    def url(self, value):
        """set a name element"""

        if isinstance(value, str):
            self.__se["url"] = value


class SWMenuItem(SWElement):
    """A Sitewide Menu Item"""

    def __init__(self, **kwargs):
        """Initialize"""

        start_index = kwargs.pop
        super().__init__(**kwargs)
        submenu = kwargs.get("menu") if "menu" in kwargs else []
        self.__subitems = []

        if isinstance(submenu, list):
            for item in submenu:
                self.__subitems.append(SWElement(**item))
        else:
            raise TypeError(f"Expected a Menu List. Got {type(menulist)}")

    def items(self):
        """return the menu items"""

        return self.__subitems

    def index(self):
        """Return the Tab Index for this Menu Item"""


class Header(SWElement):
    """Sitewide Header"""

    def __init__(self, sitewide, **kwargs):
        """Initialize"""

        self.__header = {
            "menu": [],
        }
        if isinstance(sitewide, Sitewide):
            self.__header.setdefault("sitewide", sitewide)
        else:
            raise TypeError(f"Expected Sitewide Object. Got {type(sitewide)}")
        super().__init__(**kwargs)
        if "menu" in kwargs:
            self.menu = kwargs.get("menu")

    @property
    def menu(self):
        """Return menu"""

        return self.__header.get("menu")

    @menu.setter
    def menu(self, menulist):
        """Set menu"""

        if isinstance(menulist, list):
            for menuitem in menulist:
                item = SWMenuItem(**menuitem)
                self.__header["menu"].append(item)


class Footer:
    """Sitewide Footer"""

    def __init__(self, sitewide, **kwargs):
        """Initialize"""

        self.__footer = {}
        if isinstance(sitewide, Sitewide):
            self.__footer.setdefault("sitewide", sitewide)
        else:
            raise TypeError(f"Expected Sitewide Object. Got {type(sitewide)}")
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Sidebar(SWElement):
    """Manage Sidebar data"""

    def __init__(self, sitewide, **kwargs):
        """Initialize"""

        super().__init__(**kwargs)
        menu = kwargs.get("menu") if "menu" in kwargs else []
        self.__bar = {
            "menu": [],
            "cindex": 3,  # Always start indexing at 3 (offset from Avatar etc.)
        }
        if isinstance(sitewide, Sitewide):
            self.__bar.setdefault("sitewide", sitewide)
        else:
            raise TypeError(f"Expected Sitewide Object. Got {type(sitewide)}")
        if menu:
            self.menu = menu

    @property
    def avatar(self):
        """Link to the avatar"""

        host = self.__bar.get("sitewide")
        return (
            host.user.avatar
            if hasattr(host.user, "avatar")
            else "/static/imgs/avatar.png"
        )

    @property
    def menu(self):
        """Return menu"""

        return self.__bar.get("menu")

    @menu.setter
    def menu(self, menulist):
        """Set menu"""

        if isinstance(menulist, list):
            for menuitem in menulist:
                item = SWMenuItem(
                    start_index=self.__bar.get("cindex"), **menuitem
                )
                self.__bar["menu"].append(item)


class Sitewide:
    """Manage information that shows across most pages in a Django website"""

    def __init__(self, **kwargs):
        """Initialize"""

        cfg = {}
        configfile = (
            "production.toml"
            if self.__exists__("production.toml")
            else "sitewide.toml"
        )
        with open(configfile, "rb") as file:
            cfg = tomllib.load(file)
        self.__sitewide = {"setting_class": Setting}
        for src in [kwargs, cfg]:
            for attr in src:
                if hasattr(self, attr):
                    setattr(self, attr, src.get(attr))
        if not self.home:
            self.__sitewide["home"] = "/"

    def __exists__(self, path):
        """confirm that path exists relative to django"""

        exists = False
        if isinstance(path, str):
            abspath = os.path.join(settings.BASE_DIR, path.lstrip(os.path.sep))
            exists = os.path.exists(abspath)
        return exists

    @property
    def favicon(self):
        """Return sitebar object"""

        return self.__sitewide.get("favicon")

    @favicon.setter
    def favicon(self, path):
        """Set the path to the favicon"""

        self.__sitewide["favicon"] = path if self.__exists__(path) else None

    @property
    def footer(self):
        """Return footer object"""

        return self.__sitewide.get("footer")

    @footer.setter
    def footer(self, kwargs):
        """Set the contents of sitewide footers"""

        footer = Footer(self, **kwargs)
        self.__sitewide["footer"] = footer

    @property
    def header(self):
        """Return header object"""

        return self.__sitewide.get("header")

    @header.setter
    def header(self, kwargs):
        """Set header object"""

        if isinstance(kwargs, bool) and self.header is not None:
            self.header.show = kwargs
        elif isinstance(kwargs, dict):
            header = Header(self, **kwargs)
            self.__sitewide["header"] = header

    @property
    def home(self):
        """Return the home path"""

        return self.__sitewide.get("home")

    @home.setter
    def home(self, path):
        """Set the home path"""

        self.__sitewide["home"] = path if self.__exists__(path) else "/"

    @property
    def logo(self):
        """Return sitewide logo"""

        return self.__sitewide.get("logo")

    @logo.setter
    def logo(self, path):
        """Set the path to the logo"""

        self.__sitewide["logo"] = path if self.__exists__(path) else None

    @property
    def settings(self):
        """Return a queryset of settings"""

        return self.settings_class.objects.all()

    @property
    def settings_class(self):
        """Return the Settings Model Class"""

        return self.__sitewide.get("setting_class")

    @property
    def sidebar(self):
        """Return sitebar object"""

        return self.__sitewide.get("sidebar")

    @sidebar.setter
    def sidebar(self, kwargs):
        """Set the sitebar object"""

        sidebar = Sidebar(self, **kwargs)
        self.__sitewide["sidebar"] = sidebar

    @property
    def sitename(self):
        """Return the name of the project"""

        return self.__sitewide.get("sitename")

    @sitename.setter
    def sitename(self, name):
        """Set the project name"""

        if isinstance(name, str):
            self.__sitewide["sitename"] = name

    @property
    def user(self):
        """Return request user"""

        return self.__sitewide.get("user")

    @user.setter
    def user(self, user):
        """Set the request user object"""

        if hasattr(user, "username"):
            self.__sitewide["user"] = user


# Create your views here.
class HomeView(TemplateView):
    template_name = "home.html"
    extra_context = {"pagetitle": "Home"}

    def get(self, request, *args, **kwargs):
        """Prepare to render view"""

        # Set sitewide request.user
        sitewide = Sitewide(user=self.request.user)
        self.extra_context["sitewide"] = sitewide
        return super().get(request, *args, **kwargs)
