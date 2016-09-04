#Json file path here
pathnm =  './'
filenm = 'vips_www1.macys.com (1).json'

#ID(s) of objects we want to find similar objects to
selectedVIPSids = ['1-21-1-1','1-21-1-2']

#Threshold (website dependent)
threshFrac = 0.62

#Path to write results to check them by highlighting
javaScriptFilePath = '/WebDataView20160625/ng-dashboard/app/contentScript/vipsSuggest.js'


import time
import numpy as np
import pandas as pd
import json
import codecs
import itertools
import xlwt

#Reading in the json file
jsonfileData = json.load(codecs.open(pathnm + '/' + filenm, 'r', 'utf-8-sig'))
jsonDF = pd.DataFrame(jsonfileData['blocks'])


#Removing unwanted/repeating attributes
def removeUnvaryingAttributes(dtfrm):
    AllColNames = set(dtfrm.columns.values.flat)
    NAColNames = []
    OnlyoneColNames = []
    BannedColNames = []
    for colname in AllColNames:
        try:
            frq = dtfrm[colname].value_counts()
            tot = sum(frq)
            frq = frq/tot
            if frq.count() == 0:
                NAColNames.append(colname)
            else:
                if frq.count() == 1:
                    OnlyoneColNames.append(colname)
        except TypeError:
            BannedColNames.append(colname)

    print('Number of attributes Total: {}'.format(len(AllColNames)))
    print('Number of attributes with NA values: {}'.format(len(NAColNames)))
    print('Number of attributes with same constant value: {}'.format(len(OnlyoneColNames)))
    AllowedColNames = (AllColNames - (set(NAColNames) | set(OnlyoneColNames) )) | set(['-vips-id'])
    return (AllColNames, NAColNames, OnlyoneColNames, BannedColNames, AllowedColNames)

#Creating dataset of useful objects
def getDFofScreenedObjects(dtfrm, sltdVIPSid):
    AttMustBeSame = ['-att-tagName',
                     '-style-max-width', '-style-cursor', '-att-autocapitalize',
                     '-att-autocomplete', '-att-draggable', '-att-type',
                     '-att-value']
    AttSameExistence = ['-att-width', '-att-height', '-att-x', '-att-y',
                        '-att-origin', '-att-search', '-att-innerHTML', '-att-innerText',
                        '-att-outerHTML', '-att-outerText', '-att-text', '-att-currentSrc',
                        '-att-src', '-att-alt', '-att-href', '-att-id',
                        '-att-pathname',
                        '-att-naturalHeight', '-att-naturalWidth']
    def Screening(refObj, obj):
        tf = refObj[AttMustBeSame].isnull() & obj[AttMustBeSame].isnull()
        if any(refObj[AttMustBeSame][~tf] != obj[AttMustBeSame][~tf]):
            return False
        elif any(refObj[AttSameExistence].isnull() != obj[AttSameExistence].isnull()):
            return False
        else:
            return True
    refObj = dtfrm[dtfrm['-vips-id'] == sltdVIPSid].squeeze()
    ScreenedObjects = []
    for idx, obj in dtfrm.iterrows():
        if Screening(refObj, obj):
            ScreenedObjects.append(obj['-vips-id'])
    screenedDF = dtfrm[dtfrm['-vips-id'].isin(ScreenedObjects)]
    return screenedDF

#Finding similarity between given objects and all others to find more similar ones
def findSimilarObjects(dtfrm, sltdVIPSid, threshFrac, AllowedColNames):
    # inputs are websiteIdentifier and object's vipsid and threshold fraction
    wbDF = dtfrm[list(AllowedColNames)]
    refObj = wbDF.loc[wbDF['-vips-id'] == sltdVIPSid].squeeze()
    SimObjects = []
    threshold = wbDF.shape[1] * threshFrac
    for idx, obj in wbDF.iterrows():
        summ = sum(obj==refObj)
        refcls = refObj['-att-className']
        objcls = obj['-att-className']
        if refcls and objcls:
            if ((refcls in objcls) | (objcls in refcls)):
                summ += 2
    #    if (refObj['-vips-endX'] - refObj['-vips-startX']) == (obj['-vips-endX'] - obj['-vips-startX']):
    #        summ += 2
        if summ > threshold:
            SimObjects.append(obj['-vips-id'])
    return SimObjects

