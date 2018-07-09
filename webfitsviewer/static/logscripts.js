/***********************************************************************

LOGSCRIPTS.JS

These functions are used by the pipeline log page to dynamically load
new content.

***********************************************************************/

//**** Global Variables
var request; // XMLHttpRequest object
var sid; // Session ID
var baseurlpath; // base url path to make absolute URL paths
var reloadtime; // reload time
var linemaxn=500; // number of lines to show

//**** Function Declarations

// LogRequest: Send request for new log messages
function logrequest() {
    // make a request object
    request = new XMLHttpRequest();
    request.onreadystatechange = logadd;
    // fill the request
    request.open("POST", baseurlpath+"/log/update", true);
    request.send("sid="+sid);
}

// LogAdd: Response function to the new data request, adds new log messages
function logadd() {
    // Check if the response is ready
    if (request.readyState==4 && request.status==200){
    	// get text from table
    	fulldata = $('#logtable').html();
    	// get index for end of header (alternate options if it's only 1 line)
    	i = Math.max(fulldata.indexOf('<tr>'),
 				     fulldata.indexOf('<TR>'));
    	startdata = Math.max(fulldata.indexOf('<tr', i+1),
				             fulldata.indexOf('<TR', i+1));
    	if (startdata < 0) {
    		startdata = Math.max(fulldata.indexOf('</tbody>', i),
		                         fulldata.indexOf('</TBODY>', i));
    	}
    	if (startdata < 0) {
    		startdata = Math.max(fulldata.indexOf('</tr>', i) + 5,
    				             fulldata.indexOf('</TR>', i) + 5 );
    	}
    	if (startdata < 0) {
    	    startdata = fulldata.length;
    	}
    	// recombine text
    	newdata = fulldata.substring(0, startdata) + request.responseText +
    	 	      fulldata.substring(startdata);
    	// get index of 1000th line in existing code -> stopdata
    	linen = linemaxn;
    	stopdata = 0;
    	while (linen > 0){
    		stopdata = Math.max(newdata.indexOf('<tr', stopdata+10 ),
    				            newdata.indexOf('<TR', stopdata+10 ));
    		if (stopdata<0){ linen = -1;
    		} else { linen = linen - 1; }
    	}
    	if (linen==0){
    		finaldata = newdata.substring(0,stopdata) + '</TBODY></TABLE>';
    	} else { finaldata = newdata; }
    	// send text to table
    	$('#logtable').html(finaldata);
    	// set time in logtimetext
    	time = new Date();
    	timestr = time.toLocaleTimeString();
    	$('#logtimetext').html(timestr);
    	// Set up next request
    	setTimeout('logrequest();', 1000*reloadtime);
    }
}
