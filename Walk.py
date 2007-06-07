# -*- coding: iso-8859-1 -*-
# License: GPL (GNU Public License)

import vim, os, os.path, string, re
from xml.sax import *
from xml.sax.handler import *
from FicIni import *

# Because of the way os.path.walk is written, I have to import the vim module here. It would certainly be cleaner
# not to do that but it would mean rewrite something like os.path.walk and i'm not sure the work worth it.

class Walk:
    def __init__(self, iniFileName):
        # Create a parser
        parser = make_parser()
        # Tell the parser we are not interested in XML namespaces
        parser.setFeature(feature_namespaces, 0)
        # Create the handler
        self.__iniFileHandler = iniFile()
        # Tell the parser to use our handler
        parser.setContentHandler(self.__iniFileHandler)
        # Parse the input
        print iniFileName
        parser.parse(iniFileName)
        self.__lstParams = self.__iniFileHandler.getLstParams()

    def walk(self, vimCommand):
        if vimCommand != "":
            self.__lstParams["VimFileCommand"] = vimCommand
        if self.__lstParams.has_key("OutFile"):
            self.__outFile = []
            for noOutFile in range(len(self.__lstParams["OutFile"])):
                self.__outFile = self.__outFile + [open(self.__lstParams["OutFile"][noOutFile]["Name"],self.__lstParams["OutFile"][noOutFile]["Mode"])]
        else:
            vim.command('let g:outPut=""')        
        # Write beginning of the page
        if self.__lstParams.has_key("ArgPagePre"):
            self.writeOutFile(self.processArg(self.__lstParams["ArgPagePre"],-1))
        for noSrcDir in range(len(self.__lstParams["RootDirs"])):
            # Write Pre Root Dir arguments
            if self.__lstParams.has_key("ArgRootDirPre"):
                self.writeOutFile(self.processArg(self.__lstParams["ArgRootDirPre"],noSrcDir))
            os.path.walk(self.__lstParams["RootDirs"][noSrcDir]["SourceDir"], self.listFiles,noSrcDir)
            # Write Post Root Dir arguments
            if self.__lstParams.has_key("ArgRootDirPost"):
                self.writeOutFile(self.processArg(self.__lstParams["ArgRootDirPost"],noSrcDir))
        # Write end of the page
        if self.__lstParams.has_key("ArgPagePost"):
            self.writeOutFile(self.processArg(self.__lstParams["ArgPagePost"],-1))
        # Write out files
        vim.command("q")
        if self.__lstParams.has_key("OutFile"):
            for noOutFile in range(len(self.__lstParams["OutFile"])):
                self.__outFile[noOutFile].close()
                print self.__lstParams["OutFile"][noOutFile]["Name"]
                if self.__lstParams["OutFile"][noOutFile].has_key("Edit") \
                        and self.__lstParams["OutFile"][noOutFile]["Edit"][0:1] in ['o', 'O', 'y', 'Y']:
                    vim.command("split")
                    vim.command("e " + self.__lstParams["OutFile"][noOutFile]["Name"])
                if self.__lstParams.has_key("OutFileCommand") and noOutFile == 0:
                    vim.command(self.__lstParams["OutFileCommand"])

    def listFiles(self, arg, dirname, names):
        noSrcDir = arg
        self.__lstParams["SubDir"] = dirname
        if self.__lstParams.has_key("WildCard"):
            wc = re.compile(self.__lstParams["WildCard"])
        else:
            wc = re.compile(".")
        # Write Pre visited Dir arguments
        if self.__lstParams.has_key("ArgSubDirPre"):
            self.writeOutFile(self.processArg(self.__lstParams["ArgSubDirPre"],noSrcDir))
        names.sort()
        for name in names:
            if os.path.isfile(dirname + "/" + name):
                if wc.search(name):
                    self.__lstParams["File"] = name
                # Write Pre File arguments
                if self.__lstParams.has_key("ArgFilePre"):
                    self.writeOutFile(self.processArg(self.__lstParams["ArgFilePre"],noSrcDir))
                for noOutFile in range(len(self.__lstParams["OutFile"])):
                    vim.command('let @' + self.__lstParams["OutFile"][noOutFile]["Register"] + '=""')
                if self.__lstParams.has_key("VimFileCommand"):
                    vim.command("silent e " + dirname + "/" + name)
                    #print self.processArg(self.__lstParams["VimFileCommand"],noSrcDir)
                    vim.command("silent " + self.processArg(self.__lstParams["VimFileCommand"],noSrcDir))
                    if self.__lstParams.has_key("OutFile"):
                        for noOutFile in range(len(self.__lstParams["OutFile"])):
                           try:
                              if vim.eval("@" + self.__lstParams["OutFile"][noOutFile]["Register"]) != "" :
                                 self.writeOutFile(vim.eval("@" + self.__lstParams["OutFile"][noOutFile]["Register"])[:-1],noOutFile)
                           except KeyError:
                             # No Register defined in the ini file
                             pass
                    #vim.command("silent bd")
                # Write Post File arguments
                if self.__lstParams.has_key("ArgFilePost"):
                    self.writeOutFile(self.processArg(self.__lstParams["ArgFilePost"],noSrcDir))
        # Write Post visited Dir arguments
        if self.__lstParams.has_key("ArgSubDirPost"):
            self.writeOutFile(self.processArg(self.__lstParams["ArgSubDirPost"],noSrcDir))

    def writeOutFile(self, strg, noOutFile=0):
        if self.__lstParams.has_key("OutFile"):
            self.__outFile[noOutFile].write(strg+"\n")
        else:
            vim.command('let g:outPut=g:outPut . "' + strg + '\n"')

    def processArg(self,prm,noSrcDir):
        """
            interprets the [[]] and {{}} arguments
        """
        ret = prm
        lstArgs=re.findall("\[\[[^\]]*\]\]",prm)
        for arg in lstArgs:
            lstElts = string.split(arg[2:-2],".")
            if len(lstElts) == 2:
                var = self.__lstParams[lstElts[0]][noSrcDir][lstElts[1]]
            elif len(lstElts) == 1:
                var = self.__lstParams[lstElts[0]]
            ret = string.replace(ret,arg,var)
        lstArgs=re.findall("\{\{[^\}]*\}\}",ret)
        for arg in lstArgs:
            if arg[2:7]=='walk.':
                func="self." + string.replace(arg[7:-2],"\\","\\\\")
                exec "var="+func
                ret = string.replace(ret,arg,var)
            elif arg[2:9]=='python.':
                func=string.replace(arg[9:-2],"\\","\\\\")
                exec "var="+func
                ret = string.replace(ret,arg,var)
            else:
                vim.command("let g:returnValue = " + string.replace(arg[2:-2],"\\","\\\\"))
                var = vim.eval("g:returnValue")
                vim.command("unlet g:returnValue")
                ret = string.replace(ret,arg,var)
        return ret

    # Now we have some other function that can be called in the ini file

    def count(self, dirname, wildcard, lib):
        """ Counts the number of files corresponding to the wildcard
        """
        wc=re.compile(wildcard)
        compteur=0
        for fic in os.listdir(dirname):
            if wc.search(fic):
                compteur+=1
        if compteur > 0:
            nb=str(compteur)
            return nb + ' ' + lib
        else:
            return ''

#vim:tw=0 ts=4 sw=4 expandtab:        