#writing results to an output file
def writeVipsSuggesJavaScriptFile(javaScriptFilePath, SimObjectsAllSelections):
    xy = ['none']*len(SimObjectsAllSelections)
    strmid = ['none']*4
    for j in range(len(SimObjectsAllSelections)):
        xy[j] =   'ids{} = ['.format(j)    +    ','.join(['"{}"'.format(x) for x in SimObjectsAllSelections[j]])    +    '];'
    strbefore = """vips = new VipsAPI(); globalBlocks = vips.getVisualBlockList();"""
    strmid[0] = """for (var i = 0; i < globalBlocks.length; i++) {for (var j = 0; j < ids0.length; j++) { if (globalBlocks[i]['-vips-id']===ids0[j]) globalBlocks[i]['-att-box'].style.border = "4px solid orange";}}; """
    strmid[1] = """for (var i = 0; i < globalBlocks.length; i++) {for (var j = 0; j < ids1.length; j++) { if (globalBlocks[i]['-vips-id']===ids1[j]) globalBlocks[i]['-att-box'].style.border = "4px solid green";}}; """
    strmid[2] = """for (var i = 0; i < globalBlocks.length; i++) {for (var j = 0; j < ids2.length; j++) { if (globalBlocks[i]['-vips-id']===ids2[j]) globalBlocks[i]['-att-box'].style.border = "4px solid blue";}}; """
    strmid[3] = """for (var i = 0; i < globalBlocks.length; i++) {for (var j = 0; j < ids3.length; j++) { if (globalBlocks[i]['-vips-id']===ids3[j]) globalBlocks[i]['-att-box'].style.border = "4px solid black";}}; """
    strafter = """confirm("We think the highlighted blocks are interest data in this page. Do you want to save it?");"""
    with open(javaScriptFilePath, 'w') as jsfile:
        jsfile.write(strbefore   +    ''.join(xy)    +   ''.join(strmid[0:len(SimObjectsAllSelections)])  +  strafter)

#Associating images to price to reviews to title, take distance between selected objects as reference to associate others
def generateAssociates(AssVips, dtfrm, SimObjectsAllSelections):
    print('Works only if all selected vips-ids are for the same product')
    def getXdsYds(refObj, obj):
        return (refObj['-vips-startX']-obj['-vips-startX'], refObj['-vips-startY']-obj['-vips-startY'])
    def checkDistWithRefDist(refPairsofDistances, obsvPairsofDistances):
        for item in zip(refPairsofDistances, obsvPairsofDistances):
            (rdx, rdy) = item[0]
            (odx, ody) = item[1]
            if not (abs(rdx-odx)/max(abs(rdx)+0.000001,abs(odx)+0.000001)<0.25 and abs(rdy-ody)/max(abs(rdy),abs(ody))<0.5):
                return False
        return True

    refPairsOfDistances = []
    for item in AssVips[1:]:
            (Xds, Yds) = getXdsYds(dtfrm[dtfrm['-vips-id'] == AssVips[0]].squeeze(), dtfrm[dtfrm['-vips-id'] == item].squeeze())
            refPairsOfDistances.append((Xds,Yds))

    otherClusters = SimObjectsAllSelections[1:]
    associates = []
    for elemId1 in SimObjectsAllSelections[0]:
        for elemId2 in list(itertools.product(*otherClusters)):
            obsvPairsOfDistances = []
            for item in elemId2:
                (Xds, Yds) = getXdsYds(dtfrm[dtfrm['-vips-id'] == elemId1].squeeze(), dtfrm[dtfrm['-vips-id'] == item].squeeze())
                obsvPairsOfDistances.append((Xds, Yds))
            if checkDistWithRefDist(refPairsOfDistances, obsvPairsOfDistances):
                associates.append( [elemId1] + list(elemId2) )
                break
    return associates


times=[time.time()]
(AllColNames, NAColNames, OnlyoneColNames, BannedColNames, AllowedColNames) = removeUnvaryingAttributes(jsonDF)
times.append(time.time())
SimObjectsAllSelections = []
for sltdVIPSid in selectedVIPSids:
    screenedjsonDF = getDFofScreenedObjects(jsonDF, sltdVIPSid)
    SimObjectsAllSelections.append( findSimilarObjects(screenedjsonDF, sltdVIPSid, threshFrac, AllowedColNames) )
times.append(time.time())
writeVipsSuggesJavaScriptFile(javaScriptFilePath, SimObjectsAllSelections)
print('javascript file updated')
times.append(time.time())
Associates = generateAssociates(selectedVIPSids, jsonDF, SimObjectsAllSelections)
times.append(time.time())


textflag = [(0 if type(jsonDF[jsonDF['-vips-id']==item].squeeze()['-att-src']) is str else 1) for item in  selectedVIPSids ]
book = xlwt.Workbook(encoding="utf-8")
sheet1 = book.add_sheet("Sheet 1")
for i, lis in enumerate(Associates):
    for j, vipid in enumerate(lis):
        sheet1.write(i, j, jsonDF[jsonDF['-vips-id']==vipid].squeeze()['-att-innerText' if textflag[j] else '-att-src'])
book.save('associates_macys2.xls')

times.append(time.time())

print('time for eliminating unchanging variables:        {}'.format(times[1]-times[0]))
print('time for finding all clusters of similar objects: {}'.format(times[2]-times[1]))
print('time for writing javascript file:                 {}'.format(times[3]-times[2]))
print('time for finding all associations:                {}'.format(times[4]-times[3]))



print(Associates)
print('----------------')
print('----------------')

for simobjects in SimObjectsAllSelections:
    print(simobjects)
    print('----------------')


