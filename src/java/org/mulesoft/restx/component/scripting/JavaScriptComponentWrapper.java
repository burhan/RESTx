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

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import javax.script.Bindings;
import javax.script.Invocable;
import javax.script.ScriptContext;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;
import javax.script.SimpleBindings;

import org.mulesoft.restx.component.api.ComponentDescriptor;
import org.mulesoft.restx.exception.RestxException;

public class JavaScriptComponentWrapper extends BaseScriptingComponent
{
    private Map<String, Object> resourceParams;

    @Override
    protected ScriptEngine newScriptEngine(ScriptEngineManager scriptEngineManager)
    {
        return scriptEngineManager.getEngineByName("javascript");
    }

    // TODO support: inputTypes ([]), outputTypes ([])

    @SuppressWarnings("unchecked")
    @Override
    protected void initialiseComponentDescriptor() throws RestxException
    {
        if (componentDescriptor != null)
        {
            return;
        }

        final Bindings bindings = new SimpleBindings();
        addCommonBindings(bindings);

        // load the component metadata into bindings
        evaluateComponent(bindings);

        // extract a component descriptor out of these bindings
        evaluateResource(bindings, "configuration_loader.js");

        componentDescriptor = (ComponentDescriptor) bindings.get("componentDescriptor");
        paramOrder = (HashMap<String, ArrayList<String>>) bindings.get("paramOrder");
        paramTypes = (HashMap<String, ArrayList<Class<?>>>) bindings.get("paramTypes");
    }

    public void _setResourceParams(Map<String, Object> resourceParams)
    {
        this.resourceParams = resourceParams;
    }

    public Object _serviceMethodDispatch(String methodName, Object[] args) throws RestxException
    {
        try
        {
            final ScriptEngine engine = getScriptEngine();
            final Bindings bindings = engine.getBindings(ScriptContext.ENGINE_SCOPE);
            addCommonBindings(bindings);

            // must evaluate first before calling a function directly
            evaluateComponent(bindings);

            // bind the resource parameters before calling the function
            bindings.putAll(resourceParams);
            return ((Invocable) engine).invokeFunction(methodName, args);
        }
        catch (final ScriptException se)
        {
            throw new RestxException(se.getMessage());
        }
        catch (final NoSuchMethodException nsme)
        {
            throw new RestxException(nsme.getMessage());
        }
    }
}
