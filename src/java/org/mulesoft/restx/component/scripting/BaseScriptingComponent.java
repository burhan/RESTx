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

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.net.URISyntaxException;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import javax.script.Bindings;
import javax.script.Compilable;
import javax.script.CompiledScript;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.ScriptException;

import org.mulesoft.restx.Settings;
import org.mulesoft.restx.component.BaseComponent;
import org.mulesoft.restx.component.api.HTTP;
import org.mulesoft.restx.component.api.Result;
import org.mulesoft.restx.exception.RestxException;
import org.mulesoft.restx.parameter.ParameterType;

public abstract class BaseScriptingComponent extends BaseComponent
{
    // TODO replace this with a RESTx-managed cache
    private final static ConcurrentMap<File, CompiledScript> CACHE = new ConcurrentHashMap<File, CompiledScript>();

    private final ScriptEngineManager scriptEngineManager = new ScriptEngineManager();

    private File componentScriptFile;

    protected File getComponentScriptFile()
    {
        if (componentScriptFile == null)
        {
            componentScriptFile = new File(Settings.getRootDir() + instanceConf.get("path"));
        }

        return componentScriptFile;
    }

    protected Object evaluateComponent(Bindings bindings) throws RestxException
    {
        return evaluate(bindings, getComponentScriptFile());
    }

    protected Object evaluateResource(Bindings bindings, String resourceName) throws RestxException
    {
        try
        {
            return evaluate(bindings, new File(getClass().getResource(resourceName).toURI()));
        }
        catch (final URISyntaxException urise)
        {
            throw new RestxException(urise.getMessage());
        }
    }

    private Object evaluate(Bindings bindings, File scriptFile) throws RestxException
    {
        try
        {
            final CompiledScript compiledScript = getCompiledScript(scriptFile);

            if (compiledScript != null)
            {
                return compiledScript.eval(bindings);
            }

            final ScriptEngine engine = getEngine(scriptEngineManager);
            return engine.eval(new FileReader(scriptFile), bindings);
        }
        catch (final FileNotFoundException fnfe)
        {
            throw new RestxException(fnfe.getMessage());
        }
        catch (final ScriptException se)
        {
            throw new RestxException(se.getMessage());
        }
    }

    protected CompiledScript getCompiledScript() throws RestxException
    {
        return getCompiledScript(getComponentScriptFile());
    }

    protected CompiledScript getCompiledScript(File scriptFile) throws RestxException
    {
        try
        {
            CompiledScript compiledScript = CACHE.get(scriptFile);

            if (compiledScript != null)
            {
                return compiledScript;
            }

            final ScriptEngine engine = getEngine(scriptEngineManager);

            if (engine instanceof Compilable)
            {
                compiledScript = ((Compilable) engine).compile(new FileReader(scriptFile));
                CACHE.put(scriptFile, compiledScript);
                return compiledScript;
            }

            return null;
        }
        catch (final FileNotFoundException fnfe)
        {
            throw new RestxException(fnfe.getMessage());
        }
        catch (final ScriptException se)
        {
            throw new RestxException(se.getMessage());
        }
    }

    protected abstract ScriptEngine getEngine(ScriptEngineManager scriptEngineManager);

    protected void addCommonBindings(final Bindings bindings)
    {
        bindings.put("HTTP", new HTTP());
        bindings.put("TYPE", new ParameterType());
        bindings.put("RESULT", new Result(500, null));
    }
}
