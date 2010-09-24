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
The Join component assumes two inputs. Each input needs to be
formatted as an array of dictionaries. Each dictionary within one
input has to be of the same format.

The join is performed based on a key field in each input. The key
fields in each input can have different names.

"""

from restx.components.api import *

class Join(BaseComponent):

    NAME             = "Join"
    DESCRIPTION      = "Capable of joining lists of dictionaries."
    DOCUMENTATION    = """<pre>
The RESTx Join component
========================
Given two resources (identified by their relative URI), this component conducts a join.


          Resource A          Resource B
          ----------          ----------
                \                /  
                 \              /
                  \            /
                   \          /
                    V        V
                New joined resource
                -------------------


Each resource is expected to produce an array of dictionaries, where each dictionary
represents a row. The key fields of each row produced by a resource are expected to
stay the same, thus representing a table.


The join is conducted on a 'key field' that can be specified individually for each
of the two source resources.


Example:


    Output from resource A:


        [
            { "email" : "a@b.c", "foo" : "A_foo_a" },
            { "email" : "b@b.c", "foo" : "A_foo_b" },
            { "email" : "c@b.c", "foo" : "A_foo_c" },
            { "email" : "d@b.c", "foo" : "A_foo_d" }
        ]


    Output from resource B:


        [
            { "Email_Address" : "x@b.c", "foo" : "B_foo_x", "bar" : "bar_x" },
            { "Email_Address" : "b@b.c", "foo" : "B_foo_b", "bar" : "bar_b" },
            { "Email_Address" : "c@b.c", "foo" : "B_foo_c", "bar" : "bar_c" }
        ]


Note that each 'record' in a resource's output contains the same fields.
The field names for resource A are [ 'email', 'foo' ] while the field
names for resource B are [ 'Email_Address', 'foo', 'bar' ].


The parameters used by the Join component are as follows:


    'resource_A_uri' :    The URI of resource A
    'resource_B_uri' :    The URI of resource B
    'keyfield_A' :        The key-field on which to perform the join for record A
    'keyfield_B' :        The key-field on which to perform the join for record B
    'prefix_name_A' :     An optional prefix for fields from A
    'prefix_name_B' :     An optional prefix for fields from B
    'new_keyfield_name' : A new name for the keyfield, if defined.
    'always_use_prefix' : Prefixes are normally only used to resolve name conflicts.


If we define the key fields in A and B to be 'email' and 'Email_Address' respectively
then the output of the join is:


    [
        { "email" : "b@b.c", "A.foo" : "A_foo_b", "B.foo" : "B_foo_b", "bar" : "bar_b" },
        { "email" : "c@b.c", "A.foo" : "A_foo_c", "B.foo" : "B_foo_c", "bar" : "bar_c" }
    ]


Note that the field "foo" needed the prefixes in order to resolve the name collision,
while the field "bar" does not, since it only appears in one of the sources.


If 'always_use_prefix' is set then the output is:


    [
        { "A.email" : "b@b.c", "A.foo" : "A_foo_b", "B.foo" : "B_foo_b", "B.bar" : "bar_b" },
        { "A.email" : "c@b.c", "A.foo" : "A_foo_c", "B.foo" : "B_foo_c", "B.bar" : "bar_c" }
    ]


If 'new_keyfield_name' is set to "Address" and 'always_use_prefix' is set then the output is:


    [
        { "Address" : "b@b.c", "A.foo" : "A_foo_b", "B.foo" : "B_foo_b", "B.bar" : "bar_b" },
        { "Address" : "c@b.c", "A.foo" : "A_foo_c", "B.foo" : "B_foo_c", "B.bar" : "bar_c" }
    ]


