/***********************************************************************

IMAGEANALYSIS.JS

This object is used by the pipeline data page to dynamically display
images.

 ***********************************************************************/

/***
 * Update notes for better logging of events
 * - Add imageanalysisobject variable - logspace, contains DOM name of log
 *   object. Disabled if ''. Given by init() - optional argument like analst
 * - Add self log function for using this. log(message) adds comment to top
 *   of log table with time stamp
 * - Use it to debug click and unclick box, then change scale, then open new
 *   image.
 */

/***
 * WCS:
 * - Imageopen: read values set coords flag to T if there are coordinate values
 * - Mousemove: If coods get imgx/y row and pixel coordinates of mouse (float)
 *              Extend message with coords (if RA/Dec - use it)
 * 
 * IDEAS / NOTES:
 * - make different tool object and have each object have a self.active
 * - Set maximal box size when in PSF mode
 * - Q why does zoomhandler() need a tools.update()?
 * - Idea: have two objects but only ONE is active at any time; that one
 *   is setting the image scale when it's on box (they also both have same color)
 * - Fabio: One box at a time is OK - too bad if scaling now goes to PSF box
 */

/**
 * ****** IMAGEANALYSIS OBJECT Object that handles the display of images and the
 * various tools and features of the display.
 */

// **** Constructor: creates the object
function imageanalysisobject() {
	// **** Object Variables
	// General Variables
	this.request = new XMLHttpRequest();
	this.stamp = ''; // Unique string (datetime is used)
	// Image Variables
	this.imgwidth = 0; // Width of raw image
	this.imgheight = 0; // Height of raw image
	this.imgraw = new Array(0); // 1D Array of raw image data
	// length==0 if data not yet arrived, [0] is the bottom left pixel
	this.imgrawsort = new Array(0); // Image data sorted
	this.imgscaled = new Array(0); // Image data scaled (0..255 for each pixel)
	this.nnans = 0; // Number of NaN in the image
	this.imgscale = '98%'; //'MinMax'; // Scale setting
	this.imgmin = 0.0; // Scale min data value
	this.imgmax = 1.0; // Scale max data value
	this.imgcolor = 'grey'; // Selected color scale
	this.imgzoom = 1.0; // Zoom factor (i.e. zoom in if >1)
	this.imgcan = 0; // image canvas object
	this.rescale = 1; // flag indicating that imgscaled needs to be recalculated
	// Coordinate system variables (others are added is coords=true)
	this.coords = false;
	// Analysis tools variables
	this.analcan = 0; // canvas for analysis object
	this.analsize = 160; // size of analysis window
	this.toollist = new Array(); // Array of analysis tool objects
	this.toolnow = null; // tool object currently selected
	this.toolmove = null; // tool object that is being moved
	this.mousex = 0; // x/y where the mouse was last seen
	this.mousey = 0;

	// **** Object Functions
	// WriteTools: writes the HTML code for the image analysis tools, a table with
	//             3 columns, 3 rows
	//             | Mouse X/Y/Value | Zoom, Scale, Color | Zoom in Window |
	//             |-----------------|--------------------|                |
	//             | Tools Selector ( 2 columns )         | ( 3 rows )     |
	//             |--------------------------------------|                |
	//             | Tools Output 1  | Tools Outout 2     |                |
	this.writetools = function() {
		document.writeln('<table><tr><td class = "tools"> \
		     <div id = "imageinfo"> \
		     Mouse&nbsp;X&nbsp;/&nbsp;Y:<br>&nbsp;<br>Value:<br>&nbsp;</div> \
		     <td class = "tools"><form> \
		     Zoom:<br> \
		     <select id = "zoomselect" disabled> \
		     <option>1/10</option> \
		     <option>1/3</option> \
		     <option>1x</option> \
		     <option>3x</option> \
		     <option>10x</option> \
		     </select><br> \
		     Scale:<br> \
		     <select id = "scaleselect" disabled> \
		     <option>MinMax</option> \
		     <option>98%</option> \
		     <option>90%</option> \
		     <option>1 StDev</option> \
			 <option>Log</option> \
			 <option>Box</option> \
		     </select><br> \
		     Color:<br> \
		     <select id = "colorselect" disabled> \
		     <option>Grey</option> \
		     <option>Rainbow</option> \
		     <option>Staircase</option> \
		     </select> \
		     </form>'
						+ '<td class = "tools" rowspan="3"> \
		     <canvas id = "analcanvas" width = "'
						+ this.analsize
						+ '"        height = "'
						+ this.analsize
						+ '"        style="border: solid 2px #ff0000;"> \
		     Your Browser does not support HTML5 - Canvas Elements - please upgrade. \
		     </canvas>');
		document.writeln(' \
				<tr><td class = "tools" id = "imagetoolselector" colspan="2"> \
				    <b>Analysis Tool:</b> \
				<tr><td class = "tools" id = "imagetoolsoutput1"> \
				    <td class = "tools" id = "imagetoolsoutput2">');
		document.writeln('</table>');
	}

	// WriteDisplay: writes the HTML code for the image display
	this.writedisplay = function() {
		document.writeln('<div id = "imagemsg"></div> \
			 <div id = "imagestat">Initializing</div> \
			 <div id = "imagediv" style = "width:100%; \
			      overflow:auto; border:solid 1px #CCC;"> \
			 <canvas id = "imagecanvas" width="200" height="200"> \
			 Your Browser does not support HTML5 - Canvas Elements \
			 - please upgrade. \
			 </canvas> \
			 </div> \
			 <div id = "imagelog"></div>');
	}

	// AddTool: add (and initialize a new image analysis tool)
	// Parameters:
	// - object: string containing the object name for the tool
	// - name: name for the tool that the user sees. If this paramter
	//         is an empty string, the tool is always active but not
	//         selectable to the user.
	// - parameters: additional parameters that are passed to the
	//               object constructor
	this.addtool = function(object, name) {
		// Get parameters - call constructor
		if ( arguments.length > 2) {
			params = arguments.slice(2, arguments.length);
			eval('tool = new ' + object + '(params)');
		} else {
			eval('tool = new ' + object + '()');
		}
		// Add tool to list
		this.toollist.push(tool);
		// Set tool name
		tool.name = name;
	}
	
	// Init: initializes the object and requests the data
	// This function needs to be called after writetools and
	// writedisplay such that the DOM elements can be accessed.
	// Addtool should also be called before init to make sure the
	// analysis tools can be initialized.
	this.init = function() {
		// **** Initialize Variables
		// get arguments
		dataurl = arguments[0];
		previewurl = arguments[1];
		// get canvas and set size
		this.imgcan = document.getElementById('imagecanvas');
		imgctx = this.imgcan.getContext('2d');
		// set imgraw to empty array
		this.imgraw = new Array(0);
		// **** Fill canvas images
		// load preview image
		if (previewurl) {
			img = new Image();
			img.onload = function() {
				this.imgcan = document.getElementById('imagecanvas');
				this.imgcan.width = img.width;
				this.imgcan.height = img.height;
				imgctx.drawImage(img, 0, 0);
			}
			img.src = previewurl;
		}
		// Fill zoom image with black
		this.analcan = document.getElementById('analcanvas');
		analctx = this.analcan.getContext('2d');
		analctx.fillstyle = 'rgb(0,0,0)';
		analctx.fillRect(0, 0, this.analsize, this.analsize);
		// **** Send the AJAX request for data
		// Set up the request object callback
		// ( Has to be done b/c onreadystatuschange has request as "this" )
		this.request.callback_object = this;
		this.request.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				// When it's done, call imageopen
				this.callback_object.imageopen();
			} else if (this.readyState !=3 || this.status !=200){
				// Else print the message unless its "Loading / OK"
				$('imagestat').html('Loading Image: State='+this.readyState+' Status='+this.status);
				imglogadd('Loading Image: State='+this.readyState+' Status='+this.status);
			}
		}
		// set the stamp to identify returning requests
		this.stamp = (new Date()).toString();
		document.getElementById('imagediv').stamp = this.stamp;
		// Send the request
		urlsplit = dataurl.split('?');
		this.request.open("POST", urlsplit[0], true);
		this.request.send(urlsplit[1]);
		// update message
		$('#imagestat').html('Loading Image Data');
		imglogadd('Loading Image Data');
		// **** Set tool selector text
		// get tool names, set first tool as toolnow
		toolnames = [];
		for( i=0; i<this.toollist.length; i++){
			nam = this.toollist[i].name;
			if( nam.length > 0 ) {
				toolnames.push(nam);
				if(this.toolnow == null){
					this.toolnow = this.toollist[i];
				}
			}
		}
		// make text
		if( toolnames.length > 1){
			toolselect =  '<b>Analysis Tools:</b>'
			toolselect += ' <select id="toolselect" disabled>';
			for( i=0; i<toolnames.length; i++){
				toolselect += '<option>'+toolnames[i]+'</option>';
			}
			toolselect += '</select>'
		} else if( toolnames.length > 0){
			toolselect = '<b>Analysis Tool: ' + toolnames[0] + '</b>';
		} else {
			toolselect = '';
		}
		// set text
		$('#imagetoolselector').html(toolselect);
	}

	// ImageOpen: Opens the image
	//     This makes new tool objects, initializes and updates them
	this.imageopen = function() {
		// check if stamp matches -> else ignore
		if (document.getElementById('imagediv').stamp != this.stamp) {
			return 0;
		}
		// update message
		$('#imagestat').html('Unpacking Image');
		imglogadd('Unpacking Image');
		// **** Import transfered data
		// get header and data
		headend = this.request.responseText.indexOf('data = ');
		headtxt = this.request.responseText.substring(0, headend);
		var datatxt = this.request.responseText.substring(headend + 7);
		// get header values
		ind = headtxt.indexOf('width = ') + 8;
		this.imgwidth = parseInt(headtxt.substring(ind));
		ind = headtxt.indexOf('height = ') + 9;
		this.imgheight = parseInt(headtxt.substring(ind));
		ind = headtxt.indexOf('bzero = ') + 8;
		var bzero = parseFloat(headtxt.substring(ind));
		ind = headtxt.indexOf('bscale = ') + 9;
		var bscale = parseFloat(headtxt.substring(ind));
		ind = headtxt.indexOf('message = ') + 10;
		len = headtxt.substring(ind).indexOf('\n');
		message = headtxt.substr(ind, len);
		// Look for coordinate values (coords)
		if( headtxt.indexOf('coordx0 = ') > -1 ){
			this.coords=true;
			ind = headtxt.indexOf('coordx0 = ') + 10;
			this.coordx0 = parseFloat(headtxt.substring(ind));
			ind = headtxt.indexOf('coordy0 = ') + 10;
			this.coordy0 = parseFloat(headtxt.substring(ind));
			ind = headtxt.indexOf('coordrowx = ') + 12;
			this.coordrowx = parseFloat(headtxt.substring(ind));
			ind = headtxt.indexOf('coordrowy = ') + 12;
			this.coordrowy = parseFloat(headtxt.substring(ind));
			ind = headtxt.indexOf('coordcolx = ') + 12;
			this.coordcolx = parseFloat(headtxt.substring(ind));
			ind = headtxt.indexOf('coordcoly = ') + 12;
			this.coordcoly = parseFloat(headtxt.substring(ind));
			ind = headtxt.indexOf('coordlblx = ') + 12;
			len = headtxt.substring(ind).indexOf('\n');
			this.coordlblx = headtxt.substr(ind, len);
			ind = headtxt.indexOf('coordlbly = ') + 12;
			len = headtxt.substring(ind).indexOf('\n');
			this.coordlbly = headtxt.substr(ind, len);
		}
		// Set message
		document.getElementById('imagemsg').innerHTML = message;
		// get data values
		var imgn = this.imgwidth * this.imgheight;
		this.imgraw = new Array(imgn);
		this.nnans = 0;
		imglogadd('Unpack Loop:');
		var i = imgn;
		var val = 0;
		while ( i > 0 ) {
			i--;
			val = parseInt(datatxt.substr(4 * i, 4), 16);
			if(val<65535){
				this.imgraw[i] = bzero + bscale * val;
			} else {
				this.imgraw[i] = NaN;
				this.nnans += 1;
			}
		}
		imglogadd('Done Unpack - Copying');
		// print result (for testing)
		//document.getElementById('imagestat').innerHTML = 'w=' + this.imgwidth +
		// ' h=' + this.imgheight + ' b0=' + bzero + ' bs=' + bscale +
		// ' nnans=' + this.nnans;
		// get sorted data array - nan are at the top
		this.imgrawsort = this.imgraw.slice();
		imglogadd('Done Copy - Sorting');
		this.imgrawsort.sort(function callback(a, b) {
			if (isNaN(a)) { return 1;
			} else if (isNaN(b)) { return -1;
			} else { return a - b; }
		});
		imglogadd('Done Sort - Setting up');
		// Initialize tool objects
		for (i=0; i<this.toollist.length; i++){
			this.toollist[i].init(this);
		}
		// **** Set canvas and selection callbacks and values
		// Set object callback for canvas mousemove, mousedown and mouseup
		this.imgcan.callback_object = this;
		this.imgcan.onmousemove = function(event) {
			this.callback_object.mousemove(event);
		}
		this.imgcan.onmousedown = function(event) {
			this.callback_object.mousedown(event);
		}
		this.imgcan.onmouseup = function(event) {
			this.callback_object.mouseup(event);
		}
		this.imgcan.onmouseout = function(event) {
			this.callback_object.mouseup(event);
		}
		// get options from existing cookies
		this.getOptions();
		// Set zoom size (make sure diagonal is at least 300 pixels long)
		this.imgzoom = 1.0;
		diag = Math.sqrt(this.imgwidth * this.imgwidth + this.imgheight
				* this.imgheight);
		while (this.imgzoom * diag < 300) {
			this.imgzoom += 1.0;
		}
		while (this.imgzoom * diag > 1800) {
			this.imgzoom /= 2.0;
		}
		// Set zoom selection dropdown
		zoomsel = $('#zoomselect')[0];
		zoomsel.disabled = false;
		if (this.imgzoom != 1.0) {
			// If zoom > 1 -> add selected "Auto" option to select
			option = new Option('Auto', 'Auto', true, true);
			zoomsel.add(option, null);
		} else {
			// If zoom == 1 -> select 1x option
			found = -1;
			for (i = 0; i < zoomsel.length; i++) {
				if (zoomsel.options[i].text == '1x')
					found = i;
			}
			if (found > -1)
				zoomsel.selectedIndex = found;
		}
		// Set zoomselect onChange function
		zoomsel.callback_object = this;
		zoomsel.onchange = function() {
			this.callback_object.zoomhandler();
		}
		// Set scaleselect index and onchange function
		scalesel = $('#scaleselect')[0];
		scalesel.disabled = false;
		found = 0;
		for (i = 0; i < scalesel.length; i++) {
			if (scalesel.options[i].text == this.imgscale)
				found = i;
		}
		scalesel.selectedIndex = found;
		scalesel.callback_object = this;
		scalesel.onchange = function() {
			this.callback_object.scalehandler();
		}
		// Set colorselect index and onchange function
		colorsel = $('#colorselect')[0];
		colorsel.disabled = false;
		found = 0;
		for (i = 0; i < colorsel.length; i++) {
			if (colorsel.options[i].text.toUpperCase() == this.imgcolor)
				found = i;
		}
		colorsel.selectedIndex = found;
		colorsel.callback_object = this;
		colorsel.onchange = function() {
			this.callback_object.colorhandler();
		}
		imglogadd('Done Setting Up - Updating Tools');
		// **** Update Tools
		// Set toolselect active and onchange function (only if toolselect exists)
		if($('#toolselect').length){
			toolsel = $('#toolselect')[0];
			toolsel.disabled = false;
			toolsel.callback_object = this;
			toolsel.onchange = function() {
				this.callback_object.toolselecthandler();
			}
		}
		// activate toolnow (it's set by this.init() )
		if(this.toolnow != null){
			this.toolnow.active = true;
		}
		// get and set image tools
		for (i = 0; i < this.toollist.length; i += 1) {
			this.toollist[i].update();
		}
		imglogadd('Done Update Tools - Drawing');
		// **** Display and message
		// Display Image
		this.imagedraw();
		// Done message
		$('#imagestat').append(' - Done');
		imglogadd('Done');
	}

	// ImageDraw: Draw the image using current scale and zoom settings
	this.imagedraw = function() {
		// **** Get image geometry constraints
		// get display size (limit display size to 5000 x 5000)
		var dispwidth = Math.round(this.imgwidth * this.imgzoom);
		if (dispwidth > 5000) {
			dispwidth = 5000;
		}
		var dispheight = Math.round(this.imgheight * this.imgzoom);
		if (dispheight > 5000) {
			dispheight = 5000;
		}
		// set imagediv height
		if (dispheight > 600) {
			document.getElementById('imagediv').style.height = '600px';
		} else {
			document.getElementById('imagediv').style.height = 'auto';
		}
		// **** Draw the image
		// get canvas context
		ctx = this.imgcan.getContext('2d');
		// make canvas image
		var canimg = ctx.createImageData(dispwidth, dispheight);
		// recalculate imagescaled values if necessary
		var imgx = 0, imgy = 0, i = 0, j = 0, k = 0;
		var imgwidth = this.imgwidth;
		var imgheight = this.imgheight;
		var imgmin = this.imgmin;
		var imgmax = this.imgmax;
		var imgraw = this.imgraw;
		var imgdiff = 1.0;
		if (this.rescale > 0) {
			imglogadd('Start Rescale Loop ' + imgmin + ' ' + imgmax);
			this.rescale = 0;
			if (this.imgscale == 'Log') {
				imgdiff = Math.log10(imgmax / imgmin);
				imglogadd(' - Logging')
			} else {
				imgdiff = imgmax - imgmin;
			}
			for (imgx = 0; imgx < imgwidth; imgx += 1) {
				for (imgy = 0; imgy < imgheight; imgy += 1) {
					i = imgy * imgwidth + imgx;
					if (this.imgscale == 'Log') {
						(this.imgscaled)[i] = Math.round( Math.log10( imgraw[i] / imgmin)
								* 255.0 / imgdiff );
					} else {
						this.imgscaled[i] = Math.round(255.0 * (imgraw[i] - imgmin)
								/ imgdiff);
					}
				}
			}
		}
		// fill canvas image
		imglogadd('Start Drawing Loop');
		var imgzoom = this.imgzoom;
		var carr = this.getRGB(0);
		for (var y = 0; y < dispheight; y += 1) {
			for (var x = 0; x < dispwidth; x += 1) {
				imgx = Math.floor(x / imgzoom);
				imgy = Math.floor(y / imgzoom);
				i = imgy * imgwidth + imgx; // index of raw image pixel
				j = (dispheight - 1 - y) * dispwidth + x;
				carr = this.getRGB(this.imgscaled[i]);
				for (k = 0; k < 4; k++) {
					(canimg.data)[4 * j + k] = carr[k];
				}
			}
		}
		imglogadd('Stop Drawing Loop');
		// set canvas size
		this.imgcan.width = dispwidth;
		this.imgcan.height = dispheight;
		// draw image
		ctx.putImageData(canimg, 0, 0);
		// **** Draw the analysis tools
		for (i = 0; i < this.toollist.length; i += 1) {
			this.toollist[i].draw();
		}
	}

	// Mousemove: Event handler to respond to mouse events
	this.mousemove = function(event) {
		// **** Update location / value display
		// Get x and y and display them
		scrollx = $('#imagediv').scrollLeft();
		scrolly = $('#imagediv').scrollTop();
		imgx = event.pageX - this.imgcan.offsetLeft + scrollx;
		imgy = event.pageY - this.imgcan.offsetTop + scrolly - 1;
		datax = Math.floor(imgx / this.imgzoom);
		datay = this.imgheight - 1 - Math.floor(imgy / this.imgzoom);
		i = datay * this.imgwidth + datax;
		val = this.imgraw[i];
		val = this.valueformat(val);
		// Message: X/Y row/column
		msg = 'Mouse&nbsp;X&nbsp;/&nbsp;Y:<br>&nbsp;&nbsp;';
		msg += datax + ' / ' + datay;
		// Message: Coordinates
		if(this.coords){
			// get mouserow/col
			mcol = imgx / this.imgzoom - 0.5;
		    mrow = this.imgheight - 1 - ( imgy / this.imgzoom - 0.5 );
			// get coordx/y
		    coordx = this.coordx0 + mcol * this.coordcolx + mrow * this.coordrowx;
		    coordy = this.coordy0 + mcol * this.coordcoly + mrow * this.coordrowy;		    
			// add x to message (check for RA)
		    if(this.coordlblx.toUpperCase().includes('RA')){
		        hr = Math.floor(coordx/15);
		        mn = Math.floor(4*coordx-60*hr);
		        sc = 240*coordx-3600*hr-60*mn;
		        if(mn<10.0){
		        	mn = '0'+mn.toFixed(0);
		        } else {
		        	mn = mn.toFixed(0);
		        }
		        if(sc<10.0){
		        	sc = '0'+sc.toFixed(2);
		        } else {
		        	sc = sc.toFixed(2);
		        }
		        msg += '<br>' + this.coordlblx + ' ' + hr.toFixed(0) + 'h' +
		               mn + 'm' + sc + 's'
 		    } else {
 		    	msg += '<br>' + this.coordlblx + ': ' + coordx.toFixed(5);
 		    }
		    // add y to message (checl for DEC)
		    if(this.coordlbly.toUpperCase().includes('DEC')){
		    	if(coordy<0){
		    		sn='-';
		    		coordy = -coordy;
		    	} else {
		    		sn='';
		    	}
		        dg = Math.floor(coordy);
		        mn = Math.floor(60*coordy-60*dg);
		        sc = 3600*coordy-3600*dg-60*mn;
		        if(mn<10.0){
		        	mn = '0'+mn.toFixed(0);
		        } else {
		        	mn = mn.toFixed(0);
		        }
		        if(sc<10.0){
		        	sc = '0'+sc.toFixed(1);
		        } else {
		        	sc = sc.toFixed(1);
		        }
		        msg += '<br>' + this.coordlbly + ' ' + sn + dg.toFixed(0) + '&deg;' +
		               mn + '\'' + sc + '"'
		    } else {
		    	msg += '<br>' + this.coordlbly + ': ' + coordy.toFixed(5);
		    }
		}
		// Message: Value and print
		msg += '<br>Value:<br>&nbsp;&nbsp;' + val;
		document.getElementById('imageinfo').innerHTML = msg;
		// **** Update Mouse analysis window
		// make image
		ctx = this.analcan.getContext('2d');
		canimg = ctx.createImageData(this.analsize, this.analsize);
		// copy and scale data
		imgdiff = this.imgmax - this.imgmin;
		sqrrad = Math.ceil(3.0 * this.imgzoom); // "radius" of square
		carr = new Array(4)
		// loop over analysis image pixels
		for (ay = 0; ay < this.analsize; ay++) {
			for (ax = 0; ax < this.analsize; ax++) {
				// get px and py coordinates of real pixel
				px = datax
						+ Math.round((ax - this.analsize / 2)
								/ (6 * this.imgzoom));
				py = datay
						+ Math.round((this.analsize / 2 - ay)
								/ (6 * this.imgzoom));
				// get value (255.0 if it's outside the image)
				if (px < 0 || py < 0 || px >= this.imgwidth
						|| py >= this.imgheight) {
					cval = 255.0;
					outside = true;
				} else {
					i = (py * this.imgwidth) + px;
					cval = this.imgscaled[i]; 
					outside = false;
				}
				// get color (but make a red frame around center pixel
				dx = Math.round(Math.abs(ax - this.analsize / 2));
				dy = Math.round(Math.abs(ay - this.analsize / 2));
				if ((dx == sqrrad && dy <= sqrrad)
						|| (dy == sqrrad && dx <= sqrrad)) {
					carr = [ 255, 0, 0, 255 ];
				} else if (outside) {
					carr = [ 255, 255, 255, 255 ];
				} else {
					carr = this.getRGB(cval);
				}
				// set pixel value
				i = ay * 160 + ax;
				for (j = 0; j < 4; j++) {
					(canimg.data)[4 * i + j] = carr[j];
				}
			}
		}
		// copy image to display
		ctx.clearRect(0, 0, this.analsize, this.analsize);
		ctx.beginPath();
		ctx.putImageData(canimg, 0, 0);
		// Move tool if it's being moved
		if( this.toolmove != null){
			this.toolmove.move(imgx,imgy);
			this.imagedraw();
		}
	}
	
	// Mousedown: Event handler to press mouse button
	this.mousedown = function(event) {
		// Get mouse coordinates
		scrollx = $('#imagediv').scrollLeft();
		scrolly = $('#imagediv').scrollTop();
		imgx = event.pageX - this.imgcan.offsetLeft + scrollx;
		imgy = event.pageY - this.imgcan.offsetTop + scrolly - 1;
		// Check connection to tool object
		this.toolmove = null;
		for( i=0; i<this.toollist.length && this.toolmove == null; i++){
			if( this.toollist[i].pickup(imgx, imgy)) {
				this.toolmove = this.toollist[i];
			}
		}
	}
	
	// Mouseup: Event handler to release mouse button
	//          This function is also used for onmouseout events
	this.mouseup = function(event) {
		// If a tool is being moved, drop it
		if( this.toolmove != null) {
			this.toolmove.drop();
			this.toolmove = null;
			this.imagedraw();
		}
	}

	// Zoomhandler: Responds to zoom selection events
	this.zoomhandler = function() {
		// Select determine new zoom value
		selectobj = document.getElementById('zoomselect');
		optlist = selectobj.options;
		switch (optlist[selectobj.selectedIndex].text) {
		case '1/10':
			this.imgzoom = 0.1;
			break;
		case '1/3':
			this.imgzoom = 0.33333;
			break;
		case '1x':
			this.imgzoom = 1.0;
			break;
		case '3x':
			this.imgzoom = 3.0;
			break;
		case '10x':
			this.imgzoom = 10.0;
			break;
		}
		// Clear Auto option if present
		found = -1;
		for (i = 0; i < selectobj.length; i++) {
			if (optlist[i].text == 'Auto')
				found = i;
		}
		if (found > -1)
			selectobj.remove(found);
		// Update tools
		for (i = 0; i < this.toollist.length; i += 1) {
			this.toollist[i].update();
		}
		// Draw image
		this.imagedraw();
	}

	// Scalehandler: Responds to scale selection events
	this.scalehandler = function() {
		// Select determine new scale value
		selectobj = document.getElementById('scaleselect');
		optlist = selectobj.options;
		// Update the value
		this.updateOptions('', optlist[selectobj.selectedIndex].text, '');
		// Draw image
		this.imagedraw();
	}

	// Colorhandler: Responds to color selection events
	this.colorhandler = function() {
		colorobj = document.getElementById('colorselect');
		optlist = colorobj.options;
		this.updateOptions('', '', optlist[colorobj.selectedIndex].text
				.toUpperCase());
		this.imagedraw();
	}

	// Toolselecthandler: Response to tool select events
	this.toolselecthandler = function() {
		// Get new tool name
		toolselobj = document.getElementById('toolselect');
		optlist = toolselobj.options;
		toolname = optlist[toolselobj.selectedIndex].text;
		// Look for new tool
		found = -1;
		for(i=0;i<this.toollist.length && found < 0;i++){
			if(this.toollist[i].name == toolname){
				found = i;
			}
		}
		imglogadd('New Tool: '+toolname+' found='+found)
		// Deactivate old tool / Activate new tool
		if(found>-1){
			this.toolnow.active = false;
			this.toolnow = this.toollist[found];
			this.toolnow.active = true;
		}
		// Update tools
		for (i = 0; i < this.toollist.length; i += 1) {
			this.toollist[i].update();
		}
		// Draw image
		this.imagedraw();
	}
	
	// updateOptions: updates the options cookie and recalculates the
	// values for the options if necessary.
	this.updateOptions = function(newzoom, newscale, newcolor) {
		// Check new zoom and set values
		// Check new scale and set values
		if ((newscale.length > 0) && (newscale != self.imgscale)) {
			// Update value
			this.imgscale = newscale;
			// Calculate new imgmin and imgmax
			pixeln = this.imgwidth * this.imgheight - this.nnans;
			switch (this.imgscale) {
			case '98%':
				this.imgmin = this.imgrawsort[Math.round(pixeln / 100)];
				this.imgmax = this.imgrawsort[Math.round(99 * pixeln / 100) - 1];
				this.rescale = 1;
				break;
			case '90%':
				this.imgmin = this.imgrawsort[Math.round(pixeln / 20)];
				this.imgmax = this.imgrawsort[Math.round(19 * pixeln / 20) - 1];
				this.rescale = 1;
				break;
			case '5 StDev':
				sum = 0.0;
				sum2 = 0.0;
				for (i = 0; i < pixeln; i++) {
					sum += this.imgrawsort[i];
					sum2 += this.imgrawsort[i] * this.imgrawsort[i];
				}
				sum /= pixeln;
				sum2 /= pixeln;
				std = Math.sqrt(sum2 + sum * sum);
				this.imgmin = sum - 2.5 * std;
				this.imgmax = sum + 2.5 * std;
				this.rescale = 1;
				break;
			case 'Log':
				// scale log(min)..log(max) or log(max/1e6)..log(max)
				this.imgmax = this.imgrawsort[pixeln-1];
				if (this.imgrawsort[0]<0.0 ||
					this.imgmax/this.imgrawsort[0] > 1e6 ){
					this.imgmin=this.imgmax/1e6;
				} else {
					this.imgmin=this.imgrawsort[0];
				}
				this.rescale = 1;
				break;
			case 'Box':
				this.imgmin = this.toolnow.imgmin;
				this.imgmax = this.toolnow.imgmax;
				this.rescale = 1;
				break;
			default:
				this.imgscale = 'MinMax';
				this.imgmin = this.imgrawsort[0];
				this.imgmax = this.imgrawsort[pixeln - 1];
				this.rescale = 1;
				break;
			}
			// Set the cookie
			$.cookie('imageanalscale', escape(this.imgscale));
		}
		// Check new color and set values
		if ((newcolor.length > 0) && (newcolor != self.imgcolor)) {
			// Update value
			this.imgcolor = newcolor;
			// Set the cookie
			$.cookie('imageanalcolor', escape(this.imgcolor))
		}
	}

	// getOptions: reads the options cookie
	this.getOptions = function() {
		// Read the cookie
		var cookies = document.cookie;
		// Check new zoom
		// Check new scale
		newscale = unescape($.cookie('imageanalscale'));
		if (newscale == null) {
			newscale = 'MinMax';
		}
		// Check new color
		newcolor = unescape($.cookie('imageanalcolor'));
		if (newcolor == null) {
			newcolor = 'GREY';
		}
		// Call updateOptions
		this.updateOptions('', newscale, newcolor);
	}

	// getRGB: returns an RGB array when given an color value in the
	// 0..255 range
	this.getRGB = function(cval) {
		// Make output color array
		var carr = new Array(4)
		carr[3] = 255;
		// Check for Nan -> return black
		if (isNaN(cval)) {
		    carr[0] = 0;
			carr[1] = 0;
			carr[2] = 0;
			return carr;
		}
		// Check range
		if (cval < 0) {
			cval = 0;
		} else if (cval > 255) {
			cval = 255;
		}
		// Switch through color values
		switch (this.imgcolor) {
		case 'GREY':
			// Grey - just use the default at the bottom
			break;
		case 'RAINBOW_OLD':
			// The color scale is:
			//     Red / Yellow / Green / Cyan / Blue / Yiolet
			//     0 51 102 153 204 255
			var ind = Math.round(cval);
			if (ind < 51) {
				carr[0] = 255;
				carr[1] = 5 * ind;
				carr[2] = 0;
			} else if (ind < 102) {
				ind -= 51;
				carr[0] = 255 - 5 * ind;
				carr[1] = 255;
				carr[2] = 0;
			} else if (ind < 153) {
				ind -= 102;
				carr[0] = 0;
				carr[1] = 255;
				carr[2] = 5 * ind;
			} else if (ind < 204) {
				ind -= 153;
				carr[0] = 0;
				carr[1] = 255 - 5 * ind;
				carr[2] = 255;
			} else {
				ind -= 204;
				carr[0] = 5 * ind;
				carr[1] = 0;
				carr[2] = 255;
			}
			return carr;
		case 'RAINBOW':
			// The color scale is:
			//     Blue / Cyan / Green / Yellow / Red
			//     0 63 127 191 255
			var ind = Math.round(cval);
			if (ind < 63) {
				carr[0] = 0;
				carr[1] = 4 * ind;
				carr[2] = 255 - 64 + ind;
			} else if (ind < 127) {
				ind -= 63;
				carr[0] = 0;
				carr[1] = 255 - ind;
				carr[2] = 255 - 4 * ind;
			} else if (ind < 191) {
				ind -= 127;
				carr[0] = 4 * ind;
				carr[1] = 255 - 64 + ind;
				carr[2] = 0;
			} else {
				ind -= 191
				carr[0] = 255 - ind;
				carr[1] = 255 - 4 * ind;
				carr[2] = 0;
			}
			return carr;
		case 'STAIRCASE':
			// // Staircase is a series of 15 colors.
			// 0-4 are 0/0/51 to 100/100/255
			// 5-9 are 0/51/0 to 100/255/100
			// 10-14 are 51/0/0 to 255/100/100
			// find index
			var ind = Math.round(cval / 17);
			if (ind < 5) {
				carr[0] = 25 * ind;
				carr[1] = 25 * ind;
				carr[2] = 51 + 51 * ind;
			} else if (ind > 9) {
				ind = ind - 10;
				carr[0] = 51 + 51 * ind;
				carr[1] = 25 * ind;
				carr[2] = 25 * ind;
			} else {
				ind = ind - 5;
				carr[0] = 25 * ind;
				carr[1] = 51 + 51 * ind;
				carr[2] = 25 * ind;
			}
			return carr;
		}
		carr[0] = cval;
		carr[1] = cval;
		carr[2] = cval;
		return carr;
	}

	// ValueFormat: format a value to a string
	this.valueformat = function(value) {
		if (Math.abs(value) > 1e5 || Math.abs(value) < 1e-2
				&& Math.abs(value) > 0.0) {
			return value.toExponential(4);
		} else {
			return value.toPrecision(5);
		}
	}
};

