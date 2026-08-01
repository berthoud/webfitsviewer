/***********************************************************************

DATASCRIPTS.JS

These functions are used by the pipeline data page to dynamically display
data and load new content.

***********************************************************************/

//**** Global Variables
// HTML data
var request1; // XMLHttpRequest object
var sid; // Session ID
var baseurlpath; // base url path to make absolute URL paths
// Image display
var width; // Image Width
var height; // Image Height
var imgraw; // 1D Array of raw image data - length==0 if data not yet arrived
var imgrawsort; // image data sorted
var imgmin, imgmax; // Scale min and max values
var imgzoom = 2.0; // Zoom factor (i.e. zoom in if >1)
var imgcan; // canvas object
// Analysis image (Zoom) display
var analcan; // canvas object for analysis

//**** Create ImageAnalysis object

// Constructor: create the object
function imageanalysisobject(){
	//**** Object Variables
	// General Variables
	this.request = new XMLHttpRequest();
	// Image Variables
	this.imgwidth=0; // Width of raw image
	this.imgheight=0; // Height of raw image
	this.imgraw = new Array(0); // 1D Array of raw image data
	                            //   length==0 if data not yet arrived
	this.imgrawsort = new Array(0); // Image data sorted
	this.imgmin = 0.0; // Scale min value
	this.imgmax = 1.0; // Scale max value
	this.imgzoom = 1.0; // Zoom factor (i.e. zoom in if >1)
	this.imgcan = 0; // image canvas object
	// Analysis tools variables
	this.analcan = 0; // canvas for analysis object
	this.analsize = 160; // size of analysis window
	
	//**** Object Functions
	// WriteTools: writes the HTML code for the image analysis tools
	this.writetools = function() {
		document.writeln(''+
		    '<table><tr><td class = "tools">'+
		    '<div id = "imageinfo">'+
		    'Mouse X / Y:<br>&nbsp;<br>Value:<br>&nbsp;</div>'+
		    '<td class = "tools"><form>'+
		    'Zoom:<br>'+
		    '<select id = "zoomselect" disabled>'+
		    '<option>1/10</option>'+
		    '<option>1/3</option>'+
		    '<option>1x</option>'+
		    '<option>3x</option>'+
		    '<option>10x</option>'+
		    '</select><br>'+
		    'Scale:<br>'+
		    '<select onChange = "" disabled>'+
		    '<option>MinMax</option>'+
		    '<option>98%</option>'+
		    '<option>90%</option>'+
		    '<option>5 StDev</option>'+
		    '</select>'+
		    '</form>'+
		    '</table>'+
		    '<canvas id = "analcanvas" width = "160" height = "160"'+
		    '        style="border: solid 2px #ff0000;">'+
		    'Your Browser does not support HTML5 - Canvas Elements - please upgrade.'+
		    '</canvas>');
	}
	
	// WriteDisplay: writes the HTML code for the image display
	this.writedisplay = function() {
		document.writeln(''+
		    '<div id = "imagemsg"></div>'+
			'<div id = "imagestat">Initializing</div>'+
			'<div id = "imagediv" style = "width:100%;'+
			'     overflow:auto; border:solid 1px #CCC;">'+
			'<canvas id = "imagecanvas" width="200" height="200">'+
			'Your Browser does not support HTML5 - Canvas Elements'+
			'- please upgrade.'+
			'</canvas>'+
			'</div>');
	}
	
	// Init: initializes the objec and requests the data
	//       This function needs to be called after writetools and
	//       writedisplay such that the DOM elements can be accessed
	//       using getElementbyId.
	this.init = function(dataurl, previewurl) {
		// get canvas and set size
		this.imgcan = document.getElementById('imagecanvas');
		imgctx = this.imgcan.getContext('2d');
		// load preview image
		if(previewurl){
			img = new Image();
			img.onload = function(){
				this.imgcan = document.getElementById('imagecanvas');
				this.imgcan.width = img.width;
				this.imgcan.height = img.height;
				imgctx.drawImage(img,0,0);
			}
			img.src = previewurl;
		}
		// Fill zoom image with black
		this.analcan = document.getElementById('analcanvas');
		analctx = analcan.getContext('2d');
		analctx.fillstyle='rgb(0,0,0)';
		analctx.fillRect(0, 0, this.analsize, this.analsize);
		// set imgraw to empty array
		this.imgraw = new Array(0);
		// Set up the request object callback
		// ( Has to be done b/c onreadystatuschange has request as "this" )
		this.request.callback_object = this;
		this.request.onreadystatechange = function(){
			if (this.readyState==4 && this.status==200){
				this.callback_object.imageopen();
			}
		}
		// fill the request
		urlsplit = dataurl.split('?');
		this.request.open("POST", urlsplit[0], true);
		this.request.send(urlsplit[1]);
		// update message
		document.getElementById('imagestat').innerHTML = 'Loading Image Data';
	}
	
	// ImageOpen: Opens the image
	this.imageopen = function() {
		// update message
		document.getElementById('imagestat').innerHTML = 'Unpacking Image';
		// get header and data
		headend = this.request.responseText.indexOf('data = ');
		headtxt = this.request.responseText.substring(0, headend);
		datatxt = this.request.responseText.substring(headend + 7);
		// get header values
		ind = headtxt.indexOf('width = ') + 8;
		this.imgwidth = parseInt(headtxt.substring(ind));
		ind = headtxt.indexOf('height = ') + 9;
		this.imgheight = parseInt(headtxt.substring(ind));
		ind = headtxt.indexOf('bzero = ') + 8;
		bzero = parseFloat(headtxt.substring(ind));
		ind = headtxt.indexOf('bscale = ') + 9;
		bscale = parseFloat(headtxt.substring(ind));
		ind = headtxt.indexOf('message = ') + 10;
		len = headtxt.substring(ind).indexOf('\n');
		message = headtxt.substr(ind,len);
		// Set message
		document.getElementById('imagemsg').innerHTML = message;
		// get data values
		this.imgraw = new Array(this.imgwidth*this.imgheight);
		for (i = 0; i< this.imgwidth*this.imgheight; i++){
			val = parseInt(datatxt.substr(4*i,4),16);
			this.imgraw[i] = bzero + bscale * val;
		}
		// print result (for testing)
		d='';
		for ( i=0; i<5; i++){
			d += ' '+this.imgraw[i];
		}
		document.getElementById('imagestat').innerHTML = 'w=' + this.imgwidth + 
	        ' h=' + this.imgheight + ' b0=' + bzero + ' bs=' + bscale;
		// Set object callback for canvas mousemove
		this.imgcan.callback_object = this;
		this.imgcan.onmousemove = function(event){
			this.callback_object.mousehandler(event);
		}
		// get color scale
		this.imgrawsort = this.imgraw.slice()
		this.imgrawsort.sort(function callback(a,b){ return a-b; })
		this.imgmin = this.imgrawsort[0]
		this.imgmax = this.imgrawsort[this.imgwidth*this.imgheight-1]
		// Set zoom size (make sure diagonal is at least 300 pixels long)
		this.imgzoom = 1.0;
		diag = Math.sqrt(this.imgwidth*this.imgwidth + 
				         this.imgheight*this.imgheight);
		while( this.imgzoom * diag < 300){
			this.imgzoom += 1.0;
		}
		// Set zoom selection dropdown
		zoomsel = document.getElementById('zoomselect');
		zoomsel.disabled = false;
		if( this.imgzoom > 1.0 ){
			// If zoom > 1 -> add "Auto" option to select and select it
			ind = zoomsel.length;
			option = document.createElement("option");
			option.text = 'Auto';
			zoomsel.add(option, null);
			zoomsel.selectedIndex = ind;
		} else {
			// If zoom == 1 -> select 1x option
			found = -1;
			for (i=0; i<zoomsel.length; i++){
				if (zoomsel.options[i].text == '1x'){
					found = i;
				}
			}
			if( found > -1 ){ zoomsel.selectedIndex = found; }
		}
		// Set zoomselect onChange function
		zoomsel.callback_object = this;
		zoomsel.onchange = function(){
			this.callback_object.zoomhandler();
		}
		log = document.getElementById('imagestat').innerHTML;
		document.getElementById('imagestat').innerHTML = log + 
		    ' min='+this.imgmin+' max='+this.imgmax+' zoom='+this.imgzoom;
		// Display Image
		this.imagedisplay();
		// Done message
		log = document.getElementById('imagestat').innerHTML;
		document.getElementById('imagestat').innerHTML = log + 
		    '<br>Done';
		//document.getElementById('imagemsg').innerHTML = 'Done';
	}
	
	// ImageDisplay: Displays the image using current scale and zoom settings
	this.imagedisplay = function(){
		// get display size (limit display size to 5000 x 5000)
		dispwidth = Math.round( this.imgwidth * this.imgzoom);
		if( dispwidth > 5000 ){
			dispwidth = 5000;
		}
		dispheight = Math.round( this.imgheight * this.imgzoom);
		if(dispheight > 5000 ){
			dispheight = 5000;
		}
		// get canvas context
		ctx = this.imgcan.getContext('2d');
		// make canvas image
		canimg = ctx.createImageData(dispwidth, dispheight);
		// fill canvas image
		imgdiff = this.imgmax-this.imgmin;
		for( y=0; y<dispheight; y+=1){
			for( x=0; x<dispwidth; x+=1){
				imgx = Math.floor(x/this.imgzoom);
				imgy = Math.floor(y/this.imgzoom);
				i = imgy * width + imgx;
				j = ( dispheight - 1 - y) * dispwidth + x;
				cval = Math.round( 255.0 * (this.imgraw[i] - this.imgmin)
						                 / imgdiff);
				(canimg.data)[4*j] = cval;
				(canimg.data)[4*j+1] = cval;
				(canimg.data)[4*j+2] = cval;
				(canimg.data)[4*j+3] = 255;
			} 
		}
		// set canvas size
		this.imgcan.width = dispwidth;
		this.imgcan.height = dispheight;
		// draw image
		ctx.putImageData(canimg,0,0);
	}
	
	// Mousehandler: Responds to mouse events
	this.mousehandler = function(event){
		//**** Update location / value display
		// Get x and y and display them
		scrollx = document.getElementById('imagediv').scrollLeft;
		xi = event.pageX - this.imgcan.offsetLeft + scrollx;
		yi = Math.round(this.imgzoom * height) + this.imgcan.offsetTop - event.pageY;
		xi = Math.floor(xi/this.imgzoom);
		yi = Math.floor(yi/this.imgzoom);
		i = yi * width + xi;
		val = this.imgraw[ i ];
		if ( Math.abs(val) > 1e5 || Math.abs(val) < 1e-2 && Math.abs(val) > 0.0){
			val = val.toExponential(4);
		} else {
			val = val.toPrecision(5);
		}
		// Make message
		msg = 'Mouse X / Y:<br>&nbsp;&nbsp;';
		msg += xi + ' / ' + yi;
		msg += '<br>Value:<br>&nbsp;&nbsp;' + val;
		document.getElementById('imageinfo').innerHTML = msg;
		//**** Update Mouse analysis window
		// make image
		ctx = this.analcan.getContext('2d');
		canimg = ctx.createImageData(160,160);
		// copy and scale data
		imgdiff = this.imgmax-this.imgmin;
		sqrrad = Math.ceil(3.0*this.imgzoom); // "radius" of square
		carr = new Array(4)
		// loop over analysis image pixels
		for(ay = 0; ay<160; ay++){
			for(ax = 0; ax<160; ax++){
				// get px and py coordinates of real pixel
				px = xi + Math.round((ax-80)/(6*this.imgzoom));
				py = yi + Math.round((80-ay)/(6*this.imgzoom));
				// get value (255.0 if it's outside the image)
				if( px < 0 || py < 0 || px >= this.imgwidth || py >= this.imgheight){
					cval = 255.0;
				} else {
					i = (py * this.imgwidth) + px;
					cval = Math.round(255.0 * (this.imgraw[i] - this.imgmin) / imgdiff);
				}
				// get color (but make a red frame around center pixel
				dx = Math.round(Math.abs(ax-80));
				dy = Math.round(Math.abs(ay-80));
				if( (dx == sqrrad && dy <= sqrrad ) || 
					(dy == sqrrad && dx <= sqrrad )){
					carr[0]=255;
					carr[1]=0;
					carr[2]=0;
					carr[3]=255;
				} else {
					carr[0]=cval;
					carr[1]=cval;
					carr[2]=cval;
					carr[3]=255;
				}
				// set pixel value
				i = ay * 160 + ax;
				for( j=0; j<4; j++){
					(canimg.data)[4*i+j] = carr[j];
				}
			}
		}
		// copy image to display
		ctx.clearRect(0,0,160,160);
		ctx.beginPath();
		ctx.putImageData(canimg,0,0);
	}
	
	// Zoomhandler:
	this.zoomhandler = function(){
		// Select determine new zoom value
		selectobj = document.getElementById('zoomselect');
		optlist = selectobj.options;
		switch (optlist[selectobj.selectedIndex].text){
		case '1/10': this.imgzoom = 0.1; break;
		case '1/3': this.imgzoom = 0.33333; break;
		case '1x': this.imgzoom = 1.0; break;
		case '3x': this.imgzoom = 3.0; break;
		case '10x': this.imgzoom = 10.0; break;
		}
		// Clear Auto option if present
		found = -1;
		for (i=0; i<selectobj.length; i++){
			if( optlist[i].text == 'Auto') found = i;
		}
		if( found > -1) selectobj.remove(found);
		// Draw image
		this.imagedisplay();
	}
}

