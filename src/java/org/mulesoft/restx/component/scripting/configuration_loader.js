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

//Supporting functions
function nz(value, defaultValue) {
    return value == undefined ? defaultValue : value 
}

function getParameterDef(type, description, required, defaultValue) {
    switch(type) {
        case TYPE.STRING  : return new org.mulesoft.restx.parameter.ParameterDefString(description, required, defaultValue)
        case TYPE.PASSWORD: return new org.mulesoft.restx.parameter.ParameterDefPassword(description, required, defaultValue)
        case TYPE.BOOLEAN : return new org.mulesoft.restx.parameter.ParameterDefBoolean(description, required, defaultValue)
        case TYPE.NUMBER  : return new org.mulesoft.restx.parameter.ParameterDefNumber(description, required, defaultValue)
        default           : throw "Unsupported parameter type: " + type
    }
}

function getServiceMeta(service) {
    serviceDescriptor = new org.mulesoft.restx.component.api.ServiceDescriptor(service.description,
                                                                               nz(service.parametersInBody, false),
                                                                               nz(service.outputTypes, null),
                                                                               nz(service.inputTypes, null))
    parameters = service.parameters
    parameterNames = new java.util.ArrayList()
    parameterTypes = new java.util.ArrayList()
    positionalParameters = new java.util.ArrayList()
    
    for (parameterName in parameters) {
        parameter = parameters[parameterName]
        parameterNames.add(parameterName)
        
        parameterDef = getParameterDef(parameter.type,
                                       parameter.description,
                                       nz(parameter.required, false),
                                       nz(parameter.defaultValue, null))
        
        parameterTypes.add(parameterDef.getJavaType())

        serviceDescriptor.addParameter(parameterName, parameterDef)
        
        if (nz(parameter.positional, false)) {
            positionalParameters.add(parameterName)
        }
    }
    
    if (!positionalParameters.isEmpty()) {
        serviceDescriptor.setPositionalParameters(positionalParameters);
    }

    return {descriptor: serviceDescriptor, parameterNames: parameterNames, parameterTypes: parameterTypes}
}

//Base configuration
this.componentDescriptor = new org.mulesoft.restx.component.api.ComponentDescriptor(name, description, documentation)

//Resource parameters
for (parameterName in parameters) {
    parameter = parameters[parameterName]
                           
    componentDescriptor.addParameter(parameterName,
                                     getParameterDef(parameter.type,
                                                     parameter.description,
                                                     nz(parameter.required, false),
                                                     nz(parameter.defaultValue, null)))
}

//Services
this.paramOrder = new java.util.HashMap()
this.paramTypes = new java.util.HashMap()

for (var functionName in this) {
    // Any local function with a description is considered to be a Service
    if (typeof this[functionName] == 'function' && this.hasOwnProperty(functionName) && this[functionName].description != undefined) {
        serviceMeta = getServiceMeta(this[functionName])
        componentDescriptor.addService(functionName, serviceMeta.descriptor)
        paramOrder.put(functionName, serviceMeta.parameterNames)
        paramTypes.put(functionName, serviceMeta.parameterTypes)
    }
}
