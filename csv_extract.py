#! /usr/bin/env python
# -*- coding:utf-8 -*-
###################################
#
# capture files parser
#
#
###################################
#
# Extract Data from .csv
#
###################################
# usage, to extract data from your own python script :
#
#
# t,n,y = myParser.ExtractData(DataSetFileName, DataSetName)
#   # or
# t,n,y,l = myParser.ExtractData(DataSetFileName, DataSetName, LinesList=True)
#   # arguments:
#   # DataSetFileName = name of .xml file which defines data to be extracted (e.g. PlotConfig.xml)
#   # DataSetName = name of node of DataSetFileName to take into account
# optional parameters :
#   # if DataSet refers to parameters by using syntax "DataValue="{n}" in filters, then define an additional argument:
#   #     DataSetParams=[] = list of parameters. While parsing DataSet, {n} will be replaced by DataSetParams[n]
#   # tmin,tmax : extract only data between tmin and tmax (defined in seconds since 1st packet of file)
#   # nbPackets : parse only a limited number of packets
#   #     Use this parameter to parse very big files by parts (tested up to 660Go)
#   #     By default ExtractData will parse one file and load all parsed data in RAM
#
# returns lists t, n, y and optionally l
# does not return anything in case of error, (or eof reached if called with argument nbPackets)
# t[i] = list of timestamps corresponding to Data defined by DataList[i]
# n[i] = list of packet numbers corresponding to Data defined by DataList[i]
# y[i] = list of values of Data defined by DataList[i]
# l = list of lines from input file corresponding to decoded data, format=format formerly used for txt files, but with absolute timestamps (long : microsec since epoch)

###################################

from xml.dom.minidom import parse
import datetime

###### csv file parser ######
'''
Example of CSV content:
Date;Prix en euros;Index total en Wh;PAPP: Puissance apparente en V.A;PTEC: Periode tarifaire (HC=0, HP=1)
2016-03-10 19:19:16.220323;0,00037548;3;1470;1
'''
class c_csv:
    def __init__(self, filename):
        self.fd = open(filename, 'r')
        self.n = 0  # packet number => numero de ligne
        self.t0us = -1  # date of first packet in microseconds since epoch
        self.firstPacket = True  # first packet ? (to update t0)

    def getNextFrame(self, tmin=-1, tmax=-1):
        # each call to this function returns one captured frame (a few filters implemented)
        # returns None when end of file reached
        # optional tmin and tmax are relative to the first packet of file, and defined in seconds
        if not (self.fd):
            return

        current_line = self.fd.readline()  # read next block type
        if current_line == "":
            # fin de fichier
            self.fd.close()
            return # eof reached

        fields_of_line = current_line.split(";")
        self.n += 1
        try:
            timestamp = datetime.datetime.strptime(fields_of_line[0], "%Y-%m-%d %H:%M:%S.%f")
            absTimestamp = (timestamp - datetime.datetime.utcfromtimestamp(0)).total_seconds()
            prix      = float(fields_of_line[1].replace(',','.'))
            index     =   int(fields_of_line[2])
            puissance =   int(fields_of_line[3])
            periode   =   int(fields_of_line[4])
        except ValueError:
            # ligne de titre
            print "Line not decoded: may be  a title ? " + current_line
            return -1

        # ligne de données
        return [self.n, absTimestamp, prix, index, puissance, periode]

