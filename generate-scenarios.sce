// new scenarios
// cc=0 no climate change
// cc=1 moderate climate change
// cc=2 high climate change
// runoff=0 current
// runoff=1 projected 2040
// runoff=2 green development
// bndconditions=0 best conditions
// bndconditions=1 worst conditions

getd()

scenario_matrix=[];
number=1;
for returnp=[2 5 10 25 50]
	for loss=[0 10 50 70 100]
		for cc=[0 1 2]
			for runoff=[0.4 0.6 0.5]
                for bndconditions=[0 1]
                    scenario_matrix=[scenario_matrix;[number,returnp,loss,cc,runoff,bndconditions]];
                    number=number+1;
                end
			end
		end
	end
end
scenario_matrix=[['scenario_number' 'return_period' 'wetland_loss' 'climate_change' 'runoff' 'bndconditions'];scenario_matrix];

csvWrite(scenario_matrix,"scenario_matrix.csv")
