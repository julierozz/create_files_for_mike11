import time
    
def create_sim_file(filename,xs_input,bnd_input,rr_input):
    intro = """// Created     : {} {}
    // DLL id      : C:\\Program Files (x86)\\DHI\\2014\bin\\pfs2004.dll
    // PFS version : Jan  6 2011 20:45:15
    """

    intro_print=intro.format(time.strftime("%x"),time.strftime("%H:%M:%S"))

    definition = """
    [Run11]
       format_version = 107, 'MIKEZero, 2011'
       Comment = ''
       [Models]
          hd = true, false
          ad = false
          st = false
          wq = false, 1, 0
          rr = true
          ff = false
          da = false
          ice = false
          SimMode = 0
          QSS = 0
       EndSect  // Models
    """
       
    input_files = """
        [Input]
          nwk = |.\\Updated_network_12.08.2013.nwk11|
          xs = {}
          bnd = {}
          rr = {}
          hd = |.\\Calibration_Flood_Season_2010_Nov.HD11|
          ad = |..\\Colombo_Water_Quality\\AD11\\4components.AD11|
          wq = ||
          st = ||
          ff = ||
          rhd = ||
          rrr = ||
          da = ||
          ice = ||
       EndSect  // Input
    """
        
    input_files_print=input_files.format(xs_input,bnd_input,rr_input)

    simulation="""
       [Simulation]
          [Simulation_Period]
             start = 2010, 11, 10, 0, 0, 0
             end = 2010, 11, 14, 0, 0, 0
             TimeStepType = 0
             timestep = 20
             timestepunit = 3
             dtFileName = ||
             dtItemName = ''
             dtItemNo = 0
             ddtMin = 1
             ddtMax = 30
             idtMinMaxUnit = 3
             ddtChangeRatio = 1.3
             bDelB_BFlag = true
             dDelB_BVal = 0.01
             dDelB_BLim = 0.01
             bDelQFlag = false
             dDelQVal = 1
             bDelQ_QFlag = true
             dDelQ_QVal = 0.01
             dDelQ_QLim = 0.01
             bDelhFlag = false
             dDelhVal = 0.01
             bDelh_hFlag = true
             dDelh_hVal = 0.01
             dDelh_hLim = 0.01
             bCourantFlagHD = false
             dCourantValHD = 10
             bCourantFlagAD = true
             dCourantValAD = 1
             ST_timestep_multiplier = 1
             RR_timestep_multiplier = 1
          EndSect  // Simulation_Period

          [Initial_Conditions]
             hd = 1, |..\\HD\\validation_nov_2005.HD11|, false, 2005, 11, 21, 0, 0, 0
             ad = 0, ||, false, 1990, 1, 1, 12, 0, 0
             st = 0, ||, false, 1990, 1, 1, 12, 0, 0
             rr = 0, |..\\Colombo_Water_Quality\\Sim_and_Results\\hotDRY2003_2004RRRRAdd.RES11|, false, 2003, 1, 15, 12, 0, 0
          EndSect  // Initial_Conditions

       EndSect  // Simulation
    """

    final="""
       [Results]
          hd = {}, '', 5, 3
          ad = |..\\Colombo_Water_Quality\\Sim_and_Results\\Dry2003_2004_AD.res11|, '', 1, 2
          st = ||, '', 1, 0
          rr = {}, '', 5, 3
       EndSect  // Results

    EndSect  // Run11"""
    
    hd_fin="|.\\Results\\Scenario{}.res11|".format(scenar_string)
    rr_fin="|.\\Results\\Scenario{}RR.res11|".format(scenar_string)

    final_print=final.format(hd_fin,rr_fin)

    file=open(filename+".sim11","w")
    file.write(intro_print+definition+input_files_print+simulation+final_print)
    file.close()

