""" MODEL.PY
    The site model provides information about the fits file database to
    the rest of the application. The model handles queries and requests
    from the controller and the view.
"""

### Preparation
import os # OS Library
import sys
import string # String Library
import logging # Logging Library
import numpy # Numpy Library
import re # Regexp search Library
from PIL import Image # Image Library
from darepype.drp.datafits import DataFits as PipeData # Pipedata object @UnresolvedImport
from darepype.drp import datafits

### Class Definition
class SiteModel(object):
    """ Model object connects to the fits file database.
    """

    def __init__(self, environ, session, config):
        """ Constructor: declares the variables
        """
        # Declare Variables
        self.env = environ
        self.session = session
        self.conf = config
        # divider character for pipe step in filename
        #     no steps if stepdiv=='', in that case step='' and steplist=[]
        self.stepdiv = ''
        # flag indicating if pipe steps are specified in the filename
        self.filenamesteps = False
        # infohead
        self.infohead = ''
        # Get data object
        pipeconf = os.path.join(self.conf['path']['basepath'],
                                self.conf['model']['pipeconf'])
        self.data = PipeData(config = pipeconf) # Stored data
        self.data.filename = ''
        # Make logger
        self.log = logging.getLogger('webview.model')
        self.log.debug('Initialized')
        self.log.debug(repr(datafits.__file__))
        self.log.debug(repr(sys.path))

    def set_selection(self):
        """ Sets and validates the session variables folder, file, step
            and data. If the values are invalid they are changed to valid
            values, and info log messages are posted. If no data is available
            all values are left empty (but session values are created
            even in that case). This function also insures that the correct
            datafile is loaded into self.data.
        """
        ### Check Folders
        #   At this point the folder depth of files is taken from
        #   the length of conf['view']['foldernames'].split(os.sep)
        # Get existing Folder value
        if 'folder' in self.session:
            foldercurr = self.session['folder']
            filen = len(self.filelist(foldercurr))
        else:
            foldercurr = ''
            filen = 0
        # if no files are available -> look for a valid folder
        if filen < 1:
            # Make sure there's valid subfolders within foldercurr
            if len(foldercurr):
                depth = len(foldercurr.split(os.sep))
                while len(foldercurr) > 0 and self.validate_folder(foldercurr) == 0:
                    # Take last path off of foldercurr
                    foldercurr = os.sep.join(foldercurr.split(os.sep)[:-1])
                    depth -= 1
            else:
                depth = 0
            # Look for a folder
            maxdepth = len(self.conf['view']['foldernames'].split(os.sep))
            while depth < maxdepth:
                # Get folderlist
                folderlist = self.folderlist(depth,foldercurr)
                # Find a valid folder
                ind = len(folderlist) - 1
                while ind > -1 and self.validate_folder(folderlist[ind]) < 1:
                    ind -=1
                # Set valid folder -> foldercurr
                if ind > -1:
                    foldercurr = folderlist[ind]
                    depth += 1
                else: # If there is no data, set all to ''
                    self.session['folder'] = ''
                    self.session['file'] = ''
                    self.session['step'] = ''
                    self.session['data'] = ''
                    self.session['plane'] = ''
                    return
            # Put valid folder into session
            self.session['folder'] = foldercurr
            self.log.info('Validate: FOLDER set to %s' % foldercurr)
        ### Check File
        # Get File list
        filelist = self.filelist()
        # Get existing File value
        if 'file' in self.session: filecurr = self.session['file']
        else: filecurr = ''
        # Check and set File value
        if not filecurr in filelist:
            if len(filelist) > 0:
                self.session['file'] = filelist[-1]
                self.log.info('Validate: FILE set to %s' % filelist[-1])
            else: # If there is no data set all to ''
                self.session['file'] = ''
                self.session['step'] = ''
                self.session['data'] = ''
                self.session['plane'] = ''
                return
        ### Check Step
        # Check stepdiv to make sure steps are available
        if self.filenamesteps:
            # Get Step list
            steplist = self.steplist()
            # Get existing Step value
            if 'step' in self.session: stepcurr = self.session['step']
            else: stepcurr = None
            # Check and set File value
            if not stepcurr in steplist:
                if len(steplist) > 0:
                    self.session['step'] = steplist[-1]
                    self.log.info('Validate: STEP set to %s' % steplist[-1])
                # else: empty list -> assume steplist changed 'file' -> all good
        else:
            self.session['step'] = ''
        ### Check Data
        # Get Data list
        datalist = self.datalist()
        # Get existing Data value
        if 'data' in self.session: datacurr = self.session['data']
        else: datacurr = ''
        # Check and set Data value
        if not datacurr in datalist:
            if len(datalist) > 0:
                self.session['data'] = datalist[0]
                self.log.info('Validate: DATA set to <%s>' % datalist[0])
            else: # If there is no data set all to ''
                self.session['data'] = ''
                self.session['plane'] = ''
        ### Check Plane
        # Get Plane list
        planelist = self.planelist()
        # Get existing Plane value
        if 'plane' in self.session: planecurr = self.session['plane']
        else: planecurr = ''
        # Check and set Plane value
        if not planecurr in planelist:
            if len(planelist) > 0:
                self.session['plane'] = planelist[0]
                self.log.info('Validate: PLANE set to %s' % planelist[0])
            else: # If there is no data set all to ''
                self.session['plane'] = ''
        self.log.debug('Set Selection')

    def validate_folder(self, folder=''):
        """ Returns > 0 if folder or a subfolder has valid data files.
            Function calls itself recursively through folder tree.
            Note: Both filelist and folderlist make sure folder exists.
        """
        # Get files from folder
        filen = len( self.filelist(folder) )
        # If no files are in folder -> look through subfolders
        if filen == 0:
            # Get subfolders
            subfolders = self.folderlist(100,folder)
            # Loop through subfolders, sum valid files
            for subfolder in subfolders:
                filen += self.validate_folder(subfolder)
        self.log.debug('Validated Folder: %s = %d' % (folder, filen))
        return filen

    def folderlist(self, depth=0, folder=''):
        """ Returns a list of all folders under the current folder at
            the specified depth. Unless specified, FOLDER is obtained
            from session and is assumed to be valid. If depth > max depth
            of folder -> sub-folders of folder are returned.
            Ex: if folder='foo/bar' and depth=1 then
                'foo/bar','foo/baz' and 'foo/qux' are returned
        """
        # Get folder
        if len(folder) == 0 and 'folder' in self.session:
            folder = self.session['folder']
        # Cut folder to desired level: Get folder list - cut it
        if len(folder) == 0:
            flist = []
        else:
            flist = folder.split(os.sep)
        if depth == 0:
            folder = ''
        elif len(flist) > depth:
            folder = os.path.join(*flist[:depth])
        # Get folderpath
        folderpath = os.path.join(self.conf['path']['basepath'],
                                  self.conf['path']['datapath'],
                                  folder)
        # Check if folderpath exists
        if not os.path.exists(folderpath):
            self.log.warn('Folderlist - non existant folder %s' % folderpath)
            return []
        # Get list of all files in folder (also check if have access)
        try:
            folderlist = os.listdir(folderpath)
        except:
            self.log.warn('Folderlist - unable to access folder %s' % folderpath)
            return []
        # Get subfolders in folderpath
        folderlist = [ f for f in folderlist
                       if os.path.isdir(os.path.join(folderpath,f))]
        folderlist.sort()
        # Join subfolders to folder
        folderlist = [ os.path.join(folder,f) for f in folderlist ]
        # Return list
        self.log.debug('FolderList returned: Listlen=%d Folder=%s' %
                       (len(folderlist), folder))
        return folderlist

    def filelist(self, folder=''):
        """ Returns a list of all files under the current FOLDER. Unless
            specified, FOLDER is obtained from session and is
            assumed to be valid. Filelist also decides if the filenames
            contain data reduction step information i.e. a special
            character '.' '_' or ' ' then a short string.
        """
        # Get folder
        if len(folder) == 0:
            folder = self.session['folder']
        # Make folderpath
        folderpath = os.path.join( self.conf['path']['basepath'],
                                   self.conf['path']['datapath'],
                                   folder )
        # Check if folderpath exists
        if not os.path.exists(folderpath):
             return []
        # Get all files in folder
        files = [ fname for fname in os.listdir(folderpath)
                  if os.path.isfile(os.path.join(folderpath,fname)) ]
        files.sort()
        # Select only files that don't contain filetoignore and have extention in fileext
        fileext = self.conf['model']['fileext']
        filetoignore = self.conf['model']['filetoignore']
        filescut = []
        for fname in files:
            fsel = False
            # Make sure filename has extension in fileext
            for ext in fileext:
                if ext.upper() in fname[-len(ext):].upper(): fsel = True
            # Exclude files that match any filetoignore entries
            for ign in filetoignore:
                if ign in fname: fsel = False
                elif re.search(ign,fname): fsel = False
            if fsel: filescut.append(fname)
        # Cut pipe step status from all files:
        # Make dict with a list of original filenames for each file
        stepdivlist = '._- '
        filesdict = {}
        for fname in filescut:
            # Get beginning and end
            self.data.filename = fname
            beg = self.data.filenamebegin
            end = self.data.filenameend
            # Make cut = beginning + end
            if len(beg) == 0 : fcut = end
            elif len(end) == 0 : fcut = beg
            elif beg[-1] in stepdivlist and end[0] in stepdivlist:
                fcut = beg[:-1] + end
            else:
                fcut = beg + end
            # Add entry to dictionary
            if fcut in filesdict:
                # Existing entry - just add
                filesdict[fcut].append(fname)
            else:
                # New entry: Get file number and name without file number nor step status
                fnumb = -1.0 # file number
                nstart, nend = 0, 0 # start and end of filenumber in name
                m = re.search(self.data.config['data']['filenum'],fname)
                if m is not None:
                    # regex may contain multiple possible matches --
                    # for middle or end of filename
                    for i,g in enumerate(m.groups()):
                        if g is not None:
                            # Get start and end for filenumber and filestatus
                            nstart = m.start(i+1)
                            nend = m.end(i+1)
                            # Get file number, multiply with 100'000 and add lower number (if exists)
                            # Assumption: it's actually an integer or float number otherwise -> 0.0
                            numb = fname[nstart:nend].split('-')
                            for j in range(len(numb)):
                                m1=re.search(r'(\d+(\.\d+)?)',numb[j])
                                if m1:
                                    numb[j] = float(m1.group())
                                else:
                                    numb[j] = 0.0
                            if len(numb) > 1:
                                fnumb = 100000 * max(numb) + min(numb)
                            else:
                                fnumb = 100000 * numb[0]
                            break
                # Get file name without number nor step status
                sstart = len(beg)
                send = len(fname)-len(end)
                if (sstart>nstart):
                    fcutcut = fname[:sstart]+fname[send:]
                    fcutcut = fcutcut[:nstart]+fcutcut[nend:]
                else:
                    fcutcut = fname[:nstart]+fname[nend:]
                    fcutcut = fcutcut[:sstart]+fcutcut[send:]
                filesdict[fcut] = [fcutcut, fnumb, fname,]
                # self.log.debug('fname=%s cutcut=%s numb=%f' % (fname,fcutcut,fnumb))
        self.data.filename = ''
        # Change dicts into lists [fcut, fcutcut, fnumb, fname . . . ]
        fullist = []
        for f in filesdict:
            fullist.append([f,]+filesdict[f])
        # Sort by file number (higher number counts for files with number range)
        fullist.sort(key=lambda x: x[2])
        # Sort by filename w/o number or status
        fullist.sort(key=lambda x: x[1])
        # Copy filenames: use uncut name if there's only one dict entry
        filelist = []
        for f in fullist:
            if len(f) > 4:
                filelist.append(f[0])
            else:
                filelist.append(f[3])
        # If the number of files is equal the number files with step
        if len(filelist) == len(filescut):
            # Set no steps and just use full filenames
            self.filenamesteps = False
        else:
            self.filenamesteps = True
        # Return list
        self.log.debug('FileList returned: ListLen=%d Folder=%s' %
                       (len(filelist), folder))
        return filelist

    def steplist(self):
        """ Returns a list of all valid steps for a file. FOLDER
            and FILE are obtained from session and are assumed to be valid.
            ** This function takes out raw data steps **
        """
        # If there is no step extension -> return empty list
        if not self.filenamesteps:
            return []
        # Make folderpath
        folderpath = os.path.join(self.conf['path']['basepath'],
                               self.conf['path']['datapath'],
                               self.session['folder'])
        # Get all files in folder
        files = [ fname for fname in os.listdir(folderpath)
                  if os.path.isfile(os.path.join(folderpath,fname)) ]
        files.sort()
        # Select only files that don't contain filetoignore and extension in fileext
        fileext = self.conf['model']['fileext']
        filetoignore = self.conf['model']['filetoignore']
        filescut = []
        for fname in files:
            fsel = False
            # Make sure filename has extention in fileext
            for ext in fileext:
                if ext.upper() in fname[-len(ext):].upper(): fsel = True
            # Exclude files that match any filetoignore entries
            for ign in filetoignore:
                if ign in fname: fsel = False
                elif re.search(ign,fname): fsel = False
            if fsel: filescut.append(fname)        
        # Select only steps in requested file
        filename = self.session['file']
        templist = []
        stepdivlist = '._- '
        for fname in filescut:
            # Make cut = beginning + end
            self.data.filename = fname
            beg = self.data.filenamebegin
            end = self.data.filenameend
            step = fname[len(beg):-len(end)]
            if len(beg) == 0 : fcut = end
            elif len(end) == 0 : fcut = beg
            elif beg[-1] in stepdivlist and end[0] in stepdivlist:
                fcut = beg[:-1] + end
            else:
                fcut = beg + end
            # Append step to list (both cases: shortened filename or original filename)
            if fcut in filename or fname in filename: 
                templist.append(step)
        self.data.filename = ''
        # Sort steps in known chronological order
        steplist = []
        steporder = [step for step in self.conf['model']['steporder'].split() ]
        for stepo in steporder:
            for stepf in templist:
                if stepo.upper() == stepf.upper():
                    steplist.append(stepf)
        # Add steps not known in above order
        for step in templist:
            if step not in steplist: steplist.append(step)
        # if there's only one step -> don't use steps for this file
        if len(steplist) == 1:
            self.filenamesteps = False
            self.log.debug('StepList: Only one step for file %s' % filename)
            steplist = []
        # Return list
        self.log.debug('StepList returned = %s' % repr(steplist))
        return steplist

    def datalist(self):
        """ Returns a list of all valid data blocks for folder / file /
            step. These are obtained from session and are assumed to be valid.
        """
        # Make folderpath
        folderpath = os.path.join(self.conf['path']['basepath'],
                               self.conf['path']['datapath'],
                               self.session['folder'])
        # if filenamesteps, get file names and pick correct one
        stepdivlist = '._- '
        if self.filenamesteps :
            # Get all files in folder
            files = [ fname for fname in os.listdir(folderpath)
                      if os.path.isfile(os.path.join(folderpath,fname)) ]
            files.sort()
            # Select only files that don't contain filetoignore and extension in fileext
            fileext = self.conf['model']['fileext']
            filetoignore = self.conf['model']['filetoignore']
            filescut = []
            for fname in files:
                fsel = False
                # Make sure filename has extention in fileext
                for ext in fileext:
                    if ext.upper() in fname[-len(ext):].upper(): fsel = True
                # Exclude files that match any filetoignore entries
                for ign in filetoignore:
                    if ign in fname: fsel = False
                    elif re.search(ign,fname): fsel = False
                if fsel: filescut.append(fname)        
            # Get filename for requested file
            filename = self.session['file']
            step = self.session['step']
            for fname in filescut:
                # Make cut = beginning + end
                self.data.filename = fname
                beg = self.data.filenamebegin
                end = self.data.filenameend
                if len(beg) == 0 : fcut = end
                elif len(end) == 0 : fcut = beg
                elif beg[-1] in stepdivlist and end[0] in stepdivlist:
                    fcut = beg[:-1] + end
                else:
                    fcut = beg + end
                if fcut in filename and step in fname:
                    filename = fname
        else: # No steps are used, usef the filename
            filename = self.session['file']
        # Make filepathname
        filepathname = os.path.join(folderpath,filename)
        # Load file if it's not loaded
        if self.data.filename != filepathname:
            self.data.load(filepathname)
        self.log.debug('DataList: FilePathName = %s' % filepathname)
        # Make data list
        datalist = list(self.data.imgnames)
        # Add TABLEs
        if len(self.data.tabnames):
        # if self.data.table != None: # commented out 2021-10-28
            if len(datalist) > 0:
                datalist.insert(1,'TABLE: ' + self.data.tabnames[0])
            else: datalist = ['TABLE: ' + self.data.tabnames[0]]
            if len(self.data.tabnames) > 1:
                datalist += ['TABLE: ' + name
                             for name in self.data.tabnames[1:] ]
        # Add HEADER
        datalist.append('HEADER')
        # Return data
        self.log.debug('DataList returned: %s' % repr(datalist))
        return datalist

    def planelist(self):
        """ Returns a list of the cube planes in the current data. If
            there are no subplanes in the data an empty list is returned.
        """
        # Check if data is loaded (i.e. data.filename != '')
        if self.data.filename == '':
            self.log.warn('Planelist: Missing FITS data')
            return []
        # Return planelist
        if self.session['data'][:6] in ['HEADER','TABLE:']:
            planelist = []
        elif self.data.imageget(self.session['data']) is None: 
            planelist = []
        else:
            shape = self.data.imageget(self.session['data']).shape
            if len(shape) > 2 :
                planelist = [ str(i) for i in range(shape[-3]) ]
            else:
                planelist = []
        self.log.debug('PlaneList returned')
        return planelist

    def imageraw(self):
        """ Returns the raw 2D image. The fits file needs to be loaded and
            the session keywords to select the file must be present and valid.
            If no image data is available, returns an array with size (0).
        """
        # Get session variables
        data = self.session['data']
        # Check if data is loaded (i.e. data.filename != '')
        if self.data.filename == '':
            self.log.warn('ImageRaw: Missing FITS data')
            return '<b>Missing FITS data</b>\n'
        # Check if data is correct
        if not data in self.data.imgnames:
            self.log.error('Data <%s> is invalid for file <%s>'
                           % (data, self.data.filename) )
            return "<b>Invalid data for Image</b>\n"
        # Get the data
        imgdata = self.data.imageget(data)
        # If data is empty -> return
        if imgdata is None:
            self.log.debug('Raw image returned - empty')
            return numpy.zeros([0,0])
        if len(imgdata) == 0:
            self.log.debug('Raw image returned - empty')
            return imgdata
        # Reshape if necessary
        self.log.debug('Shape: %d %d' % (len(imgdata.shape), imgdata.shape[0]))
        if len(imgdata.shape) > 2:
            if len(imgdata.shape) > 3:
                imgdata = imgdata[0,...]
            imgdata = imgdata[int(self.session['plane']),...]
        # Check image size and crop if necessary
        maxsize = int(self.conf['model']['maxsize'])
        if imgdata.shape[0] > maxsize:
            imgdata = imgdata[0:maxsize,:].copy()
        if imgdata.shape[1] > maxsize:
            imgdata = imgdata[:, 0:maxsize].copy()
        # Set Inf and Nan values to median
        isnanlist = numpy.isnan(imgdata)
        isinflist = numpy.isinf(imgdata)
        imgdata[isnanlist] = numpy.median(imgdata)
        imgdata[isinflist] = numpy.median(imgdata)
        # Return data
        self.log.debug('Raw image returned')
        return imgdata
        

    def imagepng(self):
        """ Makes a png of an image, saves it and returns image string.
            Returns zeros if no data is available.
        """
        # Get the data
        imgdata = self.imageraw()
        # If no data available, return empty values
        if len(imgdata) == 0:
            self.log.debug('No PNG image returned')
            return ('',0,0,'')
        # Get scale range - if wid*hei>1000 -> cut top and bottom 0.1%
        if imgdata.shape[0]*imgdata.shape[1] >= 1000:
            try:
                imin = numpy.nanpercentile(imgdata,0.1)
                diff = numpy.nanpercentile(imgdata,99.9) - imin
            except:
                imin = numpy.nanmin(imgdata)
                diff = numpy.nanmax(imgdata) - imin
        else:
            imin = numpy.nanmin(imgdata)
            diff = numpy.nanmax(imgdata) - imin    
        # Scale data to 0..1
        if diff > 0:
            imgscale = ( imgdata - imin ) / diff
        else:
            imgscale = imgdata - imin
        # Flip vertically
        imgscale = imgscale[range(imgscale.shape[0]-1,-1,-1),:]
        # Make output image
        imgout = Image.new('L',(imgscale.shape[1],imgscale.shape[0]))
        shape = imgscale.shape[0]*imgscale.shape[1]
        imgout.putdata((255.*imgscale).reshape(shape))
        # Save image
        outfilename = self.session['sid']+'.gif'
        outfilepathname = os.path.join(self.conf['path']['basepath'],
                                       self.conf['path']['images'],
                                       outfilename)
        imgout.save(outfilepathname)
        self.log.debug('Saved image %s' % outfilepathname)
        # Prepare image string
        outfileurlpath = os.path.join(self.conf['path']['imagesurl'],
                                      outfilename)
        n = 1
        minsize = int(self.conf['model']['minsize'])
        imgsmax = numpy.array(imgscale.shape).max()
        while imgsmax * n < minsize:
            n += 1
        outstring = '<img src=%s width="%d" height="%d">' % ( outfileurlpath,
                     imgscale.shape[1]*n, imgscale.shape[0]*n)
        self.log.debug('Returned PNG image')
        return (outstring, imgscale.shape[1], imgscale.shape[0], outfileurlpath)
        
    def datahead(self):
        """ Returns the header of the current data. The fits file needs to be loaded
            and the session keywords to select the file must be present and valid.
            If no image data is available, returns an empty dictionary.
        """
        # Get session variables
        data = self.session['data']
        if data[:6] == 'TABLE:': data = data[7:]
        # Check if data is loaded (i.e. data.filename != '')
        if self.data.filename == '':
            self.log.warn('ImageRaw: Missing FITS data')
            return '<b>Missing FITS data</b>\n'
        # Check if data is correct
        if not data in self.data.imgnames and not data in self.data.tabnames:
            self.log.error('Data <%s> is invalid for file <%s>'
                           % (data, self.data.filename) )
            return "<b>Invalid data for Image</b>\n"
        # Return the data
        return self.data.getheader(data)
    
        
    def gettable(self):
        """ Returns table data for the current file.
        """
        # Check if data is loaded (i.e. data.filename != '')
        if self.data.filename == '':
            self.log.warn('GetTable: Missing FITS data')
            return []
        # Get Session variables
        data = self.session['data']
        # Get Table Name
        if data[:7] == 'TABLE: ': tabname = data[7:]
        else: tabname = data
        self.log.debug('Returning Table %s' % tabname)
        # Return Table
        try:
            return self.data.tableget(tabname)
        except:
            return numpy.rec.array([('No Table Data')], 
                                   names = 'Info', formats = 'a20')
        
    def getheader(self):
        """ Returns header data for the current file and current session
            data. The header is returned as a list of lists with each
            element having key, value and comment. To get the raw header
            of the current image, use datahead function.
        """
        # Check if data is loaded (i.e. data.filename != '')
        if self.data.filename == '':
            self.log.warn('GetHeader: Missing FITS data')
            return []
        # Get header
        if 'HEADER' in self.session['data']:
            try:
                header = self.data.getheader(self.conf['model']['infohead'])
            except:
                header = self.data.header
        else:
            header = self.datahead()
        # Create Response
        headdata = []
        for card in header.cards:
            card.verify('fix')
            headdata.append([card.keyword,card.value,card.comment])
        # Return Response
        self.log.debug('Header returned')
        return headdata

    def getheadval(self, key):
        """ Returns the value for a specified header key in the current file.
        """
        # Check if data is loaded (i.e. data.filename != '')
        if self.data.filename == '':
            self.log.warn('GetHeadVal: Missing FITS data')
            return ''
        # Get key
        try:
            value = self.data.getheadval(key, 
                        dataname = self.infohead)
        except:
            self.log.info('No Header Value for HDU = %s Key = %s' % 
                          (self.infohead,key ) )
            return ''
        # Return value
        self.log.debug('Header Value returned: %s = <%s>' % (key,repr(value)))
        return value
    
    def loadfolderhead(self, folder):
        """ Loads the header for a specified subfolder into the data.
        """
        # Make aorpath
        folderpath = os.path.join(self.conf['path']['basepath'],
                               self.conf['path']['datapath'],
                               folder )
        # Get all FITS files in folder
        files = [ fname for fname in os.listdir(folderpath)
                  if os.path.isfile(os.path.join(folderpath,fname))
                     and '.f' in fname[-7:] ]
        files.sort()
        # Select only files that don't contain filetoignore and extention in fileext
        fileext = self.conf['model']['fileext']
        filetoignore = self.conf['model']['filetoignore']
        filescut = []
        for fname in files:
            fsel = False
            # Make sure filename has extension in fileext
            for ext in fileext:
                if ext.upper() in fname[-len(ext):].upper(): fsel = True
            # Exclude files that match any filetoignore entries
            for ign in filetoignore:
                if ign in fname: fsel = False
                elif re.search(ign,fname): fsel = False
            if fsel: filescut.append(fname)        
        # Check for available files else set empty pipedata objects
        if len(filescut) == 0:
            self.log.warn('No files in Folder = %s' % folder)
            self.data = PipeData(config = self.data.config)
            return
        # See if there are files with reduction status, use it:
        # i.e. filename longer than filenamebegin+filenameend
        fileind = len(filescut)
        filepathname = ''
        while fileind:
            fileind-=1
            self.data.filename = filescut[fileind]
            if len(self.data.filename) > len(self.data.filenamebegin+self.data.filenameend):
                filepathname = os.path.join(folderpath,filescut[fileind])
                break
        if not len(filepathname):
            filepathname = os.path.join(folderpath, filescut[-1])
        # Load first file info header
        self.infohead = self.conf['model']['infohead']
        loaded = False
        self.log.debug('For %s loading header %s' % (folder, filepathname) )
        if len(self.infohead) > 0:
            try:
                self.data.loadhead(filepathname,
                                   dataname=self.infohead)
                loaded = True
            except:
                pass
        if not loaded:
            try:
                self.infohead = ''
                self.data.loadhead(filepathname)
            except:
                self.log.warn('loadhead error with file = %s' % filescut[-1])
                self.data = PipeData(config = self.data.config)
        self.log.debug('folderhead loaded, file=%s' % filescut[-1])
    
    def loglist(self):
        """ Returns list with the log information for the current
            loglevel session setting.
        """
        # Set levels
        levels = ['DEBUG','INFO','WARNING','ERROR','CRITICAL']
        level = self.session['loglevel']
        if not level in levels:
            levels = levels[1:]
        else:
            ind = levels.index(level)
            levels = levels[ind:]
        # Adjust level format
        if 'levelformat' in self.conf['model']:
            lvlfmt = self.conf['model']['levelformat']
            levels = [lvlfmt % level for level in levels]
        # Open log file
        logfilename = os.path.join(self.conf['path']['pipelog'])
        logfile = open(logfilename,'rb')
        # Read Last entries from log file (last 50kb)
        if os.path.getsize(logfilename) > 51000:
            logfile.seek(-50000,2)
        loglines = logfile.readlines()[1:]
        logfile.close()
        # Make list of requested Lines
        outlist = []
        for line in loglines:
            line = line.decode('ascii')
            for level in levels:
                if level in line:
                    outlist.append(line)
        # Cut the list to 1000 entries
        if len(outlist) > 1000:
            outlist = outlist[-1000:]
        # Return the list
        return outlist

""" === History ===
    -->> See Controller.py <<--
"""

