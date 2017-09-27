#!/usr/bin/env python
# encoding: utf-8


import os
import sys, traceback
import numpy as np
import matplotlib.pyplot as pl
import statsmodels.api as st
import scipy.stats as sts
import matplotlib.patches as mpatches


Colors=['#0000ff','#cc0000','#00cc00','#cc9000','#00e5d8','#5100e5','#d002bf','#000000']
Cnames=['Blue','Red','Green','Orange','Cyan','Purple','Pink','Black']
ColorLookup={'Blue':'#0000ff','Red':'#cc0000','Green':'#00cc00','Orange':'#cc9000','Cyan':'#00e5d8','Purple':'#5100e5','Pink':'#d002bf','Black':'#000000'}

class InputFile:
    
    def __init__(self,csvFile='',usecolumns=[],groupbycolumn=np.nan,header=0,legend=1,groupbyrow=np.nan):
        self.csvfile=csvFile
        self.usecolumns=usecolumns
        self.groupbycolumn=groupbycolumn
        self.header=header
        self.legend=legend
        self.groupbyrow=groupbyrow
        
    def set_csvfile(self,csvFile):
        self.csvfile=csvFile
    def set_usecolumns(self,usecolumns):
        self.usecolumns=usecolumns
    def set_groupbycolumn(self,groupbycolumn):
        self.groupbycolumn=groupbycolumn
    def set_header(self,header):
        self.header=header
    def set_legend(self,legend):
        self.legend=legend
    def set_groupbyrow(self,groupbyrow):
        self.groupbyrow=groupbyrow
    
    def copy_self(self):
        NewInputFile=InputFile(self.csvfile,self.usecolumns,self.groupbycolumn,self.header,self.legend,self.groupbyrow)
        return(NewInputFile)
        
        
        
# Class For each individual Violin Plot
class ViolinPlot:
    def __init__(self,histogramData,histogramLabel,color='Blue'):
        self.data=[]
        self.label=''
        if isinstance(histogramData,list):
            if len(histogramData)==1:
                histogramData=[histogramData[0]*.99,histogramData[0]*1.01]
            self.data=list(histogramData)
            
        else:
            print('HistogramData must be a list')
        
        if isinstance(histogramLabel,str):
            self.label=histogramLabel
        else:
            print('label Must be a string, not list')

        self.color=ColorLookup[color]
    
    def set_color(self,color):
        if ColorLookup.has_key(color):      
            self.color=ColorLookup[color]
        else:
            print'Valid Color Choices are {}'.format(ColorLookup.keys())

# Class for each subgroup, a collection of violin plots in the same subplot
class SubGroup:
    
    def __init__(self):
        self.violinGroups=[]
        self.nViolins=0

    def add_violin(self,violin):
        if isinstance(violin,ViolinPlot):
            violin.set_color(Cnames[self.nViolins])
            self.violinGroups.append(violin)
            self.nViolins=len(self.violinGroups)
        else:
            print('Data must be of class ViolinPlot.  Use "add_lists" to add a categorized list')
    
    def add_list(self,Lists,cats):
        if isinstance(Lists,list):
            if len(Lists)==len(cats):
            
                for ic,data,cat in zip(range(len(Lists)),Lists,cats):
                    
                    if len(data)>=1:
                        vplot=ViolinPlot(list(data),str(cat))
                        vplot.set_color(Cnames[np.mod(ic,len(Cnames))])
                        self.violinGroups.append(vplot) 
                        self.nViolins=len(self.violinGroups)
                        
            else:
                print('Unequal number of lists and lables')
        else:
            print('Arrays Must be numpy structured array')

    def get_data(self):
        data=[]
        for violin in self.violinGroups:
            data.append(violin.data)
        return data
        
    def get_labels(self):
        Lables=[]
        for violin in self.violinGroups:
            Lables.append(violin.label)
        return Lables

    def set_GroupColor(color):
        if ColorLookup.has_key(color): 
            for v in self.violinGroups:
                v.set_color(color)
        else:
            print'Valid Color Choices are {}'.format(ColorLookup.keys())
        
# Class for each subplot, can have multiple groups
class SubPlot:
    
    def __init__(self):
        self.SubGroups=[]
        self.nGroups=0
        self.Title=''
        self.legend=True
        
    def add_subgroup(self,subgroup):
        if isinstance(subgroup,SubGroup):
            self.SubGroups.append(subgroup)
            self.nGroups=len(self.SubGroups)
        else:
            print('Data must be of class SubGroup')
            
    def add_lists(self,lists):
        SubGroups=True
        if isinstance(lists,list):                  
            if SubGroups:                   
                for data,cats in lists:
                    sg=SubGroup()
                    sg.add_list(data,cats)
                    self.SubGroups.append(sg)
                    self.nGroups=len(self.SubGroups)
            else:
                sg=SubGroup()
                for data in datas:
                    sg.add_list([cats,data])
                self.SubGroups.append(sg)
                self.nGroups=len(self.SubGroups)

        else:
            print('Input Must Be a List')
    
    def set_title(self,title):
        self.Title=title
    def set_legend(self,legend):
        self.legend=legend
    

# Class for the overall figure, can have multiple subplots      
class MainFigure:
    def __init__(self):
        self.SubPlots=[]
        self.nPlots=0
        
    def add_subplot(self,subplot):
        if isinstance(subplot,SubPlot):
            self.SubPlots.append(subplot)
            self.nPlots=len(self.SubPlots)
            
        else:
            print('Data must be of class SubPlot')

