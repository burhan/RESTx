name = "TwitterComponent"

parameters = {
  account_name     : { type: "string", desc: "Twitter account name" },
  account_password : { type: "string", desc: "Password" }
}

description = "Provides access to a Twitter account."

documentation = "The Twitter component is designed to provide access to a Twitter account.\n"
              + "It can be used to get as well as update status, or to view the timeline of a Twitter account.\n"
              + "To create the resource, the Twitter account name and password need to be specified.\n"

services = {
  
  status : {
    desc : "You can GET the status or POST a new status to it.",
    impl : function(method, input) {
      
      function getStatus() {
        // TODO HTTP GET on "http://api.twitter.com/1/users/show.json?screen_name=" + parameters.account_name.value
        return "status of " + parameters.account_name.value;
      }
      
      function postStatus(input) {
        // TODO HTTP POST "http://api.twitter.com/1/statuses/update.xml status=" + input
        return "Status updated"
      }
      
      switch(method) {
        case HTTP.GET : return getStatus();
        case HTTP.POST: return postStatus(input);
        default       : throw "Unsupported method: " + method;
      }
    }
  }
  
}

