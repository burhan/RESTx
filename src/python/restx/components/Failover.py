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
A failover component. Requests data from up to three specified URIs.
If the first request is successful it will complete. If not it will
try the second URI and so on.

For each URI a separate timeout can be specified.

"""
from restx.components.api import *

class Failover(BaseComponent):
    NAME             = "Failover"
    DESCRIPTION      = "Requests data from a URI and/or two backup URIs."
    DOCUMENTATION    = "Specify up to three URIs which are tried in turn. Each can have a separate timeout specified. If the first one fails, the second one is tried, and so on."

    PARAM_DEFINITION = {
                           "site_1_uri" :         ParameterDef(PARAM_STRING, "The first URI to try", required=True),
                           "site_1_timeout" :     ParameterDef(PARAM_NUMBER, "Timeout for the first URI (-1 means: no timeout)", required=False, default=10),
                           "site_2_uri" :         ParameterDef(PARAM_STRING, "The first URI to try", required=False, default=""),
                           "site_2_timeout" :     ParameterDef(PARAM_NUMBER, "Timeout for the first URI (-1 means: no timeout)", required=False, default=10),
                           "site_3_uri" :         ParameterDef(PARAM_STRING, "The first URI to try", required=False, default=""),
                           "site_3_timeout" :     ParameterDef(PARAM_NUMBER, "Timeout for the first URI (-1 means: no timeout)", required=False, default=10),
                           "account_name" :       ParameterDef(PARAM_STRING, "Account name", required=False, default=""),
                           "account_password" :   ParameterDef(PARAM_STRING, "Account pasasword", required=False, default=""),
                           "expected_status" :    ParameterDef(PARAM_NUMBER, "Expected status code. If not received then this is treated like a timeout: We move on to the next URI. If no more URIs are available, we return this status code. (0 means: No particular status, anything that's not a timeout will be returned)", required=False, default=0),
                       }
    
    SERVICES         = {
                           "access" : {
                               "desc" : "Sends requests (GET or POST) to the specified URI(s).",
                           }
                       }
        

    def access(self, method, input):
        if method not in [ HttpMethod.GET, HttpMethod.POST ]:
            return Result(HTTP.METHOD_NOT_ALLOWED, "Only supporting GET or POST for this resource")

        if input:
            if type(input) not in [ str, unicode ]:
                # Convert back to string if this was an object
                input = self.toJson(input)

        if self.account_name  and  self.account_password:
            self.httpSetCredentials(self.account_name, self.account_password)

        try_targets = [ (self.site_1_uri, self.site_1_timeout), (self.site_2_uri, self.site_2_timeout), (self.site_3_uri, self.site_3_timeout) ]
        data = ""
        for uri, timeout in try_targets:
            if uri:
                if timeout < 0:
                    timeout = None

                if method == HttpMethod.POST:
                    code, data = self.httpPost(uri, input, timeout=timeout)
                elif method == HttpMethod.GET:
                    code, data = self.httpGet(uri, timeout=timeout)

                if self.expected_status > 0:
                    if self.expected_status == code:
                        # We got exactly what we were looking for
                        return Result(code, data)
                    else:
                        # Not the result we are looking for yet
                        continue
                else:
                    # No expected status, so anything that's not a timeout is good
                    if code != HTTP.REQUEST_TIMEOUT:
                        return Result(code, data)
            
        return Result(HTTP.REQUEST_TIMEOUT, data)