def PrintInstructions():
    print('\n')
    #print('Usage: ./ViolinPlot [-i] <csvFile1> [<csvFile2>] ... [<csvFileN>] [-skipfirstcol [-firstrowlabel] [-r] [-c] [-h] [-t <label>] [-p] [-s <SavePath>]\n')
    #print('Usage: ./ViolinPlot [-i] <csvFile1> [<csvFile2>] ... [<csvFileN>] [-rowheader] [-usecolumns] [-rowlabel] [-collabel] [-h] [-legend] [-s <SavePath>]\n')
    print('Usage: ./ViolinPlot [-i] <csvFile1> [-usecolumns <ColumnList1>]  ... -i [<csvFileN>] [-usecolumns <ColumnListN>] [-header <0,1,2>] [-groupbycolumn <column number>] [-legend <1,0>] [-h]  [-s <SavePath>]\n')

    print('\t[] = optional input')
    print('\t<> = Value to be replaced with relevant user input\n')

    print('-i: indicateds that the following value is an input CSV file.  Multiple files may be input, as long as they are each preceded with "-i"\n')
    
    print('<csvFile1>: A csv file with multiple columns in which each column is plotted as a violin plot\n')
    print('[<csvFileN>]: Any number of additonal csv files.  Each CSV file becomes its own subplot')
    print('\tData Must be numeric')
    
    print('-usecolumns: specifies which columns to use in the program.  Leave unspecified to use all columns. Syntax is as follows:')
    print('\tThe first column is considered Column 1\n')
    print('\tColumn Range: 4:10')
    print('\tColumn List: 5,26,27,28,68')
    print('\tCombination: 1:10,15,20,30:40  - use of colon ":" indicates a range of columns, each of which is its own violin plot.')
    print('\tGroup Columns: [1:3],[4:6] - use of brackets "[]" results in TWO violin plots, plot 1 is the combination of columns 1-3, plot 2 is the combination of columns 4-6')
    print('\tCreate Subplot: 3,5,6;[7:10],11;13:16 - use of semicolon ";" instead of a comma indicates to create a new subplot for each range specified between semicolons.')
    print('\tIn this example, if there are no other groupings specified by "-groupbycolumn", there will be three subplots:')
    print('\tSubplot 1: 3 violin plots: Column 3, Column 5, and Column 6')
    print('\tSubplot 2: 2 violin plots: Columns 7-10 combined as 1, and Column 11')
    print('\tSubplot 3: 4 violin plots, Column 13, Column 14, Column 15, and Column 16\n')
    
    print('\tAlways separate ranges and individual columns with a comma.  Spaces in the range will result in errors\n')

    print('-header: is value 0, 1, or 2.')
    print('\t0: There is no header in the file; treat the first row as data')
    print('\t1: There is a header in the file, and it should be ignored.  Ignore the first row')
    print('\t2: There is a header in the file, and it should be used as graph labels.\n')

    print('-groupbycolumn: "first" or "last".  specifies which column to use for data grouping.  If this is specified, violin plots will be sub-grouped by the value in this column.')
    print('\tThis can be the keywords "first" or "last" corrosponding to the first and last column')
    print('\tGroups in the specified column may be numeric (i.e. "1", "2", "3"), or labels (i.e. "old", "young"). ')
    print('\tLabels are NOT Case Sensetive.  There should be at least two members of each group.')
    print('\tWith this option, each column will now produce as many violin plots as there are row lables')
    print('\tEvery row in the sheet must have a label for proper functioning.\n')
    
    # print('-collabel: specifies which row to use for lables.  If this is specified, violin plots will be sub-grouped by the value in this row.')
    # print('\tThis can ONLY be specified as the keyword "first" or "last" corrosponding to the first and last row')
    # print('\tRows in the middle of the data set CANNOT be used as labels.  Think about it - That would just be ridiculous.\n')
    # print('\tGroups in the specified row may be numeric (i.e. "1", "2", "3"), or labels (i.e. "old", "young"). Labels are NOT')
    # print('\tCase Sensetive.  There must be at least two members of each group.')
    # print('\tAny Group with one memeber will be discared from the plot.')
    # print('\tWith this option, each row will now produce as many violin plots as there are row lables')
    # print('\tEvery row in the sheet must have a label.')
    # print('\tThis can be used with the -rowlabel option\n')

    print('-legend: 0 or 1. Turns legend on or off.  Default is on.  1 = on, 0 = off\n')
    
    print('-h: Hides the plot from showing in the end\n')
    
    # print('-t <label>: Preform t-test on means of violin plots, using "label" as the group to test against')
    # print('\tIf you are using this option with -r, the label MUST be one of the row lables.')
    # print('\tIf you are using this option with -c, the label MUST be one of the column lables')
    # print('\tIf you are using this option with -r AND -c, the label must be one of the row lables')
    # print('\tIf you are using this option WITHOUT -r or -c, the label must be a column header')
    # print('\tResults will be saved in text files in the output directory specified by <SavePath>\n')
    # 
    # 
    # print('-p annotate graph with significance values (BETA)')
    # print('\t This only kinda works.  Its in beta.  Basically tries to add stars to indicate significance across violin plots')

    print(' [-s <SavePath>]: The output path of the images to be saved, without extensions.  If not path is provided,')
    print('\tThe Image WILL NOT BE SAVED"')

    return()

def StatsOn2(Data1,Data2,pthresh):
    Data1=np.array(Data1)
    Data2=np.array(Data2)

    print np.shape(Data1)
    print np.shape(Data2)
    #t,p=sts.ttest_ind(Data1,Data2)
    t,p=sts.ttest_rel(Data1,Data2)
    #t,p=sts.ttest_ind(Data1,Data2)
    if p<=0.001:
        sig=3
    elif p<=0.01:
        sig=2
    elif p<=0.05:
        sig=1
    else:
        sig=0
            
    return(t,p,sig) 

def makeSigLine(p1,p2,x):
    x.annotate("",xy=p2,xycoords='data',xytext=p1,textcoords='data',arrowprops=dict(arrowstyle="->",connectionstyle="bar",fraction="0.2"))
    return x

def CheckforSingular(DataLists):
    NewDataList=[]
    for data in DataLists:      
        if all([i==data[0] for i in data]) and len(data)!=1:
            if data[0]==0:
                data[0]=0.01
                data[-1]=-0.01
            else:
                data[0]=data[0]*.99
                data[-1]=data[-1]*1.01
        NewDataList.append(data)
    return(NewDataList)


