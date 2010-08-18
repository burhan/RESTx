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

public class ParameterDefPassword extends ParameterDef
{
    private final String defaultVal;

    public ParameterDefPassword(String desc)
    {
        this(desc, true, null);
    }

    public ParameterDefPassword(String desc, String defaultVal)
    {
        this(desc, false, defaultVal);
    }

    public ParameterDefPassword(String desc, boolean required, String defaultVal)
    {
        super("password", desc, required);
        this.defaultVal = defaultVal;
    }

    @Override
    public Object getDefaultVal()
    {
        return defaultVal;
    }

    @Override
    public Class<?> getJavaType()
    {
        return String.class;
    }
}