//**** Functions Declarations

// DataInit: Send request for image data
function datainit(fileurlpathname) {
	//**** Load the image
	// get canvas and set size
	imgcan = document.getElementById('imagecanvas1');
	imgcan.width = width;
	imgcan.height = height;
	ctx = imgcan.getContext('2d');
	// load image
	img = new Image();
	img.onload = function(){
		ctx.drawImage(img,0,0);
	}
	img.src = fileurlpathname;
	// Fill zoom image with black
	analcan = document.getElementById('analcanvas1');
	analctx = analcan.getContext('2d');
	analctx.fillstyle='rgb(0,0,0)';
	analctx.fillRect(0,0,100,100);
	//**** Make the request for image data
	// set imgraw to empty array
	imgraw = new Array(0);
	// make a request object
	request1 = new XMLHttpRequest();
	request1.onreadystatechange = imageopen1;
	// fill the request
	request1.open("POST", baseurlpath+"/data/raw", true);
	request1.send("sid="+sid);
	// update message
	document.getElementById('imagestat1').innerHTML = 'Loading Image Data1';
}

// ImageOpen: Response function for the data request, opens up the image
function imageopen1() {
	// Check if the response is ready
	if (request1.readyState==4 && request1.status==200){
		// update message
		document.getElementById('imagestat1').innerHTML = 'Unpacking Image';
		// get header and data
		headend = request1.responseText.indexOf('data = ');
		headtxt = request1.responseText.substring(0, headend);
		datatxt = request1.responseText.substring(headend + 7);
		// get header values
		ind = headtxt.indexOf('width = ') + 8;
		width = parseInt(headtxt.substring(ind));
		ind = headtxt.indexOf('height = ') + 9;
		height = parseInt(headtxt.substring(ind))
		ind = headtxt.indexOf('bzero = ') + 8;
		bzero = parseFloat(headtxt.substring(ind));
		ind = headtxt.indexOf('bscale = ') + 9;
		bscale = parseFloat(headtxt.substring(ind));
		ind = headtxt.indexOf('message = ') + 10;
		len = headtxt.substring(ind).indexOf('\n');
		message = headtxt.substr(ind,len);
		// Set message
		document.getElementById('imagemsg1').innerHTML = message;
		// get data values
		imgraw = new Array(width*height);
		for (i = 0; i< width*height; i++){
			val = parseInt(datatxt.substr(4*i,4),16);
			imgraw[i] = bzero + bscale * val;
		}
		// print result (for testing)
		d='';
		for ( i=0; i<5; i++){
			d += ' '+imgraw[i];
		}
		document.getElementById('imagestat1').innerHTML = 'w=' + width + 
	        ' h=' + height + ' b0=' + bzero + ' bs=' + bscale;
		// set canvas mousemove
		imgcan.onmousemove = mousehandler;
		// get color scale
		imgrawsort = imgraw.slice()
		imgrawsort.sort(function callback(a,b){ return a-b; })
		imgmin = imgrawsort[0]
		imgmax = imgrawsort[width*height-1]
		// Set zoom size (make sure diagonal is at least 300 pixels long)
		imgzoom = 1.0;
		diag = Math.sqrt(width*width + height*height);
		while( imgzoom * diag < 300){
			imgzoom += 1.0;
		}
		// Set zoom selection dropdown
		zoomsel = document.getElementById('zoomselect1');
		zoomsel.disabled = false;
		if( imgzoom > 1.0 ){
			// If zoom > 1 -> add "Auto" option to select and select it
			ind = zoomsel.length;
			option = document.createElement("option");
			option.text = 'Auto';
			zoomsel.add(option, null);
			zoomsel.selectedIndex = ind;
		} else {
			// If zoom == 1 -> select 1x option
			found = -1;
			for (i=0; i<zoomsel.length; i++){
				if (zoomsel.options[i].text == '1x'){
					found = i;
				}
			}
			if( found > -1 ){ zoomsel.selectedIndex = found; }
		}
		log = document.getElementById('imagestat1').innerHTML;
		document.getElementById('imagestat1').innerHTML = log + 
		    ' min='+imgmin+' max='+imgmax+' zoom='+imgzoom;
		// Display Image
		imagedisplay();
		// Done message
		log = document.getElementById('imagestat1').innerHTML;
		document.getElementById('imagestat1').innerHTML = log + 
		    '<br>Done';
		//document.getElementById('imagemsg').innerHTML = 'Done';
	}
}

