"""
RESTx: Sane, simple and effective data publishing and integration. 

Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by 
the Free Software Foundation, either version 3 of the License, or 
(at your option) any later version. 

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details. 

You should have received a copy of the GNU General Public License 
along with this program.  If not, see <http://www.gnu.org/licenses/>. 

"""

"""
This module provides renderers for data into
different output formats.

You can import these classes straight from module level:

    * BaseRenderer

"""
# Export classes on module level, so that users don't need
# to specify the individual file names in their imports.
from restx.render.htmlrenderer     import HtmlRenderer
from restx.render.jsonrenderer     import JsonRenderer
from restx.render.wwwformrenderer  import WwwFormRenderer
from restx.render.textrenderer     import TextRenderer

# Add new renderers here...
KNOWN_RENDERERS = {
    ""                                   : HtmlRenderer,
    "*/*"                                : HtmlRenderer,
    "text/html"                          : HtmlRenderer,
    "text/plain"                         : TextRenderer,
    "application/json"                   : JsonRenderer,
    "application/x-www-form-urlencoded"  : WwwFormRenderer,
}

DEFAULT_OUTPUT_TYPES          = [ "application/json", "text/html", "*/*" ]
DEFAULT_INPUT_TYPES           = [ "application/json", "application/x-www-form-urlencoded" ]

KNOWN_INPUT_RENDERERS  = dict( [ (type_str, KNOWN_RENDERERS[type_str]) for type_str in KNOWN_RENDERERS.keys() if KNOWN_RENDERERS[type_str]().canParse() ] )
KNOWN_OUTPUT_RENDERERS = dict( [ (type_str, KNOWN_RENDERERS[type_str]) for type_str in KNOWN_RENDERERS.keys() if KNOWN_RENDERERS[type_str]().canRender() ] )


