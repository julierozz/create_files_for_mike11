import os

model="G:\\wetland_simulations"

from pandas import read_csv
import os

localmodel=os.getcwd()
modelsimfolder="G:\\wetland_simulations\\sim11files\\"


scenarios=read_csv(localmodel+"\\scenario_matrix.csv")
numsim=len(scenarios)

outputtext="""set path=%path%;C:\\Program Files (x86)\\DHI\\2011\\bin\n"""

for i in scenarios.index:
    scenar_number=scenarios.ix[i,'scenario_number']
    if scenar_number<10:
        scenar_string="00"+str(scenar_number)
    elif scenar_number<100:
        scenar_string="0"+str(scenar_number)
    else:
        scenar_string=str(scenar_number)
    addline="set dsn=C:\wetland_simulations\sim11files\Scenario_{}.sim11".format(scenar_string)
    outputtext+=addline+"\n"+"start /w MzLaunch.exe %dsn% -x\n"
    
file=open("batchallsimbat.txt","w")
file.write(outputtext)
file.close()