###### parse 1 frame ######
class c_FrameParser:
    def __init__(self, name, p, enumDic={}):
        self.name = name
        self.header = p.header
        self.footer = p.footer
        self.keyName = p.keyName
        self.subParserDic = p.subParserDic
        self.enumDic = enumDic

    def __DecodeData(self, data, invert, display):
        # decodes data provided as string (e.g. "0123") according to 'invert' and 'display' options
        if (invert == "True"):  # invert bytes order
            result = ''
            for i in range(len(data) / 2): result = data[2 * i:2 * i + 2] + result
            data = result
        data = data.replace(' ', '')
        if (display == "HEX"): return "0x" + data
        # convert to int
        try:
            dataint = int(data, 16)
        except:
            dataint = -1
        if (display == "DEC" or not (self.enumDic)): return dataint
        if (not (self.enumDic)): return ""
        # enum
        if (display in self.enumDic):
            if (dataint in self.enumDic[display]):
                return self.enumDic[display][dataint] + " (" + str(dataint) + ")"
            else:
                print("Warning, enum data value not found: {" + display + " : " + str(dataint) + "}")
                return dataint
        else:
            print("Warning, enum data type not found: " + display)
        return ""

    def parse(self, msg, parserDic):
        # parses 1 frame, and returns 3 lists:
        TypesList = [self.name]  # list of names of parsers successively invoked
        DataList = []  # list of decoded data
        DataNamesList = []  # list of data names
        # parse header
        for h in self.header:
            DataList.append(self.__DecodeData(msg[0:2 * h.length], h.invertBytes, h.display))
            DataNamesList.append(h.dataName)
            msg = msg[2 * h.length:]
        # look for "data" field
        FooterSize = 0
        for f in self.footer: FooterSize = FooterSize + f.length
        data = msg[0:len(msg) - 2 * FooterSize]
        # try to find a parser of lower level -> recursive call
        data_decoded = False
        if self.keyName:
            # at least one sub-parser is defined
            # one data with corresponding DataName should exist in frame (else, config file is inconsistent...)
            if self.keyName in DataNamesList:  # OK
                keyValue = str(DataList[DataNamesList.index(self.keyName)])
                if self.subParserDic.has_key(keyValue):
                    # sub-parser found
                    SubParser = c_FrameParser(self.subParserDic[keyValue], parserDic[self.subParserDic[keyValue]],
                                              self.enumDic)
                    TypesSubList, DataSubList, DataNamesSubList = SubParser.parse(data, parserDic)
                    TypesList = TypesList + TypesSubList
                    DataList = DataList + DataSubList
                    DataNamesList = DataNamesList + DataNamesSubList
                    data_decoded = True
        if (not (data_decoded) and len(data) > 0):
            DataList.append("0x" + data)
            DataNamesList.append("data")
        # footer
        msg = msg[len(msg) - 2 * FooterSize:]
        for f in self.footer:
            DataList.append(self.__DecodeData(msg[0:2 * f.length], f.invertBytes, f.display))
            DataNamesList.append(f.dataName)
            msg = msg[2 * f.length:]

        return TypesList, DataList, DataNamesList


###########################
class NamedStruct(object):
    ''' Named Structure definition
        Similar to Named Tuple, but:
        - fields value can be udpated
        - fields can be added
        - auto-completion is available in certain circumstances '''

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def exist(self, field):
        ''' Return True if the field specified exist '''
        return hasattr(self, str(field))

    def field(self, name):
        ''' Access to a field by using its name as a string'''
        return self.__dict__[str(name)]


