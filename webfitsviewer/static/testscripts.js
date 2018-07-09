/***********************************************************************

TESTSCRIPTS.JS

These functions are used by the browser test page to confirm browser
compatibility.

***********************************************************************/

//**** Global Variables
var count;


//**** Functions

// Browsertests: Run tests to determine compatibility of the local browser.
function browsertests(){
	// Set message target
	target = 'browsertests';
	resultadd(target,'<br>Running . . .');
	// test Base64.decode
	resultadd(target,'<br>Testing Base64.decode');
    input = 'SGFsbG8='; // stands for 'Hallo'
	output = Base64.decode(input);
	resultadd(target,'<br>. . . Done: output=' + output);
	// atob and btoa base64 tests - DOESN'T WORK WITH IE9 - try IE 10
	// Test writing a table (important for IE)
	count = 0;
	resultadd(target,'<br>Testing writing table');
	txt = '<table>';
	txt +='<tr><th>Cell1</th><th>Cell2</th>';
	txt +='</table>';
	document.getElementById('testfield').innerHTML = txt;
	resultadd(target,'<br>. . . Done');
	// Date Test
	id = (new Date()).toString()
	resultadd(target,'<br> ID = '+id);
	if ('bla'.indexOf('ba') > -1){ resultadd(target,'<br>In');
	} else { resultadd(target,'<br>Out'); }
	// Function parameter test
	resultadd(target,'<br>Function Argument Tests:');
	functarg();
	functarg(1);
	functarg(2,'ee');
	functarg('xy',3,'set',3);
	// Final Message
	resultadd(target,'<br>Test of eval with variables: ');
	i=3;
	s='a';
	eval("s=s+i+' blabber';");
	resultadd(target,s);
	resultadd(target,'<br>Tests Complete');
}

// Buttonf(): Run tests triggered by a button
function buttonf(){
	// update count
	count += 1;
	// get text from table
	fulldata = document.getElementById('testfield').innerHTML;
	// get index for end of header (alternate options if it's only 1 line)
	//     search with upper case needed for Internet Explorer
	i = Math.max(fulldata.indexOf('<tr>'),
				 fulldata.indexOf('<TR>') );
	startdata = Math.max(fulldata.indexOf('<tr', i+1),
						 fulldata.indexOf('<TR', i+1) );
	if (startdata < 0) {
	    startdata = Math.max(fulldata.indexOf('</tbody>', i),
	    		             fulldata.indexOf('</TBODY>', i) );
	}
	if (startdata < 0) {
	    startdata = Math.max(fulldata.indexOf('</tr>', i) + 5,
	    		             fulldata.indexOf('</TR>', i) + 5 );
	}
	if (startdata < 0) {
	    startdata = fulldata.length;
	}
	// make new line
	newline = '<tr><td>Bla</td><td>blo'+count+'</td></tr>';
	// recombine text
	newdata = fulldata.substring(0, startdata) + newline +
	 	      fulldata.substring(startdata);
	document.getElementById('testfield').innerHTML = newdata;
	document.getElementById('testtext').value = newdata+' '+i+' '+startdata;
}

// Resultsadd: Add text to the specified DOM field.
function resultadd(target, text){
	targetext = document.getElementById(target).innerHTML;
	targetext = targetext+text;
	document.getElementById(target).innerHTML = targetext;
}

// FunctArg: test for function arguments:
function functarg(x, y) {
    resultadd('browsertests','<br>&nbsp; X='+x+' Y='+y);
    for( i=0; i< arguments.length; i++) {
        resultadd('browsertests',' arg['+i+']='+arguments[i]);
    }
}