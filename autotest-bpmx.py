# #
# Test to ensure all dataObjects are in Lanes and have source and target CallActivities
# Also to ensure that all dataInputs are outside of Lanes, and have a target but no source
# and to ensure that all dataOutputs are outside of Lanes, and have a source but no target
#
######################################################################################################
import os,re, string
from re import fullmatch
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring, fromstring

#defaultDir = "C:/IBM/gitrepo/bpstest/BPS892 for Standard Tooling"
defaultDir = "./BPS892 for Standard Tooling"
errCount = 0

ns = {'bpmn': 'http://www.ibm.com/xtools/bpmn/2.0'}

def listFiles(dir):                                                                                                  
    fileList = []
    for root, dirs, files in os.walk(dir):
        for name in files:
            fileList.append(os.path.join(root, name))
    return fileList

for filename in listFiles(defaultDir):
    if not filename.endswith(".bpmx"): 
        #print('\n' + filename)
        continue

    ET = ElementTree(file=filename)
    root = ET.getroot()

    for child in root:
        if child.tag == '{http://www.ibm.com/xtools/bpmn/2.0}process':

            flagProcessFound = True
            process = child

            allDataInAssObjects = []
            allDataOutAssObjects = []
            errorText = ''

            # find all call Activities in this process
            for callActivity in process.findall('bpmn:callActivity', ns):
                # find all dataInputAssociations and dataOutputAssociations in this process
                dataInAssObjects = callActivity.findall('bpmn:dataInputAssociation', ns)
                allDataInAssObjects += dataInAssObjects
                dataOutAssObjects = callActivity.findall('bpmn:dataOutputAssociation', ns)
                allDataOutAssObjects += dataOutAssObjects

            # find all service tasks in this process (for OPM ServiceProcesses)
            for serviceTask in process.findall('bpmn:serviceTask', ns):
                # find all dataInputAssociations and dataOutputAssociations in this process
                dataInAssObjects = serviceTask.findall('bpmn:dataInputAssociation', ns)
                allDataInAssObjects += dataInAssObjects
                dataOutAssObjects = serviceTask.findall('bpmn:dataOutputAssociation', ns)
                allDataOutAssObjects += dataOutAssObjects

            # for each data object, find the associated dataInputAssociation (flow FROM the data object)
            # and dataOutputAssociation (flows TO the data object) 

            # find all data objects in this process
            for dataObject in process.findall('bpmn:dataObject', ns):
                doID = dataObject.get('id')
                name = dataObject.get('name')
                doSourceFlag = False
                doTargetFlag = False

                # try to locate a dataInputAssociation and a dataOutputAssociation
                for dia in allDataInAssObjects:
                    if doID == dia.find('bpmn:sourceRef', ns).text.split(':')[1]:
                        doSourceFlag = True
                    if doID == dia.find('bpmn:targetRef', ns).text.split(':')[1]:
                        doTargetFlag = True

                for doa in allDataOutAssObjects:
                    if doID == doa.find('bpmn:sourceRef', ns).text.split(':')[1]:
                        doSourceFlag = True
                    if doID == doa.find('bpmn:targetRef', ns).text.split(':')[1]:
                        doTargetFlag = True

                # if both input and output associations exist, then the data object is connected
                if not (doSourceFlag & doTargetFlag is True):
                    errorText = errorText + '\ndataObject ' + name + ' is invalid\n\n'

            # for each data input, find the associated dataInputAssociation 
            # (flows FROM the data input object) 
            # find all data objects in this process
            for ioSpecs in process.findall('bpmn:ioSpecification', ns):
                for dataInputObject in ioSpecs.findall('bpmn:dataInput', ns):
                    diID = dataInputObject.get('id')
                    name = dataInputObject.get('name')
                    diSourceFlag = False
                    diTargetFlag = False

                    # try to locate a dataInputAssociation and a dataOutputAssociation
                    for doa in allDataOutAssObjects:
                        if diID == doa.find('bpmn:sourceRef', ns).text.split(':')[1]:
                            diSourceFlag = True
                        if diID == doa.find('bpmn:targetRef', ns).text.split(':')[1]:
                            diTargetFlag = True

                    for dia in allDataInAssObjects:
                        if diID == dia.find('bpmn:sourceRef', ns).text.split(':')[1]:
                            diSourceFlag = True
                        if diID == dia.find('bpmn:targetRef', ns).text.split(':')[1]:
                            diTargetFlag = True

                    # if only a output associations exists, then the data output is connected correctly
                    if not (diSourceFlag is True and diTargetFlag is False):
                        errorText = errorText + '\ndataInputObject ' + name + ' is invalid\n\n'

                # for each data output, find the associated dataOutputAssociation 
                # (flows TO the data output object) 
                # find all data output objects in this process
                for dataOutputObject in ioSpecs.findall('bpmn:dataOutput', ns):
                    doID = dataOutputObject.get('id')
                    name = dataOutputObject.get('name')
                    doSourceFlag = False
                    doTargetFlag = False

                    # try to locate a dataInputAssociation and a dataOutputAssociation
                    for doa in allDataOutAssObjects:
                        if doID == doa.find('bpmn:sourceRef', ns).text.split(':')[1]:
                            doSourceFlag = True
                        if doID == doa.find('bpmn:targetRef', ns).text.split(':')[1]:
                            doTargetFlag = True

                    for dia in allDataInAssObjects:
                        if doID == dia.find('bpmn:sourceRef', ns).text.split(':')[1]:
                            doSourceFlag = True
                        if doID == dia.find('bpmn:targetRef', ns).text.split(':')[1]:
                            doTargetFlag = True

                    # if only a output associations exists, then the data output is connected correctly
                    if not (doSourceFlag is False and doTargetFlag is True):
                        errorText = errorText + '\ndataOutputObject ' + name + ' is invalid\n\n'
            if len(errorText) > 0:
                print(filename + '\n' + errorText)
                errCount += 1

print ('BPMX Tests Done: '+ str(errCount) +' errors found')