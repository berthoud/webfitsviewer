""" VIEWS.PY
    The site view provides the contents for the requests to the website.
    The view is instructed by the controller to produce strings that are
    added to the output.
"""

### Preparation
import os
import string
import time
import logging
import math
import numpy
from astropy.wcs import WCS

### Class Definition
class SiteViews(object):
    """ Views object creates the contents of the response to the http
        request.
    """

    def __init__(self, environ, session, config):
        """ Constructor: declares the variables
        """
        # Declare Variables
        self.env = environ
        self.session = session
        self.conf = config
        self.model = None # Model object
        # Make logger
        self.log = logging.getLogger('webview.views')
        self.log.debug('Initialized')
        # Get foldernames
        self.foldernames = self.conf['view']['foldernames'].split(os.sep)

    def header(self):
        """ Returns the text for the page header
        """
        # Make text string
        #   Entries: pagetitle%s stylefile%s iconfilepathname%s
        #            scriptsinclude%s logofilepathname%s sitetitle%s
        #            siteurl%s listfolder%s listlabel%s
        #            siteurl%s siteurl%s helpurl%s searchurl%s
        text = """
<!DOCTYPE html>
<html>
<head>
<title>%s</title>
<link rel = "stylesheet" type = "text/css" href = "%s">
<link rel = "icon" type = "image/png" href = "%s">
%s</head>
<body>
<table class = "header">
<tr><td class = "header" width = "150" align = "center" rowspan=2>
<img src = "%s">
<td class = "header" align = "center" valign = "middle" colspan=5>
<h1>%s</h1>
<td class = "header" width = "150">
<tr>
<td class = "header" align = "left"><b>Options:</b>
<td class = "header" align = "left"><a href = "%s/list%s">%s</a>
<td class = "header" align = "left"><a href = "%s/data">Data Viewer</a>
<td class = "header" align = "left"><a href = "%s/log">Pipeline Log</a>
<td class = "header" align = "left"><a href = "%s" target = "_blank">Help / Manual</a>
<td class = "header">%s
</table>
"""
        # Make image folder
        staticpath = self.conf['path']['static']
        # Make listlabel (label for list view considering folder names)
        listlabel = ' / '.join(self.foldernames)
        listlabel = '%s List' % listlabel
        # Make pagetitles
        titlelist = {'data':': Data Display',
                     'log':': Pipeline Log',
                     'error':': Error',
                     'list':': '+listlabel,
                     'search':': Search',
                     'test':': Test'}
        pagetitle = self.conf['view']['sitename'] + ' '
        pagetitle += titlelist[self.session['page']]
        # Make logo/iconfilepathname
        logofilepathname = os.path.join(staticpath,
                                        self.conf['view']['pagelogo'])
        iconfilepathname = os.path.join(staticpath,
                                        self.conf['view']['pageicon'])
        # Get style file path
        if 'stylefile' in self.conf['path']:
            stylefile = os.path.join(staticpath,self.conf['path']['stylefile'])
        else:
            stylefile = os.path.join(staticpath,'style.css')
        # Initialize string to include scripts
        baseinclude = '<script src="%s/%s"></script>\n'
        scriptsinclude = ''
        # Get common scripts
        for s in self.conf['scripts']['common'].split('|'):
            if len(s) > 0:
                scriptsinclude += baseinclude % (staticpath, s)
        # Get page scripts
        if self.session['page'] in self.conf['scripts'].keys():
            for s in self.conf['scripts'][self.session['page']].split('|'):
                if len(s) > 0:
                    scriptsinclude += baseinclude % (staticpath, s)
        # Get listfolder (to make sure "Subfolder List" points to current folder)
        listfolder = ''
        if self.session['page'] == 'data':
            listflight = '/'+self.session['folder'].split(os.sep)[0]
        if self.session['page'] == 'list':
            listflight = '/'+self.session['listfolder']
        # Get search url
        searchurl = self.conf['view']['searchurl']
        if len(searchurl):
            searchurl = '<a href="%s">Search</a>' % searchurl
        # Return string
        siteurl = self.conf['path']['siteurl']
        text = text % (pagetitle, stylefile, iconfilepathname,
                       scriptsinclude, logofilepathname,
                       self.conf['view']['sitename'],
                       siteurl, listfolder, listlabel,
                       siteurl,
                       siteurl, self.conf['view']['helpurl'],
                       searchurl)
        self.log.debug('Header Written')
        return text

    def data(self):
        """ Returns the text for the data view page
        """
        ### Make basic strings
        # Make text string
        #   Entries: SelectText%s InfoText%s ImgTools%s
        #            DataDisplay%s
        text = """
<table><tr><td class="tools">
%s
<td class = "tools">
%s
%s
</table>
%s
"""
        # Make Tools Bar
        selecttext = self.selections()
        infotext = self.fileinfo()
        imgtools = self.imgtools()
        # Make display
        if self.session['data'] == 'HEADER':
            display = self.headdisplay()
        elif self.session['data'][:7] == 'TABLE: ':
            display = self.tabledisplay()
            display += '<h3>Header:</h3>\n'
            display += self.headdisplay()
        else:
            display = self.imgdisplay()
            display += '<h3>Header:</h3>\n'
            display += self.headdisplay()
        # Return string
        text = text % (selecttext, infotext, imgtools, display)
        self.log.debug('Data written')
        return text

    def selections(self):
        """ Returns the text for the selections in the data view page.
        """
        # Make selectform string
        #   Entries: siteurl%s FolderSelections%s FileSelectons%s
        #            StepSelections%s DataOptions%s PlaneSelection%s sid%s
        #            filelinks%s
        selecttext = """
<h3>Selection:</h3>
<form action = "%s/data" method = "post" style = "margin: 0px; padding : 0px;">
%s
File : %s<br>
%s
Display : <select name = "data_selection"
    onChange = "setselectaction(this);
                this.form.submit();">
%s
</select><br>
%s
<input type = "hidden" name = "sid" value = "%s">
</form>
<br>
%s
"""
        ### Determine Options
        # Make Folder Selections String
        #   Entries: TopName%s TopOptions%s SubName %s SubOptions%s
        #            DefaultFolder%s
        foldersel = """
%s : <select name = "folder0_selection"
    onChange = "setselectaction(this);
                this.form.submit();">
%s
</select><br>
%s : <select name = "folder1_selection"
    onChange = "setselectaction(this);
                this.form.submit();">
%s
</select><br>
<input type = "hidden" name = "folder_selection" value = "%s">
"""
        # Make Top Folder options
        folderlist = self.model.folderlist(0)
        folderlist.reverse()
        foldercurr = self.session['folder'].split(os.sep)[0]
        topopt = ''
        for f in folderlist:
            if f == foldercurr:
                topopt += '<option selected>%s</option>' % f
            else:
                topopt += '<option>%s</option>' % f
        # Make Sub Folder options
        folderlist = self.model.folderlist(1)
        folderlist.reverse()
        foldercurr = self.session['folder']
        subopt = ''
        for subfolder in folderlist:
            # Add to options list
            subfull = os.path.split(subfolder)[1]
            if subfolder == foldercurr:
                subopt += '<option value="%s" selected>%s' % (subfolder,
                                                              subfull)
            else:
                subopt += '<option value="%s">%s' % (subfolder, subfull)
        # Fill foldersel
        foldersel = foldersel % (self.foldernames[0], topopt,
                                 self.foldernames[1], subopt,
                                 self.session['folder'] )
        # Make File options: Get file list and current file
        filelist = self.model.filelist()
        filelist.reverse()
        filecurr = self.session['file']
        # Check if it's a single file
        if len(filelist) < 2:
            fileselections = filelist[0]
            fileselections = fileselections.replace('.','.<wbr>')
            fileselections = fileselections.replace('_','_<wbr>')
        else:
            # Search common start and end of all files
            # if possible at a . - _ or space 
            file0 = filelist[0]
            startlen = -1
            nfits = len(filelist)
            self.log.debug(' %d %d' % (len(filelist), nfits) )
            while nfits == len(filelist):
                startlen += 1
                nfits = sum([1 for f in filelist if f[startlen] == file0[startlen] ])
                self.log.debug('startlen=%d nfits=%d' % (startlen,nfits))
            sl = startlen
            while sl > 1 and file0[sl-1] not in '._- ' : sl-=1
            if sl>1: startlen = sl
            endlen = 1
            nfits = len(filelist)
            while nfits == len(filelist):
                endlen -= 1
                nfits = sum([1 for f in filelist if f[endlen-1] == file0[endlen-1] ])
            el = endlen
            while el < len(file0) and file0[el] not in '._- ' : el +=1
            if el < len(file0): endlen = el
            # Make list of file options
            fileopt = ''
            for f in filelist:
                if f == filecurr:
                    fileopt += '<option value="%s" selected>%s</option>' % (
                        f, f[startlen:endlen] )
                else:
                    fileopt += '<option value="%s">%s</option>' % (
                        f, f[startlen:endlen])
            filecommonstart = file0[:startlen]
            filecommonend = file0[endlen:]
            # Set file selections
            fileselections = """%s<select name = "file_selection"
                onChange = "setselectaction(this);
                this.form.submit();">%s</select>
                %s""" % (filecommonstart,fileopt, filecommonend)
        # Get step names
        stepnames = self.conf['view']['stepnames'].split('|')
        stepnames = dict([[name.split()[0].upper(),''.join(name.split()[1:])]
                          for name in stepnames])
        # Get step options
        steplist = self.model.steplist()
        if self.model.filenamesteps :
            stepcurr = self.session['step']
        # Check if there are steps
        if len(steplist) > 0:
            # Make step options
            stepopt = ''
            for step in steplist:
                # Make start with selected
                if step == stepcurr:
                    stepopt += '<option selected '
                else:
                    stepopt += '<option '
                # Make end with value and stepname
                if step.upper() in stepnames:
                    stepopt += 'value="%s">%s</option>' % (step, stepnames[step.upper()])
                else:
                    stepopt += '>%s</option>' % step
            # Make step selection
            stepsel = """
Pipe Step : <select name = "step_selection"
    onChange = "setselectaction(this);
                this.form.submit();">
%s
</select><br>
"""
            stepsel = stepsel % stepopt
        else:
            stepsel = ''
        # Make Data options
        datalist = self.model.datalist()
        datacurr = self.session['data']
        dataopt = ''
        for data in datalist:
            if data == datacurr:
                dataopt += '<option selected>%s' % data
            else:
                dataopt += '<option>%s' % data
        # Make Plane selection and options
        planelist = self.model.planelist()
        planecurr = self.session['plane']
        planesel = ''
        if len(planelist) > 1:
            planesel = """
Image Frame: <select name = "plane_selection"
    onChange = "this.form.submit();">
%s
</select><br>
"""
            planeopt = ''
            for plane in planelist:
                if plane == planecurr:
                    planeopt += '<option selected>%s' % plane
                else:
                    planeopt += '<option>%s' % plane
            planesel = planesel % planeopt
        ### Make file download
        # Set up Text - Entries: fitsfileurlpath%s staticpath%s
        #                        folderlink%s staticpath%s foldernames%s
        filedownload = """
<center>
<a href="%s"><img src="%s/fitsicon.gif" alt="">Download Selected FITS File</a><br />
<a href="%s"><img src="%s/foldericon.gif" valign="bottom" alt="">View Selected %s Folder</a>
</center>
"""
# Couldn't get button to work easily with Safari -> revert to <anchor>
#<input type = "button"
#        onClick="window.location='%s';" doesn't work with Safari
#       value = "Download Selected FITS File">
# onClick="window.location.href='%s';" doesn't work with Safari
# onClick="window.open('%s','Download');" doesn't work with Safari

        # Make Link to Folder
        folderlink = os.path.join(self.conf['path']['dataurlpath'],
                                  self.session['folder'])
        # Make Link to Fits Image
        fitsimage = os.path.split(self.model.data.filename)[-1]
        fitslink = os.path.join(folderlink,
                                fitsimage)
        # Staticpath
        staticpath = self.conf['path']['static']
        # foldernames
        foldernames = self.conf['view']['foldernames']
        # Combine filedownload
        filedownload = filedownload % (fitslink, staticpath, folderlink,
                                       staticpath, foldernames)
        ### Combine to select text
        selecttext = selecttext % (self.conf['path']['siteurl'],
                                   foldersel, fileselections, stepsel,
                                   dataopt, planesel, self.session['sid'],
                                   filedownload)
        self.log.debug('  Selections Text Written')
        return selecttext

    def fileinfo(self):
        """ Returns the text for the information in the data view page.
        """
        # Make infotext string
        #   Entries: infovals%s
        infotext = """
<h3>Info:</h3>
%s
"""
        # Collect infostring data
        infolist = self.conf['view']['infolist'].split('|')
        infovals = ''
        for info in infolist:
            ind = info.rfind(' ')
            if ind > -1:
                # Get the value
                try:
                    val = self.model.getheadval(info[ind+1:])
                except:
                    val = ''
                # Only make entry if value is found and contains text
                if len(("%s" % val).strip()):
                    infovals += '%s%s<br>\n' % (info[:ind], val)
            else:
                infovals += '%s<br>\n' % info
        # Combine to information text
        infotext = infotext % infovals
        self.log.debug('  Info Text Written')
        return infotext

    def imgtools(self):
        """ Returns the text for the image tools in the data view page.
        """
        # If data is header -> don't return image tools
        if self.session['data'][:6] in ['HEADER', 'TABLE:']:
            return ''
        # Return image tools
        imgtools = """
<td class = "tools">
<h3>Image Tools:</h3>
<script language = "javascript"><!--
analimg = new imageanalysisobject();
analimg.writetools();
// --></script>
"""
        return imgtools

    def imgdisplay(self):
        """ Returns the text for the image display in the data view page.
        """
        ### New Image
        # Make image string
        #   Entries: AddToolCmds%s DataUrl%s Previewurl%s
        imgdisplay = """
<script language = "javascript"><!--
analimg.writedisplay();
// request image data
%s
analimg.init("%s", "%s");
// --></script>
"""
        # Get image width, height and filestring
        filestring, width, height, fileurlpath = self.model.imagepng()
        # Check if image is empty
        if width*height == 0:
            self.log.debug('  Image Display Written - No Image')
            return """<center>Selected File has no image in selected
                              data Display.<br>
                              Choose a different Display or File.</center>"""
        # Get data url
        dataurl = self.conf['path']['siteurl']+'/data/raw';
        dataurl += '?sid=%s' % self.session['sid'];
        # Determine AddToolCommands
        if self.model.filenamesteps:
            if self.session['step'] in ['PLOTS','PLT','FCS']:
                addtools = ""
            else:
                addtools = "analimg.addtool('imagetoolstatsobject','Stats');"
                addtools +="analimg.addtool('imagetoolpsfobject','PSF');"
        else:
            addtools = "analimg.addtool('imagetoolstatsobject','Stats');"
            addtools +="analimg.addtool('imagetoolpsfobject','PSF');"
        # Combine display text
        imgdisplay = imgdisplay % (addtools, dataurl, fileurlpath)
        self.log.debug('  Image Display Written')
        return imgdisplay

    def headdisplay(self):
        """ Returns the text for the header display in the data view page.
        """
        # Make header String
        #   Entries: tabletext%s
        disptext = """
<table>
<tr><th>Keyword <th>Value <th>Comment
%s
</table>
"""
        # Get header data from model
        headdata = self.model.getheader()
        #headdata = [['BLA',1,'Blabber'],['ACTION','blue','The next step'],
        #            ['HIST','And so it is written.']]
        # Make Table Entries
        tabletext = ''
        for lin in headdata:
            tabletext += '<tr>'
            if lin[0] == 'COMMENT' or lin[0] == 'HISTORY':
                tabletext += '<td>%s <td colspan=2>%s\n' % tuple(lin[0:2])
            elif 'XPADDING' in lin[0]:
                pass
            elif not len(lin[0]):
                tabletext += '<td colspan=3 bgcolor="#CCCCCC"> \n'
            else:
                tabletext += '<td>%s <td>%s <td>%s\n' % tuple(lin)
        # Combine display text
        disptext = disptext % (tabletext)
        self.log.debug('  Header Display Written')
        return disptext

    def tabledisplay(self):
        """ Returns the text for the table display in the data view page.
        """
        # Make header string
        #   Entries: tabletext%s
        disptext = """
<div id = 'tablediv' style = "width:100%%; overflow:auto;
                              border:solid 1px #CCC;">
<table style = "width:auto">
%s
</table>
</div>
"""
        # Get table data from model
        table = self.model.gettable()
        if len(table.shape) > 0:
            nrow = table.shape[0]
        else:
            nrow = 1
        # Make table entries
        tabletext = ''
        if nrow > 1:
            # Normal table: one table entry for each table cell
            for rowi in range(len(table)):
                # Make table header (every 16th line)
                if rowi%16 == 0:
                    tabletext += '<tr>'
                    for head in table.dtype.names:
                        tabletext += '<th>%s ' % head
                # Add dimension and data type for first row
                if rowi == 0:
                    tabletext += '<tr>'
                    for head in table.dtype.names:
                        typ = table[head].dtype.name
                        sha = table[head].shape
                        if len(sha)>1:
                            sha = ['%d' % i for i in sha[1:] ]
                            sha = string.join(sha,'x')
                            tabletext += '<td>%s  %s' % (sha, typ)
                        else:
                            tabletext += '<td>%s' % typ
                # Make data entry
                line = table[rowi]
                tabletext += '<tr>'
                for value in line:
                    valtxt = str.split(str(value))
                    tabletext += '<td>'
                    # if it's too long, shorten it
                    if len(valtxt) < 7:
                        tabletext += str(value)
                    else:
                        tabletext += string.join(valtxt[:3]) + ' ... '
                        tabletext += string.join(valtxt[-3:])
        else:
            # Make table header
            tabletext += '<tr>'
            for head in table.dtype.names:
                tabletext += '<th>%s ' % head
            # Print only one line
            tabletext += '<tr>'
            for name in table.dtype.names:
                tabletext += '<td>%s ' % str(table[name]).strip('()[],')
        # Combine display text
        disptext = disptext % tabletext
        return disptext

    def dataraw(self):
        """ QUERY FUNCTION: Called by the urlpath data/raw
            Returns the data of the current image in the following format
            width = nnn
            height = nnn
            bscale = fffloat
            bzero = fffloat
            message = image message text
            encoding = Uint16
            data = dddddaaaaattttaaaa
        """
        ### Prepare image and header
        message = ''
        # Get image
        image = self.model.imageraw()
        # Get header and check for WCS coordinates
        head = self.model.datahead()
        if 'CTYPE1' in head:
            self.log.debug('dataraw: WCS detected')
            # Get wcs and size
            wcs = WCS(head)
            ncol, nrow = self.model.getheadval('NAXIS1'), self.model.getheadval('NAXIS2')
            # Get midpoints of sides ([coli, rowi] for each)
            indlist = [[ncol/2.+0.5,1],[ncol/2+0.5,nrow],[1,nrow/2+0.5],[ncol,nrow/2+0.5]]
            mx, my = [], [] # middle coordinates
            for i in range(len(indlist)):
                inds = indlist[i]
                wc = numpy.array(wcs.all_pix2world(inds[0],inds[1],1))
                mx.append(wc[0])
                my.append(wc[1])
            # Get center
            cx = sum(mx)/len(mx)
            cy = sum(my)/len(my)
            # Get row/column x and y
            colx = (mx[3]-mx[2]) / (ncol-1)
            coly = (my[3]-my[2]) / (ncol-1)
            rowx = (mx[1]-mx[0]) / (nrow-1)
            rowy = (my[1]-my[0]) / (nrow-1)
            # Get origin (i.e. pixel [0,0])
            x0 = cx - (nrow-1.)/2.*rowx - (ncol-1.)/2.*colx
            y0 = cy - (nrow-1.)/2.*rowy - (ncol-1.)/2.*coly
            # Get x/y label (only take before '-')
            xlabel = self.model.getheadval('CTYPE1').split('-')[0]
            ylabel = self.model.getheadval('CTYPE2').split('-')[0]
        # Check image size and crop if necessary
        maxsize = int(self.conf['view']['maxsize'])
        if image.shape[0] > maxsize:
            image = image[0:maxsize,:]
            message = ' Large image -> Image has been cropped'
            message += ' to %dx%d.' % (maxsize, maxsize)
        if image.shape[1] > maxsize:
            image = image[:, 0:maxsize]
            message = ' Large image -> Image has been cropped'
            message += ' to %dx%d.' % (maxsize, maxsize)
        # Set up response
        retdata = ''
        # Get shape
        wid = image.shape[1]
        hei = image.shape[0]
        # Get scale (remember FFFF is for NaN)
        imgmin = numpy.nanmin(image)
        imgmax = numpy.nanmax(image)
        imgstd = numpy.std(image)
        # Cut top and bottom 0.1% if extreme outliers exist
        # - better way to detect outliers may be possible -
        if imgstd * 1000 < imgmax - imgmin:
            try: # has to be tried b/c not all interpreters have numpy 1.9
                bzero = numpy.nanpercentile(image, 0.1)
                bscale = numpy.nanpercentile(image, 99.9)
                image[image<bzero] = bzero
                image[image>bscale] = bscale
                message += ' Outlying datapoints -> image scale has been cut to [0.1 . . . 99.9] percentile.'
            except:
                bzero = imgmin
                bscale = imgmax                
        else:
            bzero = imgmin
            bscale = imgmax
        bscale = (bscale-bzero)/(2.**16-2)
        if bscale == 0:
            bscale = 1.0
        # Update message
        if len(message) > 0:
            message = '<b>Notice:</b>%s Download FITS File to view original data.' % message
        # Make data header
        retdata += "width = %d\n" % wid
        retdata += "height = %d\n" % hei
        retdata += "bzero = %e\n" % bzero
        retdata += "bscale = %e\n" % bscale
        retdata += "message = %s\n" % message
        retdata += "encoding = %s\n" % "UInt16"
        if 'CTYPE1' in head:
            retdata += "coordx0 = %.5f\n" % x0
            retdata += "coordy0 = %.5f\n" % y0
            retdata += "coordrowx = %.5f\n" % rowx
            retdata += "coordrowy = %.5f\n" % rowy
            retdata += "coordcolx = %.5f\n" % colx
            retdata += "coordcoly = %.5f\n" % coly
            retdata += "coordlblx = %s\n" % xlabel
            retdata += "coordlbly = %s\n" % ylabel
        ### Convert data
        #   Issue: '\x00' becomes '' in a numpy array of strings
        #   -> can not use numpy arrays -> need to use a loop
        # Prepare data
        imgdata = ''
        image = image.copy()
        image.shape = wid*hei
        image = (image-bzero)/bscale
        image[numpy.isnan(image)] = 2.**16-1 # Set Nan to 2**16-1
        image = numpy.array(numpy.round(image), dtype = numpy.uint16)
        for i in range(wid*hei):
            imgdata += '%4X' % image[i]
        retdata += "data = %s" % imgdata
        # Return data
        self.log.debug('Dataraw Returned length = %d' % len(imgdata))
        return retdata

    def pipelog(self):
        """ Returns the pipeline log page
        """
        # Make text string
        #   Entries: LevelOptions%s Sid%s Sid%s
        #            siteurl%s ReloadTime%s LineMaxN%s
        logdisplay = """
<h2>Pipeline Log</h2>
<form id = "selectform" action = "" method = "post">
Level : <select name = "log_level"
    onChange = "this.form.submit();">
%s
</select>
<input type = "hidden" name = "sid" value = "%s">
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Last Reload @ 
<span id='logtimetext'>SpanText</span>
</form>
<div id="logtable"><table><tbody>
<tr><th>Time </th><th>Source </th><th>Level </th><th>Message</th></tr>
</tbody></table></div>
<script language="javascript"><!--
// set global variables
sid = "%s";
siteurl = "%s";
reloadtime = %s;
linemaxn = %s;
// request log table data
logrequest();
// --></script>
"""
        # Get Level Options
        levels = ['DEBUG','INFO','WARNING','ERROR','CRITICAL']
        levelopt = ''
        for level in levels:
            if level == self.session['loglevel']:
                levelopt += '<option selected>%s</option>' % level
            else:
                levelopt += '<option>%s</option>' % level
        # Set logtime
        self.session['logtime'] = '2000-01-01 00:00:00'
        # Combine display text
        logdisplay = logdisplay % (levelopt, self.session['sid'],
                                   self.session['sid'],
                                   self.conf['path']['siteurl'],
                                   self.conf['view']['logreloadtime'],
                                   self.conf['view']['loglinemaxn'])
        self.log.debug('PipeLog written')
        return logdisplay
    
    def logupdate(self):
        """ QUERY FUNCTION: Called by the urlpath log/update
            Returns a list of new log messages that were added since the
            last update. Internal checks insure that no message is sent
            twice and that two requests at least two seconds apart return
            all messages.
        """
        # Get log text
        list = self.model.loglist()
        # Check if list is empty
        if len(list) == 0:
            self.log.debug('LogUpdate written')
            return ''
        # Get lasttime (from logtime) and last time on the list (listtime)
        try:
            lasttime = time.strptime(self.session['logtime'],'%Y-%m-%d %H:%M:%S')
        except:
            lasttime = time.strptime('2000-01-01 00:00:00','%Y-%m-%d %H:%M:%S')
        lasttime = time.mktime(lasttime)
        listsplit = list[-1].split(' - ')
        listtime = (listsplit[0].strip().split(',')[0])
        listtime = time.strptime(listtime, '%Y-%m-%d %H:%M:%S')
        listtime = time.mktime(listtime)
        # Set New Logtime
        # If logtime < listtime-1s
        # -> Assume there have been log enties since the last update
        # -> Return all entries up to listtime-1s
        #    (Because there could be more entries during the current second)
        if lasttime < listtime - 1:
            newlasttime = listtime - 1
        # Else (logtime >= listtime-1s)
        # -> Assume there have been no log entries since the last update
        #    (at least 2 seconds ago)
        # -> Return all entries in the list
        else:
            newlasttime = listtime
        # Get new entries
        logtext = ''
        logbaseline = '<tr class="log%s"><td>%s </td><td>%s </td><td>%s </td><td>%s</td></tr>\n'
        logtime = ''
        logsrc = ''
        loglvl = 'DEBUG'
        for ind in range(len(list)-1,-1,-1):
            # Split entry
            logsplit = list[ind].split(' - ')
            if len(logsplit) > 2:
                # Get epoch time
                logtime = (logsplit[0].strip().split(',')[0])
                rawtime = time.strptime(logtime, '%Y-%m-%d %H:%M:%S')
                rawtime = time.mktime(rawtime)
                # Check if it's between logtime and newlogtime
                if rawtime <= lasttime or rawtime > newlasttime: continue
                # Get log information and add line to text
                logtime = (logsplit[0].strip().split(',')[0]).replace(' ','&nbsp;')
                # set outputs
                logsrc = logsplit[1].strip()
                loglvl = logsplit[2].strip()
                logmsg = ' - '.join(logsplit[3:]).strip()
                logmsg = logmsg.replace('&','&amp;').replace('>','&gt;').replace('<','&lt;')
            else:
                # Just get message, do not set loglvl (assume unchanged)
                logsrc = ''
                logmsg = logsplit[0].strip()
            logline = logbaseline % ( loglvl.lower(), logtime, logsrc,
                                      loglvl, logmsg)
            logtext += logline
        # Set new logtime session keyword
        newlasttime = time.localtime(newlasttime)
        self.session['logtime'] = time.strftime('%Y-%m-%d %H:%M:%S', newlasttime)
        self.log.debug('LogUpdate written')
        return logtext
    
    def folderlist(self):
        """ Returns the Folders and Subfolders list
        """
        # Make text string
        #   Entries: FolderNames%s FolderTop%s siteurl%s FolderOptions%s
        #            FolderTop%s SubFolder%s Sid% tabletext%s
        listdisplay = """
<h2>%s List</h2>
<form id = "folderselect" action = "" method = "post">
<b>Display:</b> %s
<select name = "folder"
        onChange = " ftext = (this.options[this.selectedIndex]).text;
                     this.form.action = '%s/list/' + ftext;
                     this.form.submit();">
%s
</select> and earlier. &nbsp;(%ss with no %ss are not shown)
<input type = "hidden" name = "sid" value = "%s">
</form>

%s
"""
        # Make foldernames, foldertop
        foldernames = ' / '.join(self.foldernames)
        # Make list for pulldown menu
        folders = self.model.folderlist(0)
        folders.reverse()
        folderopts = ''
        for folder in folders:
            if folder == self.session['listfolder']:
                folderopts += '<option selected>%s</option>' % folder
            else:
                folderopts += '<option>%s</option>' % folder
        ### Make list text
        tabletext = ''
        listkeys = self.conf['view']['listkeyw'].split('|')
        coln = len(listkeys)+1
        # Find first -> indbeg
        indbeg = folders.index(self.session['listfolder'])
        if indbeg < 0: indbeg = 0
        # Make sure first flight has valid data
        while( len(self.model.folderlist(1,folders[indbeg])) ==0 and
               indbeg < len(folders) - 1 ) :
            indbeg+=1
        # Find last -> indend
        if len(folders) > indbeg + int(self.conf['view']['listfoldern']):
            indend = indbeg + int(self.conf['view']['listfoldern'])
        else:
            indend = len(folders)
        # Make string for observation link
        #   Entries: siteurl%s fullfolder%s subfolder%s
        obslink = '<tr><td><a href = "%s/data/%s">%s</a>'
        # Loop through topfolders
        folderi = indbeg # index counts up
        subfoldern = int(self.conf['view']['listsubfoldern']) # counts down
        sortkeyw = self.conf['view']['sortkeyw']
        while ( folderi < indend or subfoldern > 0 ) and folderi < len(folders) :
            # Get folder and update folderi
            folder = folders[folderi]
            folderi += 1
            # Topfolder title
            foldertext = '<table><tr><td colspan="%d">' % coln
            foldertext += '<b>%s: %s</b>' % (self.foldernames[0], folder)
            # Table Headings
            foldertext += '<tr><th>%s ' % self.foldernames[1]
            for item in listkeys:
                ind = item.rfind(' ')
                if ind > -1: foldertext += '<th>%s' % item[:ind]
                else: foldertext += '<tr>%s' % item
            # subfolder items - make list
            siteurl = self.conf['path']['siteurl']
            subfolders = self.model.folderlist(1,folder)
            subfolders.reverse()
            subfoldern -= len(subfolders)
            subtextlist = [] # list with sortkeyword and text
            for sfolder in subfolders:
                # subfolder title
                subtext = obslink % ( siteurl, sfolder,
                                      sfolder.split(os.sep)[1])
                # Load subfolder header
                self.model.loadfolderhead(sfolder)
                # AOR items
                for item in listkeys:
                    ind = item.rfind(' ')
                    # if no valid listkey entry -> no value
                    if ind < 0: val = '-'
                    # if no file loaded -> no value
                    elif not len(self.model.data.filename):
                        val = '-'
                    # get value
                    else:
                        val = self.model.getheadval(item[ind+1:])
                        if not isinstance(val, str):
                            val    = repr(val) # Change to string
                        if not len(val) : val = '-' # Add dash if no content
                    subtext += '<td>%s' % val
                # Add sortkey if needed
                if len(sortkeyw):
                    subtext = self.model.getheadval(sortkeyw) + subtext
                subtextlist.append(subtext)
            # sort subfolders and add to folder text
            subtextlist.sort()
            subtextlist.reverse()
            for subtext in subtextlist:
                ind = subtext.find(obslink[:5])
                if ind<0:
                    foldertext += subtext
                else:
                    foldertext += subtext[ind:]
            # add foldertext to full table
            if len(subfolders) > 0:
                tabletext += foldertext + '</table>'
        # Combine display text
        listdisplay = listdisplay % (foldernames, self.foldernames[0],
                                     self.conf['path']['siteurl'],
                                     folderopts, self.foldernames[0],
                                     self.foldernames[1], self.session['sid'],
                                     tabletext )
        self.log.debug('FolderList written')
        return listdisplay

    def search(self):
        """ Returns the search page
        """
        # Make text string
        #   Entries: SearchURL%s
        searchtext = """
<iframe width = "100%%" height = "500px" src="%s"></iframe>
"""
        searchurl = self.conf['view']['searchurl']
        text = searchtext % searchurl
        self.log.debug('Search written %s' % searchurl)
        return text

    def test(self):
        """ Returns a page to test server and browser compatibility
        """
        # Make text string
        #   Entries: ServerResults%s BrowserResults%s 
        testtext = """
<hr>
<h2>Server Tests:</h2>
<div id="servertests">
%s
</div>
<h2>Browser Tests:</h2>
<div id="browsertests">
%s
</div>
<p>
Button and Field for tests:
<div id="testfield">
</div>
<form><input type = 'Button' value = 'Test'
                   onclick = 'buttonf();'>
<textarea id='testtext' rows = '5' cols = '60'>TextText</Textarea>
</form>
<script language="javascript"><!--
browsertests();
//--></script>
<h2>Feedback Message:</h2>
<form action = "" method = "post">
<input type='text' id='messagetext' name='messagetext' cols = '60'>aa
<input type = 'Submit' value = 'Send'>
</form>
<p>
<table style="width:70%%; border-style:ridge;
              margin-left:auto; margin-right:auto"><tr><td>
If any of the tests did not complete, please update your web browser. We suggest
you use <a href="http://www.mozilla.org/firefox/">Firefox</a>.
</table>
"""
        ### Run server Tests
        serverresults = 'Running . . .'
        serverresults += '<br>Tests Complete'
        ### Run browser tests
        browserresults = 'Loading . . .'
        ### Combine display text
        testtext = testtext % (serverresults, browserresults)
        self.log.debug('Test written')
        return testtext

    def error(self,message):
        """ Returns an Error message
        """
        # Make text string
        #   Entires: message%s backurl%s
        text = """
<hr>
<h2>Error Detected:</h2>
%s
<p>
<a href="%s">Back to Data List</a>
"""
        # get base url path
        siteurl = self.conf['path']['siteurl']
        text = text % (message, siteurl)
        self.log.debug('Error written')
        return text

""" === History ===
    -->> See Controller.py <<--
"""
