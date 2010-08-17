/*
 * Component Declaration
 */
name = "JsTwitterComponent"

parameters = {
  account_name     : { type: TYPE.STRING, description: "Twitter account name", required: true },
  account_password : { type: TYPE.PASSWORD, description: "Password", required: true }
}

description = "Provides access to a Twitter account."

documentation = "The Twitter component is designed to provide access to a Twitter account.\n"
              + "It can be used to get as well as update status, or to view the timeline of a Twitter account.\n"
              + "To create the resource, the Twitter account name and password need to be specified.\n"

services = {
  status : {
    description : "You can GET the status or POST a new status to it."
  },
  
  timeline : {
    description : "You can GET the timeline of the user.",
    parameters  : {
      count  : { type: TYPE.NUMBER, description: "Number of results", required: false, defaultValue: 20},
      filter : { type: TYPE.BOOLEAN, description: "If set, only 'important' fields are returned", required: false, defaultValue: true}
    }
  }
}

/*
 * Services Implementation
 */
function status(method, input) {
  
  function getStatus() {
    // TODO HTTP GET on "http://api.twitter.com/1/users/show.json?screen_name=" + parameters.account_name.value
    return "status of " + parameters.account_name.value
  }
  
  function postStatus(input) {
    // TODO HTTP POST "http://api.twitter.com/1/statuses/update.xml status=" + input
    return "Status updated"
  }
  
  switch(method) {
    case HTTP.GET : return getStatus()
    case HTTP.POST: return postStatus(input)
    default       : throw "Status unsupported method: " + method
  }
}

function timeline(method, input, count, filter) {
  if (method != HTTP.GET) throw "Timeline unsupported method: " + method

  // TODO implement
  return "fake timeline"
}