If prefix names are not defined then in case of name collision, "A" and "B" will be used
as default prefixes.
</pre>
"""

    PARAM_DEFINITION = {
                           "resource_A_uri" :    ParameterDef(PARAM_STRING, "URI of a first resource", required=True),
                           "resource_B_uri" :    ParameterDef(PARAM_STRING, "URI of a second resource", required=True),
                           "keyfield_A" :        ParameterDef(PARAM_STRING, "Name of key field of resource A", required=True),
                           "keyfield_B" :        ParameterDef(PARAM_STRING, "Name of key field of resource B", required=True),
                           "prefix_name_A" :     ParameterDef(PARAM_STRING, "Prefix used for fields from resource A", required=False, default="A"),
                           "prefix_name_B" :     ParameterDef(PARAM_STRING, "Prefix used for fields from resource B", required=False, default="B"),
                           "new_keyfield_name" : ParameterDef(PARAM_STRING, "New name for the keyfield. If not define, use shortest name.", required=False, default=""),
                           "always_use_prefix" : ParameterDef(PARAM_BOOL,   "Always prefix field names with resource names?", required=False, default=True),
                       }
    
    SERVICES         = {
                           "join" : {
                               "desc" : "Get the join result",
                               "output_types" : [ "application/json", "text/html" ],
                                "params"     : {
                                    "op"     : ParameterDef(PARAM_STRING, "The operation, such as 'select'", required=False, default=""),
                                },
                               
                           }
                       }

    def __make_keyfield_name(self):
        #
        # The new name of the keyfield
        #
        # If no new_keyfield_name was specified, it takes the shorter name of the keyfield from the two data sources.
        #
        if self.new_keyfield_name:
            new_keyfield_name = self.new_keyfield_name
        else:
            keyfield_name_A = self.prefix_name_A + "." + self.keyfield_A if self.always_use_prefix else self.keyfield_A
            keyfield_name_B = self.prefix_name_B + "." + self.keyfield_B if self.always_use_prefix else self.keyfield_B
            
            new_keyfield_name = keyfield_name_A if len(keyfield_name_A) <= len(keyfield_name_B) else keyfield_name_B

        return new_keyfield_name

    def __make_field_translation_tables(self, new_keyfield_name, rec_A, rec_B):
        #
        # Pre-prepare the keyfield tables, which allow us to quickly join the records.
        #
        if self.always_use_prefix:
            # Create lookup tables if we always want the prefix. Keyfield is excluded since that is
            # provid by other means.
            table_A = dict( [ (k, self.prefix_name_A + "." + k) for k in rec_A.keys() if k != self.keyfield_A ] )
            table_B = dict( [ (k, self.prefix_name_B + "." + k) for k in rec_B.keys() if k != self.keyfield_B ] )
        else:
            # Ok, so we need to make key fields unique, using the prefixes, but only if there is a conflict.
            table_A = dict()
            table_B = dict()
            names_in_B = list()
            for k in rec_A.keys():
                if k != self.keyfield_A:
                    if k in rec_B:
                        table_A[k] = self.prefix_name_A + "." + k
                        table_B[k] = self.prefix_name_B + "." + k
                        names_in_B.append(k)
                    else:
                        table_A[k] = k
            # A is done, so now we need to complete B
            for k in rec_B.keys():
                if k not in names_in_B  and  k != self.keyfield_B:
                    table_B[k] = k

        return (table_A, table_B)
            
    def __join_two_records(self, rec_A, rec_B, new_keyfield_name, keyfield_val):
        """
        Create a new record out of two given records. We know that
        they match in their key fields, since otherwise we would not
        have been called here.

        We now need to deal with prefixes and similarly named fields
        and such.

        """
        if not self.translation_tables:
            # Cache the output of this, so we don't have to do this for every record
            self.translation_tables = self.__make_field_translation_tables(new_keyfield_name, rec_A, rec_B)

        table_A, table_B = self.translation_tables

        d = dict()
        d[new_keyfield_name] = keyfield_val
        d.update([ (table_A[k], rec_A[k]) for k in table_A.keys() ])
        d.update([ (table_B[k], rec_B[k]) for k in table_B.keys() ])

        return d

    def join(self, method, input):
        # Some processing ahead of time
        new_keyfield_name = self.__make_keyfield_name()
        self.translation_tables = None

        # Get the data from the two join resources
        status, data_A = accessResource(self.resource_A_uri)
        if status != 200:
            raise RestxException("Could not get data from resource A")
        status, data_B = accessResource(self.resource_B_uri)
        if status != 200:
            raise RestxException("Could not get data from resource B")

        # Index the data from each table by the key field
        data_A_dict = dict([ (e[self.keyfield_A], e) for e in data_A ])
        data_B_dict = dict([ (e[self.keyfield_B], e) for e in data_B ])

        # Create the join
        out = list()
        for keyval, data_A_record in data_A_dict.items():
            data_B_record = data_B_dict.get(keyval)
            if data_B_record:
                out.append(self.__join_two_records(data_A_record, data_B_record, new_keyfield_name, keyval))

        return Result.ok(out)


# ============
# Testing
# ============
if __name__ == '__main__':

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
    def make_component(resource_creation_params, component_class):
        c = component_class()
        for key, value in resource_creation_params.items():
            setattr(c, key, value)
        return c

    #
    # Overriding the accessResource() API method with a mock method that
    # returns the desired data.
    #
    RESOURCE_DICT = dict()
    def accessResource(name):
        # Creating the fake data for the resource accesses
        return 200, RESOURCE_DICT[name]

    #
    # A helper method that can compare the output with a 'should' output
    #
    def compare_outputs(is_list, should_list):
        # Assumes two lists of dictionaries
        if len(is_list) != len(should_list):
            return "Lists don't have the same length: is=%d, should=%d" % (len(is_list), len(should_list))
        for i, row_is in enumerate(is_list):
            row_should = should_list[i]
            if row_is.keys() != row_should.keys():
                return "Keys in rows don't match:\n    is:     %s\n    should: %s" % (row_is.keys(), row_should.keys())
            for k in row_is.keys():
                if row_is[k] != row_should[k]:
                    return "Wrong value field:\n    is[%s]     == '%s'\n    should[%s] == '%s'" % (k, row_is[k], k, row_should[k])
        return None

    #
    # Print error/success output based on test results.
    #
    def test_evaluator(test_name, out):
        # Prints test results in a nice manner
        if out:
            print "*** %s: Error: %s" % (test_name, out)
        else:
            print "--- %s: Success!" % test_name
            
    #
    # -------------------------------------------------------------------
    # The actual tests
    # -------------------------------------------------------------------
    #

    print "\n--- Executing tests for the Join component ---\n"

    #
    # Test 1: Always prefix, two matches
    #
    rctp = dict(
        keyfield_A         = "email",
        keyfield_B         = "Email",
        prefix_name_A      = "A",
        prefix_name_B      = "B",
        new_keyfield_name  = "BlahBlah",
        always_use_prefix  = True,
        resource_A_uri     = "/resource/A",
        resource_B_uri     = "/resource/B",
    )
    c = make_component(rctp, Join)

    data_A = [
        { "email" : "a@b.c", "foo" : "A foo A" },
        { "email" : "b@b.c", "foo" : "A foo B" },
        { "email" : "c@b.c", "foo" : "A foo C" },
    ]
    data_B = [
        { "Email" : "x@b.c", "foo" : "B foo x", "bar" : "bar X" },
        { "Email" : "b@b.c", "foo" : "B foo b", "bar" : "bar B" },
        { "Email" : "c@b.c", "foo" : "B foo c", "bar" : "bar C" },
        { "Email" : "d@d.d", "foo" : "B foo c", "bar" : "bar C" },
    ]
    RESOURCE_DICT = { c.resource_A_uri : data_A, c.resource_B_uri : data_B }

    res = c.join(None, None)
    should_be = [ {'A.foo': 'A foo C', 'B.bar': 'bar C', 'B.foo': 'B foo c', 'BlahBlah': 'c@b.c'},
                  {'A.foo': 'A foo B', 'B.bar': 'bar B', 'B.foo': 'B foo b', 'BlahBlah': 'b@b.c'} ]

    test_evaluator("Test 1", compare_outputs(res.entity, should_be))

    #
    # Test 2: Same data, but not always prefix
    #
    rctp['always_use_prefix'] = False
    c = make_component(rctp, Join)
    res = c.join(None, None)
    should_be = [ {'A.foo': 'A foo C', 'B.foo': 'B foo c', 'BlahBlah': 'c@b.c', 'bar': 'bar C'},
                  {'A.foo': 'A foo B', 'B.foo': 'B foo b', 'BlahBlah': 'b@b.c', 'bar': 'bar B'} ]

    test_evaluator("Test 2", compare_outputs(res.entity, should_be))

    #
    # Same data, but no new keyfield name
    #
    rctp['new_keyfield_name'] = None
    c = make_component(rctp, Join)
    res = c.join(None, None)
    should_be = [ {'A.foo': 'A foo C', 'B.foo': 'B foo c', 'email': 'c@b.c', 'bar': 'bar C'},
                  {'A.foo': 'A foo B', 'B.foo': 'B foo b', 'email': 'b@b.c', 'bar': 'bar B'} ]

    test_evaluator("Test 3", compare_outputs(res.entity, should_be))

    #
    # Testing with no resulting joins
    #
    data_B[1]['Email'] = "bb@b.c"
    data_B[2]['Email'] = "cc@c.c"
    res = c.join(None, None)
    should_be = []
    test_evaluator("Test 4", compare_outputs(res.entity, should_be))

    #
    # Testing with one input empty
    #
    data_B = dict()
    res = c.join(None, None)
    should_be = []
    test_evaluator("Test 5", compare_outputs(res.entity, should_be))

    #
    # Testing with both inputs empty
    #
    data_A = dict()
    data_B = dict()
    res = c.join(None, None)
    should_be = []
    test_evaluator("Test 6", compare_outputs(res.entity, should_be))

    print