def SeqStatsOnSubplot(group,nref,ref,pos,skip=0):
    print group.get_labels()
    
    #print ref
    
    #nref= np.where([a==ref for a in group.get_labels()])[0]
    # nref=0
    # violinRef=group.violinGroups[np.where([a==ref for a in group.get_labels()])[0]]
    
    labels=group.get_labels()
    ts=[]
    ps=[]
    sigs=np.zeros(len(labels))
    pthresh=0.05
    OutputTemp='{0: <26}\t\t{1: <1.7f}\t{2: <1.6e}\t{3}'
    Out=''
    violinRef=group.violinGroups[nref]
    for nv,violin in enumerate(group.violinGroups):
        if skip <=nv:
            if not violin.label==ref:
                print violin.label
                t,p,sig=StatsOn2(violinRef.data,violin.data,pthresh)
                ts.append(t)
                ps.append(p)
                sigs[nv]=sig
                
                meth=labels[nv]
                if sig>=1:
                    sg='<*>'
                    
                    p1=(pos[nref],np.amax(violinRef.data))
                    p2=(pos[nv],np.amax(violinRef.data))
                    #print p1
                    #print p2
                    
                    #x=makeSigLine(p1,p2,x)
                else:
                    sg=''
    
    
                Out=Out+OutputTemp.format(ref+' vs '+meth,t,p,sg)+'\n'

    Out='\n\n'+'=======================================================================================\n'+'{0: ^26}\t\t{1: ^9s}\t{2: ^10s}\t{3: ^3}\n'.format('Comparison','t Value','p Value','Sig')+'---------------------------------------------------------------------------------------\n'+Out
    #print Out
    return (Out,sigs)

def LoadFromExcel(inputs,SaveFile): 
    
    global runTtest
    global useRowLabels
    global useColLabels
    global annotateSig
    global tTestRef
    global skipFirstCol 

    if not (useRowLabels or useColLabels):
        
        MainFig=LoadBasic(inputs,skipFirstCol)
        
    elif (useRowLabels and not useColLabels):
        
        MainFig=LoadWithR(inputs,skipFirstCol)
        
    elif (useColLabels and not useRowLabels):
        
        MainFig=LoadWithC(inputs,skipFirstCol)
        
    elif (useRowLabels and useColLabels):
        
        MainFig=LoadWithRC(inputs,skipFirstCol)
        
    
        
    
    main(MainFig,SaveFile)
    
    return()

def LoadBasic(inputs,skip):
    print ('LOADBASIC')

    global firstRowLabel

    
    
    MainFig=MainFigure()    
    
    for si,struct in enumerate(inputs):
        
        sp=SubPlot()
        sub=struct.csvfile
        UseCols=struct.usecolumns
        header=struct.header
        print UseCols
        
        sg=SubGroup()
        
        checkHeaders=np.loadtxt(sub,dtype=str,usecols=UseCols,delimiter=',')[0]
        LenFile=len(checkHeaders)
        defaultNames=['{}'.format(i) for i in range(LenFile)]
        
        if header==0:
               
            data=np.genfromtxt(sub,names=defaultNames,usecols=UseCols,delimiter=',',case_sensitive='lower')
            lables=list(data.dtype.names)
                
        elif header==1:

            data=np.genfromtxt(sub,names=defaultNames,usecols=UseCols,delimiter=',',case_sensitive='lower',skip_header=1)
            lables=list(data.dtype.names)
            
        elif header==2:
            
            checkHeaders=np.loadtxt(sub,dtype=str,usecols=UseCols,delimiter=',')[0]
            if not len(checkHeaders)==len(np.unique(checkHeaders)):
                print('*****  WARNING!:File {} Has repeated column headers.  Adding suffix "_n" where n is the number of repetitions *****'.format(sub))           
            
            data=np.genfromtxt(sub,names=True,usecols=UseCols,delimiter=',',case_sensitive='lower')
            lables=list(data.dtype.names)
            
        else:
            
            checkHeaders=np.loadtxt(sub,dtype=str,usecols=UseCols,delimiter=',')[0]
            LenFile=len(checkHeaders)
            defaultNames=['{}'.format(i) for i in range(LenFile)]
            
            data=np.genfromtxt(sub,names=defaultNames,usecols=UseCols,delimiter=',',case_sensitive='lower')
            if all([np.isnan(i) for i in data[0]]):
                data=np.genfromtxt(sub,names=True,usecols=UseCols,delimiter=',',case_sensitive='lower')
            lables=list(data.dtype.names)
            
        if np.isnan(data[0][0]):
            print('***** WARNING!: Nans found in first column of data.  If first column is lables, Exclude it from the analysis\n  Attempting to remove... *****')
            data=data[lables[1:]]
            lables=lables[1:]
            
        TitleStr=''
        # if firstRowLabel: 
        # 
        #   for t in lables:
        #       TitleStr=TitleStr+t+' '
        #   sp.set_title(TitleStr)

        DataList=[]
        badLables=[]
        for l in lables:
            tempList=data[l]
            if not all(np.isnan(tempList)):
                tempList=np.delete(tempList,(np.where(np.isnan(tempList))[0]))          
                DataList.append(tempList)
            else:
                badLables.append(l)
        if badLables:
            for bl in badLables:
                del lables[np.where([i==bl for i in lables])[0][0]]
            

        
        OverrideLabels=lables
        DataList=CheckforSingular(DataList)
        
        sg.add_list(DataList,list(lables))
        sp.add_subgroup(sg)
        sp.set_legend(struct.legend)
        
        
        MainFig.add_subplot(sp)
        
    return(MainFig)

