
String.prototype.startsWith = function(str) 
{return (this.match("^"+str)==str)}

String.prototype.endsWith = function(str) 
{return (this.match(str+"$")==str)}

var orig_background = null;
var orig_color      = null;
var interval_id     = null;
var link_elems      = new Array();
var elems           = new Array();
var blink_interval  = 250;

function ScrollToElement(theElement){
  // Code for this function is from: http://radio.javaranch.com/pascarello/2005/01/09/1105293729000.html
  var selectedPosX = 0;
  var selectedPosY = 0;

  while(theElement != null){
    selectedPosX += theElement.offsetLeft;
    selectedPosY += theElement.offsetTop;
    theElement = theElement.offsetParent;
  }
  current_scroll_offset = parent.top.frames[2].pageYOffset;
  if (top.frames[2].innerHeight + current_scroll_offset < selectedPosY  ||  selectedPosY < current_scroll_offset) {
      parent.top.frames[2].scrollTo(selectedPosX,selectedPosY);
  }
}

function linkHigh(lname)
{
    if (lname in link_elems) {
        link = link_elems[lname];
        if (orig_background == null) {
            orig_background = link.style.backgroundColor;
            orig_color      = link.style.color;
        }
        link.style.backgroundColor="#ff0000";
        link.style.color="#ffffff";
        setTimeout("linkLow('" + lname + "')", blink_interval);
    }
}

function linkLow(lname, no_high)
{
    if (lname in link_elems) {
        link = link_elems[lname];
        link.style.backgroundColor=orig_background;
        link.style.color=orig_color;
        if (no_high === undefined) {
            setTimeout("linkHigh('" + lname + "')", blink_interval);
        }
    }
}

function getLinkByUrl(url)
{
    var search_start = false;
    if (url.endsWith("###")) {
        url = url.substring(0, url.length-3);
        search_start = true;
    }
    doc = parent.top.frames[2].document;
    var links = doc.getElementsByTagName("A");
    var total = links.length
    for (i=0; i<total; i++) {
        if ((!search_start  &&  (links[i].innerHTML == url))  ||  (search_start && links[i].innerHTML.startsWith(url))) {
            ScrollToElement(links[i]);
            return links[i];
        }
    }
    return null;
}

function linkHighlight(url)
{
    link = getLinkByUrl(url);
    if (link != null) {
        link_elems[link.innerHTML] = link;
        linkHigh(link.innerHTML);
    }
}

function stopLinkHighlight(url)
{
    link = getLinkByUrl(url);
    if (link != null) {
        link_name = link.innerHTML;
        if (link_name in link_elems) {
            linkLow(link_name, true);
            delete link_elems[link_name];
        }
    }
}

function getElemById(id)
{
    doc = parent.top.frames[2].document;
    var elem = doc.getElementById(id);
    return elem;
}

function elemHighlight(id)
{
    elem = getElemById(id);
    if (elem != null) {
        elems[id] = elem;
        ScrollToElement(elem);
        elemHigh(id);
    }
}

function rowHighlight(id)
{
    elemHighlight(id+"_name");
    //elemHighlight(id+"_value");
}

function elemHigh(id)
{
    if (id in elems) {
        elem = elems[id];
        if (orig_background == null) {
            orig_background = elem.style.backgroundColor;
        }
        elem.style.background="#ff8888";
        //setTimeout("elemLow('" + id + "')", blink_interval);
    }
}

function elemLow(id, no_high)
{
    if (id in elems) {
        elem = elems[id];
        elem.style.background=orig_background;
        if (no_high === undefined) {
            setTimeout("elemHigh('" + id + "')", blink_interval);
        }
    }
}

function stopElemHighlight(id)
{
    elem = getElemById(id);
    if (elem != null  &&  id in elems) {
        elemLow(id, true);
        delete elems[id];
    }
}

function stopRowHighlight(id)
{
    stopElemHighlight(id+"_name");
    //stopElemHighlight(id+"_value");
}

