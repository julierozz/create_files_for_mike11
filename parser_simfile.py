from pyparsing import *
from collections import OrderedDict
import json

# Turn the parsed output to JSON

def to_lists(toks):
    if isinstance(toks, ParseResults):
        return [to_lists(t) for t in toks]
    else:
        return toks

def build_dict(toks):
    if isinstance(toks, list):
        if len(toks) == 0:
            return []
        elif len(toks) > 1 and isinstance(toks[0], basestring) and isinstance(toks[1], list):
            return OrderedDict([[toks[0], build_dict(toks[1])]])
        elif isinstance(toks[0], list):
            json = OrderedDict()
            for t in toks:
                json[t[0]] = build_dict(t[1])
            return json
        else:
            return toks
        return []

# Grammar
integer = Combine(Optional('-') + Word(nums)).setParseAction(lambda toks: int(toks[0]))
real =  Combine(Optional('-') + Word(nums) + '.' + Word(nums)).setParseAction(lambda toks: float(toks[0]))
name = Word(alphas, alphanums)
comment = Suppress(Literal('//'))+name
le = Suppress(LineEnd())
string = QuotedString("'")
path = QuotedString("|")
bool = Keyword('true') | Keyword('false')
lst = Group(delimitedList(string | path | bool | real | integer))
definition = Group(name + Suppress(Literal('=')) + lst) + Optional(comment)

sectionName = Suppress(Literal('[')) + name + Suppress(Literal(']'))
sectionEnd = Suppress(Keyword('EndSect')) + Optional(comment)
section = Forward()
section << Group(sectionName + Group(ZeroOrMore(section | definition)) + sectionEnd)

mike11 = ZeroOrMore(comment | section).setParseAction(lambda toks: to_lists(toks))

test = open('Scenario_01.sim11.txt', 'r').read()
#print json.dumps(mike11.parseString(test)[0], indent=2)

# Tests
def tests():
    simpleDefinition = "nwk = |.\\Updated_network_12.08.2013.nwk11|"
    print(definition.parseString(simpleDefinition))

    multipleLineSection = """
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
    print(mike11.parseString(multipleLineSection))

    nestedSections = """
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
         hd = 1, |..\HD\validation_nov_2005.HD11|, false, 2005, 11, 21, 0, 0, 0
         ad = 0, ||, false, 1990, 1, 1, 12, 0, 0
         st = 0, ||, false, 1990, 1, 1, 12, 0, 0
         rr = 0, |..\Colombo_Water_Quality\Sim_and_Results\hotDRY2003_2004RRRRAdd.RES11|, false, 2003, 1, 15, 12, 0, 0
      EndSect  // Initial_Conditions
   EndSect  // Simulation
    """
    print(json.dumps(mike11.parseString(nestedSections)[0]))

    complexSection = r"""
    [BndItem]
    DescType = 0, 1, 'Torrington_B01', 0, 0, '', ''
    OpenDesc = 0, 0
    Dam = 0, 0, 0
    Inflow = true, false, false, false
    ADRR = '', 0, 0
    QhADM12 = 2, 1, 0
    AutoCalQh = 0, 0.001, 40
    BndTS = 0, ||, 0, 0, '', 0, 1
    [FractionArray]
    EndSect  // FractionArray

    [HDArray]
    EndSect  // HDArray

    [InflowArray]
    Inflow = 2, 0, 1, |..\..\..\Colombo_Water_Quality\dfs0\2003Nov_2004Jan.dfs0|, 0.001, 1, 'ZeroDis', 0, 1
    EndSect  // InflowArray

    [QhArray]
    EndSect  // QhArray

    [ComponentArray]
    Component = 1, 0, 1, ||, 0, 0, '', 0, 1
    Component = 2, 0, 0, |..\..\..\Colombo_Water_Quality\dfs0\Polution_concentrations.dfs0|, 0, 3, 'Non_decay_low', 0, 1
    Component = 3, 0, 0, |..\..\..\Colombo_Water_Quality\dfs0\Polution_concentrations.dfs0|, 0, 6, 'decay_low', 0, 1
    Component = 4, 0, 1, ||, 0, 0, '', 0, 1
    EndSect  // ComponentArray

    EndSect  // BndItem
    """
    print(json.dumps(mike11.parseString(complexSection)[0], indent=2))

    withComments = """
    // Created     : 2014-01-30 14:40:40
    // DLL id      : C:\Program Files (x86)\DHI\2011\Bin\pfs2004.dll
    // PFS version : Jan  6 2011 20:45:15
    
    [Results]
      hd = |.\Results\Scenario01.res11|, '', 5, 3
      ad = |..\Colombo_Water_Quality\Sim_and_Results\Dry2003_2004_AD.res11|, '', 1, 2
      st = ||, '', 1, 0
      rr = |.\Results\All_Interventions(NEW)_50YR-Average_RR.res11|, '', 5, 3
   EndSect  // Results
    """
    print(mike11.parseString(withComments))

tests()
