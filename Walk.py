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
        parser.parse(iniFileName)

    def walk(self, vimCommand):
        self.__lstParams = self.__iniFileHandler.getLstParams()
        if vimCommand != "":
            self.__lstParams["VimFileCommand"] = vimCommand
        if self.__lstParams.has_key("OutFile"):
            self.__outFile = open(self.__lstParams["OutFile"][0]["name"],self.__lstParams["OutFile"][0]["mode"])
            # vim.command('let @f="' + string.replace(self.__lstParams["OutFile"],"\\","\\\\") + '"')
        else:
            vim.command('let @x=""')        
        # Write beginning of the page
        if self.__lstParams.has_key("ArgPagePre"):
            self.writeOutFile(self.processArg(self.__lstParams["ArgPagePre"],-1))
        for i in range(len(self.__lstParams["RootDirs"])):
            # Write Pre Root Dir arguments
            if self.__lstParams.has_key("ArgRootDirPre"):
                self.writeOutFile(self.processArg(self.__lstParams["ArgRootDirPre"],i))
            os.path.walk(self.__lstParams["RootDirs"][i]["SourceDir"], self.listFiles,i)
            # Write Post Root Dir arguments
            if self.__lstParams.has_key("ArgRootDirPost"):
                self.writeOutFile(self.processArg(self.__lstParams["ArgRootDirPost"],i))
        # Write end of the page
        if self.__lstParams.has_key("ArgPagePost"):
            self.writeOutFile(self.processArg(self.__lstParams["ArgPagePost"],-1))
        if self.__lstParams.has_key("OutFile"):
            self.__outFile.close()
            vim.command("e " + self.__lstParams["OutFile"][0]["name"])
            if self.__lstParams.has_key("OutFileCommand"):
                vim.command(self.__lstParams["OutFileCommand"])

    def listFiles(self, arg, dirname, names):
        i = arg
        self.__lstParams["SubDir"] = dirname
        if self.__lstParams.has_key("WildCard"):
            wc = re.compile(self.__lstParams["WildCard"])
        else:
            wc = re.compile(".")
        # Write Pre visited Dir arguments
        if self.__lstParams.has_key("ArgSubDirPre"):
            self.writeOutFile(self.processArg(self.__lstParams["ArgSubDirPre"],i))
        for name in names:
            if wc.search(name):
                self.__lstParams["File"] = name
                # Write Pre File arguments
                if self.__lstParams.has_key("ArgFilePre"):
                    self.writeOutFile(self.processArg(self.__lstParams["ArgFilePre"],i))
                vim.command('let @o=""')
                if self.__lstParams.has_key("VimFileCommand"):
                    vim.command("silent e " + dirname + "\\" + name)
                    vim.command("silent " + self.__lstParams["VimFileCommand"])
                if vim.eval("@o") != "" :
                    self.writeOutFile(vim.eval("@o")[:-1])
                # Write Post File arguments
                if self.__lstParams.has_key("ArgFilePost"):
                    self.writeOutFile(self.processArg(self.__lstParams["ArgFilePost"],i))
        # Write Post visited Dir arguments
        if self.__lstParams.has_key("ArgSubDirPost"):
            self.writeOutFile(self.processArg(self.__lstParams["ArgSubDirPost"],i))

    def writeOutFile(self, strg):
        if self.__lstParams.has_key("OutFile"):
            self.__outFile.write(strg+"\n")
        else:
            vim.command('let @X="' + strg + '\n"')

    def processArg(self,prm,i):
        ret = prm
        lstArgs=re.findall("\[\[[^\]]*\]\]",prm)
        for arg in lstArgs:
            lstElts = string.split(arg[2:-2],".")
            if len(lstElts) == 2:
                var = self.__lstParams[lstElts[0]][i][lstElts[1]]
            elif len(lstElts) == 1:
                var = self.__lstParams[lstElts[0]]
            ret = string.replace(ret,arg,var)
        lstArgs=re.findall("\{\{[^\}]*\}\}",ret)
        for arg in lstArgs:
            vim.command("let @r = " + string.replace(arg[2:-2],"\\","\\\\"))
            var = vim.eval("@r")
            ret = string.replace(ret,arg,var)
        return ret