/**
 * ****** IMAGETOOLSTATS OBJECT Object that creates a movable statistics box and
 * prints the image statistics for the values in the box. If the box is not
 * used, the image statistics is calculated for the entire image.
 */

// **** Constructor: creates the object
function imagetoolstatsobject() {
	// **** Object Variables
	this.imganalobj = null; // The imageanalysis object
	this.name = ''; // name that the tool has for the user
	this.active = false; // Flag indicating if the tool is used
	this.shown = true; // Flag indicating if the box is shown
	this.color = 'blue'; // Color of the frame
	this.datax0 = 0;  // DATA coordinates: coordinates of the box in the
	this.datax1 = 10; // unscaled data frame. Coordinates
	this.datay0 = 0;  // are measured such that BOTTOM left
	this.datay1 = 10; // is (0/0)
	this.imgx0 = 0;  // IMG coordinates: coordinates of the box in the
	this.imgx1 = 10; // scaled data frame. Coordinates are
	this.imgy0 = 0;  // measured such that TOP left is (0/0)
	this.imgy1 = 10;
	// About Coordinates: usually, dataxy and imgxy correspond to each other
	// except when the box is being moved. Then dataxy are
	// not changed, while imgxy moves with the box.
	this.moving = 0;  // Flag indicating which box sides (UDLR) are being
                      // moved. If moving==0, the box is not being moved.
	                  // L~1 R~2 U~4 D~8 so for moving==15 the entire box
                      // is being moved.
	this.mousex0 = 0; // IMG coordinates of the mouse position at the start
	this.mousey0 = 0; //     of the current move.
	this.pickupx0 = 0;  // IMG coordinates at pickup location
	this.pickupx1 = 10; //   while moving, corresponds to DATA
	this.pickupy0 = 0;  //   coordinates
	this.pickupy1 = 10;
	this.imgmin = 0;  // Holds min/max of the pixels in the box
	this.imgmax = 1;

	// **** Object Functions

	// INIT: Initializes the analysis object (this is NOT the constructor)
	this.init = function(imganalobj) {
		// Assign variables
		this.imganalobj = imganalobj;
		// Initialize box size
		this.datax0 = Math.round(this.imganalobj.imgwidth / 10);
		this.datax1 = this.imganalobj.imgwidth - this.datax0;
		this.datay0 = Math.round(this.imganalobj.imgheight / 10);
		this.datay1 = this.imganalobj.imgheight - this.datay0;
	}

	// DRAW: Draws the box with the current color at the current location.
	this.draw = function() {
		if (this.shown & this.active) {
			// Get the canvas
			ctx = this.imganalobj.imgcan.getContext('2d');
			// Draw the square
			ctx.strokeStyle = this.color;
			ctx.lineWidth = 2;
			ctx.strokeRect(this.imgx0, this.imgy0, this.imgx1 - this.imgx0,
					this.imgy1 - this.imgy0);
		}
	}

	// UPDATE: Updates the tool: Recalculates the imgxy coordinates from dataxy.
	// Recalculates the statistics and prints it.
	this.update = function() {
		// If it's not active -> return
		if ( ! this.active ){
			return;
		}
		// Get raw and sorted data for statistics
		imglogadd('Analstats: Going');
		if (this.shown) { // If box is shown -> get contents
			// Calculate box shape from imganalobj
			datady = this.imganalobj.imgheight;
			zoom = this.imganalobj.imgzoom;
			this.imgx0 = this.datax0 * zoom;
			this.imgx1 = this.datax1 * zoom;
			this.imgy0 = (datady-this.datay1) * zoom;
			this.imgy1 = (datady-this.datay0) * zoom;
			// Get data and sort
			var boxdata = new Array();
			for (yi = this.datay0; yi < this.datay1; yi += 1) {
				yoff = yi * this.imganalobj.imgwidth;
				x0 = yoff + this.datax0;
				x1 = yoff + this.datax1;
				adddata = this.imganalobj.imgraw.slice(x0, x1);
				boxdata.push.apply(boxdata,adddata); // Append to array
			}
			boxdata=boxdata.filter(function(x) { return !isNaN(x);});
			imglogadd('Analstats: Got data');
			boxdata.sort(function callback(a, b) {
				return a - b;
			});
		} else {
			// Get sorted data from imganalobj
			var npix = this.imganalobj.imgwidth * this.imganalobj.imgheight - this.imganalobj.nnans;
			var boxdata = this.imganalobj.imgrawsort.slice(0,npix);
		}
		imglogadd('Analstats: Got Sorted data');
		// Calculate statistics
		imgn = boxdata.length;
		this.imgmin = this.imganalobj.valueformat(boxdata[0]);
		this.imgmax = this.imganalobj.valueformat(boxdata[imgn - 1]);
		imgmed = this.imganalobj.valueformat(boxdata[Math.round(imgn / 2)]);
		var sum = 0.0;
		var sum2 = 0.0;
		// put min and max in there
		// also get boxval = boxdata[i] (local var) then use it only
		var i = imgn;
		var val = 0;
		while ( i > 0 ) {
			i--;
			val = boxdata[i];
			sum += val;
			sum2 += val * val;
		}
		imgavg = sum / imgn;
		imgstd = Math.sqrt(sum2 / imgn - imgavg * imgavg);
		imgavg = this.imganalobj.valueformat(imgavg);
		imgstd = this.imganalobj.valueformat(imgstd);
		imglogadd('Analstats: Got stats');
		// Display statistics
		$('#imagetoolsoutput1')
				.html('<form> \
					   <input type="checkbox" id="statsbox">\
					   <span id="statscolor">&nbsp;Box&nbsp;</span><br />Min: '
					  + this.imgmin + '<br />Max: ' + this.imgmax);
		$('#imagetoolsoutput2').html(
				'Median: ' + imgmed + '<br />Average: ' + imgavg
						+ '<br />StdDev: ' + imgstd);
		// Set [./]box callback functions
		statsbox = $('#statsbox')[0];
		statsbox.callback_object = this;
		statsbox.onchange = function() {
			this.callback_object.checkhandler();
		}
		statsbox.checked = this.shown;
		if(this.shown){
			textcol = {'red':'black','lime':'black','blue':'white',
					   'black':'white'}[this.color];
			$('#statscolor').css('background',this.color);
			$('#statscolor').css('color',textcol);
			statscolor = $('#statscolor')[0]
			statscolor.callback_object = this;
			statscolor.onclick = function() {
				this.callback_object.boxcolor();
			}
		}
		// If ImageAnalysisObject.imgscale=='Box' -> call updateOptions
		if(this.imganalobj.imgscale=='Box'){
			this.imganalobj.updateOptions('','Box','');
		}
	}

	// CHECKHANDLER: Handles check events from the checkbox. Toogles the shown
	// flag, updates the widget and redraws the imageanalysisobject
	this.checkhandler = function() {
		// Toogle shown status
		this.shown = !this.shown;
		// Update the data
		this.update();
		// Redraw the image
		this.imganalobj.imagedraw();
	}
	
	// BOXCOLOR: Handles clicks on the box color switcher.
	this.boxcolor = function() {
		// Set next color
		this.color={'red':'lime','lime':'blue','blue':'black',
				    'black':'red'}[this.color];
		// Update the text color
		textcol = {'red':'black','lime':'black','blue':'white',
				   'black':'white'}[this.color];
		$('#statscolor').css('background',this.color);
		$('#statscolor').css('color',textcol);
		this.imganalobj.imagedraw();
	}
	
	// PICKUP: Checks if the image mouse location (x/y) is correct to pick up
	//         the box. If so true is returned and the box is set to moving.
	this.pickup = function(mousex,mousey){
		// Ignore if not shown or inactive
		if( ! this.shown || ! this.active) {
			return false;
		// Check if move is in progress: finish move
		} else if( this.moving > 0){
			this.dropoff();
			return false;
		// Check if mouse is inside the box
		} else if( mousex > this.imgx0-3 && mousex < this.imgx1+3 &&
		           mousey > this.imgy0-3 && mousey < this.imgy1+3 ){
			// Initialize move
			this.pickupx0 = this.imgx0;
			this.pickupx1 = this.imgx1;
			this.pickupy0 = this.imgy0;
			this.pickupy1 = this.imgy1;
			this.mousex0 = mousex;
			this.mousey0 = mousey;
			// Check movement of edges
			if( mousex < this.imgx0+3) { this.moving = this.moving + 1; }
			if( mousex > this.imgx1-3) { this.moving = this.moving + 2; }
			if( mousey < this.imgy0+3) { this.moving = this.moving + 4; }
			if( mousey > this.imgy1-3) { this.moving = this.moving + 8; }
			// Check movement of full box
			if( !this.moving ){
				this.moving = 15;
			}
			// Return
			return true;
		} else {
			return false;
		}
	}
	
	// MOVE: Moves the box to the new coordinates, updates imgx/y0/1
	//       datax/y0/1 and movex/y0 are used to calculate the move
	this.move = function(mousex,mousey){
		// calculate maximal valid indices
		zoom = this.imganalobj.imgzoom;
		imgdx = Math.round(this.imganalobj.imgwidth * zoom) - 1;
		imgdy = Math.round(this.imganalobj.imgheight * zoom) - 1;
		// calculate offsets
		mousedx = mousex-this.mousex0;
		mousedy = mousey-this.mousey0;
		// calculate new coordinates
		if(this.moving & 1) { this.imgx0 = this.pickupx0+mousedx; }
		if(this.moving & 2) { this.imgx1 = this.pickupx1+mousedx; }
		if(this.moving & 4) { this.imgy0 = this.pickupy0+mousedy; }
		if(this.moving & 8) { this.imgy1 = this.pickupy1+mousedy; }
		// check new coordinates
		if( mousedx < 0 ){
			// Check left
			if( this.imgx0 < 0 ) { this.imgx0 = 0; }
			if( this.imgx1 < 5 ) { this.imgx1 = 5; }
			if( this.imgx1 < this.imgx0+5) { this.imgx1 = this.imgx0+5; }
		} else {
			// Check right
			if( this.imgx1 > imgdx ) { this.imgx1 = imgdx; }
			if( this.imgx0 > imgdx-5) { this.imgx0 = imgdx-5; }
			if( this.imgx0 > this.imgx1-5) { this.imgx0 = this.imgx1-5; }
		}
		if( mousedy < 0){
			// Check top
			if( this.imgy0 < 0 ) { this.imgy0 = 0; }
			if( this.imgy1 < 5 ) { this.imgy1 = 5; }
			if( this.imgy1 < this.imgy0+5) { this.imgy1 = this.imgy0+5; }
		} else {
			// Check bottom
			if( this.imgy1 > imgdy ) { this.imgy1 = imgdy; }
			if( this.imgy0 > imgdy-5) { this.imgy0 = imgdy-5; }
			if( this.imgy0 > this.imgy1-5) { this.imgy0 = this.imgy1-5; }			
		}
	}
	
	// DROP: Finishes the move by updating imgx/y0/1 to the current
	//          datax/y0/1 coordinates. The box is set to non-moving.
	// ### make sure box stays at least 2x2
	this.drop = function(){
		if( this.moving ){
			// Calculate new data coordinates
			datady = this.imganalobj.imgheight;
			zoom = this.imganalobj.imgzoom;
			this.datax0 = Math.round(this.imgx0/zoom);
			this.datax1 = Math.round(this.imgx1/zoom);
			this.datay0 = datady - Math.round(this.imgy1/zoom);
			this.datay1 = datady - Math.round(this.imgy0/zoom);
			// Clear moving
			this.moving = 0;
			// Update
			this.update();
		}
		
	}
};

