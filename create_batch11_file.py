from pandas import read_csv
import os

localmodel=os.getcwd()
model="G:\\wetland_simulations"


scenarios=read_csv(localmodel+"\\scenario_matrix.csv")
numsim=len(scenarios)

sim11files_folder=model+'\\sim11files\\'
rr11files_folder=model+'\\rr11files\\'
bnd11files_folder=model+'\\bnd11files\\'
xns11files_folder=model+'\\xns11files\\'
dfs0files_folder=model+'\\dfs0files\\'
otherfiles_folder=model+'\\otherfiles\\'
res11files_folder=model+'\\res11files\\'

intro="""// Created     : 2014-06-30 15:58:49
// DLL id      : C:\\Program Files (x86)\\DHI\\2011\\Bin\\pfs2004.dll
// PFS version : Dec 16 2013 19:42:22

[MIKE_BS1]
   [Global_Variables]
      [Global_Values]
         BaseFileName = '{}Scenario_001.sim11'
         NbOfSimulations = {}
         NbOfParameters = 10
         ColName = 'Cross section'
         ColWidth = 300
         HorizontalAlignment = 0
         Format = 0
         Control = 0
         DefaultValue = ''
         ChoiceList = ''
         UserPtr = 'NULL'
         ColName = ' '
         ColWidth = 20
         HorizontalAlignment = 0
         Format = 0
         Control = 52514
         DefaultValue = ''
         ChoiceList = '...'
         UserPtr = 'Cross section (*.XNS11)|*.XNS11|All files (*.*)|*.*||'
         ColName = 'Boundary'
         ColWidth = 300
         HorizontalAlignment = 0
         Format = 0
         Control = 0
         DefaultValue = ''
         ChoiceList = ''
         UserPtr = 'NULL'
         ColName = ' '
         ColWidth = 20
         HorizontalAlignment = 0
         Format = 0
         Control = 52514
         DefaultValue = ''
         ChoiceList = '...'
         UserPtr = 'Boundary (*.BND11)|*.BND11|All files (*.*)|*.*||'
         ColName = 'RR parameters'
         ColWidth = 300
         HorizontalAlignment = 0
         Format = 0
         Control = 0
         DefaultValue = ''
         ChoiceList = ''
         UserPtr = 'NULL'
         ColName = ' '
         ColWidth = 20
         HorizontalAlignment = 0
         Format = 0
         Control = 52514
         DefaultValue = ''
         ChoiceList = '...'
         UserPtr = 'RR parameters (*.RR11)|*.RR11|All files (*.*)|*.*||'
         ColName = 'HD result file'
         ColWidth = 300
         HorizontalAlignment = 0
         Format = 0
         Control = 0
         DefaultValue = ''
         ChoiceList = ''
         UserPtr = 'NULL'
         ColName = ' '
         ColWidth = 20
         HorizontalAlignment = 0
         Format = 0
         Control = 52514
         DefaultValue = ''
         ChoiceList = '...'
         UserPtr = 'HD result file (*.RES11)|*.RES11|All files (*.*)|*.*||'
         ColName = 'RR result file'
         ColWidth = 300
         HorizontalAlignment = 0
         Format = 0
         Control = 0
         DefaultValue = ''
         ChoiceList = ''
         UserPtr = 'NULL'
         ColName = ' '
         ColWidth = 20
         HorizontalAlignment = 0
         Format = 0
         Control = 52514
         DefaultValue = ''
         ChoiceList = '...'
         UserPtr = 'RR result file (*.RES11)|*.RES11|All files (*.*)|*.*||'
"""
scenar_description="""         Value = '{}'
         Value = ''
         Value = '{}'
         Value = ''
         Value = '{}'
         Value = ''
         Value = '{}'
         Value = ''
         Value = '{}'
         Value = ''
"""


outputtext=intro.format(sim11files_folder,str(numsim))
         
for i in scenarios.index:
    scenar_number=scenarios.ix[i,'scenario_number']
    if scenar_number<10:
        scenar_string="00"+str(scenar_number)
    elif scenar_number<100:
        scenar_string="0"+str(scenar_number)
    else:
        scenar_string=str(scenar_number)
    filename="Scenario_"+scenar_string
    if scenarios.ix[i,'wetland_loss']==0:
        xs_input="Updated_XSec_12.08.2013.xns11"
    else:
        wlpcloss=scenarios.ix[i,'wetland_loss']
        xs_input="{}%_wetland_loss.xns11".format(str(wlpcloss))
    if scenarios.ix[i,'climate_change']==0:
        cc="current"
    elif scenarios.ix[i,'climate_change']==1:
        cc="moderate"
    elif scenarios.ix[i,'climate_change']==2:
        cc="high"
    if scenarios.ix[i,'bndconditions']==0:
        bc="Low"
        sat="low"
    elif scenarios.ix[i,'bndconditions']==1:
        bc="High"
        sat="high"
    bnd_input="{}_Kelani-{}.bnd11".format(bc,cc)
    rp=scenarios.ix[i,'return_period']
    if scenarios.ix[i,'runoff']==0.4:
        ro="Calibrated"
    elif scenarios.ix[i,'runoff']==0.6:
        ro="Projected(2040)"
    elif scenarios.ix[i,'runoff']==0.5:
        ro="Green"
    rr_input="NAM-{}-{}YR-{}-{}Saturation.RR11".format(ro,str(rp),cc,sat)
    hd_res="Scenario{}.res11".format(scenar_string)
    rr_res="Scenario{}RR.res11".format(scenar_string)
    outputtext+=scenar_description.format(xns11files_folder+xs_input,bnd11files_folder+bnd_input,rr11files_folder+rr_input,res11files_folder+hd_res,res11files_folder+rr_res)
    
fin="""      EndSect  // Global_Values

   EndSect  // Global_Variables

EndSect  // MIKE_BS1
"""

outputtext+=fin

file=open("batchallsim.bs11","w")
file.write(outputtext)
file.close()

    