// ImageDisplay: Displays the image using current scale and zoom settings
function imagedisplay(){
	// get display size (limit display size to 5000 x 5000)
	dispwidth = Math.round( width * imgzoom);
	if( dispwidth > 5000 ){
		dispwidth = 5000;
	}
	dispheight = Math.round( height * imgzoom);
	if(dispheight > 5000 ){
		dispheight = 5000;
	}
	// get canvas context
	ctx = imgcan.getContext('2d');
	// make canvas image
	canimg = ctx.createImageData(dispwidth, dispheight);
	// fill canvas image
	imgdiff = imgmax-imgmin;
	for( y=0; y<dispheight; y+=1){
		for( x=0; x<dispwidth; x+=1){
			imgx = Math.floor(x/imgzoom);
			imgy = Math.floor(y/imgzoom);
			i = imgy * width + imgx;
			j = ( dispheight - 1 - y) * dispwidth + x;
			cval = Math.round( 255.0 * (imgraw[i] - imgmin) / imgdiff);
			(canimg.data)[4*j] = cval;
			(canimg.data)[4*j+1] = cval;
			(canimg.data)[4*j+2] = cval;
			(canimg.data)[4*j+3] = 255;
		} 
	}
	// set canvas size
	imgcan.width = dispwidth;
	imgcan.height = dispheight;
	// draw image
	ctx.putImageData(canimg,0,0);
}

