import numpy as np
from create_sim_file import *

scenar_number=1

if scenar_number<10:
    scenar_string="00"+str(scenar_number)
elif scenar_number<100:
    scenar_string="0"+str(scenar_number)

filename="Scenario_"+scenar_string

xs_input="|.\\Updated_XSec_12.08.2013.xns11|"
bnd="|.\\High_Kelani-Current.bnd11|"
rr="|.\\NAM-Projected(2040)-25YR-CURRENT.RR11|"