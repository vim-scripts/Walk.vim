import os, string, re, stat, time
from xml.sax.handler import *
from types import *

class iniFile(ContentHandler, DTDHandler, EntityResolver, ErrorHandler):
    """ Provides a parser for XML ini files

        !! WARNING : This is my first use of a XML parser so it may certainly
            be improved.
            If you have remarks to improve it, i'd be glad to know them
            (particularly to make something more general : not having the
            "type" argument and be able to make more complicated trees)
        Datas read from the ini file are written in a dictionnary.
        You may have two types of elements (you have to provide the "type" argument) :
        LISTS :
        <listArg type="lst">
            <arg1>...</arg1><arg2>...</arg2>
            <arg1>...</arg1><arg2>...</arg2>
            <arg1>...</arg1><arg2>...</arg2>
        </listArg>
        For this argument, the dictionnary will have an entry valued with a list of dictionnaries :
        {'listArg' : [{'arg1':... , 'arg2':...},{'arg1':... , 'arg2':...},{'arg1':... , 'arg2':...}]}

        ELEMENTS
        <element type="elt">...</element>
        The dictionnary will be added a new entry :
        {'element' : ...}

        To Use these ini datas in a python program :
        # import xml utilities :
        from xml.sax import *
        from xml.sax.handler import *

        # init the dictionnary
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

        Use the dictionnary :
        self.__lstParams = self.__iniFileHandler.getLstParams()
        for i in range(len(self.__lstParams["listArg"])):
            ...
        myVar = self.__lstParams["element"]
    """
    def __init__(self):
        """ 
            
        """
        self.__iniFile = {}
        self.__pile = []
        self.__currentType = ""

    def getLstParams(self):
        return self.__iniFile

    def startElement(self, name, attrs):
        if attrs.get('type', None)=="lst":
            self.__currentType = "lst"
            self.__iniFile[name]=[{}]
            self.__currentDic = self.__iniFile[name][0]
        elif attrs.get('type', None)=="elt":
            self.__currentType = "elt"
            self.__iniFile[name]=""
            self.__currentDic = self.__iniFile
        elif self.__currentType != "":
            if self.__currentType == "lst":
                if self.__currentDic.has_key(name):
                    self.__iniFile[self.__pile[1]].append({})
                    self.__currentDic = self.__iniFile[self.__pile[1]][-1]
        self.__pile.append(name)

    def characters(self, content):
        content = content.encode("Latin-1")
        if len(self.__pile) > 2:
            self.__currentDic[self.__pile[-1]] = content
        elif self.__currentType == "elt" and len(self.__pile)==2:
            self.__currentDic[self.__pile[-1]] = self.__currentDic[self.__pile[-1]] + content

    def endElement (self, name):
        if len(self.__pile) > 1:
            if not self.__currentDic.has_key(name):
                self.__currentDic = self.__iniFile
            if type(self.__currentDic[self.__pile[-1]]):
                if self.__currentDic[self.__pile[-1]] == "\n":
                    del self.__currentDic[self.__pile[-1]]
                else:
                    if self.__currentDic[self.__pile[-1]][0] == "\n":
                        self.__currentDic[self.__pile[-1]] = self.__currentDic[self.__pile[-1]][1:]
                    if self.__currentDic[self.__pile[-1]][-1] == "\n":
                        self.__currentDic[self.__pile[-1]] = self.__currentDic[self.__pile[-1]][:-1]
            self.__pile.pop()