/**
 * ****** IMAGETOOLPSF OBJECT Object that creates a movable box, fits a PSF
 * to the data in the box and prints the fitted parameters.
 */

// **** Constructor: creates the object
function imagetoolpsfobject() {
	// **** Object Variables
	this.imganalobj = null; // The imageanalysis object
	this.name = ''; // name that the tool has for the user
	this.active = false; // Flag indicating if the tool is used
	this.shown = true; // Flag indicating if the box is shown
	this.color = 'red'; // Color of the frame
	this.boxmaxsize = 50; // Maximal size of the box in data units
	this.datax0 = 0;  // DATA coordinates: coordinates of the box in the
	this.datax1 = 10; // unscaled data frame. Coordinates
	this.datay0 = 0;  // are measured such that BOTTOM left
	this.datay1 = 10; // is (0/0)
	this.imgx0 = 0;  // IMG coordinates: coordinates of the box in the
	this.imgx1 = 10; // scaled data frame. Coordinates are
	this.imgy0 = 0;  // measured such that TOP left is (0/0)
	this.imgy1 = 10;
	// About Coordinates: usually, dataxy and imgxy correspond to each other
	// except when the box is being moved. Then dataxy are
	// not changed, while imgxy moves with the box.
	this.moving = 0;  // Flag indicating which box sides (UDLR) are being
                      // moved. If moving==0, the box is not being moved.
	                  // L~1 R~2 U~4 D~8 so for moving==15 the entire box
	                  // is being moved.
	this.mousex0 = 0; // IMG coordinates of the mouse position at the start
	this.mousey0 = 0; //     of the current move.
	this.pickupx0 = 0;  // IMG coordinates at pickup location
	this.pickupx1 = 10; //   while moving, corresponds to DATA
	this.pickupy0 = 0;  //   coordinates
	this.pickupy1 = 10;
	this.imgmin = 0;  // Holds min/max of the pixels in the box
	this.imgmax = 1;

	// **** Object Functions

	// INIT: Initializes the analysis object (this is NOT the constructor)
	this.init = function(imganalobj) {
		// Assign variables
		this.imganalobj = imganalobj;
		// Initialize box size
		this.datax0 = Math.round(this.imganalobj.imgwidth / 10);
		this.datax1 = this.imganalobj.imgwidth - this.datax0;
		this.datay0 = Math.round(this.imganalobj.imgheight / 10);
		this.datay1 = this.imganalobj.imgheight - this.datay0;
		// Check if it's too large
		if( this.datax1-this.datax0 > this.boxmaxsize ){
			xmed = Math.round(this.imganalobj.imgwidth / 2);
			this.datax0 = xmed - this.boxmaxsize / 2;
			this.datax1 = xmed + this.boxmaxsize / 2;
		}
		if( this.datay1-this.datay0 > this.boxmaxsize ){
			ymed = Math.round(this.imganalobj.imgheight / 2);
			this.datay0 = ymed - this.boxmaxsize / 2;
			this.datay1 = ymed + this.boxmaxsize / 2;
		}
	}

	// DRAW: Draws the box with the current color at the current location.
	this.draw = function() {
		if (this.shown & this.active) {
			// Get the canvas
			ctx = this.imganalobj.imgcan.getContext('2d');
			// Draw the square
			ctx.strokeStyle = this.color;
			ctx.lineWidth = 2;
			ctx.strokeRect(this.imgx0, this.imgy0, this.imgx1 - this.imgx0,
					this.imgy1 - this.imgy0);
			// Get Zoom
			zoom = this.imganalobj.imgzoom;
			centerx = (this.centerx + 0.5) * zoom;
			centery = ( this.imganalobj.imgheight - this.centery - 0.5 ) * zoom;
			sig1 = this.sig1 * zoom;
			sig2 = this.sig2 * zoom;
			ctx.beginPath();
			ctx.ellipse(centerx,centery,sig1,sig2,-this.theta,0.0,2*Math.PI);
			ctx.stroke();
		}
	}

	// UPDATE: Updates the tool: Recalculates the imgxy coordinates from dataxy.
	// Recalculates the statistics and prints it.
	this.update = function() {
		// If it's not active -> return
		if ( ! this.active ){
			return;
		}
		imglogadd('AnalPsf: Going');
		//** Get the data into boxdata and sorted to boxsort (latter w/o Nans)
		// Calculate box shape from imganalobj
		nx = this.datax1 - this.datax0;
		ny = this.datay1 - this.datay0;
		datady = this.imganalobj.imgheight;
		zoom = this.imganalobj.imgzoom;
		this.imgx0 = this.datax0 * zoom;
		this.imgx1 = this.datax1 * zoom;
		this.imgy0 = (datady-this.datay1) * zoom;
		this.imgy1 = (datady-this.datay0) * zoom;
		// Get data -> boxdata
		var boxdata = new Array();
		for (yi = this.datay0; yi < this.datay1; yi += 1) {
			yoff = yi * this.imganalobj.imgwidth;
			x0 = yoff + this.datax0;
			x1 = yoff + this.datax1;
			adddata = this.imganalobj.imgraw.slice(x0, x1);
			boxdata.push.apply(boxdata,adddata); // Append to array
		}
		// Remove Nan's and sort
		boxsort=boxdata.filter(function(x) { return !isNaN(x);});
		boxsort.sort(function callback(a, b) {
			return a - b;
		});
		this.imgmin = boxsort[0];
		this.imgmax = boxsort[boxsort.length-1];
		imglogadd('AnalPsf: Got data, sorted');
		//** Calculate PSF center (means) using scaled probability
		// Scale to a probability with floor = min - (med-min)/2
		floor = 2* boxsort[Math.round(boxsort.length/100)] - 
		           boxsort[Math.round(boxsort.length/2)];
		floor = boxsort[Math.round(boxsort.length/5)];
		sum = 0.0;
		for( i = 0; i<boxsort.length; i++){
			sum += boxsort[i] - floor;
		}
		prob = new Array(boxdata.length);
		for( i = 0; i<boxdata.length; i++){
			prob[i] = ( boxdata[i] - floor ) / sum;
		}
		// X0 = Sum( P * X ), Y0 = Sum( P * Y)
		centerx = 0.0;
		centery = 0.0;
		for( xi = 0; xi < nx; xi++ ) {
			for( yi = 0; yi < ny; yi++ ) {
				ind = yi * nx + xi;
				if( !isNaN(prob[ind]) ){
					centerx += prob[ind] * xi;
					centery += prob[ind] * yi;
				}
			}
		}
		//** Calculate Offset: Get median of data far from center.
		// Make array fardata, distance sqrt(nx*ny)/2.2 from center
		rlimit = nx*ny/5.0; // square of the limit radius
		boxfar = new Array();
		for( xi = 0; xi < nx; xi++ ) {
			for( yi = 0; yi < ny; yi++ ) {
				ind = yi * nx + xi;
				rdist = (xi-centerx)*(xi-centerx)+(yi-centery)*(yi-centery);
				if( (!isNaN(boxdata[ind])) && (rdist > rlimit)) {
					boxfar.push(boxdata[ind]);
				}
			}
		}
		// Sort the array, get median as new offset / floor
		boxfar.sort(function callback(a,b) {
			return a-b;
		});
		off = boxfar[Math.round(boxfar.length/2)];
		// Calculate sum then recalculate probability
		sum -= boxsort.length * (off-floor); // correct for new offset
		for( i = 0; i<boxdata.length; i++){
			prob[i] = ( boxdata[i] - off ) / sum;
		} // ( I checked that Sum of prob == 1.0)
		//** Calculate covariances, get stdev, angle and amplitude
		covxx = 0.0;
		covxy = 0.0;
		covyy = 0.0;
		for( xi = 0; xi < nx; xi++ ) {
			for( yi = 0; yi < ny; yi++ ) {
				ind = yi * nx + xi;
				xoff = xi-centerx;
				yoff = yi-centery;
				if( !isNaN(boxdata[ind]) ) {
					covxx += xoff*xoff*prob[ind];
					covxy += xoff*yoff*prob[ind];
					covyy += yoff*yoff*prob[ind];
				}
			}
		}
		// Trace Determinante Eigenvectors
		tr = covxx + covyy;
		det = covxx * covyy - covxy * covxy;
		tt4d = tr * tr / 4.0 - det;
		if( tt4d < 0.0 ) { tt4d=0.0; }
		ev1 = tr/2 + Math.sqrt(tt4d);
		ev2 = tr/2 - Math.sqrt(tt4d);
		// Sigmas, Angle and Amplitude, get all values
		this.sig1 = Math.sqrt(ev1);
		this.sig2 = Math.sqrt(ev2);
		this.theta = Math.atan(covxy/(ev1-covyy));
		this.ampl = sum / (2.0 * Math.PI * this.sig1 * this.sig2);
		this.off = off;
		this.centerx = centerx + this.datax0;
		this.centery = centery + this.datay0;
		//** Display Statistics
		$('#imagetoolsoutput1')
		.html('<form> \
			   <span id="psfcolor">&nbsp;Color&nbsp;</span><br /> \
			   CenterX: ' + this.imganalobj.valueformat(this.centerx) +
			  '<br />CenterY: ' + this.imganalobj.valueformat(this.centery) + 
			  '<br />Off: ' + this.imganalobj.valueformat(off) );
		$('#imagetoolsoutput2').html(
				'Ampl: ' + this.imganalobj.valueformat(this.ampl) +
				'<br />&sigma;1: ' + this.imganalobj.valueformat(this.sig1) +
				'<br />&sigma;2: ' + this.imganalobj.valueformat(this.sig2) +
				'<br />Angle: ' + this.imganalobj.valueformat(180*this.theta/Math.PI) +
				'&deg;');
		// Set PSFcolor
		if(this.shown){
			textcol = {'red':'black','lime':'black','blue':'white',
					   'black':'white'}[this.color];
			$('#psfcolor').css('background',this.color);
			$('#psfcolor').css('color',textcol);
			psfcolor = $('#psfcolor')[0]
			psfcolor.callback_object = this;
			psfcolor.onclick = function() {
				this.callback_object.boxcolor();
			}
		}
		// OLD Get raw and sorted data for statistics (puts sorted w/o Nans into boxdata)
		// OLD Calculate statistics
/*		imgn = boxdata.length;
		this.imgmin = this.imganalobj.valueformat(boxdata[0]);
		this.imgmax = this.imganalobj.valueformat(boxdata[imgn - 1]);
		imgmed = this.imganalobj.valueformat(boxdata[Math.round(imgn / 2)]);
		var sum = 0.0;
		var sum2 = 0.0;
		// put min and max in there
		// also get boxval = boxdata[i] (local var) then use it only
		var i = imgn;
		var val = 0;
		while ( i > 0 ) {
			i--;
			val = boxdata[i];
			sum += val;
			sum2 += val * val;
		}
		imgavg = sum / imgn;
		imgstd = Math.sqrt(sum2 / imgn - imgavg * imgavg);
		imgavg = this.imganalobj.valueformat(imgavg);
		imgstd = this.imganalobj.valueformat(imgstd);
		imglogadd('AnalPsf: Got stats');
		// OLD Display statistics
		$('#imagetoolsoutput1')
				.html('<form> \
					   <input type="checkbox" id="statsbox">\
					   <span id="statscolor">&nbsp;Box&nbsp;</span><br />Min: '
					  + this.imgmin + '<br />Max: ' + this.imgmax);
		$('#imagetoolsoutput2').html(
				'Median: ' + imgmed + '<br />Average: ' + imgavg
						+ '<br />StdDev: ' + imgstd);
		// Set [./]box callback functions
		statsbox = $('#statsbox')[0];
		statsbox.callback_object = this;
		statsbox.onchange = function() {
			this.callback_object.checkhandler();
		}
		statsbox.checked = this.shown;
		if(this.shown){
			textcol = {'red':'black','lime':'black','blue':'white',
					   'black':'white'}[this.color];
			$('#statscolor').css('background',this.color);
			$('#statscolor').css('color',textcol);
			statscolor = $('#statscolor')[0]
			statscolor.callback_object = this;
			statscolor.onclick = function() {
				this.callback_object.boxcolor();
			}
		} // */
		// If ImageAnalysisObject.imgscale=='Box' -> call updateOptions
		if(this.imganalobj.imgscale=='Box'){
			this.imganalobj.updateOptions('','Box','');
		}
	}

	// CHECKHANDLER: Handles check events from the checkbox. Toogles the shown
	// flag, updates the widget and redraws the imageanalysisobject
	this.checkhandler = function() {
		// Toogle shown status
		this.shown = !this.shown;
		// Update the data
		this.update();
		// Redraw the image
		this.imganalobj.imagedraw();
	}
	
	// BOXCOLOR: Handles clicks on the box color switcher.
	this.boxcolor = function() {
		// Set next color
		this.color={'red':'lime','lime':'blue','blue':'black',
				    'black':'red'}[this.color];
		// Update the text color
		textcol = {'red':'black','lime':'black','blue':'white',
				   'black':'white'}[this.color];
		$('#psfcolor').css('background',this.color);
		$('#psfcolor').css('color',textcol);
		this.imganalobj.imagedraw();
	}
	
	// PICKUP: Checks if the image mouse location (x/y) is correct to pick up
	//         the box. If so true is returned and the box is set to moving.
	this.pickup = function(mousex,mousey){
		// Ignore if not shown or inactive
		if( ! this.shown || ! this.active) {
			return false;
		// Check if move is in progress: finish move
		} else if( this.moving > 0){
			this.dropoff();
			return false;
		// Check if mouse is inside the box
		} else if( mousex > this.imgx0-3 && mousex < this.imgx1+3 &&
		           mousey > this.imgy0-3 && mousey < this.imgy1+3 ){
			// Initialize move
			this.pickupx0 = this.imgx0;
			this.pickupx1 = this.imgx1;
			this.pickupy0 = this.imgy0;
			this.pickupy1 = this.imgy1;
			this.mousex0 = mousex;
			this.mousey0 = mousey;
			// Check movement of edges
			if( mousex < this.imgx0+3) { this.moving = this.moving + 1; }
			if( mousex > this.imgx1-3) { this.moving = this.moving + 2; }
			if( mousey < this.imgy0+3) { this.moving = this.moving + 4; }
			if( mousey > this.imgy1-3) { this.moving = this.moving + 8; }
			// Check movement of full box
			if( !this.moving ){
				this.moving = 15;
			}
			// Return
			return true;
		} else {
			return false;
		}
	}
	
	// MOVE: Moves the box to the new coordinates, updates imgx/y0/1
	//       datax/y0/1 and movex/y0 are used to calculate the move
	this.move = function(mousex,mousey){
		// calculate maximal valid indices
		zoom = this.imganalobj.imgzoom;
		imgdx = Math.round(this.imganalobj.imgwidth * zoom) - 1;
		imgdy = Math.round(this.imganalobj.imgheight * zoom) - 1;
		// calculate offsets
		mousedx = mousex-this.mousex0;
		mousedy = mousey-this.mousey0;
		// calculate new coordinates
		if(this.moving & 1) { this.imgx0 = this.pickupx0+mousedx; }
		if(this.moving & 2) { this.imgx1 = this.pickupx1+mousedx; }
		if(this.moving & 4) { this.imgy0 = this.pickupy0+mousedy; }
		if(this.moving & 8) { this.imgy1 = this.pickupy1+mousedy; }
		// check new coordinates
		if( mousedx < 0 ){
			// Check left
			if( this.imgx0 < 0 ) { this.imgx0 = 0; }
			if( this.imgx1 < 5 ) { this.imgx1 = 5; }
			if( this.imgx1 < this.imgx0+5) { this.imgx1 = this.imgx0+5; }
			if( this.imgx1 > this.imgx0+this.boxmaxsize*zoom ) { 
				this.imgx1 = this.imgx0+this.boxmaxsize*zoom; }
		} else {
			// Check right
			if( this.imgx1 > imgdx ) { this.imgx1 = imgdx; }
			if( this.imgx0 > imgdx-5) { this.imgx0 = imgdx-5; }
			if( this.imgx0 > this.imgx1-5) { this.imgx0 = this.imgx1-5; }
			if( this.imgx0 < this.imgx1-this.boxmaxsize*zoom ) {
				this.imgx0 = this.imgx1-this.boxmaxsize*zoom; }
		}
		if( mousedy < 0){
			// Check top
			if( this.imgy0 < 0 ) { this.imgy0 = 0; }
			if( this.imgy1 < 5 ) { this.imgy1 = 5; }
			if( this.imgy1 < this.imgy0+5) { this.imgy1 = this.imgy0+5; }
			if( this.imgy1 > this.imgy0+this.boxmaxsize*zoom ) { 
				this.imgy1 = this.imgy0+this.boxmaxsize*zoom; }
		} else {
			// Check bottom
			if( this.imgy1 > imgdy ) { this.imgy1 = imgdy; }
			if( this.imgy0 > imgdy-5) { this.imgy0 = imgdy-5; }
			if( this.imgy0 > this.imgy1-5) { this.imgy0 = this.imgy1-5; }			
			if( this.imgy0 < this.imgy1-this.boxmaxsize*zoom ) { 
				this.imgy0 = this.imgy1-this.boxmaxsize*zoom; }
		}
	}
	
	// DROP: Finishes the move by updating imgx/y0/1 to the current
	//          datax/y0/1 coordinates. The box is set to non-moving.
	// ### make sure box stays at least 2x2
	this.drop = function(){
		if( this.moving ){
			// Calculate new data coordinates
			datady = this.imganalobj.imgheight;
			zoom = this.imganalobj.imgzoom;
			this.datax0 = Math.round(this.imgx0/zoom);
			this.datax1 = Math.round(this.imgx1/zoom);
			this.datay0 = datady - Math.round(this.imgy1/zoom);
			this.datay1 = datady - Math.round(this.imgy0/zoom);
			// Clear moving
			this.moving = 0;
			// Update
			this.update();
		}
		
	}
};

