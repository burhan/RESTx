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

package org.mulesoft.restx.component.scripting;

import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.SimpleBindings;

import org.mulesoft.restx.component.api.ComponentDescriptor;
import org.mulesoft.restx.exception.RestxException;

public class JavaScriptComponent extends BaseScriptingComponent
{
    private final ScriptEngine javaScriptEngine = new ScriptEngineManager().getEngineByExtension("js");

    @Override
    protected ScriptEngine getEngine()
    {
        return javaScriptEngine;
    }

    @Override
    protected void initialiseComponentDescriptor() throws RestxException
    {
        final SimpleBindings bindings = new SimpleBindings();
        evaluate(bindings);
        componentDescriptor = new ComponentDescriptor((String) bindings.get("name"),
            (String) bindings.get("description"), (String) bindings.get("documentation"));
    }
}
