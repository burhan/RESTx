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
    DOCUMENTATION    = """<pre>
The RESTx Failover component
============================
With this component it is possible to create a resource that encapsulates
access to a third-party URI, allowing the definition of alternative (or
'failover') URIs in case the first one does not work. Essentially, resources
based on this component act as failover proxies.


   client ------> /resource/Foo/access --------> http://first-choice.com
                                          |
                                          |----> http://second-choice.com
                                          |
                                           ----> http://third-choice.com


Specify up to three URIs which are tried in turn. Each can have a separate
timeout specified. If the first one fails, the second one is tried, and so on.


You can also specify access credentials for basic HTTP authentication. It is
assumed that the same credentials will work on all failover URIs as well.
Basically, all URIs need to provide the same service.


Besides the timeout, this component can also check the HTTP return code
to consider if access to a resource has failed. You specify an 'expected
status'. That way, if you expect 200 but instead get a 404 then this will
also lead to the next URI being tried. If the expected status is set to 0
then all returned status codes are accepted.


The status code and data by the last URI that was tried is returned if
the status code is as expected. However, if the status code is not expected
OR if even the last request is timed out, then we return 408 (request timed
out). This is to simplify error handling in the client, which does not have
to know about the expected status codes defined with the resource: If we
cannot get the data that we expect from any of the URIs then the status code
is always going to be 408.


Currently, GET and POST operations are supported.
</pre>
"""

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


# ============
# Testing
# ============
if __name__ == '__main__':

    #
    # Print error/success output based on test results.
    #
    def test_evaluator(test_name, out):
        # Prints test results in a nice manner
        if out:
            print "*** %s: Error: %s" % (test_name, out)
        else:
            print "--- %s: Success!" % test_name

    def compare_outputs(is_res, should_status, should_entity):
        if is_res.status != should_status:
            return "Status code is not correct. is=%d, should=%d" % (is_res.status, should_status)
        if is_res.entity != should_entity:
            return "Returned data is not correct. is='%s', should='%s'" % (is_res.entity, should_entity)
        return None
            
    #
    # -------------------------------------------------------------------
    # We will mock the httpGet method of the base capabilities, so that
    # we can force our own request responses without having to open
    # an actual HTTP server.
    # -------------------------------------------------------------------
    #
    from org.mulesoft.restx.component.api    import HttpResult, HTTP
    def base_capability_mock(bc):
        def newHttpGet(url, headers=None, timeout=None):
            # Allow client to determine return status with URLs like "..../status/200"
            STATUS_ELEM = "/status/"
            if STATUS_ELEM in url:
                i = url.find(STATUS_ELEM) + len(STATUS_ELEM)
                try:
                    code = int(url[i:url.index("/", i+1)])
                except:
                    code = int(url[i:])
            else:
                code = 200

            RET_ELEM = "/return/"
            if RET_ELEM in url:
                i = url.find(RET_ELEM) + len(RET_ELEM)
                try:
                    ret_str = url[i:url.index("/", i+1)]
                except:
                    ret_str = url[i:]
            else:
                ret_str = "Hello!"

            res = HttpResult()
            res.status = code
            res.data   = ret_str
            return res

        def newHttpPost(url, data=None, headers=None, timeout=None):
            # Just ignoring the data
            return newHttpGet(url, headers, timeout)

        bc.httpGet  = newHttpGet
        bc.httpPost = newHttpPost

    #
    # Create a new component of the specified class and initialized
    # with the provided resource-creation-time-parameters (given
    # as a dict).
    #
    from restx.components.base_capabilities import BaseCapabilities
    def make_component(resource_creation_params, component_class):
        c  = component_class()
        bc = BaseCapabilities(c)
        base_capability_mock(bc)
        c.setBaseCapabilities(bc)
        for key, value in resource_creation_params.items():
            setattr(c, key, value)
        return c

    #
    # -------------------------------------------------------------------
    # The actual tests
    # -------------------------------------------------------------------
    #

    print "\n--- Executing tests for the Failover component ---\n"

    #
    # Test 1: No failover and expected return value
    #
    rctp = dict(
        site_1_uri       = "http://localhost:8091/status/200/return/foo",
        site_1_timeout   = 10,
        site_2_uri       = "",
        site_2_timeout   = 10,
        site_3_uri       = "",
        site_3_timeout   = 10,
        account_name     = "",
        account_password = "",
        expected_status  = 200,
    )
    c   = make_component(rctp, Failover)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 1", compare_outputs(res, 200, "foo"))

    #
    # Test 2: No failover and un-expected return value
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/201/return/foo"
    c   = make_component(rctp, Failover)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 2", compare_outputs(res, HTTP.REQUEST_TIMEOUT, "foo"))

    #
    # Test 3: Failover because of unexpected return code
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/201/return/foo"
    rctp['site_2_uri'] = "http://localhost:8091/status/200/return/bar"
    c   = make_component(rctp, Failover)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 3", compare_outputs(res, 200, "bar"))

    #
    # Test 4: Failover because of timeout return code
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/200/return/bar"
    c   = make_component(rctp, Failover)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 4", compare_outputs(res, 200, "bar"))

    #
    # Test 5: Failover and error even on last URI
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/201/return/bar"
    c   = make_component(rctp, Failover)
    res = c.access(HttpMethod.GET, None)
    test_evaluator("Test 5", compare_outputs(res, HTTP.REQUEST_TIMEOUT, "bar"))

    #
    # Test 6: Failover and error even on last URI, this time with POST
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/201/return/bar"
    c   = make_component(rctp, Failover)
    res = c.access(HttpMethod.POST, None)
    test_evaluator("Test 6", compare_outputs(res, HTTP.REQUEST_TIMEOUT, "bar"))

    #
    # Test 6: Failover and expected return on last URI, this time with POST
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/200/return/bar"
    c   = make_component(rctp, Failover)
    res = c.access(HttpMethod.POST, None)
    test_evaluator("Test 7", compare_outputs(res, 200, "bar"))

    #
    # Test 7: Failover and expected return on last URI, but with method that's not allowed
    #
    rctp['site_1_uri'] = "http://localhost:8091/status/%d/return/foo" % HTTP.REQUEST_TIMEOUT
    rctp['site_2_uri'] = "http://localhost:8091/status/200/return/bar"
    c   = make_component(rctp, Failover)
    res = c.access(HttpMethod.PUT, None)
    test_evaluator("Test 8", compare_outputs(res, HTTP.METHOD_NOT_ALLOWED, "Only supporting GET or POST for this resource"))


    print


