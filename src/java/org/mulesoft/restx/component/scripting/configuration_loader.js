// Supporting functions
function getParameterDef(type, description, required, defaultValue) {
	switch(type) {
		case "string"  : return new org.mulesoft.restx.parameter.ParameterDefString(description, required, defaultValue)
		case "password": return new org.mulesoft.restx.parameter.ParameterDefPassword(description, required, defaultValue)
		// TODO add more types
		default        : throw "Unsupported parameter type: " + type
	}
}

// Base configuration
_componentDescriptor = new org.mulesoft.restx.component.api.ComponentDescriptor(name, description, documentation)

// Resource parameters
// TODO
for (parameterName in parameters) {
	parameter = parameters[parameterName]
	                       
	_componentDescriptor.addParameter(parameterName,
									  getParameterDef(parameter.type, parameter.description, parameter.required, parameter.defaultValue))
}

// Services
// TODO

_componentDescriptor