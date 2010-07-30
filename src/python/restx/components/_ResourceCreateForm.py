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
A sample template for RESTx components, written in Python.

"""
import urllib

import restx.components
import restx.settings as settings

from   restx.resources              import makeResourceFromClass
from   restx.platform_specifics     import STORAGE_OBJECT
from   restx.components.api         import *
from   org.mulesoft.restx.exception import *

class _ResourceCreateForm(BaseComponent):
    # Name, description and doc string of the component as it should appear to the user.
    NAME             = "_ResourceCreateForm"    # Names starting with a '_' are kept private
    DESCRIPTION      = "Allows creation of a new resource by displaying a resource creation form"
    DOCUMENTATION    = \
"""The resource gets the name of a component as parameter at run time.
It then reads information about the component and constructs a proper
HTML form suitable for resource creation.

The user submits the filled-out form and a new resource is created.
"""

    PARAM_DEFINITION = {}
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           "form" : {
                               "desc" : "Show the resource creation form",
                               "params" : {
                                   "component_name" : ParameterDef(PARAM_STRING, "Name of the component", required=True),
                                   "message"        : ParameterDef(PARAM_STRING, "An error message", required=False, default=""),
                                   "specialized"    : ParameterDef(PARAM_BOOL,   "Indicates if this is based on a specialized component", required=False, default=False),
                               },
                               "positional_params": [ "component_name" ]
                            },
                            "create" : {
                               "desc" : "Accepts a posted resource creation form",
                               "params" : {
                                   "component_name" : ParameterDef(PARAM_STRING, "Name of the component", required=True),
                                   "specialized"    : ParameterDef(PARAM_BOOL,   "Indicates if this is based on a specialized component", required=False, default=False),
                               },
                               "positional_params": [ "component_name" ]
                           }
                       }
    
    def error_return(self, component_name, message, specialized=False):
        """
        Sends client back to form page with error message.

        """
        return Result.temporaryRedirect("%s%s/form/%s?message=%s%s" % (settings.DOCUMENT_ROOT, self.getMyResourceUri(),
                                                                       component_name, message, "&specialized=y" if specialized else ""))

    def create(self, method, input, component_name, specialized=False):
        """
        Accept a resource creation form for a specified component.

        """
        if not input:
            return self.error_return(component_name, "Need form input!", specialized)

        d = dict()
        for name, value in input.items():
            path_elems = name.split("__")
            d2 = d
            for i, pe in enumerate(path_elems):
                if i < len(path_elems)-1:
                    # More elements to come later? We must create a dict
                    d2 = d2.setdefault(pe, dict())
                else:
                    if value:
                        d2[pe] = value

        try:
            ret_msg = makeResource(component_name, d, specialized)
        except RestxException, e:
            return self.error_return(component_name, e.msg, specialized)
        
        return Result.ok(ret_msg)

    def form(self, method, input, component_name, message="", specialized=False):
        """
        Display a resource creation form for a specified component.
        
        @param method:          The HTTP request method.
        @type method:           string
        
        @param input:           Any data that came in the body of the request.
        @type input:            string

        @param component_name:  Name of the component for which to create the resource.
        @type component_name:   string

        @param message:         An error message to be displayed above the form.
        @type message:          string

        @return:                The output data of this service.
        @rtype:                 Result

        """
        if specialized:
            # Need to read the definition of the partial resource and get the
            # component name from there.
            specialized_code_name = component_name
            specialized_def       = STORAGE_OBJECT.loadResourceFromStorage(specialized_code_name, True)
            component_uri         = specialized_def['private']['code_uri']
            elems                 = component_uri.split("/")
            component_name        = elems[len(elems)-1]

        # Take the parameter map from the component
        cc = restx.components.get_code_map().get(component_name)
        if not cc:
            return Result.notFound("Cannot find component '%s'" % component_name)
        header = settings.HTML_HEADER

        # Assemble the form elements for the parameters
        params = dict()
        comp = cc()
        params.update(comp.getParams())  # In case this is a Java component, we get a Python dict this way

        if specialized:
            fname = specialized_def['public']['name']
            fdesc = specialized_def['public']['desc']
            # Remove all parameters that have been specified in the specialized component resource
            # definition already
            spec_params = specialized_def['private'].get('params')
            if spec_params:
                for name in spec_params:
                    if name in params:
                        del params[name]
        else:
            fname = comp.getName()
            fdesc = comp.getDesc()

        param_fields_html = ""
        if params:
            param_field_names = params.keys()
            param_field_names.sort()
            for pname in param_field_names:
                pdef = params[pname]
                if not pdef.required:
                    opt_str = "<br>optional, default: %s" % pdef.getDefaultVal()
                else:
                    opt_str = ""
                param_fields_html += \
"""<tr>
    <td valign=top>%s<br><small>(%s%s)</small></td>
    <td valign=top>%s</td>
</tr>""" % (pname, pdef.desc, opt_str, pdef.html_type("params__"+pname))

        if message:
            msg = "<b><i><font color=red>%s</font></i></b><br><p>" % message
        else:
            msg = ""

        body = """
<h3>Resource creation form for: %s</h3>
<p><i>"%s"</i></p>

<hr>
Please enter the resource configuration...<br><p>
%s
<form name="input" action="%s" method="POST">
    <table>""" % (fname, fdesc, msg, "%s%s/create/%s%s" % (settings.DOCUMENT_ROOT, self.getMyResourceUri(),
                                                           component_name if not specialized else specialized_code_name, "?specialized=y" if specialized else ""))
        if not specialized:
            body += """
        <tr>
            <td>Make this a specialized component:</td>
            <td><input type="checkbox" id=resource_creation_params__specialized name="resource_creation_params__specialized" /><label for=resource_creation_params__specialized><small>Can only be used as basis for other resources</small></label></td>
        </tr>
            """
        body += """
        <tr>
            <td>Resource name:</td>
            <td><input type="text" name="resource_creation_params__suggested_name" /></td>
        </tr>
        <tr>
            <td>Description:<br><small>(optional)</small></td>
            <td><input type="text" name="resource_creation_params__desc" /></td>
        </tr>
        %s
        <tr><td colspan=2 align=center><input type="submit" value="Submit" /></tr></tr>
    </table>
</form>""" % (param_fields_html)

        footer = settings.HTML_FOOTER

        res = Result.ok(header + body + footer)
        res.addHeader("Content-type", "text/html; charset=UTF-8")

        return res

