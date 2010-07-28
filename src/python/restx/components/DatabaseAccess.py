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
A database access component for SnakeSQL

"""
# Imports all aspects of the API
from restx.components.api import *
import os

import SnakeSQL

def count(tname):
    # Doesn't support count...
    return len(cursor.execute("SELECT ID FROM %s" % tname))

def insert(tname, valdict):
    new_id = count(tname) + 1
    colstr = ', '.join([k for k in valdict.keys()])
    valstr = ', '.join([(valdict[k] if type(valdict[k]) in [int, long, float] else "'%s'" % valdict[k]) for k in valdict.keys()])
    cmdstr = "INSERT INTO %s (ID, %s) VALUES (%d, %s)" % (tname, colstr, new_id, valstr)
    print "@@@ Executing: ", cmdstr
    cursor.execute(cmdstr)
    connection.commit()
    return new_id


class DatabaseAccess(BaseComponent):
    NAME             = "DatabaseAccess"
    DESCRIPTION      = "Accesses to an SQL database"
    DOCUMENTATION    = "Service methods and capabilities to access a SQL database"

    PARAM_DEFINITION = {
                           "db_connection_string" : ParameterDef(PARAM_STRING,  "The database connection string", required=True),
                           "table_name"           : ParameterDef(PARAM_STRING,  "Name of the DB table", required=True),
                           "columns"              : ParameterDef(PARAM_STRING,  "Comma separated list of DB columns for the result, specify '*' for all", required=False, default="*"),
                           "id_column"            : ParameterDef(PARAM_STRING,  "Name of the column that holds the unique ID", required=True),
                           "where1"               : ParameterDef(PARAM_STRING,  "WHERE clause (SQL syntax), specify '-' to leave unset", required=False, default=""),
                           "where2"               : ParameterDef(PARAM_STRING,  "Additional WHERE clause (SQL syntax), specify '-' to leave unset", required=False, default=""),
                           "allow_updates"        : ParameterDef(PARAM_BOOL,    "Can the user create new entries or update existing ones?", required=False, default=False),
                           "name_value_pairs"     : ParameterDef(PARAM_BOOL,    "Return name/value pairs if set, otherwise plain lists", required=False, default=True),
                       }
    
    # A dictionary with information about each exposed service method (sub-resource).
    SERVICES         = {
                           "entries" : {
                               "desc" : "The stored entries. You can POST a new entry, PUT an update or GET an existing one. For PUT and GET the ID of the entry needs to be specified as the 'id' parameter.",
                               "params" : {
                                   "id"  : ParameterDef(PARAM_NUMBER, "The ID of the entry, needed for PUT and GET", required=False, default=-1),
                               },
                               "positional_params": [ "id" ],
                           }
                       }

    CONNECTION_CACHE = dict()

    cursor = None

    def __get_connection(self):
        if self.db_connection_string in self.CONNECTION_CACHE:
            connection = self.CONNECTION_CACHE[self.db_connection_string]
        else:
            connection = SnakeSQL.connect(database=self.db_connection_string)
            self.CONNECTION_CACHE[self.db_connection_string] = connection
        cursor = connection.cursor()
        return connection, cursor

    def __column_sanity_check(self, columns):
        elems = columns.split(",")
        for e in elems:
            e = e.strip()
            if " " in e  or  "(" in e  or  ")" in e  or  ";" in e:
                raise RestxException("Malformed columns")

    def __get_where_str(self, id=None):
        if self.where2 != "-" and (self.where1 == "-"  or  not self.where1):
            # Making sure that where1 is set
            self.where1 = self.where2
            self.where2 = None
        if self.where1  and  self.where1 != "-":
            if id and id > -1:
                where_str = " WHERE %s AND %s=%s" % (self.where1, self.id_column, id)
            else:
                where_str = " WHERE %s" % self.where1
            if self.where2  and  self.where2 != "-":
                where_str += " AND %s" % self.where2
        else:
            if id and id > -1:
                where_str = " WHERE %s=%s" % (self.id_column, id)
            else:
                where_str = ""
        return where_str


    def __get_entry(self, connection, cursor, id):
        #
        # Getting data
        #
        where_str = self.__get_where_str(id)
        cmd_str = str("SELECT %s FROM %s%s" % (self.columns, self.table_name, where_str))
        results = cursor.execute(cmd_str)
        if self.name_value_pairs:
            if self.columns.strip() != "*":
                colnames = [ cname.strip() for cname in self.columns.split(",")]
            else:
                # Need to get the column names myself, necessary because it was just '*'
                colnames = cursor.columns(self.table_name)
            data = [ dict(zip(colnames, row)) for row in results ]
        else:
            data = [ row for row in results ]
        if id and id > -1:
            # Only one result
            if len(data) == 0:
                return Result.notFound("Could not find entity with id '%s'" % id)
            elif len(data) > 1:
                return Result.internalServerError("Data inconsistency")
            else:
                data = data[0]
        return Result.ok(data)


    def __post_entry(self, connection, cursor, obj, colnames):
        # The new ID we will use to store this object
        new_id = len(cursor.execute(str("SELECT %s FROM %s" % (self.id_column, self.table_name)))) + 1
        obj[self.id_column] = new_id

        colnames.insert(0, self.id_column)

        colstr  = ', '.join(colnames)
        valstr  = ', '.join([(str(obj[k]) if type(obj[k]) in [int, long, float] else "'%s'" % obj[k]) for k in colnames ])
        cmd_str = "INSERT INTO %s (%s) VALUES (%s)" % (self.table_name, colstr, valstr)
        cursor.execute(str(cmd_str))
        connection.commit()
        return Result.created(str(Url("%s/%d" % (self.getMyResourceUri(), new_id))))


    def __put_entry(self, connection, cursor, obj, colnames, id):
        # Check that this element exists in the database
        res = cursor.execute(str("SELECT %s FROM %s WHERE %s=%d" % (self.id_column, self.table_name, self.id_column, id)))
        if len(res) > 1:
            return Result.internalServerError("Data inconsistency")
        elif len(res) == 0:
            return Result.notFound("Entry with id '%d' cannot be found" % id)
        colsets = ', '.join([ ("%s=%s" % (k, (str(obj[k]) if type(obj[k]) in [int, long, float] else "'%s'" % obj[k]))) for k in colnames ])
        cmd_str = "UPDATE %s SET %s WHERE %s=%d" % (self.table_name, colsets, self.id_column, id)
        cursor.execute(str(cmd_str))
        connection.commit()
        return Result.ok("Update successful")
     


    def entries(self, method, input, id):
        if self.columns  and  self.columns != "*":
            self.__column_sanity_check(self.columns)

        connection, cursor = self.__get_connection()

        if method == HttpMethod.GET:
            #
            # Getting data
            #
            return self.__get_entry(connection, cursor, id)

        elif self.allow_updates:

            if method in [ HttpMethod.POST, HttpMethod.PUT ]:
                #
                # Creating a new entry or updating an existing one
                #
                obj = self.fromJson(input)

                if method == HttpMethod.POST:
                    # Creating a new one?
                    if id > 0:
                        return Result.badRequest("Cannot specify ID when creating a new entry (ID is determined by server)")
                    else:
                        # We set the ID ourselves, just quietly remove it
                        if self.id_column in obj:
                            del obj[self.id_column]

                # Getting the column names for the table and making sure that we are
                # only referring to existing columns
                colnames = cursor.columns(self.table_name)
                for name in obj.keys():
                    if name not in colnames:
                        return Result.badRequest("Unknown column '%s'" % name)

                # Some sanity checking on those
                for name, value in obj.items():
                    for illegal in ";*()":
                        if illegal in name:
                            return Result.badRequest("Illegal character in column name: " + name)
                        if type(value) in [ str, unicode ]:
                            if illegal in value:
                                return Result.badRequest("Illegal character in value for column '%s'" % name)

                # Get the properly ordered list of columns that we have actually specified.
                # This allows us to ommit optional values.
                cols = [ name for name in colnames if name in obj ]

                if method == HttpMethod.POST:
                    return self.__post_entry(connection, cursor, obj, cols)
                else:
                    return self.__put_entry(connection, cursor, obj, cols, id)

        else:
            return Result.unauthorized("You don't have permission to modify this resource")


