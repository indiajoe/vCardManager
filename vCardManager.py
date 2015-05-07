#!/usr/bin/env python
""" This is a simple vCard manager for manageing all your contacts """

class vCard(dict):
    """ Class for a single contact's vCard """
    def __init__(self,vCardEntryList = None):
        super(vCard, self).__init__()
        self.VERSION = 3.0  # Some default Version to Initialize
        self.ContentList = []  # List which gives order to contents in the dictionary
        if vCardEntryList is not None:  # Load the input list of strings
            self.LoadFromString(vCardEntryList)

    def SplitInpString(self,InpString):
        """ Splits the Inpur vCard line into its various components. viz,  KEY;PARAMS:DATA"""
        InpString = InpString.rstrip()
        Header = InpString.split(':')[0]
        HeaderList = Header.split(';')
        LineDict = {}
        LineDict['DATA'] = InpString[len(Header+':'):]  # Remaining part of string is DATA
        LineDict['KEY'] = HeaderList[0]  # First part of HeaderList is KEY
        LineDict['PARAMS'] = HeaderList[1:]  # List of strings split by ;
        return LineDict

    def LoadFromString(self,vCardStringList):
        """ Loads the vCard Instance with parameters from a list of Input text vCard lines """
        print('vCard Version {0}'.format(self.VERSION))
        for line in vCardStringList:
            LineDic = self.SplitInpString(line)
            if LineDic['KEY'].upper() == 'VERSION' : # New Version number
                self.VERSION = float(LineDic['DATA'])
                print('vCard Version {0}'.format(self.VERSION))
            elif LineDic['KEY'].upper() == 'LABEL' : # In Version (2.1 and 3.0) it belongs to previous adress
                # Add the param LABEL to the previous ADR key in the vCard
                try :
                    self['ADR'][-1][0]['LABEL'] = LineDic['DATA']
                except KeyError:
                    print('ERROR: LABEL Card without a previous ADR card in the input vCard')
                    print('Discarding...: '+line)
                    continue
            else : # Normal entry !
                ParamsDic = {}
                if self.VERSION in set((3.0,4.0,2.1)):
                    # Parameters are inFormat PARAM=VALUE. OR simply VALUE when PARAM is TYPE in version 2.1
                    for parval in LineDic['PARAMS']: 
                        if len(parval.split('=')) > 1 :
                            ParamsDic.setdefault(parval.split('=')[0],[]).append(*parval.split('=')[1].split(','))
                        else:  # Version 2.1 without TYPE key
                            ParamsDic.setdefault('TYPE',[]).append(*parval.split('=')[0].split(','))
                else :
                    print('vCard Version {0}'.format(self.VERSION))
                    raise NotImplementedError

                self.setdefault(LineDic['KEY'],[]).append([ParamsDic,LineDic['DATA']])   # Format [{PARAMS},DATA]
                # Update the order list
                self.ContentList.append(LineDic['KEY'])
                
    def __str__(self):
        """ Print the vCard in its output version format """
        String = '\n'.join(['BEGIN:VCARD','VERSION:{0}'.format(self.VERSION)])+'\n'
        for entry in self.ContentList:
            for multientry in self[entry]:
                ExtraLineToAppend = None
                ParamDic,Data = multientry
                ParStringList=[]
                for par in ParamDic:
                    if (self.VERSION == 2.1) and (par == 'TYPE'):
                        ParStringList+= ParamDic[par]  # Append to Parameter list without the TYPE= Key word
                    elif (self.VERSION in set((2.1,3.0))) and (entry == 'ADR') and (par == 'LABEL'):
                        # Skip this LABEL par for now and append it as a new line in end
                        ExtraLineToAppend = '{0}{1}:{2}\n'.format(par,';'.join(['']+ParStringList),ParamDic[par])
                    else :
                        ParStringList+= ['{0}={1}'.format(par,','.join(ParamDic[par]))]  # Append to Parameter list
                
                # Append everything to Newline
                String += '{0}{1}:{2}'.format(entry,';'.join(['']+ParStringList),Data)+'\n'

                if ExtraLineToAppend is not None: String += ExtraLineToAppend
                
        String += 'END:VCARD'  # Note: No trailing \n to avoid a blank line at the end
        return String

    
                    


class vCardList(list):
    """ This is a list of vVard objects with some extra features """
    def __init__(self,inpfile = None):
        super(vCardList, self).__init__()
        if inpfile is not None:
            self.LoadVCFfile(inpfile)
    
    def LoadVCFfile(self,vcfFile):
        """ Loads all the vCards from the input .vcf File """
        with open(vcfFile,'r') as inpfile:
            vCardEntryList = []
            vCardLine = False                    
            for line in inpfile:
                line = line.rstrip()
                if not line : # line is empty ''
                    continue
                elif line[0:len('BEGIN:VCARD')].upper() == 'BEGIN:VCARD' : #Star of vCard Entry
                    vCardLine = True
                    vCardEntryList = []
                elif line[0:len('END:VCARD')].upper() == 'END:VCARD' : #End of vCard Entry    
                    vCardLine = False 
                    # Load the Vcard !!
                    self.append( vCard(vCardEntryList=vCardEntryList) )
                elif line[0] == ' ': # Continuation of previous line
                    vCardEntryList[-1] += line[1:]
                elif vCardLine : # If vCardLine is True 
                    vCardEntryList.append(line)
                    
    def WriteVCFfile(self,Outfilename,mode='a'):
        """ Writes the vCarList into a .vcf file
        mode = 'a' will append to any existing .vcf file
             = 'w' will overwrite any existing .vcf file """
        with open(Outfilename,mode) as outfile:
            outfile.write('\n'.join((str(vc) for vc in self))+'\n')
        