// **** Logadd: adds log messages to #imagelog
function imglogadd(message){
	if(true){ // true/false
		time = (new Date()).toLocaleTimeString();
		$('#imagelog').append('<br>'+time+': '+message)
	}
}
	
/***
 * === History ===
 * 2016 March: Marc Berthoud - Add scaling options: log and box
 * - New imagescaled[] array that contains cval for each pixel. This
 *   array is filled by imagedraw() and used by imagedraw() and
 *   mousemove(). A flag (rescale) is used to indicate to
 *   imagedraw() that imagescaled[] needs to be recalculated.
 * - Scale = LOG option: if selected, imgmin and imgmax contain
 *   log values (set by updateoptions() ). imagedraw() has an
 *     if imgscale=='LOG'
 *   check when imagescaled[] is recalculated.
 * - New ToolStats.imgmin/imgmax: updated by update()
 * - Scale = BOX option: 
 *   - updateOptions() gets ToolStats.imgmin/imgmax
 *   - if ToolStats.update() finds ImgAnal.imgscale == 'BOX'
 *     it calls ImgAnal.updateOptions() 
 * 
 * 2014 March: Marc Berthoud - Streamline code for efficiency
 * - Replace array.concat with push.apply -> Much faster
 * - Improve efficiency of innermost loops in unpacking and drawing
 *   (mostly using local variables - with var definition)
 * - Add imglogadd(message) function to evaluate run efficiency of code
 * ==>> Time Consuming now are equally:
 *      unpack loop, sort(all), sort(stats), draw loop
 *      - Sorting can be avoided by using quickselect repeatedly on the 
 *        increasinly sorted array. (Factor 3-6 for large images)
 * 
 * 2012 July: Marc Berthoud - Add statistics object
 * - Make a statistics object with
 *   - variables: moving, shown, data/imagex/y0/1, color
 *   - functions: draw, update, pickup, move, drop, input
 *   - while moving dataxy!~imagexy
 * - imageanalysis object will have a toollist and toolmove variables
 *   - will have functions mousemove/down/up/out
 * - the canvas will have the frame as another object (make sure it's erased,
 *   maybe toolstats::draw can erase things
 * - The cookies will be called configuration and getconf(name, default)
 *   and setconf(name, value) should be used throughout
 * Tasks:
 * ./ Make a canvas and check for mousedown/up/move events if click in image
 *   but release outside image (also if image is in smaller div with scrollbars)
 *   ==>> Need to use mouseout to drop if move is in progres
 * ./ Add Script loading into all headers (views.py)
 * ./ Add jQuery to logscripts.js
 * ./ Make the setcook getcook functions (shortcut: use jQuerry .cookie)
 * ./ Use them throughout
 * ./ Make the basic stats object
 *   ./ Variables
 *   ./ Init function -> add to imageanaysis object
 *   ./ Draw -> add to imageanalysis object
 *   ./ Update -> add to imageanalysis object
 * ./ Add tools to imageanalysis object: insert init, draw, update
 *   - > Make statsbox always on and test things
 * ./ Wire up stats[./] checkbox: give it a DOM name - hook up with statsobj
 *   init function -> test it
 * ./ Write toolstats pickup, move, drop
 * ./ Write imageanalysis move(new), mousedown, mouseup, mouseout -> test
 */
