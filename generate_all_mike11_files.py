import numpy as np
from create_sim_file import *
from create_rr11_files import *
from pandas import read_csv
import os

scenarios=read_csv("scenario_matrix.csv")
sim11files_folder='sim11files/'
rr11files_folder='rr11files/'

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
    if scenarios.ix[i,'runoff']==0:
        ro="Calibrated"
    elif scenarios.ix[i,'runoff']==1:
        ro="Projected(2040)"
    elif scenarios.ix[i,'runoff']==2:
        ro="Green"
    rr_input="NAM-{}-{}YR-{}-{}Saturation.RR11".format(ro,str(rp),cc,sat)
    intro_txtfile=rr11files_folder+'NAM-intro-catchment-list.txt'
    ro_sat_txtfile=rr11files_folder+'NAM-{}-{}Saturation.txt'.format(ro,sat)
    rp_cc_txtfile=rr11files_folder+'{}Yr_{}.txt'.format(str(rp),cc)
    if not os.path.isfile(rr11files_folder+rr_input):
        create_rr11_files(intro_txtfile,ro_sat_txtfile,rp_cc_txtfile,rr11files_folder+rr_input)
    create_sim_file(sim11files_folder+filename,scenar_string,xs_input,bnd_input,rr_input)








