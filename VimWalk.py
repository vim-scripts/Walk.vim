import vim, os, os.path, string, re
# Because of the way os.path.walk is written, I have to import the vim module here. It would certainly be cleaner
# not to do that but it would mean rewrite something like os.path.walk and i'm not sure the work worth it.

class VimWalk:
    def __init__(self, arg):
        self.__inDirs=string.split(vim.eval("@d"),'\n')
        self.__outFile=string.replace(vim.eval("@f"),'\n','')
        self.__wildcard=string.replace(vim.eval("@w"),'\n','')
        print self.__inDirs
        print self.__outFile
        # init outfile
        fichierOut=open(self.__outFile, 'w')
        fichierOut.close()
        # Visits each directories trees using the python os.path.walk function
        for inDir in self.__inDirs:
            if inDir != '':
                os.path.walk(inDir, self.listFiles, [self.__wildcard, self.__outFile, arg])

    def listFiles(self, arg, dirname, names):
        print dirname
        for name in names:
            wc = re.compile(arg[0])
            if wc.search(name):
                vim.command('let @o=""')
                if arg[2] != "":
                    vim.command("silent e " + dirname + "\\" + name)
                    vim.command("silent " + arg[2])
                else:
                    vim.command('let @o="' + string.replace(dirname,"\\","\\\\") + "\\\\" + name + '\n"')
                if vim.eval("@o") != "" and arg[1] != "":
                    fo=open(arg[1],'a')
                    fo.write(vim.eval("@o"))
                    fo.close()

