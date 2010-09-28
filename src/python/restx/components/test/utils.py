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
Commonly used helper functions when creating tests for Python components.

"""

#
# -------------------------------------------------------------------
# Test helper methods
# -------------------------------------------------------------------
#

#
# Create a new component of the specified class and initialized
# with the provided resource-creation-time-parameters (given
# as a dict).
#
# With 'base_capability_mock', a callable can be specified (taking
# a 'base_capability' object as parameter, which patches up a
# such an object. For example, with custom httpGet methods, or so.
#
from restx.components.base_capabilities import BaseCapabilities

def make_component(resource_creation_params, component_class, base_capability_mock=None):
    c  = component_class()
    bc = BaseCapabilities(c)
    if base_capability_mock:
        base_capability_mock(bc)
    c.setBaseCapabilities(bc)
    for key, value in resource_creation_params.items():
        setattr(c, key, value)
    return c

#
# Overriding the accessResource() API method with a mock method that
# returns the desired data.
#
def make_accessResource(resource_dict):
    def accessResource(name):
        # Creating the fake data for the resource accesses
        return 200, resource_dict[name]
    return accessResource

#
# A helper method that can compare the output with a 'should' output
# Used to compare string results.
#
def compare_out_str(res, should_status, should_str):
    if res.status != should_status:
        return "Status type is not correct.  is == %d, should == %d" % (res.status, should_status)
    is_str = res.entity
    if is_str != should_str:
        return "Wrong output strings:   is  == '%s'  should == '%s'" % (is_str, should_str)

#
# A helper method that can compare the output with a 'should' output
# Used to compare list of result records.
#
def compare_out_lists(res, should_status, should_list):
    if res.status != should_status:
        return "Status type is not correct.  is == %d, should == %d" % (res.status, should_status)
    is_list = res.entity
    # Assumes two lists of dictionaries
    if len(is_list) != len(should_list):
        return "Lists don't have the same length: is == %d, should == %d" % (len(is_list), len(should_list))
    for i, row_is in enumerate(is_list):
        row_should = should_list[i]
        if row_is.keys() != row_should.keys():
            return "Keys in rows don't match:\n    is:     %s\n    should: %s" % (row_is.keys(), row_should.keys())
        for k in row_is.keys():
            if row_is[k] != row_should[k]:
                return "Wrong value field:\n    is[%s]     == '%s'\n    should[%s] == '%s'" % (k, row_is[k], k, row_should[k])
    return None

#
# A helper method that can compare the output with a 'should' output
# Used to compare dictionaries of result records.
#
def compare_out_dicts(res, should_status, should_dict):
    if res.status != should_status:
        return "Status type is not correct.  is == %d, should == %d" % (res.status, should_status)
    is_dict = res.entity
    # Assumes two dictionaries of dictionaries
    if len(is_dict) != len(should_dict):
        return "Dictionaries don't have the same length: is == %d, should == %d" % (len(is_list), len(should_list))
    for k, row_is in is_dict.items():
        row_should = should_dict[k]
        if row_is.keys() != row_should.keys():
            return "Keys in rows don't match:\n    is:     %s\n    should: %s" % (row_is.keys(), row_should.keys())
        for k in row_is.keys():
            if row_is[k] != row_should[k]:
                return "Wrong value field:\n    is[%s]     == '%s'\n    should[%s] == '%s'" % (k, row_is[k], k, row_should[k])
    return None

#
# A helper method to simply compare two iterables.
#
def compare_list(is_list, should_list):
    for i, elem in enumerate(is_list):
        if elem != should_list[i]:
            return "Wrong value field:   is[%d] == '%s'   should[%d] == '%s'" % (elem, should_list[i])
    return None

#
# A helper method for element comparison
#
def compare_elem(is_elem, should_elem):
    if is_elem != should_elem:
        return "Wrong element value:   is == '%s'   should == '%s'" % (is_elem, should_elem)
    return None

_TEST_COUNT  = 0
_TEST_FAILED = 0
def init_test_run():
    global _TEST_COUNT, _TEST_FAILED
    _TEST_COUNT  = 0
    _TEST_FAILED = 0

def get_test_result():
    return ( _TEST_FAILED, _TEST_COUNT )
    
#
# Print error/success output based on test results.
#
def test_evaluator(test_name, out):
    global _TEST_COUNT, _TEST_FAILED
    # Prints test results in a nice manner
    _TEST_COUNT += 1
    if out:
        print "*** %s: Error: %s" % (test_name, out)
        _TEST_FAILED += 1
    else:
        print "--- %s: Success!" % test_name