def LoadWithR(inputs,skip):
    print ('LOAD WITH R')
    global firstRowLabel
    global OverrideLabels
    

    
    MainFig=MainFigure()    

    for si,struct in enumerate(inputs):
        sp=SubPlot()
        sub=struct.csvfile
        UseCols=struct.usecolumns
        header=struct.header        
        sg=SubGroup()
        LabelCol=struct.groupbycolumn
        if np.isnan(LabelCol):
            print('Invalid selection for grouping column.  Valid options are "first" or "last"')
            return()
        
        if any([i==LabelCol for i in UseCols]):
            print('WARNING! Attempting to include the grouping column in the selected range of columns is punishable by death.\n  Come on, just think about it.')
            return()
        
        # Extract Final Column, which has the row group key     
        checkHeaders=np.loadtxt(sub,dtype=str,usecols=UseCols,delimiter=',')[0]
        LenFile=len(checkHeaders)
        defaultNames=['{}'.format(i) for i in range(LenFile)]
        
        if header==0:
               
            data=np.genfromtxt(sub,names=defaultNames,usecols=UseCols,delimiter=',',case_sensitive='lower')
            lables=list(data.dtype.names)
            RowGroups=np.loadtxt(sub,dtype=str,usecols=[LabelCol],delimiter=',')

                
        elif header==1:

            data=np.genfromtxt(sub,names=defaultNames,usecols=UseCols,delimiter=',',case_sensitive='lower',skip_header=1)
            lables=list(data.dtype.names)
            RowGroups=np.loadtxt(sub,dtype=str,usecols=[LabelCol],delimiter=',',skiprows=1)

            
        elif header==2:
            
            checkHeaders=np.loadtxt(sub,dtype=str,usecols=UseCols,delimiter=',')[0]
            if not len(checkHeaders)==len(np.unique(checkHeaders)):
                print('*****  WARNING!:File {} Has repeated column headers.  Adding suffix "_n" where n is the number of repetitions *****'.format(sub))           
            
            data=np.genfromtxt(sub,names=True,usecols=UseCols,delimiter=',',case_sensitive='lower')
            lables=list(data.dtype.names)
            #print lables
            RowGroups=np.loadtxt(sub,dtype=str,usecols=[LabelCol],delimiter=',',skiprows=1)
            #print RowGroups

            
            
        if UseCols==[]:
            # Remove the label column from the loaded data.
            del lables[LabelCol]
            data=data[lables]

        # Catch if first column is unused lables
        if np.isnan(data[0][0]):
            print('*************************************************************************************************')
            print('***** WARNING!: Nans found in first column of data.  Double Check Specified Columns for use *****')
            print('*************************************************************************************************')
            return()
            
        # Catch if last Column is unused lables
        if np.isnan(data[0][-1]):
            print('*************************************************************************************************')
            print('***** WARNING!: Nans found in Last column of data.  Double Check Specified Columns for use  *****')
            print('*************************************************************************************************')
            return()
            
        DataList=[]
        for l in lables:
            DataList.append(data[l])
        del data

        RowKey=np.unique(RowGroups)
        #print RowKey
        SortedDataList=[]
        FinalLabelList=[]
        
        for data,label in zip(DataList,lables): 
            sg=SubGroup()
            
            SubGroupDataList=[]
            SubGroupLabel=[]
            
            for key in RowKey:
                tempData=data[np.where(RowGroups==key)]
                if not all(np.isnan(tempData)):
                    tempData=np.delete(tempData,(np.where(np.isnan(tempData))[0]))
                    SubGroupDataList.append(tempData)
                    SubGroupLabel.append('{}'.format(label))
                    FinalLabelList.append('{}'.format(key))
            
            SubGroupDataList=CheckforSingular(SubGroupDataList)
            sg.add_list(SubGroupDataList,SubGroupLabel)
            
            OverrideLabels=RowKey
            sp.add_subgroup(sg)
            
        
        TitleStr=''
        #if firstRowLabel:  

            # for t in lables:
            #   TitleStr=TitleStr+t+' '
            
        sp.set_title(TitleStr)
        sp.set_legend(struct.legend)
        
        MainFig.add_subplot(sp)
        
    return(MainFig)

def LoadWithC(inputs,skip):
    print ('LOAD WITH C')

    global firstRowLabel
    global OverrideLabels

    MainFig=MainFigure()    


    for si,struct in enumerate(inputs):
        sp=SubPlot()
        sub=struct.csvfile
        UseCols=struct.usecolumns
        header=struct.header        
        sg=SubGroup()
        LabelCol=struct.groupbycolumn
        LabelRow=struct.groupbyrow
        
        if np.isnan(LabelRow):
            print('Invalid selection for grouping row.  Valid options are "first" or "last"')
            return()
        
        # Retrieve headers/first row for futire use
        checkHeaders=np.loadtxt(sub,dtype=str,usecols=UseCols,delimiter=',')[0]
        LenFile=len(checkHeaders)
        defaultNames=['{}'.format(i) for i in range(LenFile)]
        
        # if the column labels aren't in the first row (they must be the last)
        if LabelRow!=0:
            

            if header==0:
                   
                data=np.genfromtxt(sub,names=defaultNames,usecols=UseCols,delimiter=',',case_sensitive='lower',skip_footer=1)
                lables=list(data.dtype.names)
    
                    
            elif header==1:
    
                data=np.genfromtxt(sub,names=defaultNames,usecols=UseCols,delimiter=',',case_sensitive='lower',skip_header=1,skip_footer=1)
                lables=list(data.dtype.names)
    
                
            elif header==2:
                
                if not len(checkHeaders)==len(np.unique(checkHeaders)):
                    print('*****  WARNING!:File {} Has repeated column headers.  Adding suffix "_n" where n is the number of repetitions *****'.format(sub))           
                
                data=np.genfromtxt(sub,names=True,delimiter=',',usecols=UseCols,case_sensitive='lower',skip_footer=1)
                lables=list(data.dtype.names)
                LenFile=len(data)+1
        
            # If not make up labels for it and include first row in data
            else:
                
                data=np.genfromtxt(sub,names=defaultNames,delimiter=',',usecols=UseCols,case_sensitive='lower',skip_footer=1)

                if all([np.isnan(i) for i in data[0]]):
                    data=np.genfromtxt(sub,names=True,usecols=UseCols,delimiter=',',case_sensitive='lower',skip_footer=1)
                    
                lables=list(data.dtype.names)
                LenFile=len(data)
                
            lables=list(data.dtype.names)
            
        # Else if the label columns ARE the first row   
        else:
            LenFile=len(checkHeaders)
            defaultNames=['{}'.format(i) for i in range(LenFile)]
            #Do not skip footer this time
            data=np.genfromtxt(sub,names=defaultNames,delimiter=',',usecols=UseCols,case_sensitive='lower',skip_header=1)
            lables=list(data.dtype.names)
            LenFile=len(data)
            
            
            
        # Extract Column groups from last row               
        ColGroups=np.loadtxt(sub,dtype=str,usecols=UseCols,delimiter=',')[LabelRow]
        

        
        # Catch if first column is unused lables
        if np.isnan(data[0][0]):
            print('*************************************************************************************************')
            print('***** WARNING!: Nans found in first column of data.  Double Check Specified Columns for use *****')
            print('*************************************************************************************************')

            return()
            
        # Catch if last Column is unused lables
        if np.isnan(data[0][-1]):
            print('*************************************************************************************************')
            print('***** WARNING!: Nans found in Last column of data.  Double Check Specified Columns for use  *****')
            print('*************************************************************************************************')
            return()
        
        
        # Initialize new Data List/Lables
        SortedDataList=[]
        SortedLabelList=[]
        
        # Find Unique Column Groups
        ColKey=np.unique(ColGroups)
        
        # Loop through unique keys and concatenate all Data from them
        for key in ColKey:
            
            # Find All Columns with the same key
            Inds=np.where(ColGroups==key)[0]
            
            ## A this point, each index corrosponds to a column.  So Inds[0]=2 means that the 3rd column has the column group label "key"
            ## Label[Inds[0]] gives the label name for that data.  Therefor, the data can be extracted by calling data[label[Inds[0]]]
            ## Because ind=Inds[0], it's simply data[label[ind]]           
            
            # Create dummy array to store values
            tempData=[]
            
            for ind in Inds:                
                tempData.extend(data[lables[ind]])
            
            # Clear any NANS from data
            if not all(np.isnan(tempData)):
                tempData=np.delete(tempData,(np.where(np.isnan(tempData))[0]))
            
                # Append this key's concatenated data to the master list and create a label
                SortedDataList.append(tempData)
                SortedLabelList.append('{}'.format(lables[Inds[0]]))
            
        # Initialize SubGroup and Subplot
        sg=SubGroup()
        sp=SubPlot()
        
        # Add Data to Subgroup and add subgroup to subplot
        sg.add_list(SortedDataList,SortedLabelList)         
        sp.add_subgroup(sg)    

        TitleStr=''
        OverrideLabels=ColKey
        # for t in ColKey:
        #   TitleStr=TitleStr+t+' '
        # 
        sp.set_title(TitleStr)
        sp.set_legend(struct.legend)
        
        MainFig.add_subplot(sp)
        
    return(MainFig)