###### the class to import ######
class c_Parser:
    def __init__(self, ConfFileName):
        # read config file (create parsers dictionary from xml conf file)
        self.__parserDic = {}
        self.__enumDic = {}
        self.__TopLevelParsers = []
        if not ConfFileName: return
        self.confFileVersion = parse(ConfFileName).getElementsByTagName("FileParser")[0].getAttribute(
            "FramesStructureVersion")
        for Elt in parse(ConfFileName).documentElement.getElementsByTagName("Parser"):
            p = self.__xmlElt2Parser(Elt)
            self.__parserDic = dict(self.__parserDic.items() + p.items())
        for Elt in parse(ConfFileName).documentElement.getElementsByTagName("DataType"):
            p = self.__xmlElt2DataType(Elt)
            self.__enumDic = dict(self.__enumDic.items() + p.items())
        for Elt in parse(ConfFileName).documentElement.getElementsByTagName("TopLevelParser"):
            p = self.__xmlElt2TopLevelParser(Elt)
            self.__TopLevelParsers.append(p)

        self.myPcap = None


    def __IdentifyParser(self, SrcIP, DstIP, DstPort):
        parserName = ""
        for topLevelParser in self.__TopLevelParsers:
            if ((DstPort >= topLevelParser.udpmin) and (DstPort <= topLevelParser.udpmax)):
                parserName = topLevelParser.parser
                return parserName, self.__parserDic[parserName]
        return "", {}

    def __xmlElt2Parser(self, Elt):
        # converts one node <Parser> of .xml configuration file to internal data format
        p = NamedStruct()
        # parser name
        pName = Elt.getAttribute("name")
        # parser header and footer
        pHeader = []
        pFooter = []
        for s in ["header", "footer"]:
            for node in Elt.getElementsByTagName(s):
                Data = NamedStruct()
                Data.dataName = node.getAttribute("dataName")
                Data.length = int(node.getAttribute("length"))
                if node.hasAttribute("invertBytes"):
                    Data.invertBytes = node.getAttribute("invertBytes")
                    assert Data.invertBytes in ["True", "False"]
                else:
                    Data.invertBytes = "True"
                if node.hasAttribute("display"):
                    Data.display = node.getAttribute("display")
                else:
                    Data.display = "DEC"
                if s == "header":
                    pHeader.append(Data)
                else:
                    pFooter.append(Data)
        p.header = pHeader
        p.footer = pFooter
        # sub-parsers
        p.keyName = ""
        p.subParserDic = {}
        for node in Elt.getElementsByTagName("subStructures"):
            p.keyName = node.getAttribute("keyName")
            assert p.keyName
            for subnode in node.getElementsByTagName("subParser"):
                keyValue = subnode.getAttribute("keyValue")
                if (keyValue.startswith('[') and keyValue.endswith(']') and (';' in keyValue)):
                    # keyValue defines a range, create all sub-parsers
                    keyRange = keyValue[1:-1].split(';')
                    parserName = subnode.getAttribute("parserName")
                    assert (len(keyRange) == 2)
                    # add all values in range in dictionary
                    for i in range(int(keyRange[0]), int(keyRange[1]) + 1):
                        subParser = {str(i): parserName}
                        p.subParserDic = dict(p.subParserDic.items() + subParser.items())
                else:
                    # keyValue defines a single value, simply add to dictionary
                    subParser = {keyValue: subnode.getAttribute("parserName")}
                    p.subParserDic = dict(p.subParserDic.items() + subParser.items())
        return {pName: p}

    def __xmlElt2DataType(self, Elt):
        # converts one node <DataType> of .xml configuration file to internal data format
        name = Elt.getAttribute("name")
        # values, labels
        dic = {}
        for node in Elt.getElementsByTagName("enum"):
            value = int(node.getAttribute("value"))
            label = node.getAttribute("label")
            dic = dict(dic.items() + {value: label}.items())
        return {name: dic}

    def __xmlElt2TopLevelParser(self, Elt):
        # converts one node <TopLevelParser> of .xml configuration file to internal data format
        Data = NamedStruct()
        Data.udpmin = Elt.getAttribute("udpmin")
        Data.udpmax = Elt.getAttribute("udpmax")
        Data.parser = Elt.getAttribute("parser")
        return Data

    def __xmlDataSetParam(self, Value, DataSetParams):
        # replace {n} by DataSetParams[n] if defined
        if (not (Value.startswith("{")) or (DataSetParams == ['']) or not (DataSetParams)):
            return (Value)
        if not (Value.endswith("}")):
            print("invalid reference to parameter found in xml file : " + Value)
            assert (False)
        try:
            nparam = int(Value[1:-1])
        except:
            print("non numeric parameter number found in xml file : " + Value)
            assert (False)
        if (nparam < len(DataSetParams)):
            return (DataSetParams[nparam])
        else:
            return (Value)

    def xmlElt2DataSet(self, Elt, DataSetParams=[]):
        # parse one node in .xml plot configuration file
        dataSet = NamedStruct()
        dataSet.name = Elt.getAttribute("name")
        dataSet.description = Elt.getAttribute("description")
        dataSet.paramName = Elt.getAttribute("parameter")
        dataSet.DataList = []
        for node in Elt.getElementsByTagName("data"):
            Data = NamedStruct()
            Data.FrameType = node.getElementsByTagName("FrameType")[0].firstChild.nodeValue
            Data.DataName = node.getElementsByTagName("DataName")[0].firstChild.nodeValue
            if Data.DataName.isnumeric(): Data.DataName = float(Data.DataName)
            Data.DataOffset = 0.0
            DataOffset = node.getElementsByTagName("DataOffset")
            if len(DataOffset) > 0:
                DataOffset = DataOffset[0].firstChild.nodeValue
                if DataOffset.isnumeric():
                    Data.DataOffset = float(DataOffset)

            Data.PlotStyle = node.getElementsByTagName("PlotStyle")[0].firstChild.nodeValue
            FilterList = []
            for NodeFilter in node.getElementsByTagName("Filter"):
                DataFilter = NamedStruct()
                DataFilter.DataName = self.__xmlDataSetParam(NodeFilter.getAttribute("DataName"),
                                                             DataSetParams)  # replace {n} by DataSetParams[n] if defined
                DataFilter.DataValue = self.__xmlDataSetParam(NodeFilter.getAttribute("DataValue"),
                                                              DataSetParams)  # replace {n} by DataSetParams[n] if defined
                FilterList.append(DataFilter)
            Data.FilterList = FilterList
            dataSet.DataList.append(Data)
        return dataSet

    def openPcap(self, InputFileName):
        # InputFileName = .pcap file generated by wireshark
        # open csv file
        self.myPcap = None

        if ".csv" in InputFileName:
            try:
                self.myPcap = c_csv(InputFileName)
            except:
                print("\n-------------\nCan't parse input file: " + InputFileName)
                print("Check file format is csv\n-------------\n")
                return
        else:
            print("\n-------------\nUnknown input file format, aborting...")
            print("input file : " + InputFileName)
            return

    def ExtractData(self, DataSetFileName, DataSetName, LinesList=False, DataSetParams=[], tmin=-1, tmax=-1,
                    nbPackets=-1):
        # DataSetFileName = name of .xml file which defines data to be extracted (e.g. PlotConfig.xml)
        # DataSetName = name of node of DataSetFileName to take into account

        # parse xml conf file
        dataSetList = []
        try:
            for Elt in parse(DataSetFileName).documentElement.getElementsByTagName("DataSet"):
                dataSetList.append(self.xmlElt2DataSet(Elt, DataSetParams))
        except:
            print("\n-------------\nError while parsing xml configuration file\n-------------")
            return

        for dataSet in dataSetList:
            if (dataSet.name == DataSetName):
                DataList = dataSet.DataList

        if not (DataList):
            print(
                "\n-------------\nError while parsing DataSet xml configuration file, DataSet " + DataSetName + " not found")
            return

        # init outputs
        t, n, y, l = [[]], [[]], [[]], []
        for _i in range(1, len(DataList)):
            t.append([])
            n.append([])
            y.append([])

        # parse pcap file
        fields = self.myPcap.getNextFrame(tmin, tmax)

        # fields = [self.n, absTimestamp, prix, index, puissance, periode]

        # prix correspond à index
        # t[i] = list of timestamps corresponding to Data defined by DataList[i]
        # n[i] = list of packet numbers corresponding to Data defined by DataList[i]
        # y[i] = list of values of Data defined by DataList[i]

        firstPacketParsed = self.myPcap.n
        while (fields and (nbPackets < 0 or (self.myPcap.n - firstPacketParsed < nbPackets))):
            if fields != -1:
                for j in xrange(4):
                    t[j].append(fields[1])
                    n[j].append(fields[0])
                    y[j].append(fields[j+2])

            # next frame
            fields = self.myPcap.getNextFrame(tmin, tmax)
        if (not (fields)):
            self.myPcap = None

        if (LinesList):
            return t, n, y, l
        else:
            return t, n, y
