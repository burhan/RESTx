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

import java.math.BigDecimal;
import java.math.BigInteger;

public class ParameterDefNumber extends ParameterDef
{
    private final BigDecimal defaultVal;

    public ParameterDefNumber(String desc)
    {
        this(desc, true, null);
    }

    public ParameterDefNumber(String desc, int defaultVal)
    {
        this(desc, false, defaultVal);
    }

    public ParameterDefNumber(String desc, float defaultVal)
    {
        this(desc, false, defaultVal);
    }

    public ParameterDefNumber(String desc, BigDecimal defaultVal)
    {
        this(desc, false, defaultVal);
    }

    public ParameterDefNumber(String desc, boolean required, Number defaultVal)
    {
        super("number", desc, required);
        this.defaultVal = toBigDecimal(defaultVal);
    }

    @Override
    public Object getDefaultVal()
    {
        return defaultVal;
    }

    private BigDecimal toBigDecimal(Number defaultVal)
    {
        if (defaultVal instanceof BigDecimal)
        {
            return (BigDecimal) defaultVal;
        }
        else if (defaultVal instanceof BigInteger)
        {
            return new BigDecimal((BigInteger) defaultVal);
        }
        else if (defaultVal instanceof Float)
        {
            return BigDecimal.valueOf(defaultVal.floatValue());
        }
        else if (defaultVal instanceof Double)
        {
            return BigDecimal.valueOf(defaultVal.doubleValue());
        }
        else if (defaultVal instanceof Long)
        {
            return BigDecimal.valueOf(defaultVal.longValue());
        }
        else if (defaultVal instanceof Integer)
        {
            return BigDecimal.valueOf(defaultVal.intValue());
        }

        return null;
    }
}