def LoadWithRC(inputs,skip):
    
    print ('LOAD WITH RC')
    global firstRowLabel
    global UseCols
    global LabelRow
    global LabelCol
    global OverrideLabels
    
    
    MainFig=MainFigure()    
    for si,sub in enumerate(inputs):
        
        
        # Retrieve headers/first row for futire use
        checkHeaders=np.loadtxt(sub,dtype=str,usecols=UseCols,delimiter=',')[0]
        LenFile=len(checkHeaders)
        
        # Remove last row label as it is actually a column label
        RowLabels=np.loadtxt(sub,dtype=str,usecols=[LabelCol],delimiter=',')
        ColGroups=np.loadtxt(sub,dtype=str,usecols=UseCols,delimiter=',')[LabelRow]

        # if the column labels aren't in the first row (they must be the last)          
        if LabelRow!=0:
            
            #Remove the last label of the rowlabel
            RowLabels=RowLabels[:-1]
            
            #Check to see if the first row is labels
            if firstRowLabel:
                if not len(checkHeaders)==len(np.unique(checkHeaders)):
                    print('*****  WARNING!:File {} Has repeated column headers.  Adding suffix "_n" where n is the number of repetitions *****'.format(sub))           
                
                data=np.genfromtxt(sub,names=True,delimiter=',',usecols=UseCols,case_sensitive='lower',skip_footer=1)
                lables=data.dtype.names
                LenFile=len(data)+1
                
                # Remove the first label of the rowlabel
                RowLabels=RowLabels[1:] 
                
            # If not make up labels for it and include first row in data
            else:
                LenFile=len(checkHeaders)
                defaultNames=['{}'.format(i) for i in range(LenFile)]           
                data=np.genfromtxt(sub,names=defaultNames,delimiter=',',usecols=UseCols,case_sensitive='lower',skip_footer=1)
            
                if all([np.isnan(i) for i in data[0]]):
                    data=np.genfromtxt(sub,names=True,usecols=UseCols,delimiter=',',case_sensitive='lower')
                    RowLabels=RowLabels[1:]

                lables=data.dtype.names
                LenFile=len(data)
                
        # Else if the label columns ARE the first row   
        else:
            RowLabels=RowLabels[1:]
            LenFile=len(checkHeaders)
            defaultNames=['{}'.format(i) for i in range(LenFile)]
                
            #Do not skip footer this time
            data=np.genfromtxt(sub,names=defaultNames,delimiter=',',usecols=UseCols,case_sensitive='lower',skip_header=1)
            lables=list(data.dtype.names)
            LenFile=len(data)
            
            
                    
        
        # Extract Column groups from last row               
        if all([np.isnan(i) for i in data[lables[0]]]):
            lables=lables[1:]
            data=data[lables]
            ColGroups=ColGroups[1:]
        #data.dtype.names=data.dtype.names[:-1]+rkey
        lables=list(data.dtype.names)       
        
        #RowLabels=data[lables[-1]]
        if UseCols==[]:
            ColGroups=ColGroups[:-1]        
            # Remove Row Labels in last Column    
            lables=lables[:-1]
            data=data[lables]
        
        # Catch if first column is unused lables
        if np.isnan(data[0][0]):
            print('*************************************************************************************************')
            print('***** WARNING!: Nans found in first column of data.  Double Check Specified Columns for use *****')
            print('*************************************************************************************************')
            return()
            
        # Catch if last Column is unused lables
        if np.isnan(data[0][-1]):
            print('*************************************************************************************************')
            print('***** WARNING!: Nans found in Last column of data.  Double Check Specified Columns for use  *****')
            print('*************************************************************************************************')
            return()

        # Initialize new Data List/Lables
        SortedDataList=[]
        SortedLabelList=[]
        UnsortedRowKey=[]
        # Find Unique Column Groups
        ColKey=np.unique(ColGroups)
        
        # Loop through unique keys and concatenate all Data from them
        sp=SubPlot()
        lables=data.dtype.names
        for key in ColKey:
            
            # Find All Columns with the same key
            Inds=np.where(ColGroups==key)[0]

            
            ## A this point, each index corrosponds to a column.  So Inds[0]=2 means that the 3rd column has the column group label "key"
            ## Label[Inds[0]] gives the label name for that data.  Therefor, the data can be extracted by calling data[label[Inds[0]]]
            ## Because ind=Inds[0], it's simply data[label[ind]]           
            
            # Create dummy array to store values
            tempData=[]
            tempRowKey=[]
            
            # Basically just add a row column for every chunk of data added (as it will be in order)
            for ind in Inds:
    
                tempData.extend(data[lables[ind]])
                tempRowKey.extend(RowLabels)

            # Clear any NANS from data
            if not all(np.isnan(tempData)):

                tempRowKey=np.delete(tempRowKey,(np.where(np.isnan(tempData))[0]))
                tempData=np.delete(tempData,(np.where(np.isnan(tempData))[0]))
                
                # Append this key's concatenated data to the master list and create a label
                SortedDataList.append(tempData)
                UnsortedRowKey.append(tempRowKey)
                SortedLabelList.append('{}'.format(key))

        RowKey=np.unique(RowLabels)
        FinalDataList=[]
        
        for dta,label,rowkey in zip(SortedDataList,SortedLabelList,UnsortedRowKey): 
            sg=SubGroup()
            
            SubGroupDataList=[]
            SubGroupLabel=[]
            FinalLegendList=[]

            for key in RowKey:            
                tempData=dta[np.where(rowkey==key)]
                tempData=np.delete(tempData,(np.where(np.isnan(tempData))[0]))
                
                SubGroupDataList.append(tempData)
                SubGroupLabel.append('{}'.format(label))
                
                #Attach Row Label as legend
                FinalLegendList.extend(['{}'.format(key)])
                
            SubGroupDataList=CheckforSingular(SubGroupDataList)
            sg.add_list(SubGroupDataList,SubGroupLabel)
            
            
            sp.add_subgroup(sg)

        OverrideLabels=RowKey
    
        TitleStr=''
        # if firstRowLabel: 
        # 
        #   for t in lables:
        #       TitleStr=TitleStr+t+' '
        #   
        sp.set_title(TitleStr)
        sp.set_legend(struct.legend)
        
        MainFig.add_subplot(sp)
               

        
    return(MainFig)

