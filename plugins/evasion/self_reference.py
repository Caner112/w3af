'''
self_reference.py

Copyright 2006 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

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

'''

from core.controllers.plugins.evasion_plugin import EvasionPlugin
from core.controllers.w3afException import w3afException
from core.data.url.HTTPRequest import HTTPRequest as HTTPRequest

# options
from core.data.options.opt_factory import opt_factory
from core.data.options.option_list import OptionList



class self_reference(EvasionPlugin):
    '''
    Add a directory self reference.
    @author: Andres Riancho (andres.riancho@gmail.com)
    '''

    def __init__(self):
        EvasionPlugin.__init__(self)

    def modifyRequest(self, request ):
        '''
        Mangles the request
        
        @param request: HTTPRequest instance that is going to be modified by the evasion plugin
        @return: The modified request

        >>> from core.data.parsers.url import URL
        >>> import re
        >>> sr = self_reference()

        >>> u = URL('http://www.w3af.com/')
        >>> r = HTTPRequest( u )
        >>> sr.modifyRequest( r ).url_object.url_string
        u'http://www.w3af.com/./'

        >>> u = URL('http://www.w3af.com/abc/')
        >>> r = HTTPRequest( u )
        >>> sr.modifyRequest( r ).url_object.url_string
        u'http://www.w3af.com/./abc/./'

        >>> u = URL('http://www.w3af.com/abc/def.htm?id=1')
        >>> r = HTTPRequest( u )
        >>> sr.modifyRequest( r ).url_object.url_string
        u'http://www.w3af.com/./abc/./def.htm?id=1'

        >>> #
        >>> #    The plugins should not modify the original request
        >>> #
        >>> u.url_string
        u'http://www.w3af.com/abc/def.htm?id=1'
        
        '''
        # We mangle the URL
        path = request.url_object.getPath()
        path = path.replace('/','/./' )
        
        # Finally, we set all the mutants to the request in order to return it
        new_url = request.url_object.copy()
        new_url.setPath( path )
        new_req = HTTPRequest( new_url , request.get_data(), 
                               request.headers, request.get_origin_req_host() )
        
        return new_req
    
    def get_options( self ):
        '''
        @return: A list of option objects for this plugin.
        '''    
        ol = OptionList()
        return ol

    def set_options( self, option_list ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of get_options().
        
        @param OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        ''' 
        pass
        
    def get_plugin_deps( self ):
        '''
        @return: A list with the names of the plugins that should be run before the
        current one.
        '''        
        return []

    def getPriority( self ):
        '''
        This function is called when sorting evasion plugins.
        Each evasion plugin should implement this.
        
        @return: An integer specifying the priority. 0 is run first, 100 last.
        '''
        return 0

    def get_long_desc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This evasion plugin adds a directory self reference.
        
        Example:
            Input:      '/bar/foo.asp'
            Output :    '/bar/./foo.asp'
        '''
