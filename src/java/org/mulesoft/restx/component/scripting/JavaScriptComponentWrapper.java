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

import javax.script.Bindings;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.SimpleBindings;

import org.mulesoft.restx.component.api.ComponentDescriptor;
import org.mulesoft.restx.component.api.HTTP;
import org.mulesoft.restx.exception.RestxException;
import org.mulesoft.restx.parameter.ParameterType;

public class JavaScriptComponentWrapper extends BaseScriptingComponent
{
    @Override
    protected ScriptEngine getEngine(ScriptEngineManager scriptEngineManager)
    {
        return scriptEngineManager.getEngineByName("javascript");
    }

    // TODO add support for: inputTypes ([]), outputTypes ([]), positionalParams
    // positionalParams([string])

    @Override
    protected void initialiseComponentDescriptor() throws RestxException
    {
        final Bindings bindings = new SimpleBindings();
        bindings.put("HTTP", new HTTP());
        bindings.put("TYPE", new ParameterType());

        // load the component metadata into bindings
        evaluateComponent(bindings);

        // extract a component descriptor out of these bindings
        componentDescriptor = (ComponentDescriptor) evaluateResource(bindings, "configuration_loader.js");
    }

    public Object serviceMethodDispatch(String methodName, Object[] args)
    {
        return true;
    }
}