def PrintMeans(Fig):
    OutputLines=''
    for nsub,subPlot in enumerate(Fig.SubPlots):
    
        print('-------- subplot {} --------'.format(nsub))
        OutputLines+='-------- subplot {} --------\n'.format(nsub)
        print('Label\tMean\tStd')
        OutputLines+='Label\tMean\tStd\n'
        for ng,group in enumerate(subPlot.SubGroups):
            labels=group.get_labels()
            data=group.get_data()
        
            for il,ll in enumerate(labels):
                print('{}:\t{}\t{}'.format(ll,np.mean(data[il]),np.std(data[il])))
                OutputLines+='{}:\t{}\t{}\n'.format(ll,np.mean(data[il]),np.std(data[il]))

    
    return(OutputLines)


def main(DataStructure,SaveBase=''):
    global OverrideLabels
    global runTtest
    global useRowLabels
    global useColLabels
    global annotateSig
    global skipFirstCol
    global tTestRef
    #global SaveBase
    #global legend
    global hidePlot
    global title
    
    print annotateSig
    print runTtest
    
    pl.close()
    nSubPlots=DataStructure.nPlots

    # Set Up Main Figure
    nsp=0
    for sp in DataStructure.SubPlots:
        nsp += sp.nGroups+.2
        for nsg in sp.SubGroups:
            nsp += nsg.nViolins
    
        
    
    fsize=nsp*7./(8.)+1
    if fsize*500.0 > 32768.0:
        fsize=32768.0/500.0
    print fsize

    #fig,axarr=pl.subplots(3,int(np.ceil(nSubPlots/3.)),sharex=True)
    

    #Declare Subplot Axes
    ax=[]            
    xl=0
    xm=1 
    ymax=-999999999
    ymin=9999999999
    fig,axarr=pl.subplots(1,int(np.ceil(nSubPlots)),figsize=(fsize,6))
    axarr=np.reshape(axarr,-1)
    #fig.set_size_inches(fsize,4)

    
    for x,subPlot in zip(axarr,DataStructure.SubPlots):
        SPlegend=[]
        VPlotlegend=[]
        #x.label_outer()
        xl=0
        xm=1 
        ymax=-999999999
        ymin=9999999999
        #x=fig.add_subplot(3,nSubPlots/3,nsub+1)
        #x.label_outer()
        #fig
        #if not nsub+1==1:
        x.yaxis.set_visible(True)
        
        x.set_title(subPlot.Title,fontsize=7)
        
        ax.append(x)

