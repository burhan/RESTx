/*
 * Component Meta Information
 */
this.name = "JsTwitterComponent"

this.parameters = {
  account_name     : { type: TYPE.STRING, description: "Twitter account name", required: true },
  account_password : { type: TYPE.PASSWORD, description: "Password", required: true }
}

this.description = "Provides access to a Twitter account."

this.documentation = "The Twitter component is designed to provide access to a Twitter account.\n"
                   + "It can be used to get as well as update status, or to view the timeline of a Twitter account.\n"
                   + "To create the resource, the Twitter account name and password need to be specified.\n"

/*
 * "Status" Service
 */
status.description = "You can GET the status or POST a new status to it."
status.inputTypes = ["text/plain"]
status.outputTypes = ["text/plain"]

function status(method, input) {
  
  function getStatus() {
    result = RESTx.httpGet("http://api.twitter.com/1/users/show.json?screen_name=" + account_name)
    
    return result.status == HTTP.OK ? RESULT.ok(RESTx.fromJsonStr(result.data).get("status").get("text"))
                                    : RESULT.internalServerError("Problem with Twitter: " + result.data)
  }
  
  function postStatus(input) {
    RESTx.httpSetCredentials(account_name, account_password)
    result = RESTx.httpPost("http://api.twitter.com/1/statuses/update.xml", "status="+ input)
    
    return result.status == HTTP.OK ? RESULT.ok("Status updated")
                                    : RESULT.internalServerError("Problem with Twitter: " + result.data)
  }
  
  switch(method) {
    case HTTP.GET : return getStatus()
    case HTTP.POST: return postStatus(input)
    default       : throw "Status unsupported method: " + method
  }
}

/*
 * "Timeline" Service
 */
timeline.description = "You can GET the timeline of the user."
timeline.parameters = {
  count  : { type: TYPE.NUMBER, description: "Number of results", required: false, defaultValue: 20},
  filter : { type: TYPE.BOOLEAN, description: "If set, only 'important' fields are returned", required: false, defaultValue: true}
}

function timeline(method, input, count, filter) {
  if (method != HTTP.GET) throw "Timeline unsupported method: " + method

  // TODO implement
  return RESULT.ok("fake timeline")
}

