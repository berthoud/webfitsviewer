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
	this.imgscale = ''; // Scale setting (Initial value is set by self.getOptions() )
	this.imgmin = 0.0; // Scale min data value
	this.imgmax = 1.0; // Scale max data value
	this.imgcolor = 'grey'; // Selected color scale
	this.imgzoom = 1.0; // Zoom factor (i.e. zoom in if >1)
	this.imgcan = 0; // image canvas object
	this.rescale = 1; // flag indicating that imgscaled needs to be recalculated
	this.filename = ''; // File name
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
	// Seth's panning stuff
	this.pan = { x: 0, y: 0 }; // coordinates of top left corner of image in canvas pixels
	this.panStart = { x: 0, y: 0};
	this.bitimg = null;
	// Seth's panning stuff
	this.pan = { x: 0, y: 0 }; // coordinates of top left corner of image in canvas pixels
	this.panStart = { x: 0, y: 0};
	this.bitimg = null;

	// **** Object Functions
	// WriteTools: writes the HTML code for the image analysis tools, a table with
	//             3 columns, 3 rows
	//             | Mouse X/Y/Value | Zoom, Scale, Color | Zoom in Window |
	//             |-----------------|--------------------|                |
	//             | Tools Selector ( 2 columns )         | ( 3 rows )     |
	//             |--------------------------------------|                |
	//             | Tools Output 1  | Tools Outout 2     |                |
	this.writetools = function() {
		// document.writeln('<table><tr><td class = "tools"> \
		//      <div id = "imageinfo"> \
		//      Mouse&nbsp;X&nbsp;/&nbsp;Y:<br>&nbsp;<br>Value:<br>&nbsp;</div> \
		//      <td class = "tools"><form> \
		//      Zoom:<br> \
		//      <select id = "zoomselect" disabled> \
		//      <option>1/10</option> \
		//      <option>1/3</option> \
		//      <option>1x</option> \
		//      <option>3x</option> \
		//      <option>10x</option> \
		//      </select><br> \
		//      Scale:<br> \
		//      <select id = "scaleselect" disabled> \
		//      <option>MinMax</option> \
		// 	 <option>99.5%</option> \
		//      <option>98%</option> \
		//      <option>90%</option> \
		//      <option>1 StDev</option> \
		// 	 <option>Log</option> \
		// 	 <option>Box</option> \
		//      </select><br> \
		//      Color:<br> \
		//      <select id = "colorselect" disabled> \
		//      <option>Grey</option> \
		//      <option>Rainbow</option> \
		//      <option>Staircase</option> \
		//      </select> \
		//      </form>'
		// 				+ '<td class = "tools" rowspan="3"> \
		//      <canvas id = "analcanvas" width = "'
		// 				+ this.analsize
		// 				+ '"        height = "'
		// 				+ this.analsize
		// 				+ '"        style="border: solid 2px #ff0000;"> \
		//      Your Browser does not support HTML5 - Canvas Elements - please upgrade. \
		//      </canvas></table>');
		// document.writeln(' \
		// 		<tr><td class = "tools" id = "imagetoolselector" colspan="2"> \
		// 		    <b>Analysis Tool:</b> \
		// 		<tr><td class = "tools" id = "imagetoolsoutput1"> \
		// 		    <td class = "tools" id = "imagetoolsoutput2"> \
        //             <div style="width: 500px;"><canvas id="psf_chart"></canvas></div>');
		// document.writeln('</table>');
	}

	// WriteDisplay: writes the HTML code for the image display
	this.writedisplay = function() {
		document.writeln('<div id = "imagemsg"></div> \
             <div id = "imagewrapper"> \
			    <div id = "imagediv" style = "width:100%; \
			        border:solid 1px #CCC;"> \
			        <canvas id = "imagecanvas" width="200" height="200"> \
			        Your Browser does not support HTML5 - Canvas Elements \
			        - please upgrade. \
			        </canvas> \
			    </div> \
                <div id = "statsdiv">\
                    <div class="tools"><div id = "imagestat">Initializing</div></div> \
                    <div class="tools"> \
                    <table><tr><td class = "tools"> \
                        <div id = "imageinfo"> \
                        Mouse&nbsp;X&nbsp;/&nbsp;Y:<br>&nbsp;<br>Value:<br>&nbsp;</div> \
                        <form> \
                        Scale: \
                        <select id = "scaleselect" disabled> \
                        <option>MinMax</option> \
                        <option>99.5%</option> \
                        <option>98%</option> \
                        <option>90%</option> \
                        <option>1 StDev</option> \
                        <option>Log</option> \
                        <option>Box</option> \
                        </select> \
                        Color: \
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
                        </canvas> \
                    </table> \
                    </div> \
                    <div class = "tools" id = "imagetoolselector" colspan="2"> \
                        <b>Analysis Tool:</b> \
                    </div> \
                    <div id="statswrapper"> \
                        <div class = "tools" id = "imagetoolsoutput1"></div> \
                        <div class = "tools" id = "imagetoolsoutput2"></div> \
                    </div> \
                    <div class = "tools"  style="display: none;"><canvas id="psf_chart"></canvas></div> \
                </div> \
             </div> ')
			//  <div id = "imagelog"></div>');
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
				this.imgcan.width = this.imgcan.parentElement.clientWidth;
				this.imgcan.height = this.imgcan.parentElement.clientHeight;
                imgctx.scale(0.25, 0.25);
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
		$('#imagestat').html('Loading Image Data - Preview Image Displayed');
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
		$('#imagetoolselector').html(toolselect + '<span id="linecolor">&nbsp;Color&nbsp;</span>');
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
		ind = headtxt.indexOf('filename = ') + 11;
		len = headtxt.substring(ind).indexOf('\n');
		this.filename = headtxt.substr(ind,len);
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
        this.imgcan.onwheel = function(event) {
            this.callback_object.mousezoomhandler(event);
        }
        this.imgcan.ondblclick = function(event) {
            this.callback_object.doubleclick(event)
        }
		// get options from existing cookies
		this.getOptions();
		// Set zoom size (make sure diagonal is at least 300 pixels long)
		this.imgzoom = 1.0;

        console.log("Image vals:" + this.imgwidth + ', ' + this.imgwidth + ', ' + this.imgheight + ', ' + this.imgheight);

        // Set the initial zoom
		diag = Math.sqrt(this.imgwidth * this.imgwidth + this.imgheight
				* this.imgheight);
		while (this.imgzoom * this.imgwidth < this.imgcan.parentElement.clientWidth - 20) {
			this.imgzoom += 0.01;
		}
        while (this.imgzoom * this.imgwidth > this.imgcan.parentElement.clientWidth - 20) {
			this.imgzoom -= 0.01;
		}

        console.log("Final zoom: " + this.imgzoom);
        
        // To be deleted...
		// Set zoom selection dropdown
		// zoomsel = $('#zoomselect')[0];
		// zoomsel.disabled = false;
		// if (this.imgzoom != 1.0) {
		// 	// If zoom > 1 -> add selected "Auto" option to select
		// 	option = new Option('Auto', 'Auto', true, true);
		// 	zoomsel.add(option, null);
		// } else {
		// 	// If zoom == 1 -> select 1x option
		// 	found = -1;
		// 	for (i = 0; i < zoomsel.length; i++) {
		// 		if (zoomsel.options[i].text == '1x')
		// 			found = i;
		// 	}
		// 	if (found > -1)
		// 		zoomsel.selectedIndex = found;
		// }
		// // Set zoomselect onChange function
		// zoomsel.callback_object = this;
		// zoomsel.onchange = function() {
		// 	this.callback_object.zoomhandler();
		// }
        
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
	this.imagedraw = async function() {
        // console.log("imagedraw")
		// **** Get image geometry constraints
		// get display size (limit display size to 5000 x 5000)
		// var dispwidth = Math.round(this.imgwidth * this.imgzoom);
		// if (dispwidth > 5000) {
		// 	dispwidth = 5000;
		// }
		// var dispheight = Math.round(this.imgheight * this.imgzoom);
		// if (dispheight > 5000) {
		// 	dispheight = 5000;
		// }
        // console.log("Thinks display width should be: " + dispwidth);

		// set imagediv height
		// if (dispheight > 600) {
		// 	// document.getElementById('imagediv').style.height = '600px';
		// } else {
		// 	document.getElementById('imagediv').style.height = 'auto';
		// }
		// **** Draw the image
		// get canvas context
		ctx = this.imgcan.getContext('2d');
		// make canvas image
		var canimg = ctx.createImageData(this.imgwidth, this.imgheight);
		// recalculate imagescaled values if necessary
		var imgx = 0, imgy = 0, i = 0, j = 0, k = 0;
		var imgwidth = this.imgwidth;
		var imgheight = this.imgheight;
		var imgmin = this.imgmin;
		var imgmax = this.imgmax;
		var imgraw = this.imgraw;
		var imgdiff = 1.0;

        // TODO: Double check this doesn't always run, and also double check when
        // this section actually does run (i.e. is it reliable)
		if (this.rescale > 0) {
            console.log('Running rescale loop');
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
            // Try and set bitmap to null so that it gets recalculated below
            this.bitimg = null;
		}

        // Clear canvas TODO: need something like this
        // ctx.clearRect(0, 0, this.imgcan.width, this.imgcan.height);

		// fill canvas image

        if (this.bitimg === null) {
            console.log("attempting to create bitmap")

            imglogadd('Start Drawing Loop');
            console.log('Running loop')
            var imgzoom = 1;
            var carr = this.getRGB(0);
            console.log(imgwidth, imgheight)
            for (var y = 0; y < imgheight; y += 1) {
                for (var x = 0; x < imgwidth; x += 1) {
                    // imgx = Math.floor(x / imgzoom);
                    // imgy = Math.floor(y / imgzoom);
                    // i = imgy * imgwidth + imgx; // index of raw image pixel
                    // j = (dispheight - 1 - y) * dispwidth + x;
                    i = y*imgwidth+x;
                    // j = (imgheight - 1 - y) * imgwidth + x;
                    carr = this.getRGB(this.imgscaled[i]);
                    for (k = 0; k < 4; k++) {
                        (canimg.data)[4 * i + k] = carr[k];
                    }
                }
            }
            imglogadd('Stop Drawing Loop');

            this.bitimg = await createImageBitmap(canimg, { imageOrientation: 'flipY' });
        }

        // console.log("bitimg" + this.bitimg.width + ", " + this.bitimg.height)

        // TODO: attempting some things from Ian
        // let fitsImgData = new ImageData(canimg.data, dispwidth, dispheight);
        
        // Get image div for reference
        let imagediv = document.getElementById('imagediv');

		// set canvas size
        // Seth say's don't change this! We want it fixed now to pan
		this.imgcan.width = imagediv.clientWidth;
		this.imgcan.height = imagediv.clientHeight;
        
        // Seth's panning
        ctx.clearRect(0, 0, this.imgcan.width, this.imgcan.height);

        ctx.save();
        ctx.translate(this.pan.x, this.pan.y);
        ctx.scale(this.imgzoom, this.imgzoom);
        
        // TODO: Currently trying to use drawImage instead with an ImageBitmap object
        // Not as laggy as before, could probably still be improved

        // Set zoom scaling
        if (this.imgzoom >= 2) {
            ctx.imageSmoothingEnabled = false;
        } else {
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = "high"
        }
        ctx.drawImage(this.bitimg, 0, 0);

		// **** Draw the analysis tools
		for (i = 0; i < this.toollist.length; i += 1) {
			this.toollist[i].draw();
		}

        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.restore();
	}

	// Mousemove: Event handler to respond to mouse events
	this.mousemove = function(event) {
		// **** Update location / value display
		// Get x and y and display them
		scrollx = $('#imagediv').scrollLeft();
		scrolly = $('#imagediv').scrollTop();
		// imgx = event.pageX - this.imgcan.offsetLeft + scrollx;
		// imgy = event.pageY - this.imgcan.offsetTop + scrolly - 1;
		//imgx = ( event.offsetX - this.pan.x ) / this.imgzoom;
		//imgy = ( event.offsetY - this.pan.y ) / this.imgzoom;
        imgx = event.offsetX - this.pan.x;
        imgy = event.offsetY - this.pan.y;

		datax = Math.floor(imgx / this.imgzoom);
		datay = this.imgheight - 1 - Math.floor(imgy / this.imgzoom);
		i = datay * this.imgwidth + datax;
		val = this.imgraw[i];

        // This seems to break hard when there are undefined values?
        // Edited valueformat to return 0 for undefined values
		val = this.valueformat(val);
		
        // Message: X/Y row/column
		msg = 'Mouse&nbsp;X&nbsp;/&nbsp;Y:<br>&nbsp;&nbsp;';
		msg += datax + ' / ' + datay;
		// Message: Coordinates
		if(this.coords){
			// get mouserow/col
			mcol = imgx / this.imgzoom - 0.5;
		    mrow = this.imgheight - 1 - ( imgy / this.imgzoom - 0.5 );
			
            // console.log("MOUSE:" + mcol + ", " + mrow)
            // get coordx/y
		    coordx = this.coordx0 + mcol * this.coordcolx + mrow * this.coordrowx;
		    coordy = this.coordy0 + mcol * this.coordcoly + mrow * this.coordrowy;		    
			
            // console.log("MOUSE2:" + coordx + ", " + coordy)
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
		msg += '<br>Value:&nbsp;&nbsp;' + val;
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
            swapy = this.imgheight - datay;
			this.toolmove.move(datax,swapy);
			this.imagedraw();
		}

        // Seth's panning stuff
        if (this.panning) {
            this.pan = {
                x: this.pan.x + (event.offsetX - this.panStart.x),
                y: this.pan.y + (event.offsetY - this.panStart.y)
            };

            this.panStart.x = event.offsetX;
            this.panStart.y = event.offsetY;
            this.imagedraw();
            // console.log(this.pan);
        }
	}
	
	// Mousedown: Event handler to press mouse button
	this.mousedown = function(event) {
		// Get mouse coordinates
		scrollx = $('#imagediv').scrollLeft();
		scrolly = $('#imagediv').scrollTop();
		// imgx = event.pageX - this.imgcan.offsetLeft + scrollx;
		// imgy = event.pageY - this.imgcan.offsetTop + scrolly - 1;
        imgx = event.offsetX - this.pan.x;
        imgy = event.offsetY - this.pan.y;

        datax = Math.floor(imgx / this.imgzoom);
		datay = Math.round(imgy / this.imgzoom);

		// Check connection to tool object
		this.toolmove = null;
		for( i=0; i<this.toollist.length && this.toolmove == null; i++){
			if( this.toollist[i].pickup(datax, datay)) {
				this.toolmove = this.toollist[i];
			}
		}

        // If we still have nothing to move
        if (this.toolmove === null) {
            // console.log('mousedown pan starting');
            this.panning = true;
            this.panStart = {
                x: event.offsetX, 
                y: event.offsetY
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
        this.panning = false;
	}

    this.mousezoomhandler = function(e) {
        // if (imageLoaded) { 
        // TODO: really need something like this to stop zoom before load
        
        e.preventDefault();

        const zoomRate = 1.0025; // scroll sensitivity
        const zoomFactor = Math.pow(zoomRate, -e.deltaY);

        const prevZoom = this.imgzoom;
        const newZoom = prevZoom * zoomFactor;

        const mouseX = e.offsetX;
        const mouseY = e.offsetY;

        this.pan.x = (newZoom*(this.pan.x - mouseX) / prevZoom) + mouseX;
        this.pan.y = (newZoom*(this.pan.y - mouseY) / prevZoom) + mouseY;

        // console.log(this.pan.x, this.pan.y)

        this.imgzoom = newZoom;
		//console.log(this.pan.x,this.pan.y);
        this.imagedraw();
    }

    this.doubleclick = function(event) {
        imgx = event.offsetX - this.pan.x;
        imgy = event.offsetY - this.pan.y;

        this.toolnow.doubleclick(imgx, imgy);
        this.toolnow.update();
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
        this.rescale = 1;
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
            this.toolnow.disable();
            // console.log(this.toolnow);
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
			case '99.5%':
				this.imgmin = this.imgrawsort[Math.round(pixeln / 400)];
				this.imgmax = this.imgrawsort[Math.round(399 * pixeln / 400) - 1];
				this.rescale = 1;
				break;
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
		// Check new zoom (not implemented, this feature would be annoying)
		// Check new scale
		newscale = unescape($.cookie('imageanalscale'));
		if (['MinMax','99.5%','98%','90%','5 StDev','Log','Box'].indexOf(newscale) < 0) {
			newscale = '99.5%';
		}
		// Check new color
		newcolor = unescape($.cookie('imageanalcolor'));
		if (['GREY','RAINBOW','STAIRCASE'].indexOf(newcolor) < 0) {
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
        if (value == undefined) {
            return 0;
        }
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
		// this.datax0 = Math.round(this.imganalobj.imgwidth / 10);
		// this.datax1 = this.imganalobj.imgwidth - this.datax0;
		// this.datay0 = Math.round(this.imganalobj.imgheight / 10);
		// this.datay1 = this.imganalobj.imgheight - this.datay0;

        this.imgx0 = Math.round(this.imganalobj.imgwidth*3 / 8);
		this.imgx1 = this.imganalobj.imgwidth - this.imgx0;
		this.imgy0 = Math.round(this.imganalobj.imgheight*3 / 8);
		this.imgy1 = this.imganalobj.imgheight - this.imgy0;
	}

	// DRAW: Draws the box with the current color at the current location.
	this.draw = function() {
        // return // Stop this for a moment
		if (this.shown & this.active) {
			// Get the canvas
			ctx = this.imganalobj.imgcan.getContext('2d');
			// Draw the square
			ctx.strokeStyle = this.color;
			ctx.lineWidth = Math.max(0.5, 3 * 1/this.imganalobj.imgzoom);
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
		this.calculatestats().then( (results) => {

            // Unpack results
            imgmed = results[0];
            imgavg = results[1];
            imgstd = results[2];
            sum = results[3];
            imgn = results[4];

            imglogadd('Analstats: Done');
            // Display statistics
            $('#imagetoolsoutput1')
                    .html('<form> \
                        <input type="checkbox" id="statsbox">\
                        <span id="statscolor">&nbsp;Box&nbsp;</span><br />Min: '
                        + this.imgmin + '<br />Max: ' + this.imgmax + 
                        '<br />Npix: ' + imgn);
            $('#imagetoolsoutput2').html(
                    'Median: ' + imgmed + '<br />Average: ' + imgavg
                            + '<br />StdDev: ' + imgstd + '<br />Sum: '
                            + this.imganalobj.valueformat(sum) );
            // Set [./]box callback functions
            statsbox = $('#statsbox')[0];
            statsbox.callback_object = this;
            statsbox.onchange = function() {
                this.callback_object.checkhandler();
            }
            statsbox.checked = this.shown;
            // if(this.shown){
            //     textcol = {'red':'black','lime':'black','blue':'white',
            //             'black':'white'}[this.color];
            //     $('#statscolor').css('background',this.color);
            //     $('#statscolor').css('color',textcol);
            //     statscolor = $('#statscolor')[0]
            //     statscolor.callback_object = this;
            //     statscolor.onclick = function() {
            //         this.callback_object.boxcolor();
            //     }
            // }
            if(this.shown){
                textcol = {'red':'black','lime':'black','blue':'white',
                        'black':'white'}[this.color];
                $('#linecolor').css('background',this.color);
                $('#linecolor').css('color',textcol);
                linecolor = $('#linecolor')[0]
                linecolor.callback_object = this;
                linecolor.onclick = function() {
                    this.callback_object.boxcolor();
                }
            }
            // If ImageAnalysisObject.imgscale=='Box' -> call updateOptions
            if(this.imganalobj.imgscale=='Box'){
                this.imganalobj.updateOptions('','Box','');
            }
        })


		// Display statistics
		// $('#imagetoolsoutput1')
		// 		.html('<form> \
		// 			   <input type="checkbox" id="statsbox">\
		// 			   <span id="statscolor">&nbsp;Box&nbsp;</span><br />Min: '
		// 			  + this.imgmin + '<br />Max: ' + this.imgmax + 
		// 			  '<br />Npix: ' + imgn);
		// $('#imagetoolsoutput2').html(
		// 		'Median: ' + imgmed + '<br />Average: ' + imgavg
		// 				+ '<br />StdDev: ' + imgstd + '<br />Sum: '
		// 				+ this.imganalobj.valueformat(sum) );
		// // Set [./]box callback functions
		// statsbox = $('#statsbox')[0];
		// statsbox.callback_object = this;
		// statsbox.onchange = function() {
		// 	this.callback_object.checkhandler();
		// }
		// statsbox.checked = this.shown;
		// if(this.shown){
		// 	textcol = {'red':'black','lime':'black','blue':'white',
		// 			   'black':'white'}[this.color];
		// 	$('#statscolor').css('background',this.color);
		// 	$('#statscolor').css('color',textcol);
		// 	statscolor = $('#statscolor')[0]
		// 	statscolor.callback_object = this;
		// 	statscolor.onclick = function() {
		// 		this.callback_object.boxcolor();
		// 	}
		// }
		// // If ImageAnalysisObject.imgscale=='Box' -> call updateOptions
		// if(this.imganalobj.imgscale=='Box'){
		// 	this.imganalobj.updateOptions('','Box','');
		// }
	}

    this.calculatestats = async function() {
        boxdata = new Array()
        if (this.shown) { // If box is shown -> get contents
			// Calculate box shape from imganalobj
			datady = this.imganalobj.imgheight;
			zoom = this.imganalobj.imgzoom;
			// this.imgx0 = this.datax0;
			// this.imgx1 = this.datax1;
			// this.imgy0 = (datady-this.datay1);
			// this.imgy1 = (datady-this.datay0);
            
            // Get data and sort
			// var boxdata = new Array();
			// for (yi = this.datay0; yi < this.datay1; yi += 1) {
			// 	yoff = yi * this.imganalobj.imgwidth;
			// 	x0 = yoff + this.datax0;
			// 	x1 = yoff + this.datax1;
			// 	adddata = this.imganalobj.imgraw.slice(x0, x1);
			// 	boxdata.push.apply(boxdata,adddata); // Append to array
			// }

            for (yi = this.imgy0; yi < this.imgy1; yi += 1) {
				yoff = yi * this.imganalobj.imgwidth;
				x0 = yoff + this.imgx0;
				x1 = yoff + this.imgx1;
				adddata = this.imganalobj.imgraw.slice(x0, x1);
				boxdata.push.apply(boxdata,adddata); // Append to array
			}

			boxdata=boxdata.filter(function(x) { return !isNaN(x);});
			imglogadd('Analstats: Got data');
			boxdata.sort(function callback(a, b) {
				return a - b;
			});

            console.log("Calculated box data")

		} else {
			// Get sorted data from imganalobj
			var npix = this.imganalobj.imgwidth * this.imganalobj.imgheight - this.imganalobj.nnans;
			boxdata = this.imganalobj.imgrawsort.slice(0,npix);
		}
		imglogadd('Analstats: Got Sorted data');

        // DATA: This needs to be in the separate thread
		// Calculate statistics
		imgn = boxdata.length;

        console.log("Found npix: " + boxdata.length)

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

        return [imgmed, imgavg, imgstd, sum, imgn];
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
		$('#linecolor').css('background',this.color);
		$('#linecolor').css('color',textcol);
		this.update();
        this.imganalobj.imagedraw();
	}
	
	// PICKUP: Checks if the image mouse location (x/y) is correct to pick up
	//         the box. If so true is returned and the box is set to moving.
	this.pickup = function(mousex,mousey){
        zoom = this.imganalobj.imgzoom;
		// Ignore if not shown or inactive
		if( ! this.shown || ! this.active) {
			return false;
		// Check if move is in progress: finish move
		} else if( this.moving > 0){
			this.dropoff();
			return false;
		// Check if mouse is inside the box
		// } else if( mousex > this.imgx0-3 && mousex < this.imgx1+3 &&
		//            mousey > this.imgy0-3 && mousey < this.imgy1+3 ){
		// 	// Initialize move
		// 	this.pickupx0 = this.imgx0;
		// 	this.pickupx1 = this.imgx1;
		// 	this.pickupy0 = this.imgy0;
		// 	this.pickupy1 = this.imgy1;
		// 	this.mousex0 = mousex;
		// 	this.mousey0 = mousey;
		// 	// Check movement of edges
		// 	if( mousex < this.imgx0+3) { this.moving = this.moving + 1; }
		// 	if( mousex > this.imgx1-3) { this.moving = this.moving + 2; }
		// 	if( mousey < this.imgy0+3) { this.moving = this.moving + 4; }
		// 	if( mousey > this.imgy1-3) { this.moving = this.moving + 8; }
		// 	// Check movement of full box
		// 	if( !this.moving ){
		// 		this.moving = 15;
		// 	}
		// 	// Return
		// 	return true;
		} else if( mousex > this.imgx0-3/zoom && mousex < this.imgx1+3/zoom &&
		           mousey > this.imgy0-3/zoom && mousey < this.imgy1+3 ){
			// Initialize move
			this.pickupx0 = this.imgx0;
			this.pickupx1 = this.imgx1;
			this.pickupy0 = this.imgy0;
			this.pickupy1 = this.imgy1;
			this.mousex0 = mousex;
			this.mousey0 = mousey;
			// Check movement of edges
			if( mousex < this.imgx0+3/zoom) { this.moving = this.moving + 1; }
			if( mousex > this.imgx1-3/zoom) { this.moving = this.moving + 2; }
			if( mousey < this.imgy0+3/zoom) { this.moving = this.moving + 4; }
			if( mousey > this.imgy1-3/zoom) { this.moving = this.moving + 8; }
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
		imgdx = Math.round(this.imganalobj.imgwidth) - 1;
		imgdy = Math.round(this.imganalobj.imgheight) - 1;
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
			this.datax0 = Math.round(this.imgx0);
			this.datax1 = Math.round(this.imgx1);
			this.datay0 = datady - Math.round(this.imgy1);
			this.datay1 = datady - Math.round(this.imgy0);
			// Clear moving
			this.moving = 0;
			// Update
			this.update();
		}
		
	}

    this.disable = function() {
        // pass
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
		// this.datax0 = Math.round(this.imganalobj.imgwidth*3 / 8);
		// this.datax1 = this.imganalobj.imgwidth - this.datax0;
		// this.datay0 = Math.round(this.imganalobj.imgheight*3 / 8);
		// this.datay1 = this.imganalobj.imgheight - this.datay0;
		// // Check if it's too large
		// if( this.datax1-this.datax0 > this.boxmaxsize ){
		// 	xmed = Math.round(this.imganalobj.imgwidth / 2);
		// 	this.datax0 = xmed - this.boxmaxsize / 2;
		// 	this.datax1 = xmed + this.boxmaxsize / 2;
		// }
		// if( this.datay1-this.datay0 > this.boxmaxsize ){
		// 	ymed = Math.round(this.imganalobj.imgheight / 2);
		// 	this.datay0 = ymed - this.boxmaxsize / 2;
		// 	this.datay1 = ymed + this.boxmaxsize / 2;
		// }

        // Initialize box size
        this.imgx0 = Math.round(this.imganalobj.imgwidth/10);
		this.imgx1 = this.imganalobj.imgwidth - this.imgx0;
		this.imgy0 = Math.round(this.imganalobj.imgheight/10);
		this.imgy1 = this.imganalobj.imgheight - this.imgy0;
		// Check if it's too large
		if( this.imgx1-this.imgx0 > this.boxmaxsize ){
            console.log("too large")
			xmed = Math.round(this.imganalobj.imgwidth / 2);
			this.imgx0 = xmed - this.boxmaxsize / 2;
			this.imgx1 = xmed + this.boxmaxsize / 2;
		}
		if( this.imgy1-this.imgy0 > this.boxmaxsize ){
			ymed = Math.round(this.imganalobj.imgheight / 2);
			this.imgy0 = ymed - this.boxmaxsize / 2;
			this.imgy1 = ymed + this.boxmaxsize / 2;
		}
	}

    this.coordstoradec = function(coordx, coordy) {
        let msg = "";

        // Get the RA
        let hr = Math.floor(coordx/15);
        let mn = Math.floor(4*coordx-60*hr);
        let sc = 240*coordx-3600*hr-60*mn;
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
        msg += this.imganalobj.coordlblx + ' ' + hr.toFixed(0) + 'h' + mn + 'm' + sc + 's';
        
        let sn = '';
        // Get the DEC
        if(coordy<0){
            sn='-';
            coordy = -coordy;
        } else {
            sn='';
        }
        let dg = Math.floor(coordy);
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
        msg += ' / ' + this.imganalobj.coordlbly + ' ' + sn + dg.toFixed(0) + '&deg;' + mn + '\'' + sc + '"';

        return msg;
    }

	// DRAW: Draws the box with the current color at the current location.
	this.draw = function() {
		if (this.shown & this.active) {
			// Get the canvas
			ctx = this.imganalobj.imgcan.getContext('2d');
			// Draw the square
			ctx.strokeStyle = this.color;
			ctx.lineWidth = Math.max(0.5, 3 * 1/this.imganalobj.imgzoom);
			ctx.strokeRect(this.imgx0, this.imgy0, this.imgx1 - this.imgx0,
					this.imgy1 - this.imgy0);
			// Get Zoom
			// zoom = this.imganalobj.imgzoom;
			centerx = (this.centerx + 0.5);
			centery = ( this.imganalobj.imgheight - this.centery - 0.5 );
			sig1 = this.sig1;
			sig2 = this.sig2;
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
		// nx = this.datax1 - this.datax0;
		// ny = this.datay1 - this.datay0;
        nx = this.imgx1 - this.imgx0;
		ny = this.imgy1 - this.imgy0;
		datady = this.imganalobj.imgheight;

        // this.imgx0 = this.datax0;
		// this.imgx1 = this.datax1;
		// this.imgy0 = (datady-this.datay1); // HERE: y0 = ..y1
		// this.imgy1 = (datady-this.datay0); //       y1 = ..y0 to keep y0<y1
		
        this.datax0 = this.imgx0;
		this.datax1 = this.imgx1;
		this.datay0 = (datady-this.imgy1); // HERE: y0 = ..y1
		this.datay1 = (datady-this.imgy0);

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
        center_in_radec = "";

        if (this.imganalobj.coords) {
            console.log(this.imganalobj.coordx0, this.imganalobj.coordy0)

            let p0x = this.imganalobj.coordx0 + this.centerx * this.imganalobj.coordcolx + this.centery * this.imganalobj.coordrowx;
            let p0y = this.imganalobj.coordy0 + this.centerx * this.imganalobj.coordcoly + this.centery * this.imganalobj.coordrowy;

            if(this.imganalobj.coordlblx.toUpperCase().includes('RA') && this.imganalobj.coordlbly.toUpperCase().includes('DEC')){
                    center_in_radec = "Center: " + this.coordstoradec(p0x, p0y) + "<br />";
            }
        }

		//** Display Statistics
		$('#imagetoolsoutput1')
		.html('<form> \
			   CenterX: ' + this.imganalobj.valueformat(this.centerx) +
			  '<br />CenterY: ' + this.imganalobj.valueformat(this.centery) +
              '<br />' + center_in_radec + 
			  '<br />Off: ' + this.imganalobj.valueformat(off) );
		$('#imagetoolsoutput2').html(
				'Ampl: ' + this.imganalobj.valueformat(this.ampl) +
				'<br />&sigma;1: ' + this.imganalobj.valueformat(this.sig1) +
				'<br />&sigma;2: ' + this.imganalobj.valueformat(this.sig2) +
				'<br />Angle: ' + this.imganalobj.valueformat(180*this.theta/Math.PI) +
				'&deg;');
		// Set PSFcolor
		// if(this.shown){
		// 	textcol = {'red':'black','lime':'black','blue':'white',
		// 			   'black':'white'}[this.color];
		// 	$('#psfcolor').css('background',this.color);
		// 	$('#psfcolor').css('color',textcol);
		// 	psfcolor = $('#psfcolor')[0]
		// 	psfcolor.callback_object = this;
		// 	psfcolor.onclick = function() {
		// 		this.callback_object.boxcolor();
		// 	}
		// }
        if(this.shown){
			textcol = {'red':'black','lime':'black','blue':'white',
					   'black':'white'}[this.color];
			$('#linecolor').css('background',this.color);
			$('#linecolor').css('color',textcol);
			linecolor = $('#linecolor')[0]
			linecolor.callback_object = this;
			linecolor.onclick = function() {
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
		$('#linecolor').css('background',this.color);
		$('#linecolor').css('color',textcol);
		this.update();
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
		imgdx = Math.round(this.imganalobj.imgwidth) - 1;
		imgdy = Math.round(this.imganalobj.imgheight) - 1;
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
			if( this.imgx1 > this.imgx0+this.boxmaxsize ) { 
				this.imgx1 = this.imgx0+this.boxmaxsize; }
		} else {
			// Check right
			if( this.imgx1 > imgdx ) { this.imgx1 = imgdx; }
			if( this.imgx0 > imgdx-5) { this.imgx0 = imgdx-5; }
			if( this.imgx0 > this.imgx1-5) { this.imgx0 = this.imgx1-5; }
			if( this.imgx0 < this.imgx1-this.boxmaxsize ) {
				this.imgx0 = this.imgx1-this.boxmaxsize; }
		}
		if( mousedy < 0){
			// Check top
			if( this.imgy0 < 0 ) { this.imgy0 = 0; }
			if( this.imgy1 < 5 ) { this.imgy1 = 5; }
			if( this.imgy1 < this.imgy0+5) { this.imgy1 = this.imgy0+5; }
			if( this.imgy1 > this.imgy0+this.boxmaxsize ) { 
				this.imgy1 = this.imgy0+this.boxmaxsize; }
		} else {
			// Check bottom
			if( this.imgy1 > imgdy ) { this.imgy1 = imgdy; }
			if( this.imgy0 > imgdy-5) { this.imgy0 = imgdy-5; }
			if( this.imgy0 > this.imgy1-5) { this.imgy0 = this.imgy1-5; }			
			if( this.imgy0 < this.imgy1-this.boxmaxsize ) { 
				this.imgy0 = this.imgy1-this.boxmaxsize; }
		}
	}
	
	// DROP: Finishes the move by updating imgx/y0/1 to the current
	//          datax/y0/1 coordinates. The box is set to non-moving.
	// ### make sure box stays at least 2x2
	this.drop = function(){
		if( this.moving ){
			// Calculate new data coordinates
			datady = this.imganalobj.imgheight;
			// zoom = this.imganalobj.imgzoom;
			this.datax0 = Math.round(this.imgx0);
			this.datax1 = Math.round(this.imgx1);
			this.datay0 = datady - Math.round(this.imgy1);
			this.datay1 = datady - Math.round(this.imgy0);
			// Clear moving
			this.moving = 0;
			// Update
			this.update();
		}
		
	}

    this.disable = function() {
        // pass
    }
};

/**
 * ****** IMAGETOOLLINE OBJECT Object that creates a movable line, set between
 * two points and displays stats.
 */

// **** Constructor: creates the object
function imagetoollineobject() {
	// **** Object Variables
	this.imganalobj = null; // The imageanalysis object
	this.name = ''; // name that the tool has for the user
	this.active = false; // Flag indicating if the tool is used
	this.shown = true; // Flag indicating if the box is shown
	this.color = 'red'; // Color of the frame
	// this.boxmaxsize = 50; // Maximal size of the box in data units
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
	this.moving = 0;  // Flag indicating which points are being
                      // moved. If moving==0, the line is not being moved.
	                  // point1 ~ 1, point2 ~ 2, both points ~ 3
	this.mousex0 = 0; // IMG coordinates of the mouse position at the start
	this.mousey0 = 0; //     of the current move.
	this.pickupx0 = 0;  // IMG coordinates at pickup location
	this.pickupx1 = 10; //   while moving, corresponds to DATA
	this.pickupy0 = 0;  //   coordinates
	this.pickupy1 = 10;
	this.imgmin = 0;  // Holds min/max of the pixels in the box
	this.imgmax = 1;
    this.notyetactivated = true;

	// **** Object Functions

	// INIT: Initializes the analysis object (this is NOT the constructor)
	this.init = function(imganalobj) {
		// Assign variables
		this.imganalobj = imganalobj;

		// Initialize line size
        // console.log("Init for lineobject");
		this.datax0 = Math.round(this.imganalobj.imgwidth / 5);
		this.datax1 = this.imganalobj.imgwidth - this.datax0;
		this.datay0 = Math.round(this.imganalobj.imgheight / 5);
		this.datay1 = this.imganalobj.imgheight - this.datay0;

        this.draw();
	}

	// DRAW: Draws the box with the current color at the current location.
	this.draw = function() {
		if (this.shown & this.active) {
            

			// Get the canvas
			ctx = this.imganalobj.imgcan.getContext('2d');
			// Draw the square
			ctx.strokeStyle = this.color;
            // Try and keep the linewidth somewhat consistent when zooming
			ctx.lineWidth = Math.max(0.5, 2 * 1/this.imganalobj.imgzoom);
            ctx.beginPath();
            ctx.moveTo(this.imgx0, this.imgy0);
            ctx.lineTo(this.imgx1, this.imgy1);
            ctx.stroke();
            ctx.fillStyle = this.color;
            
            boxsize = Math.max(1, 6 * 1/this.imganalobj.imgzoom);
            ctx.fillRect(this.imgx0-boxsize/2, this.imgy0-boxsize/2, boxsize,boxsize);		
            ctx.fillRect(this.imgx1-boxsize/2, this.imgy1-boxsize/2, boxsize,boxsize);	
		} else {
            if (!this.notyetactivated) {
                this.notyetactivated = true;
            }  
        }
	}

    this.coordstoradec = function(coordx, coordy) {
        let msg = "";

        // Get the RA
        let hr = Math.floor(coordx/15);
        let mn = Math.floor(4*coordx-60*hr);
        let sc = 240*coordx-3600*hr-60*mn;
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
        msg += this.imganalobj.coordlblx + ' ' + hr.toFixed(0) + 'h' + mn + 'm' + sc + 's';
        
        let sn = '';
        // Get the DEC
        if(coordy<0){
            sn='-';
            coordy = -coordy;
        } else {
            sn='';
        }
        let dg = Math.floor(coordy);
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
        msg += ' / ' + this.imganalobj.coordlbly + ' ' + sn + dg.toFixed(0) + '&deg;' + mn + '\'' + sc + '"';

        return msg;
    }

	// UPDATE: Updates the tool: Recalculates the imgxy coordinates from dataxy.
	// Recalculates the statistics and prints it.
	this.update = function() {
		// If it's not active -> return
		if ( ! this.active ){
			return;
		}

        if (this.notyetactivated) {
                this.notyetactivated = false;
                // console.log(this.imganalobj)
                // console.log(this.imganalobj.imgwidth*this.imganalobj.imgzoom, this.imganalobj.imgcan.width, this.imganalobj.imgheight*this.imganalobj.imgzoom, this.imganalobj.imgcan.height)
                // console.log(this.imganalobj.pan)
                // If the image takes up less than the whole canvas, initialize the line across the image with some margin
                if (this.imganalobj.imgwidth*this.imganalobj.imgzoom < this.imganalobj.imgcan.width || this.imganalobj.imgheight*this.imganalobj.imgzoom < this.imganalobj.imgcan.height) {
                    this.imgx0 = Math.round(this.imganalobj.imgwidth / 5);
                    this.imgx1 = this.imganalobj.imgwidth - this.imgx0;
                    this.imgy0 = Math.round(this.imganalobj.imgheight / 5);
                    this.imgy1 = this.imganalobj.imgheight - this.imgy0;
                } else {
                    // Otherwise, initialize the line in the middle of the actual viewport
                    // console.log('init 2')

                    this.imgx0 = Math.round(-this.imganalobj.pan.x/this.imganalobj.imgzoom) + Math.round(this.imganalobj.imgcan.width/this.imganalobj.imgzoom/5);
                    this.imgx1 = this.imgx0 + this.imganalobj.imgcan.width/this.imganalobj.imgzoom - 2*Math.round(this.imganalobj.imgcan.width/this.imganalobj.imgzoom/5);

                    this.imgy0 = Math.round(-this.imganalobj.pan.y/this.imganalobj.imgzoom + this.imganalobj.imgcan.height/this.imganalobj.imgzoom/2);
                    this.imgy1 = this.imgy0;
                }

                datady = this.imganalobj.imgheight;
                this.datax0 = this.imgx0;
                this.datax1 = this.imgx1;
                this.datay0 = (datady-this.imgy0);
                this.datay1 = (datady-this.imgy1);
        }

		imglogadd('AnalLine: Going');
        datady = this.imganalobj.imgheight;
		zoom = this.imganalobj.imgzoom;
		this.datax0 = this.imgx0;
		this.datax1 = this.imgx1;
		this.datay0 = (datady-this.imgy0);
		this.datay1 = (datady-this.imgy1);

        // console.log("DATAY: " + this.datay0 + ", " + this.datay1);

        let x0 = this.datax0;
        let y0 = this.datay0;
        let x1 = this.datax1;
        let y1 = this.datay1;

        // Get a list of all the data on our line (rounds to nearest)
        // x0, y0 = psf_lines[img][0]
        // x1, y1 = psf_lines[img][1]
        // length = int(np.hypot(x1-x0, y1-y0))
        // x, y = np.linspace(x0, x1, length), np.linspace(y0, y1, length)
        //     # Extract values along this PSF line
        // psf_i = img_data[y.astype(int), x.astype(int)]
        let points_in_radec = "";
        
        // End points and length in arc seconds
        if (this.imganalobj.coords) {
            // console.log(this.imganalobj.coordx0, this.imganalobj.coordy0)

            let p0x = this.imganalobj.coordx0 + x0 * this.imganalobj.coordcolx + y0 * this.imganalobj.coordrowx;
            let p0y = this.imganalobj.coordy0 + x0 * this.imganalobj.coordcoly + y0 * this.imganalobj.coordrowy;
            let p1x = this.imganalobj.coordx0 + x1 * this.imganalobj.coordcolx + y1 * this.imganalobj.coordrowx;
            let p1y = this.imganalobj.coordy0 + x1 * this.imganalobj.coordcoly + y1 * this.imganalobj.coordrowy;

            console.table(x0, y0, x1, y1);
            console.table(p0x, p0y, p1x, p1y);

            if(this.imganalobj.coordlblx.toUpperCase().includes('RA') && this.imganalobj.coordlbly.toUpperCase().includes('DEC')){
                points_in_radec += "P0: " + this.coordstoradec(p0x, p0y) + "<br />";
                points_in_radec += "P1: " + this.coordstoradec(p1x, p1y) + "<br />";

                // Find the length in terms of arcseconds
                let diff_arcsec = Math.sqrt((p1x-p0x)**2 + (p1y-p0y)**2) * 3600;
                // TODO: Fix this...
                points_in_radec += "Total Distance: " + diff_arcsec.toFixed(1)+'"';
                points_in_radec += "<br /> Est. Plate Scale: " + (diff_arcsec / (Math.sqrt((x1-x0)**2 + (y1-y0)**2))).toFixed(3) + '"/pix';
            }
        }

        // console.log(points_in_radec);

        this.line_len = Math.round(Math.sqrt((x1-x0)**2 + (y1-y0)**2));
        let step_x = (x1-x0) / this.line_len;
        let step_y = (y1-y0) / this.line_len;

        // console.log(x0, y0);
        // console.log(x1, y1);
        // console.log(this.line_len);

        // TODO: Decide whether this should double count pixels or not (which
        // it currently does)
        let psf_i = [];
        let scaled_psf_i = [];
        for (let i = 0; i <= this.line_len; i++) {
            let cx = x0 + step_x * i;
            let cy = y0 + step_y * i;

            let yoff = Math.round(cy) * this.imganalobj.imgwidth;
			let data_index = yoff + Math.round(cx);

            // Add the scaled data to the graph points
            scaled_psf_i.push(this.imganalobj.imgscaled[data_index])

            if (isNaN(this.imganalobj.imgraw[data_index])) {
                psf_i.push(0)
            } else {
                psf_i.push(this.imganalobj.imgraw[data_index]);
            }
        }

        // console.log('PSF Data:');
        // console.log(psf_i);
        // let psf_max = Math.max(...psf_i);
        // console.log(psf_max);

        const chart_ctx = document.getElementById('psf_chart');

        if (!this.is_chart_init) {
            this.chart = new Chart(chart_ctx, {
                type: 'line',
                data: {
                labels: Array.from(Array(this.line_len).keys()),
                datasets: [{
                    label: 'Raw Counts',
                    data: psf_i,
                    borderWidth: 2,
                    backgroundColor: this.color,
                    borderColor: this.color,
                }]
                },
                options: {
                scales: {
                    y: {
                        beginAtZero: false
                    }
                },
				animation: false,
                elements: {
                    point: {
                        pointStyle: false
                    }
                },
                plugins: {
                    decimation: {
                        enabled: true
                    }
                }
                }
            });
            this.is_chart_init = true;
            chart_ctx.parentElement.style = "display: block;";
        } else {
            chart_ctx.parentElement.style = "display: block;";
            this.chart.data = {
                labels: Array.from(Array(this.line_len).keys()),
                datasets: [{
                    label: 'Raw Counts',
                    data: psf_i,
                    borderWidth: 2,
                    backgroundColor: this.color,
                    borderColor: this.color,
                }]
            }
            this.chart.update();
        }

        // TODO: Add RA/DEC information to CSV output
        // Prep the download information
        let col1_nums = Array.from(Array(this.line_len).keys());
        let col2_data = psf_i;
        let csv_data = col1_nums.map(function(e, i) {
            return [e, col2_data[i]];
        });
        let csv = arrayToCsv(csv_data);

		//** Display Statistics */
		$('#imagetoolsoutput1')
		.html('<div> \
			   P0: (' + this.imganalobj.valueformat(this.datax0) +
			  ', ' + this.imganalobj.valueformat(this.datay0) + ')' +
			  '<br />P1: (' + this.imganalobj.valueformat(this.datax1) +
              ', ' + this.imganalobj.valueformat(this.datay1) +  ')' +
              '<br />Length: ' + this.imganalobj.valueformat(this.line_len) +'px' +
              '<br /><a id="data_download">Download</a></div>' );
        
        // Set the download information
        // Give this a filename that includes the image name and the coordinates of the line
		let fname = this.imganalobj.filename.split('.')[0]+`_line_${this.datax0}_${this.datay0}_${this.datax1}_${this.datay1}.csv`
        let encoded_uri = getDownloadBlobURL(csv, fname, 'text/csv;charset=utf-8;')
        let link = document.getElementById('data_download');
        link.setAttribute("href", encoded_uri);
        link.setAttribute("download", fname);

        //** Display arc length */
        $('#imagetoolsoutput2').html(points_in_radec);
		
        // Set PSFcolor
		if(this.shown){
			textcol = {'red':'black','lime':'black','blue':'white',
					   'black':'white'}[this.color];
			$('#linecolor').css('background',this.color);
			$('#linecolor').css('color',textcol);
			linecolor = $('#linecolor')[0]
			linecolor.callback_object = this;
			linecolor.onclick = function() {
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
		$('#linecolor').css('background',this.color);
		$('#linecolor').css('color',textcol);
		this.update();
        this.imganalobj.imagedraw();
	}
	
	// PICKUP: Checks if the image mouse location (x/y) is correct to pick up
	//         the box. If so true is returned and the box is set to moving.
	this.pickup = function(mousex,mousey){
        // console.log("Line pickup at:");
        // console.log(mousex, mousey)
        // console.log(this.imgx0, this.imgy0, this.imgx1, this.imgy1);
		// Ignore if not shown or inactive
		if( ! this.shown || ! this.active) {
			return false;
		// Check if move is in progress: finish move
		} else if( this.moving > 0){
			this.drop();
			return false;
        // Check if mouse at a point
		// Check if mouse is inside the box
        } else if( (mousex - this.imgx0)**2 + (mousey - this.imgy0)**2 < 100 ) {
            this.moving = 1;
            console.log("P0 Picked");
            // Initialize move
			this.pickupx0 = this.imgx0;
			this.pickupx1 = this.imgx1;
			this.pickupy0 = this.imgy0;
			this.pickupy1 = this.imgy1;
			this.mousex0 = mousex;
			this.mousey0 = mousey;
            return true;
        } else if ( (mousex - this.imgx1)**2 + (mousey - this.imgy1)**2 < 100 ) {
            this.moving = 2;
            console.log("P1 Picked");
            // Initialize move  
			this.pickupx0 = this.imgx0;
			this.pickupx1 = this.imgx1;
			this.pickupy0 = this.imgy0;
			this.pickupy1 = this.imgy1;
			this.mousex0 = mousex;
			this.mousey0 = mousey;
            return true;
        } else if ( Math.abs((this.imgy1 - this.imgy0)*mousex - (this.imgx1 - this.imgx0)*mousey + this.imgx1*this.imgy0 - this.imgy1*this.imgx0) / Math.sqrt((this.imgx1-this.imgx0)**2 + (this.imgy1-this.imgy0)**2) < 10 ) {
            this.moving = 3;
            console.log("Both Picked");
            // Initialize move  
			this.pickupx0 = this.imgx0;
			this.pickupx1 = this.imgx1;
			this.pickupy0 = this.imgy0;
			this.pickupy1 = this.imgy1;
			this.mousex0 = mousex;
			this.mousey0 = mousey;
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

        // Set the limits
		imgdx = Math.round(this.imganalobj.imgwidth) - 1;
		imgdy = Math.round(this.imganalobj.imgheight) - 1;
		
        // Calculate mouse offsets
		mousedx = mousex-this.mousex0;
		mousedy = mousey-this.mousey0;

        // Debug
        // console.log("Moving: " + this.moving);
        // console.log(this.pickupx0, this.pickupy0, this.pickupx1, this.pickupy1);

        if (this.moving & 1) {
            this.imgx0 = this.pickupx0+mousedx;
            this.imgy0 = this.pickupy0+mousedy;
        }
        if (this.moving & 2) {
            this.imgx1 = this.pickupx1+mousedx;
            this.imgy1 = this.pickupy1+mousedy;
        }

		// check new coordinates
		if( mousedx < 0 ){
			// Check left
			if( this.imgx0 < 0 ) { this.imgx0 = 0; }
			if( this.imgx1 < 0 ) { this.imgx1 = 0; }
		} else {
			// Check right
			if( this.imgx1 > imgdx ) { this.imgx1 = imgdx; }
			if( this.imgx0 > imgdx) { this.imgx0 = imgdx; }
		}
		if( mousedy < 0){
			// Check top
			if( this.imgy0 < 0 ) { this.imgy0 = 0; }
			if( this.imgy1 < 0 ) { this.imgy1 = 0; }
		} else {
			// Check bottom
			if( this.imgy1 > imgdy ) { this.imgy1 = imgdy; }
			if( this.imgy0 > imgdy) { this.imgy0 = imgdy; }
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
			this.datax0 = Math.round(this.imgx0);
			this.datax1 = Math.round(this.imgx1);
			this.datay0 = this.imganalobj.imgheight - Math.round(this.imgy0);
			this.datay1 = this.imganalobj.imgheight - Math.round(this.imgy1);
			// Clear moving
			this.moving = 0;
            // console.log("Set moving to 0");
            // console.log(this.imgx0)
            // console.log(this.datax0, this.datay0, this.datax1, this.datay1);
			// Update
			this.update();
		}
		
	}

    this.doubleclick = function(mx, my){
        if (this.shown & this.active) {
            // console.log(this.imganalobj.pan)
            // If the image takes up less than the whole canvas, initialize the line across the image with some margin
            if (this.imganalobj.imgwidth*this.imganalobj.imgzoom < this.imganalobj.imgcan.width || this.imganalobj.imgheight*this.imganalobj.imgzoom < this.imganalobj.imgcan.height) {
                this.imgx0 = Math.round(this.imganalobj.imgwidth / 5);
                this.imgx1 = this.imganalobj.imgwidth - this.imgx0;
                this.imgy0 = Math.round(this.imganalobj.imgheight / 5);
                this.imgy1 = this.imganalobj.imgheight - this.imgy0;
            } else {
                // Otherwise, initialize the line in the middle of the actual viewport
                this.imgx0 = Math.round(-this.imganalobj.pan.x/this.imganalobj.imgzoom) + Math.round(this.imganalobj.imgcan.width/this.imganalobj.imgzoom/5);
                this.imgx1 = this.imgx0 + this.imganalobj.imgcan.width/this.imganalobj.imgzoom - 2*Math.round(this.imganalobj.imgcan.width/this.imganalobj.imgzoom/5);
                // Set to mouse y
                this.imgy0 = my / this.imganalobj.imgzoom;
                this.imgy1 = this.imgy0;
            }

            this.imgx0 = Math.round(this.imgx0);
            this.imgx1 = Math.round(this.imgx1);
            this.imgy0 = Math.round(this.imgy0);
            this.imgy1 = Math.round(this.imgy1);
        }
        // Update the data
		this.update();
		// Redraw the image
		this.imganalobj.imagedraw();
    }

    this.disable = function() {
        // Turn off the chart
        const chart_ctx = document.getElementById('psf_chart');
        chart_ctx.parentElement.style = "display: none;";
        console.log("disabling chart");
    }
};

// **** Logadd: adds log messages to #imagelog
function imglogadd(message){
	if(true){ // true/false
		time = (new Date()).toLocaleTimeString();
		$('#imagelog').append('<br>'+time+': '+message)
	}
}

// Below is from Seth 

/**
 * Convert a 2D array into a CSV string
 * Taken from https://stackoverflow.com/a/68146412
 */
function arrayToCsv(data){
  return data.map(row =>
    row
    .map(String)  // convert every value to String
    .map(v => v.replaceAll('"', '""'))  // escape double quotes
    .map(v => `"${v}"`)  // quote it
    .join(',')  // comma-separated
  ).join('\r\n');  // rows starting on new lines
}

/**
 * Download contents as a file
 * Source: https://stackoverflow.com/questions/14964035/how-to-export-javascript-array-info-to-csv-on-client-side
 */
function getDownloadBlobURL(content, filename, contentType) {
    // Create a blob
    var blob = new Blob([content], { type: contentType });
    var url = URL.createObjectURL(blob);
  
    return url;
}

/**
 * ****** IMAGETOOLELLIPSE OBJECT
 * With the help of Claude
 *
 * Object that creates a movable, rotatable ellipse defined by three control
 * points and reports the ellipse center plus the sum of the pixels enclosed.
 *
 * The three control points are:
 *   - center : sets the position of the ellipse.
 *   - MAJOR  : a point on the semi-major axis. Its distance from the center
 *              sets the semi-major length `a`, and its direction sets the
 *              rotation `theta` of the whole ellipse.
 *   - MINOR  : a point on the semi-minor axis. Dragging it aims the minor
 *              axis at the mouse, which sets the semi-minor length `b` and
 *              rotates the whole ellipse; the major axis stays perpendicular
 *              and keeps its length. (The major handle behaves the same way
 *              for its own axis, so you can rotate from either handle.)
 *
 * Coordinate conventions (identical to the other tools in this file):
 *   - IMG  coords : top-left origin, un-zoomed pixels. All handles are stored
 *                   in this frame and drawing happens in this frame (the canvas
 *                   already has translate(pan) + scale(zoom) applied, which is
 *                   why line widths / handle sizes are divided by imgzoom).
 *   - DATA coords : bottom-left origin. This is how imgraw[] is indexed
 *                   ( idx = datay*imgwidth + datax , datay==0 is the BOTTOM
 *                   row ) and what we report to the user.
 *   Relationship  : datax = imgx ,  datay = imgheight - imgy .
 *
 * Tool interface expected by imageanalysisobject:
 *   init(imganalobj), draw(), update(), pickup(mx,my)->bool,
 *   move(mx,my), drop(), doubleclick(mx,my), disable()
 *   + properties name/active/shown/color
 */

// **** Constructor: creates the object
function imagetoolellipseobject() {
	// **** Object Variables
	this.imganalobj = null;     // The imageanalysis object
	this.name = '';             // Name the tool has for the user
	this.active = false;        // Flag indicating if the tool is selected/used
	this.shown = true;          // Flag indicating if the ellipse is shown
	this.color = 'lime';        // Colour of the ellipse + handles

	// Ellipse geometry, stored in IMG coords (top-left origin, un-zoomed)
	this.cx = 0;                // center x
	this.cy = 0;                // center y
	this.a = 10;                // semi-major axis length (pixels)
	this.b = 5;                 // semi-minor axis length (pixels)
	this.theta = 0;             // rotation of the major axis (radians, IMG frame)

	// DATA-coord mirror of the center (bottom-left origin), set on drop()
	this.datacx = 0;
	this.datacy = 0;

	// Interaction state
	this.moving = 0;            // 0 none, 1 center, 2 major handle, 3 minor handle
	this.mousex0 = 0;           // IMG mouse position at the start of a move
	this.mousey0 = 0;
	this.pickupcx = 0;          // center at pickup (used when translating)
	this.pickupcy = 0;

	// Cached results of the last sum
	this.sum = 0;               // sum of enclosed raw pixel values
	this.npix = 0;              // number of (non-NaN) enclosed pixels

	// Deferred-placement flag (mirrors the line tool): when true, the next
	// update() lays the ellipse out for the current view. It is re-armed by
	// draw() whenever the tool is hidden/deactivated, exactly like the line
	// tool. ---> To make placement "sticky" (never auto-replace after the
	// first time), delete the re-arm block in draw() marked LINE-TOOL PARITY.
	this.notyetactivated = true;

	// Behaviour switches
	this.MINMAJOR = 2;          // minimum semi-major length, pixels
	this.MINMINOR = 2;          // minimum semi-minor length, pixels

	// **** Object Functions

	// HANDLES: returns the IMG-coord positions of the three control points,
	//          derived from the current geometry.
	this.handles = function() {
		var ct = Math.cos(this.theta), st = Math.sin(this.theta);
		return {
			center: { x: this.cx,                 y: this.cy },
			major:  { x: this.cx + this.a * ct,   y: this.cy + this.a * st },
			// perpendicular direction is (theta + 90deg) = (-sin, cos)
			minor:  { x: this.cx - this.b * st,   y: this.cy + this.b * ct }
		};
	}

	// VIEWREGION: returns the region the ellipse should be laid out into,
	//             as {cx, cy, w, h} in IMG coords. Mirrors the line tool's
	//             notyetactivated test:
	//   - If the whole image fits in the canvas (zoomed out) -> use the image.
	//   - Otherwise (zoomed in) -> use the currently visible viewport.
	this.viewregion = function() {
		var o = this.imganalobj;
		var zoom = o.imgzoom;
		var fullVisible = (o.imgwidth  * zoom < o.imgcan.width) ||
		                  (o.imgheight * zoom < o.imgcan.height);
		if (fullVisible) {
			// center of the image, sized relative to the image
			return { cx: o.imgwidth / 2, cy: o.imgheight / 2,
			         w: o.imgwidth,      h: o.imgheight };
		} else {
			// Visible viewport, expressed in IMG coords
			var vw = o.imgcan.width  / zoom;
			var vh = o.imgcan.height / zoom;
			var vx0 = -o.pan.x / zoom;        // viewport top-left (IMG coords)
			var vy0 = -o.pan.y / zoom;
			return { cx: vx0 + vw / 2, cy: vy0 + vh / 2, w: vw, h: vh };
		}
	}

	// CLAMPcenter: keep the center inside the image bounds (IMG coords).
	this.clampcenter = function() {
		var W = this.imganalobj.imgwidth, H = this.imganalobj.imgheight;
		if (this.cx < 0) { this.cx = 0; } else if (this.cx > W - 1) { this.cx = W - 1; }
		if (this.cy < 0) { this.cy = 0; } else if (this.cy > H - 1) { this.cy = H - 1; }
	}

	// PLACEINVIEW: full layout of the ellipse for the current view -- center,
	//              default size and axis-aligned orientation. Used for the
	//              deferred initial placement.
	this.placeInView = function() {
		var r = this.viewregion();
		this.cx = Math.round(r.cx);
		this.cy = Math.round(r.cy);
		this.a  = Math.max(this.MINMAJOR, Math.round(r.w / 5));
		this.b  = Math.max(this.MINMINOR, Math.round(r.h / 8));
		this.theta = 0;
		this.clampcenter();
		this.datacx = this.cx;
		this.datacy = this.imganalobj.imgheight - this.cy;
	}

	// INIT: Initialises the analysis object (this is NOT the constructor).
	//       The real placement is deferred to the first update() (so that the
	//       final zoom / pan / canvas size are known), via notyetactivated.
	//       We still set a sane fallback here.
	this.init = function(imganalobj) {
		this.imganalobj = imganalobj;
		this.notyetactivated = true;
		this.cx = Math.round(imganalobj.imgwidth / 2);
		this.cy = Math.round(imganalobj.imgheight / 2);
		this.a = Math.max(this.MINMAJOR, Math.round(imganalobj.imgwidth / 5));
		this.b = Math.max(this.MINMINOR, Math.round(imganalobj.imgheight / 8));
		this.theta = 0;
		this.datacx = this.cx;
		this.datacy = imganalobj.imgheight - this.cy;
	}

	// DRAW: Draws the ellipse + axis guides + handles in the current colour.
	//       Runs inside the already-transformed canvas context (IMG coords).
	this.draw = function() {
		if (!(this.shown & this.active)) {
			// ---- LINE-TOOL PARITY: re-arm deferred placement when hidden /
			//      deactivated, so re-showing re-centers on the current view.
			//      Delete these two lines to make placement sticky instead.
			if (!this.notyetactivated) { this.notyetactivated = true; }
			return;
		}

		var ctx  = this.imganalobj.imgcan.getContext('2d');
		var zoom = this.imganalobj.imgzoom;
		var lw   = Math.max(0.5, 2 * 1 / zoom);       // line width ~constant on screen
		var hs   = Math.max(1,   6 * 1 / zoom);       // handle size ~constant on screen
		var h    = this.handles();

		ctx.strokeStyle = this.color;
		ctx.fillStyle   = this.color;
		ctx.lineWidth   = lw;

		// Ellipse outline
		ctx.beginPath();
		ctx.ellipse(this.cx, this.cy, this.a, this.b, this.theta, 0, 2 * Math.PI);
		ctx.stroke();

		// Faint axis guide lines from center to each handle
		ctx.save();
		ctx.lineWidth = lw / 2;
		ctx.beginPath();
		ctx.moveTo(this.cx, this.cy); ctx.lineTo(h.major.x, h.major.y);
		ctx.moveTo(this.cx, this.cy); ctx.lineTo(h.minor.x, h.minor.y);
		ctx.stroke();
		ctx.restore();

		// center handle: small circle
		ctx.beginPath();
		ctx.arc(h.center.x, h.center.y, hs / 2, 0, 2 * Math.PI);
		ctx.fill();

		// Major handle: square
		ctx.fillRect(h.major.x - hs / 2, h.major.y - hs / 2, hs, hs);

		// Minor handle: diamond (rotated square) to distinguish it visually
		ctx.save();
		ctx.translate(h.minor.x, h.minor.y);
		ctx.rotate(Math.PI / 4);
		ctx.fillRect(-hs / 2, -hs / 2, hs, hs);
		ctx.restore();
	}

	// COLTOWORLD: converts DATA-coord (col,row) to world coords (degrees) using
	//             the same CD-matrix expansion as the line tool / mousemove().
	this.coltoworld = function(col, row) {
		var o = this.imganalobj;
		return {
			x: o.coordx0 + col * o.coordcolx + row * o.coordrowx,
			y: o.coordy0 + col * o.coordcoly + row * o.coordrowy
		};
	}

	// COORDSTORADEC: formats a (RA,Dec) pair in sexagesimal, same style as the
	//                line tool. coordx in degrees of RA, coordy in degrees Dec.
	this.coordstoradec = function(coordx, coordy) {
		var msg = "";
		var hr = Math.floor(coordx / 15);
		var mn = Math.floor(4 * coordx - 60 * hr);
		var sc = 240 * coordx - 3600 * hr - 60 * mn;
		mn = (mn < 10.0) ? '0' + mn.toFixed(0) : mn.toFixed(0);
		sc = (sc < 10.0) ? '0' + sc.toFixed(2) : sc.toFixed(2);
		msg += this.imganalobj.coordlblx + ' ' + hr.toFixed(0) + 'h' + mn + 'm' + sc + 's';

		var sn = '';
		if (coordy < 0) { sn = '-'; coordy = -coordy; }
		var dg = Math.floor(coordy);
		mn = Math.floor(60 * coordy - 60 * dg);
		sc = 3600 * coordy - 3600 * dg - 60 * mn;
		mn = (mn < 10.0) ? '0' + mn.toFixed(0) : mn.toFixed(0);
		sc = (sc < 10.0) ? '0' + sc.toFixed(1) : sc.toFixed(1);
		msg += ' / ' + this.imganalobj.coordlbly + ' ' + sn + dg.toFixed(0) + '&deg;' + mn + '\'' + sc + '"';
		return msg;
	}

	// CALCULATESUM: Sums the raw pixel values whose center lies inside the
	//               ellipse. Returns {sum, npix, mean}.
	//               imgraw is indexed in DATA coords, so each IMG pixel (ix,iy)
	//               maps to idx = (imgheight-1-iy)*imgwidth + ix .
	this.calculatesum = function() {
		var W = this.imganalobj.imgwidth;
		var H = this.imganalobj.imgheight;
		var raw = this.imganalobj.imgraw;
		var ct = Math.cos(this.theta), st = Math.sin(this.theta);
		var a2 = this.a * this.a, b2 = this.b * this.b;

		// Axis-aligned bounding box half-extents of the rotated ellipse
		var ex = Math.sqrt(a2 * ct * ct + b2 * st * st);
		var ey = Math.sqrt(a2 * st * st + b2 * ct * ct);

		var ixmin = Math.max(0,     Math.floor(this.cx - ex));
		var ixmax = Math.min(W - 1, Math.ceil (this.cx + ex));
		var iymin = Math.max(0,     Math.floor(this.cy - ey));
		var iymax = Math.min(H - 1, Math.ceil (this.cy + ey));

		var sum = 0.0, npix = 0;
		for (var iy = iymin; iy <= iymax; iy++) {
			var dataRow = (H - 1 - iy) * W;       // correct vertical flip
			var dyc = iy - this.cy;
			for (var ix = ixmin; ix <= ixmax; ix++) {
				var dxc = ix - this.cx;
				// Rotate the offset into the ellipse's own frame
				var xr =  dxc * ct + dyc * st;
				var yr = -dxc * st + dyc * ct;
				if ((xr * xr) / a2 + (yr * yr) / b2 <= 1.0) {
					var val = raw[dataRow + ix];
					if (!isNaN(val)) { sum += val; npix += 1; }
				}
			}
		}
		this.sum = sum;
		this.npix = npix;
		return { sum: sum, npix: npix, mean: (npix > 0 ? sum / npix : 0) };
	}

	// UPDATE: Refreshes DATA coords from IMG coords, recomputes the sum and
	//         writes the results into the tool output panels.
	this.update = function() {
		if (!this.active) { return; }

		// ---- Deferred initial placement (mirrors the line tool) ----
		// Runs the first time the tool is active+updated, when the real zoom /
		// pan / canvas size are known. Lays the ellipse out for the current
		// view (centerd on the image if fully visible, else on the viewport).
		if (this.notyetactivated) {
			this.notyetactivated = false;
			this.placeInView();
		}

		// Keep the DATA-coord center in sync with the IMG-coord center
		this.datacx = this.cx;
		this.datacy = this.imganalobj.imgheight - this.cy;

		var res = this.calculatesum();
		var fmt = (v) => this.imganalobj.valueformat(v);

		// ---- center (pixel coords, and RA/Dec when WCS is present) ----
		var centerMsg = 'center&nbsp;X/Y: (' + fmt(this.datacx) + ', ' + fmt(this.datacy) + ')';
		var abArcsec = '';   // appended to the a/b line when WCS is present
		if (this.imganalobj.coords) {
			// center in world coords (use the center as (col,row), like the line tool)
			var wc = this.coltoworld(this.datacx, this.datacy);
			if (this.imganalobj.coordlblx.toUpperCase().includes('RA') &&
			    this.imganalobj.coordlbly.toUpperCase().includes('DEC')) {
				centerMsg += '<br />' + this.coordstoradec(wc.x, wc.y);
			} else {
				centerMsg += '<br />' + this.imganalobj.coordlblx + ': ' + wc.x.toFixed(5) +
				             '<br />' + this.imganalobj.coordlbly + ': ' + wc.y.toFixed(5);
			}

			// Semi-axis lengths in arcsec: convert the major / minor axis
			// endpoints to world coords and take their separation from the
			// center, * 3600 (the same degree-distance method as the line tool).
			// Endpoints in DATA coords (datay = imgheight - imgy):
			var ct = Math.cos(this.theta), st = Math.sin(this.theta);
			var wMaj = this.coltoworld(this.datacx + this.a * ct,
			                           this.datacy - this.a * st);
			var wMin = this.coltoworld(this.datacx - this.b * st,
			                           this.datacy - this.b * ct);
			var aArcsec = Math.sqrt((wMaj.x - wc.x) ** 2 + (wMaj.y - wc.y) ** 2) * 3600;
			var bArcsec = Math.sqrt((wMin.x - wc.x) ** 2 + (wMin.y - wc.y) ** 2) * 3600;
			abArcsec = ' (' + aArcsec.toFixed(2) + '" / ' + bArcsec.toFixed(2) + '")';
		}

		// ---- Output panel 1 : checkbox + center + shape ----
		$('#imagetoolsoutput1').html('<form> \
			<input type="checkbox" id="ellipsebox"> \
			<span id="ellipsecolor">&nbsp;Ellipse&nbsp;</span></form>' +
			centerMsg +
			'<br />a / b: ' + fmt(this.a) + ' / ' + fmt(this.b) + ' px' + abArcsec +
			'<br />Angle: ' + (this.theta * 180 / Math.PI).toFixed(1) + '&deg;');

		// ---- Output panel 2 : the sum (the headline result) + extras ----
		$('#imagetoolsoutput2').html(
			'Sum: '   + fmt(res.sum) +
			'<br />Npix: '  + res.npix +
			'<br />Mean: '  + fmt(res.mean));

		// Wire the show/hide checkbox
		var ebox = $('#ellipsebox')[0];
		ebox.callback_object = this;
		ebox.onchange = function() { this.callback_object.checkhandler(); };
		ebox.checked = this.shown;

		// Wire the colour swatch (shared #linecolor element, like the other tools)
		if (this.shown) {
			var textcol = { 'red':'black','lime':'black','blue':'white','black':'white' }[this.color];
			$('#linecolor').css('background', this.color);
			$('#linecolor').css('color', textcol);
			var lc = $('#linecolor')[0];
			lc.callback_object = this;
			lc.onclick = function() { this.callback_object.boxcolor(); };
		}

		// If the image scale is driven by a box selection, refresh options
		if (this.imganalobj.imgscale == 'Box') {
			this.imganalobj.updateOptions('', 'Box', '');
		}
	}

	// CHECKHANDLER: toggles shown, updates and redraws.
	this.checkhandler = function() {
		this.shown = !this.shown;
		this.update();
		this.imganalobj.imagedraw();
	}

	// BOXCOLOR: cycles the ellipse colour (same palette/order as the other tools).
	this.boxcolor = function() {
		this.color = { 'red':'lime','lime':'blue','blue':'black','black':'red' }[this.color];
		var textcol = { 'red':'black','lime':'black','blue':'white','black':'white' }[this.color];
		$('#linecolor').css('background', this.color);
		$('#linecolor').css('color', textcol);
		this.update();
		this.imganalobj.imagedraw();
	}

	// PICKUP: hit-tests the three handles. mousex/mousey arrive in IMG coords.
	//         The grab radius is scaled by 1/zoom so the on-screen target stays
	//         ~10 px regardless of zoom level.
	this.pickup = function(mousex, mousey) {
		if (!this.shown || !this.active) { return false; }
		if (this.moving > 0) { this.drop(); return false; }

		var zoom = this.imganalobj.imgzoom;
		var grab = Math.max(6, 10 / zoom);     // grab radius in IMG pixels
		var grab2 = grab * grab;
		var h = this.handles();

		// Helper to start a move (stash pickup state)
		var begin = (mode) => {
			this.moving = mode;
			this.pickupcx = this.cx;
			this.pickupcy = this.cy;
			this.mousex0 = mousex;
			this.mousey0 = mousey;
			return true;
		};

		// Check the axis handles first, then the center.
		if ((mousex - h.major.x) ** 2 + (mousey - h.major.y) ** 2 < grab2) { return begin(2); }
		if ((mousex - h.minor.x) ** 2 + (mousey - h.minor.y) ** 2 < grab2) { return begin(3); }
		if ((mousex - h.center.x) ** 2 + (mousey - h.center.y) ** 2 < grab2) { return begin(1); }

		// Otherwise: grabbing anywhere inside the ellipse also moves it.
		var ct = Math.cos(this.theta), st = Math.sin(this.theta);
		var dxc = mousex - this.cx, dyc = mousey - this.cy;
		var xr =  dxc * ct + dyc * st;
		var yr = -dxc * st + dyc * ct;
		if ((xr * xr) / (this.a * this.a) + (yr * yr) / (this.b * this.b) <= 1.0) {
			return begin(1);
		}
		return false;
	}

	// MOVE: applies the drag. mousex/mousey arrive in IMG coords.
	this.move = function(mousex, mousey) {
		var W = this.imganalobj.imgwidth;
		var H = this.imganalobj.imgheight;

		if (this.moving === 1) {
			// Translate the center, clamped to the image.
			this.cx = this.pickupcx + (mousex - this.mousex0);
			this.cy = this.pickupcy + (mousey - this.mousey0);
			this.clampcenter();

		} else if (this.moving === 2) {
			// Major handle sets BOTH the semi-major length and the rotation.
			var dx = mousex - this.cx, dy = mousey - this.cy;
			this.a = Math.max(this.MINMAJOR, Math.sqrt(dx * dx + dy * dy));
			this.theta = Math.atan2(dy, dx);

		} else if (this.moving === 3) {
			// Minor handle sets BOTH the semi-minor length and the rotation.
			// The minor axis lies at (theta + 90deg), so aiming it at the mouse
			// gives theta = atan2(dy,dx) - 90deg. The major axis stays
			// perpendicular and keeps its current length, so the figure remains
			// a proper ellipse -- this mirrors the major handle's behaviour.
			var dx = mousex - this.cx, dy = mousey - this.cy;
			this.b = Math.max(this.MINMINOR, Math.sqrt(dx * dx + dy * dy));
			this.theta = Math.atan2(dy, dx) - Math.PI / 2;
		}
	}

	// DROP: finishes the move, syncs DATA coords, recomputes and redraws.
	this.drop = function() {
		if (this.moving) {
			this.datacx = Math.round(this.cx);
			this.datacy = this.imganalobj.imgheight - Math.round(this.cy);
			this.moving = 0;
			this.update();
		}
	}

	// DOUBLECLICK: moves the ellipse to the center of the viewer's current
	//              position (mirrors the line tool's double-click). The mouse
	//              coords arrive as (offsetX - pan.x, offsetY - pan.y), i.e.
	//              screen pixels from the image top-left; we recenter on the
	//              viewport so they are not needed directly. The shape
	//              (a, b, theta) is preserved -- only the center moves.
	this.doubleclick = function(mx, my) {
		if (this.shown & this.active) {
			var r = this.viewregion();
			this.cx = Math.round(r.cx);
			this.cy = Math.round(r.cy);
			this.clampcenter();
			this.datacx = this.cx;
			this.datacy = this.imganalobj.imgheight - this.cy;
		}
		// Recompute + redraw (the main dispatcher also calls update(), which is
		// harmless; kept here for parity with the line tool).
		this.update();
		this.imganalobj.imagedraw();
	}

	// DISABLE: nothing to tear down (no chart, unlike the PSF/line tools).
	this.disable = function() {
		// pass
	}
};

	
/***
 * === History ===
 * 2019 Feb: Marc Berthoud - Fix getting scaling options from cookies
 * 
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