# Place Data On Subplots
        
        nGroups=subPlot.nGroups
        
        vinc=1./nGroups     
        nit=0

        pos=[]
        TickLables=[]
        TickPos=[]              
        pdmax=[]
        pdmin=[]        
        
        for ng,group in enumerate(subPlot.SubGroups):
            
            
            
            TickLables.extend(group.get_labels())
            
            
            nViolins=group.nViolins
            subinc=vinc/(nViolins+1)
            pad=subinc/2.5          
            



            for m in range(nViolins):               
                pdmin.append(np.amin(group.violinGroups[m].data))
                pdmax.append(np.amax(group.violinGroups[m].data))
    
            yl=np.amin(pdmin)
            yh=np.amax(pdmax)           
                
            if yl<ymin:
                ymin=yl
            if yh>ymax:
                ymax=yh
    
            ViolinPositions=np.linspace(pad*2,vinc-pad*2,nViolins)+nit
            Vspace=1./(nViolins*2)
            ymeans=[]
            
            
            for vi,vplot in enumerate(group.violinGroups):
                

                st.graphics.violinplot([vplot.data],ax=x,labels=[vplot.label],positions=[ViolinPositions[vi]],show_boxplot=False,plot_opts={'cutoff':True,'cutoff_val':2,'violin_fc':vplot.color,'violin_width':(Vspace/nGroups)*1.5})
                x.boxplot([vplot.data],notch=False,sym='cv',whis=2,positions=[ViolinPositions[vi]],widths=Vspace/nGroups)
                
                VPlotlegend.append(vplot.label)
                SPlegend.extend([vplot.color])

                y=np.mean(vplot.data)
                t=ViolinPositions[vi]
                x.plot(t,y,'o',color='red',alpha=0.5,markersize=2.)
                ymeans.append(y)
            
            pos.extend(ViolinPositions)
                
            # Add grey background to separate within-plot Groups
            if np.mod(ng,2):                
                x.add_patch(pl.Rectangle((nit,-200),vinc,600,zorder=0,alpha=0.8,linewidth=0,color='#e0e0e0'))
                
            nit=nit+vinc
            
            #########################################
            ############ STats from HERE ---v ########
            ##########################################

            
            if runTtest==1:
            
                if tTestRef=='':
                    RefList=group.get_labels()
                else:
                    RefList=[tTestRef]
                
                for i in range(len(RefList)):
                    
                    
                    tTestRef=RefList[i]
                    nref=np.where(np.array(group.get_labels())==tTestRef)[0][0]
                    print group.get_labels()
                    print tTestRef
                    
                    Out,sigs=SeqStatsOnSubplot(group,nref,tTestRef,ViolinPositions,i)
                    tt=0
                    adj=.036*(ymax+(ymax-ymin)*.1)
                    nsig=sum((sigs>=1).astype(int))
                    modadj=3-nsig
                    
                    
                    
                    #####################################
                    ## SET nref here!! ##########
                    ##########################
                    
                    
                    
                    for nv,sig in enumerate(sigs[1:]):
                      ref=tTestRef
                      nvadj=nv+1
                      print adj
                      
                      if sig>=1:
                          print group.get_labels()
                          nref=i#=np.where([a==ref for a in group.get_labels()])[0]
                          print nref
                          #nref=0
                          violinReg=group.violinGroups[nref]
                          p1=(ViolinPositions[nref],np.amax(violinReg.data)*.95)
                          p2=(ViolinPositions[nvadj],np.amax(violinReg.data)*.95)
                          #print p1
                          #print p2
                          if p1[0]>p2[0]:
                              modtt=-1
                              p2=p1
                              p1=(ViolinPositions[nvadj],np.amax(violinReg.data)*.95)
                          else:
                              modtt=0
                          if annotateSig==1:
                            x.annotate("",xy=p2,xycoords='data',xytext=p1,textcoords='data',arrowprops=dict(arrowstyle="-",connectionstyle="bar,fraction=-0.17"))
                            
                            if sig==1:
                                sa='*'
                            elif sig==2:
                                sa='*'
                            elif sig==3:
                                sa='**'
                            x.text((p1[0]+p2[0])/2,p1[1]+adj*(tt+modadj)+adj/4+.17,sa,fontsize=12,ha='center')
                          tt=tt+1+modtt
                          #print 'x:{}\ty:{}'.format((p1[0]+p2[0])[0]/2,p1[1]+adj*tt)
                    Out=subPlot.Title+'_Group {}'.format(nsp)+Out
                    txt='{}_{}{}grp{}stats.txt'.format(SaveBase,subPlot.Title,nsp,ng)
                    if i==0:
                        File=open('{}_{}{}grp{}stats.txt'.format(SaveBase,subPlot.Title,nsp,ng),'w')
                    else:
                        File=open('{}_{}{}grp{}stats.txt'.format(SaveBase,subPlot.Title,nsp,ng),'a')
                    File.write(Out)
                    File.close()
  
            #########################################
            ############ to HERE ---^ ########
            ##########################################
            
            
        if not (useRowLabels or useColLabels):
            
            TickPos=pos
            
        elif (useRowLabels and not useColLabels):
            
            nPlots=len(pos)
            nViolin2subGroup=nPlots/nGroups
            TickPos=[]
            newTickLabels=[]
            for i in range(0,nPlots,nViolin2subGroup):
                TickPos.append(np.mean(pos[i:i+nViolin2subGroup]))
                newTickLabels.append(TickLables[i])
                
            TickLables=newTickLabels
            
        elif (useColLabels and not useRowLabels):
            TickPos=pos
    
    #   
        elif (useRowLabels and useColLabels):
            nPlots=len(pos)
            nViolin2subGroup=nPlots/nGroups
            TickPos=[]
            newTickLabels=[]
            for i in range(0,nPlots,nViolin2subGroup):
                TickPos.append(np.mean(pos[i:i+nViolin2subGroup]))
                newTickLabels.append(TickLables[i])
                
            TickLables=newTickLabels

        
        labelFont=int(14)
        TitleFont=int(18)
        pl.setp(x.get_yticklabels(),fontsize=labelFont)
        x.set_xlim([xl,xm])
        ticks=TickPos
            
        x.set_xticks(ticks)
        x.set_xticklabels(TickLables)
        pl.setp(x.xaxis.get_ticklabels(),fontsize=labelFont)
        pl.setp(x.xaxis.get_ticklabels(),rotation=45,ha='right')
    
        x.set_title(subPlot.Title,fontsize=TitleFont)
        x.yaxis.grid(True)
        for tic in x.xaxis.get_major_ticks():
            tic.tick1On = tic.tick2On = False
        #nsub+=nsub
        x.set_ylim([0,ymax+(ymax-ymin)*.1]) 
        ax.append(x)
        legend=sp.legend
        if legend==1:
            x.hold(True)
            
            if OverrideLabels!=[]:
                labels=OverrideLabels
                SPlegend=SPlegend[:len(labels)]
                dummies=[x.plot([],[],'s',ms=5,c=c,label=l,alpha=0.5,)[0] for c,l in zip(SPlegend,labels)]
            
            
            else:
                
                labels=VPlotlegend
                colors=SPlegend
                dummies=[x.plot([],[],'s',ms=5,c=c,label=l,alpha=0.5,)[0] for c,l in zip(colors,labels)]
                    
            x.legend(dummies,labels,markerscale=3,loc=0,numpoints=1)
    
            
        x.set_ylim([yl-np.abs(yh-yl)*.1,yh+(yh-yl)*.1])
        #print '{}\t{}'.format(yl,yh)
        x.yaxis.grid(True)
        
    # for n,a in enumerate(ax):
    #   a.set_ylim([ymin-np.abs(ymax-ymin)*.1,ymax+(ymax-ymin)*.1])
    #   a.yaxis.grid(True)
        
    fig.subplots_adjust(left=0.1,bottom=0.22,right=0.97,top=0.94,wspace=.13,hspace=0.13)
    #fig.set_size_inches((fsize,3.5))    
    
    
    
    pl.title(title)

    if hidePlot==0:
        pl.show()
    if not SaveBase=='':
        pl.savefig('{}_Violin.pdf'.format(SaveBase),dpi=500,pad_inches=0.5)
        pl.savefig('{}_Violin.png'.format(SaveBase),dpi=500,pad_inches=0.5)
    
    pl.close()

    LineOut=PrintMeans(DataStructure)
    #print LineOut
    if not SaveBase=='':
        File=open('{}_Violin_Stats.txt'.format(SaveBase),'w')
        File.write(LineOut)
        File.close()



