"""
generic.py

Copyright 2011 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
from urllib import urlencode

import w3af.core.controllers.output_manager as om

from w3af.core.data.options.opt_factory import opt_factory
from w3af.core.data.options.option_list import OptionList
from w3af.core.controllers.plugins.auth_plugin import AuthPlugin
from w3af.core.controllers.exceptions import BaseFrameworkException


class generic(AuthPlugin):
    """Generic authentication plugin."""

    def __init__(self):
        AuthPlugin.__init__(self)

        self.username = ''
        self.password = ''
        self.username_field = ''
        self.password_field = ''
        self.auth_url = 'http://host.tld/'
        self.check_url = 'http://host.tld/'
        self.check_string = ''
        self._login_error = True

    def login(self):
        """
        Login to the application.
        """
        try:
            return self.do_user_login()
        except BaseFrameworkException, e:
            if self._login_error:
                om.out.error(str(e))
                self._login_error = False
            return False

    def do_user_login(self):
        """
        Send the request to login the user.
        :return: True if the login was successful otherwise raise a
                 BaseFrameworkException
        """
        msg = 'Logging into the application using %s/%s' % (self.username,
                                                            self.password)
        om.out.debug(msg)

        data = urlencode({self.username_field: self.username,
                          self.password_field: self.password})

        # TODO Why we don't use FuzzableRequest+send_mutant here?
        self._uri_opener.POST(self.auth_url, data=data)

        if not self.is_logged():
            msg = "Can't login into web application as %s/%s"
            raise BaseFrameworkException(msg % (self.username, self.password))
        else:
            om.out.debug('Login success for %s/%s' % (self.username,
                                                      self.password))
            return True

    def logout(self):
        """User login."""
        return None

    def is_logged(self):
        """
        Check user session.
        """
        try:
            http_response = self._uri_opener.GET(self.check_url, grep=False,
                                                 cache=False)
            body = http_response.get_body()
            logged_in = self.check_string in body

            msg_yes = 'User "%s" is currently logged into the application'
            msg_no = 'User "%s" is NOT logged into the application'
            msg = msg_yes if logged_in else msg_no
            om.out.debug(msg % self.username)

            return logged_in
        except Exception:
            return False

    def get_options(self):
        """
        :return: A list of option objects for this plugin.
        """
        options = [
            ('username', self.username, 'string',
             'Username for using in the authentication process'),

            ('password', self.password, 'string',
             'Password for using in the authentication process'),

            ('username_field', self.username_field,
             'string', 'Username parameter name (ie. "uname" if the HTML looks'
                       ' like <input type="text" name="uname">...)'),

            ('password_field', self.password_field,
             'string', 'Password parameter name (ie. "pwd" if the HTML looks'
                       ' like <input type="password" name="pwd">...)'),

            ('auth_url', self.auth_url, 'url',
             'URL where the username and password will be sent using a POST'
             ' request'),

            ('check_url', self.check_url, 'url',
             'URL used to verify if the session is still active by looking for'
             ' the check_string.'),

            ('check_string', self.check_string, 'string',
             'String for searching on check_url page to determine if the'
             'current session is active.'),
        ]

        ol = OptionList()
        for o in options:
            ol.add(opt_factory(o[0], o[1], o[3], o[2], help=o[3]))

        return ol

    def set_options(self, options_list):
        """
        This method sets all the options that are configured using
        the user interface generated by the framework using
        the result of get_options().

        :param options_list: A dict with the options for the plugin.
        :return: No value is returned.
        """
        self.username = options_list['username'].get_value()
        self.password = options_list['password'].get_value()
        self.username_field = options_list['username_field'].get_value()
        self.password_field = options_list['password_field'].get_value()
        self.check_string = options_list['check_string'].get_value()
        self.auth_url = options_list['auth_url'].get_value()
        self.check_url = options_list['check_url'].get_value()

        missing_options = []

        for o in options_list:
            if not o.get_value():
                missing_options.append(o.get_name())

        if missing_options:
            msg = ("All parameters are required and can't be empty. The"
                   " missing parameters are %s")
            raise BaseFrameworkException(msg % ', '.join(missing_options))

    def get_long_desc(self):
        """
        :return: A DETAILED description of the plugin functions and features.
        """
        return """
        This authentication plugin can login to Web applications which use
        common authentication schemes.

        Seven configurable parameters exist:
            - username
            - password
            - username_field
            - password_field
            - auth_url
            - check_url
            - check_string
        """
