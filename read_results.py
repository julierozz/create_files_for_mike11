from pandas import read_table,DataFrame,read_csv,concat
from numpy import round
import os.path
import math

def get_scenario_results(scenar_number):
    if scenar_number<10:
        scenar_string="00"+str(scenar_number)
    elif scenar_number<100:
        scenar_string="0"+str(scenar_number)
    else:
        scenar_string=str(scenar_number)
    fname="outputfiles-prasanga\scenario{}_all.txt".format(scenar_string)
    if os.path.isfile(fname):
        scenar=read_table(fname,low_memory=False,header=1)
        # if scenar['Time'].tail(1).values!='2010-11-14T00:00:00':
            # scenar=0
    else:
        scenar=0
    return scenar
    
# xychain=read_table("xychainage.txt",skipinitialspace=True,header=0,sep=4*'\s')
ip=read_table("interesting_places.txt")
cmc=read_table("cmc_locations.txt")

scenar_def=read_csv("scenario_matrix.csv")

listofnames=list()

sc=1
scenar=get_scenario_results(sc)
hop=scenar.columns.tolist()

for i in ip.index:
    theplace=ip['Branch Name'][i].upper()+'('+str(math.trunc(ip['Chainage'][i]))+'.'
    loc=[s for s in hop if theplace in s]
    if loc!=[]: 
        listofnames.append(loc[0])

for i in cmc.index:
    theplace=cmc['Branch Name'][i].upper()+'('+str(math.trunc(cmc['Chainage'][i]))+'.'
    loc=[s for s in hop if theplace in s]
    if loc!=[]: 
        listofnames.append(loc[0])

output=DataFrame(columns=listofnames,index=range(1,451))
scenar_def.index=range(1,451)

def extract_results(sc,listofnames,output,scenar):
	for thecol in listofnames:
		if (scenar[thecol].max()>scenar[thecol][0])&(scenar[thecol].max()>scenar[thecol].tail(1).values):
			output.loc[sc,thecol]=scenar[thecol].max()
	return output
	
output=extract_results(sc,listofnames,output,scenar)
    
for sc in range(2,451):
	scenar=get_scenario_results(sc)
	if type(scenar)!=int:
		output=extract_results(sc,listofnames,output,scenar)
			
output_and_def=concat([output,scenar_def],axis=1)
            
output_and_def.to_csv("output_and_def_oct28.csv")