runTtest=0
useRowLabels=0
useColLabels=0
LabelRow=0
LabelCol=0
annotateSig=0
skipFirstCol=0
tTestRef=''
SaveBase=''
firstRowLabel=0
hidePlot=0
OverrideLabels=[]
legend=1
title=''


        
if __name__=="__main__":
    
    
    idetected=0
    
    #print('Usage: ./ViolinPlot [-i] <csvFile1> [-usecolumns <ColumnList1>]  ... -i [<csvFileN>] [-usecolumns <ColumnListN>] [-header <0,1,2>] [-groupbycolumn <column number>] [-legend <1,0>] [-h]  [-s <SavePath>]\n')

    inputvalues=['-i','-groupbycolumn','-groupbyrow','-header','-rowlabel','-collabel','-t','-p','-s','-h','-usecolumns','-legend']
    
    if len(sys.argv)>=2:
        inputs=[]
        newInput=[]

        try:    
            arg=[]
            arg=sys.argv[1:]
            while arg:
                i=str(arg.pop(0))
                i=i.rstrip()
                if i=='-i' :
                    
                    if not newInput==[]:
                        inputs.append(newInput)
                        
                    newInput=InputFile()
                    
                    ValIn=arg[0]
                    while not (any([t==ValIn for t in inputvalues])) and len(arg)>=1 and not ValIn[0]=='-':     
                            ValIn=arg[0]
                            if not ((any([t==ValIn for t in inputvalues]))):
                                newInput.set_csvfile(ValIn)
                                del arg[0]
                    
                    idetected=1
                
                elif i=='-usecolumns':
                    UseCols=[]
                    colstring=arg[0]
                    
                    if not colstring[0]=='-':
                        if isinstance(newInput,InputFile):
                            newInput.set_usecolumns(colstring)
                        else:
                            print('Must define input before "-usecolumns"')
                        del arg[0]
                        

                elif (i=='-rowlabel' or i=='-groupbycolumn'):
                    useRowLabels=1
                    LabelCol=arg[0]
                    del arg[0]
                    if LabelCol=='first':
                        LabelCol=0
                    elif LabelCol=='last':
                        LabelCol=-1
                    else:
                        print('Invalid selection for -groupbycolumn')
                        useRowLabels=0
                        LabelCol=np.nan
                        
                    if isinstance(newInput,InputFile):
                            newInput.set_groupbycolumn(LabelCol)
                    else:
                        print('Must define input before "-groupbycolumn"')



                elif (i=='-collabel' or i=='-groupbyrow'):
                    useColLabels=1
                    LabelRow=arg[0]
                    del arg[0]
                    if LabelRow=='first':
                        LabelRow=0
                    elif LabelRow=='last':
                        LabelRow=-1
                    else:
                        print('Invalid selection for -groupbycolumn')
                        useRowLabels=0
                        LabelRow=np.nan
                    if isinstance(newInput,InputFile):
                            newInput.set_groupbyrow(LabelRow)
                    else:
                        print('Must define input before "-groupbyrow"')                     
                    print LabelRow
                    
                    
                elif i=='-header':
                    firstRowLabel=int(arg[0])

                    if firstRowLabel==0 or firstRowLabel==1 or firstRowLabel==2:

                        del arg[0]

                    else:
                        print('Invalid Selection for -header')
                        firstRowLabel=0
                    
                    if isinstance(newInput,InputFile):
                        newInput.set_header(firstRowLabel)
                    else:
                        print('Must define input before "-header"')
                    
                    
                    
                elif i=='-t':
                    runTtest=1
                    if len(arg)>0:
                        
                        if (any([t==arg[0] for t in inputvalues])):
                            tTestRef=''
                        else:
                            tTestRef=arg[0]
                            del arg[0]

                elif i=='-p':
                    annotateSig=1
                    
                    
                elif i=='-s':
                    SaveBase=arg[0]
                    del arg[0]
                    
                elif i=='-h':
                    hidePlot=1
                    
                elif i=='-legend':
                    legend=int(arg[0])
                    if not (legend == 1 or legend == 0):
                        print('Unrecognized value for "-legend"')
                        legend=True
                    else:
                        del arg[0]
                        
                    if isinstance(newInput,InputFile):
                        newInput.set_legend(bool(legend))
                    else:
                        print('Must define input before "-legend"')
                        
                elif i=='-title':
                    title=arg[0]
                    del arg[0]

                else:
                    print 'Unrecognized Argument "{}"'.format(i)
                    print i=='-groupbycolumn'
                    #PrintInstructions()         
                
                
            inputs.append(newInput)
                
                
            if idetected ==1:
                
                NewInputs=[]
                for inp in inputs:
                    colstring=inp.usecolumns
                    
                    if not colstring==[]:
                        UseCols=[]
                        colstring=colstring.split('/')
                        print len(colstring)
                        if len(colstring)>1:
                            
                            for spstring in colstring:
                                UseCols=[]
                                copyInput=inp.copy_self()       
                                spcolstring=spstring.split(',')                     
                                for chunk in spcolstring:
                                    if chunk.find(':')==1:
                                        start,end=chunk.split(':')  
                                        UseCols.extend(eval('range({},{})'.format(int(start)-1,end)))
                                    else:
                                        UseCols.append(int(chunk))
                                print UseCols
                                copyInput.set_usecolumns(UseCols)
                                print copyInput.usecolumns
                                NewInputs.append(copyInput)
                                
                                
                        else:
                            colstring=colstring[0]
                            colstring=colstring.split(',')
                            
                            for chunk in colstring:
                                if chunk.find(':')==1:
                                    start,end=chunk.split(':')  
                                    UseCols.extend(eval('range({},{})'.format(int(start)-1,end)))
                                else:
                                    UseCols.append(int(chunk))                  
                            inp.set_usecolumns(UseCols)
                            NewInputs.append(inp)
                    else:
                        NewInputs.append(inp)
                
                
                print len(NewInputs)
                LoadFromExcel(NewInputs,SaveBase)
            else:
                print("No Inputs Detected.  List of input Files Must be prefaced with '-i'")
        except:
            #PrintInstructions()
            print traceback.print_exc(file=sys.stdout)
    else:
        PrintInstructions()