// Mousehandler: Responds to mouse events
function mousehandler(event){
	//**** Update location / value display
	// Get x and y and display them
	scrollx = document.getElementById('imagediv1').scrollLeft;
	xi = event.pageX - imgcan.offsetLeft + scrollx;
	yi = Math.round(imgzoom * height) + imgcan.offsetTop - event.pageY;
	xi = Math.floor(xi/imgzoom);
	yi = Math.floor(yi/imgzoom);
	i = yi * width + xi;
	val = imgraw[ i ];
	if ( Math.abs(val) > 1e5 || Math.abs(val) < 1e-2 && Math.abs(val) > 0.0){
		val = val.toExponential(4);
	} else {
		val = val.toPrecision(5);
	}
	// Make message
	msg = 'Mouse X / Y:<br>&nbsp;&nbsp;';
	msg += xi + ' / ' + yi;
	msg += '<br>Value:<br>&nbsp;&nbsp;' + val;
	document.getElementById('imageinfo1').innerHTML = msg;
	//**** Update Mouse analysis window
	// make image
	ctx = analcan.getContext('2d');
	canimg = ctx.createImageData(160,160);
	// copy and scale data
	imgdiff = imgmax-imgmin;
	sqrrad = Math.ceil(3.0*imgzoom); // "radius" of square
	carr = new Array(4)
	// loop over analysis image pixels
	for(ay = 0; ay<160; ay++){
		for(ax = 0; ax<160; ax++){
			// get px and py coordinates of real pixel
			px = xi + Math.round((ax-80)/(6*imgzoom));
			py = yi + Math.round((80-ay)/(6*imgzoom));
			// get value (255.0 if it's outside the image)
			if( px < 0 || py < 0 || px >= width || py >= height){
				cval = 255.0;
			} else {
				i = (py * width) + px;
				cval = Math.round(255.0 * (imgraw[i] - imgmin) / imgdiff);
			}
			// get color (but make a red frame around center pixel
			dx = Math.round(Math.abs(ax-80));
			dy = Math.round(Math.abs(ay-80));
			if( (dx == sqrrad && dy <= sqrrad ) || 
				(dy == sqrrad && dx <= sqrrad )){
				carr[0]=255;
				carr[1]=0;
				carr[2]=0;
				carr[3]=255;
			} else {
				carr[0]=cval;
				carr[1]=cval;
				carr[2]=cval;
				carr[3]=255;
			}
			// set pixel value
			i = ay * 160 + ax;
			for( j=0; j<4; j++){
				(canimg.data)[4*i+j] = carr[j];
			}
		}
	}
	// copy image to display
	ctx.clearRect(0,0,160,160);
	ctx.beginPath();
	ctx.putImageData(canimg,0,0);
}

// Zoomhandler: Responds to zoom selection events
function zoomhandler(){
	// Select determine new zoom value
	selectobj = document.getElementById('zoomselect1');
	optlist = selectobj.options;
	switch (optlist[selectobj.selectedIndex].text){
	case '1/10': imgzoom = 0.1; break;
	case '1/3': imgzoom = 0.33333; break;
	case '1x': imgzoom = 1.0; break;
	case '3x': imgzoom = 3.0; break;
	case '10x': imgzoom = 10.0; break;
	}
	// Clear Auto option if present
	found = -1;
	for (i=0; i<selectobj.length; i++){
		if( optlist[i].text == 'Auto') found = i;
	}
	if( found > -1) selectobj.remove(found);
	// Draw image
	imagedisplay();
}
