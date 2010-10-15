/*      
 *  RESTx: Sane, simple and effective data publishing and integration. 
 *  
 *  Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com 
 *  
 *  This program is free software: you can redistribute it and/or modify 
 *  it under the terms of the GNU General Public License as published by 
 *  the Free Software Foundation, either version 3 of the License, or 
 *  (at your option) any later version. 
 * 
 *  This program is distributed in the hope that it will be useful, 
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of 
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
 *  GNU General Public License for more details. 
 * 
 *  You should have received a copy of the GNU General Public License 
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>. 
 */

package org.mulesoft.restx.parameter;

import org.mulesoft.restx.exception.RestxException;

import java.util.List;

public abstract class ParameterDefList extends ParameterDef
{
    public ParameterDefList(String ptype, String desc, boolean required)
    {
        super(ptype, desc, required);
    }

    public boolean isList()
    {
        return true;
    }

    private boolean findInArray(String[] arrayObj, String value)
    {
        for (String v: arrayObj) {
            if (v.equals(value)) {
                return true;
            }
        }
        return false;
    }

    public String html_type(String name, String[] initial)
    {
        if (choices != null) {
            String buf = "<select name=" + name + " id=" + name + " multiple size=" + Math.min(8, choices.length) + " >";

            /*
            if (!this.required) {
                // If we are not required then we definitely have a default value
                buf += "<option value=\"\">--- Accept default ---</option>";
            }
            */
                
            for (String c: choices) {
                String args = "";
                if ((initial != null)  &&  (findInArray(initial, c))) {
                    args = " selected=\"selected\"";
                }
                buf += "<option value=\"" + c + "\"" + args + ">" + c + "</option>";
            }
            buf += "</select>";
            return buf;
        }
            
        return "<input type=text name=" + name + " id=" + name + "##### STRING FOR LIST #########" + "/>";
    }
}

