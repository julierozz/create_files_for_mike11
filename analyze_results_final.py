from pandas import read_csv, DataFrame,concat,notnull,isnull,Series
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
import numpy as np
from scipy.stats import gaussian_kde
from scipy.optimize import fsolve
from scipy.interpolate import InterpolatedUnivariateSpline

# Selects only 2 cross sections
varin1='PARLIAMENT'
varin2='SEBASTIAN'

def load_data(varin1,varin2):
	data=read_csv("output_and_def_oct28.csv")
	data.index=data['scenario_number']
	flooded=read_csv("people_flooded.csv")
	flooded.index=flooded['scenario_number']
	flooded=flooded.drop('scenario_number',axis=1)

	data.rename(columns={'PARLIAMENT BRIDGE 3(150.0000)':'PARLIAMENT', 'KOTTE ELA NORTH(0.0000)':'KOTTE', 
						 'KIRILLAPONE2(771.0500)':'KIRILLAPONE2', 'PARLIAMENT_UPPER_REACH(1803.5500)':'PARLIAMENT_UPPER_REACH', 
			 'TALANGAMA(3416.0000)':'TALANGAMA', 'KIRILLAPONE2(1388.0300)':'KIRILLAPONE22', 'TORRINGTON CNL(81.6800)':'TORRINGTON', 
			 'TORRINGTON_B01(33.0600)':'TORRINGTON_B01', 'MAHAWATTA TO HEEN ELA(349.6500)':'MAHAWATTA', 
			 'MAHAWATTA ELA(49.9900)':'MAHAWATTA2', 'WELLAWATTA CNL(0.0000)':'WELLAWATTA', 'DEMATAGODA ELA(0.0000)':'DEMATAGODA', 
			 'DEMATAGODA ELA 2(3414.8899)':'DEMATAGODA2', 'ST. SEBASTIAN NORTH CANAL(1400.8700)':'SEBASTIAN2',
			 'ST. SEBASTIAN SOUTH CANAL(-75.0000)':'SEBASTIAN3', 'MAIN DRAIN(1094.8000)':'MAIN',
			 'DEHIWARA CNL(1003.8000)':'DEHIWARA', 'KIRILLAPONE3(2156.1499)':'KIRILLAPONE3',
			 'KIRILLAPONE2(934.0800)':'KIRILLAPONE23', 'TORRINGTON_B01(33.0600).1':'TORRINGTON_B012',
			 'SERPENTINE(40.0000)':'SERPENTINE', 'ST.SEBASTIAN_SOUTH_DIVERSION(200.0000)':'SEBASTIAN_SOUTH_DIVERSION', 
			 'ST. SEBASTIAN SOUTH CANAL(1025.1801)':'SEBASTIAN', 'MAIN DRAIN(1177.1600)':'MAIN2'}, inplace=True)

	subdata=data[[varin1, varin2, 'return_period','wetland_loss','climate_change','runoff','bndconditions','scenario_number']]
	subdata=concat([subdata,flooded],axis=1)
	subdata.rename(columns={'Estimated Population Exposed using GN method': 'Pop','share of Total Population using A2': 'share'}, inplace=True)
	return subdata

def prepare_data(subdata,gdp_gr,gdp_per_capita_2013,pop_multiplier,pop_affected,endyear):

	def calccost(pop_exposed,gdp_gr,gdp_per_capita_2013,pop_multiplier,endyear):
		cost=pop_exposed*gdp_per_capita_2013*(1+gdp_gr)**(endyear-2013)*pop_multiplier
		return cost

	subdata.ix[notnull(subdata['share']),'cost']=calccost(pop_affected,gdp_gr,gdp_per_capita_2013,pop_multiplier,endyear)
	subdata.ix[notnull(subdata['share']),'costlog']=np.log(subdata.ix[notnull(subdata['share']),'cost'])

	### predicts missing water level data points

	formula=varin1+" ~ return_period + wetland_loss + climate_change + runoff  + bndconditions"
	olsmodel=sm.ols(formula,data=subdata).fit()
	predictions=olsmodel.predict(subdata)
	subdata.loc[subdata[varin1].isnull().values,varin1]=predictions[subdata[varin1].isnull().values]

	formula=varin2+" ~ return_period + wetland_loss + climate_change + runoff  + bndconditions"
	olsmodel2=sm.ols(formula,data=subdata).fit()
	res2=olsmodel2.params
	predictions2=olsmodel2.predict(subdata)
	subdata.loc[subdata[varin2].isnull().values,varin2]=predictions2[subdata[varin2].isnull().values]

	### predicts damages based on a few points using water level
	subdata['log{}'.format(varin1)]=np.log(subdata[varin1])
	subdata['log{}'.format(varin2)]=np.log(subdata[varin2])

	formula="costlog ~ log{}".format(varin1)
	damagemodel=sm.ols(formula,data=subdata).fit()
	predicted_damages=damagemodel.predict(subdata)
	subdata.loc[subdata['costlog'].isnull().values,'costlog']=predicted_damages[subdata['costlog'].isnull().values]
	subdata['costestimated']=np.exp(subdata['costlog'])
	return subdata
	
def calc_option_value(subdata,R):

	def risk_averse_losses(x,wetland_loss,R):
		def calc_int(c,wetland_loss):
			subcost=cost.ix[cost['wetland_loss']==wetland_loss,:].copy()
			s = InterpolatedUnivariateSpline(subcost['return_period'], subcost['costestimated'], k=1)
			zerocost=DataFrame({'return_period':[100,10000],'costestimated':[s(100),s(100)]})
			subcost=concat([zerocost,subcost])
			subcost.sort(columns='return_period', inplace=True)
			subcost['frequency']=1/subcost['return_period']
			subcost['costestimated']=subcost['costestimated'].astype(float)
			subcost.index=range(len(subcost))
			subcost['utility']=np.log(R-subcost['costestimated']+c)
			inte=0
			for i in range(1,len(subcost)):
				trapeze =(subcost.loc[i-1,'frequency']-subcost.loc[i,'frequency'])*(subcost.loc[i,'utility']+subcost.loc[i-1,'utility'])/2
				inte += trapeze
			inte += subcost.loc[len(subcost)-1,'utility']*subcost.loc[len(subcost)-1,'frequency']
			return inte
		cost=x.ix[:,['return_period','costestimated','wetland_loss']].copy()    
		func = lambda c : calc_int(c,100)-calc_int(0,wetland_loss)
		c_initial_guess = np.mean(cost['costestimated'])
		result,info,ier,msg = fsolve(func, c_initial_guess,full_output=True)
		if ier!=1:
			return 0
		return result[0]

	charac_col2=['climate_change','runoff','bndconditions']
	charac=subdata.groupby(charac_col2).apply(lambda x:x[charac_col2].head(1))
	bb=DataFrame(charac.values,columns=charac_col2)
	new_data2=DataFrame()
	for wetland_loss in [0,10,50,70]:
		vo=subdata.groupby(charac_col2).apply(lambda x:risk_averse_losses(x,wetland_loss,R))
		scenar=subdata.groupby(charac_col2).apply(lambda x:x.ix[(x['wetland_loss']==wetland_loss)&(x['return_period']==5),'scenario_number'])
		aa=DataFrame({'scenario_number':scenar.values,'option_value':vo.values,'wetland_kept':[100-wetland_loss]*len(scenar.values)})
		new_data2=new_data2.append(concat([bb,aa],axis=1),ignore_index=True)
	new_data2.index=range(len(new_data2))
	return new_data2
	
def calc_annual_losses(subdata,R):
	def annual_losses(x):
		cost=x.ix[:,['return_period','costestimated']].copy()
		s = InterpolatedUnivariateSpline(cost['return_period'], cost['costestimated'], k=1)
		
		zerocost=DataFrame({'return_period':[100,10000],'costestimated':[s(100),s(100)]})
		cost=concat([zerocost,cost])
		cost.sort(columns='return_period', inplace=True)
		cost.index=range(len(cost))
		cost['costestimated']=cost['costestimated'].astype(float)
		cost['frequency']=1/cost['return_period']
		inte=0
		for i in range(1,len(cost)):
			trapeze =(cost.loc[i-1,'frequency']-cost.loc[i,'frequency'])*(cost.loc[i,'costestimated']+cost.loc[i-1,'costestimated'])/2
			inte += trapeze
		inte += cost.loc[len(cost)-1,'costestimated']*cost.loc[len(cost)-1,'frequency']
		return inte

	charac_col=['wetland_loss','climate_change','runoff','bndconditions']
	annloss=subdata.groupby(charac_col).apply(lambda x:annual_losses(x))
	charac=subdata.groupby(charac_col).apply(lambda x:x[charac_col].head(1))
	scenar=subdata.groupby(charac_col).apply(lambda x:x['scenario_number'].head(1))
	new_data=concat([scenar,charac],axis=1)
	new_data.index=range(len(new_data))
	annloss.index=range(len(annloss))
	new_data['annuallosses']=annloss/10**9
	return new_data
	
def create_distrib_per_wetland(subdata):
	def event_damage_distrib(x):
		cost=x.ix[:,['return_period','costestimated']].copy()
		s = InterpolatedUnivariateSpline(cost['return_period'], cost['costestimated'], k=1)
		zerocost=DataFrame({'return_period':[1,100,200,10000],'costestimated':[0,s(100),s(200),s(200)]})
		cost=concat([zerocost,cost])
		cost.sort(columns='return_period', inplace=True)
		cost.index=range(len(cost))
		cost['costestimated']=cost['costestimated'].astype(float)
		f = InterpolatedUnivariateSpline(cost['return_period'], cost['costestimated'], k=1)
		events=np.linspace(0.000001,1,num=500)
		damages = f(1/events)
		return damages
	charac_col=['wetland_loss','climate_change','runoff','bndconditions']
	annloss=subdata.groupby(charac_col).apply(lambda x:event_damage_distrib(x))
	charac=subdata.groupby(charac_col).apply(lambda x:x[charac_col].head(1))
	scenar=subdata.groupby(charac_col).apply(lambda x:x['scenario_number'].head(1))
	new_data=concat([scenar,charac],axis=1)
	new_data.index=range(len(new_data))
	annloss.index=range(len(annloss))
	new_data['annuallosses']=annloss
	losses_wetlands=DataFrame()
	for wetland_loss in new_data['wetland_loss'].unique():
		select=new_data['wetland_loss']==wetland_loss
		out=[]
		for i in new_data[select].index:
			out=np.concatenate([out,new_data.ix[i,'annuallosses']])
		losses_wetlands['{}wetlandloss'.format(wetland_loss)]=out
	return losses_wetlands
	
def vo_all(R,losses_wetlands):
	out=DataFrame(columns=['wetland_loss','option_value','risk_premium'])
	for wetlandloss in [0,10,50,70]:
		funcy = lambda c : np.mean(np.log(R-losses_wetlands['100wetlandloss']+c))-np.mean(np.log(R-losses_wetlands['{}wetlandloss'.format(wetlandloss)]))
		c_initial_guess = np.mean(losses_wetlands['{}wetlandloss'.format(wetlandloss)])
		result,info,ier,msg = fsolve(funcy, c_initial_guess,full_output=True)
		if ier!=1:
			vo=0
		else:
			vo=result[0]
		rp=vo-(np.mean(losses_wetlands['100wetlandloss'])-np.mean(losses_wetlands['{}wetlandloss'.format(wetlandloss)]))
		out.loc[len(out),:]=[wetlandloss,vo,rp]
	return out


endyear=2013

#GDP per capita 2013 in constant lkr
# gdp_per_capita_2013=160*10**3 #national GDP
# gdp_per_capita_2013=424*10**3 #based on Anusha's data
gdp_per_capita_2009=47783*12 #based on census
gdp_per_capita_2013=gdp_per_capita_2009*1.075**4 #based on census
ini_pop=2.3*10**6
pop_gr=0
gdp_gr=0
losses_share=0.05
urban_policy=0
subdata=load_data(varin1,varin2)
pop_multiplier=2.8*losses_share
nb_people_exposed=(1+pop_gr)**(endyear-2013)*ini_pop
R=(1+gdp_gr)**(endyear-2013)*gdp_per_capita_2009*nb_people_exposed
pop_affected=(1+pop_gr)**(endyear-2013)*subdata.ix[notnull(subdata['share']),'Pop']
subdata=prepare_data(subdata,gdp_gr,gdp_per_capita_2009,pop_multiplier,pop_affected,endyear)
subdata.to_csv("subdata2010.csv")

alllosses=DataFrame()
for losses_share in [0.05,0.07,0.1,0.12]:
	subdata=load_data(varin1,varin2)
	pop_multiplier=2.8*losses_share
	nb_people_exposed=(1+pop_gr)**(endyear-2013)*ini_pop
	R=(1+gdp_gr)**(endyear-2013)*gdp_per_capita_2013*nb_people_exposed
	pop_affected=(1+pop_gr)**(endyear-2013)*subdata.ix[notnull(subdata['share']),'Pop']
	subdata=prepare_data(subdata,gdp_gr,gdp_per_capita_2013,pop_multiplier,pop_affected,endyear)
	losses          = calc_annual_losses(subdata,R)
	x1=DataFrame({'Popgr':[pop_gr]*len(losses),'GDPgr':[gdp_gr]*len(losses),'losses_share':[losses_share]*len(losses),'urban_policy':[urban_policy]*len(losses)})
	alllosses=alllosses.append(concat([x1,losses],axis=1),ignore_index=True)
alllosses.to_csv("all_economic_losses_2013.csv".format(endyear),index=False)

endyear=2030
	
alllosses=DataFrame()
alloptionvalues=DataFrame()
alllosses_wetlands=DataFrame()
allvo_and_rp=DataFrame()

uncert_var = DataFrame(columns=["var","min","max"])
uncert_var.loc[len(uncert_var),:]=["pop_gr",0,0.03]
uncert_var.loc[len(uncert_var),:]=["gdp_gr",0,0.07]
uncert_var.loc[len(uncert_var),:]=["losses_share",0.05,0.3]
uncert_var.loc[len(uncert_var),:]=["resilience",0.4,0.8]
from pyDOE import *
lhsample= lhs(4,samples=500,criterion="corr")
scenarios=lhsample*np.diff(uncert_var[['min','max']].values).T+uncert_var['min'].values
scenarios=DataFrame(scenarios,columns=uncert_var['var'])

for scenar in range(len(scenarios)):
	for urban_policy in [0,1]:

		subdata=load_data(varin1,varin2)
		
		pop_multiplier=2.8*scenarios.loc[scenar,"losses_share"]
		nb_people_exposed=(1+scenarios.loc[scenar,"pop_gr"])**(endyear-2013)*ini_pop
		R=(1+scenarios.loc[scenar,"gdp_gr"])**(endyear-2013)*gdp_per_capita_2013*nb_people_exposed
		if urban_policy==0:
			pop_affected=(1+scenarios.loc[scenar,"pop_gr"])**(endyear-2013)*subdata.ix[notnull(subdata['share']),'Pop']
		elif urban_policy==1:
			pop_affected=subdata.ix[notnull(subdata['share']),'Pop']

		subdata=prepare_data(subdata,scenarios.loc[scenar,"gdp_gr"],gdp_per_capita_2013,pop_multiplier,pop_affected,endyear)

		losses          = calc_annual_losses(subdata,R)/scenarios.loc[scenar,"resilience"]
		losses_wetlands = create_distrib_per_wetland(subdata)
		vo_and_rp       = vo_all(R,losses_wetlands)
		x1=DataFrame({'Popgr':[scenarios.loc[scenar,"pop_gr"]]*len(losses),'GDPgr':[scenarios.loc[scenar,"gdp_gr"]]*len(losses),'losses_share':[scenarios.loc[scenar,"losses_share"]]*len(losses),'urban_policy':[urban_policy]*len(losses)})
		alllosses=alllosses.append(concat([x1,losses],axis=1),ignore_index=True)
		alllosses_wetlands=alllosses_wetlands.append(losses_wetlands,ignore_index=True)
		allvo_and_rp=allvo_and_rp.append(vo_and_rp,ignore_index=True)
				
alllosses.to_csv("all_economic_losses_{}.csv".format(endyear),index=False)
# alllosses_wetlands.to_csv("all_losses_wetlands.csv",index=False)
# allvo_and_rp.to_csv("all_vo_and_rp.csv",index=False)

if False:
				
	for pop_gr in [0, 0.01, 0.02]:
		for gdp_gr in [0, 0.01, 0.02, 0.03]:
			for urban_policy in [0,1]:

				subdata=load_data(varin1,varin2)
				
				nb_people_exposed=(1+pop_gr)**(endyear-2013)*ini_pop
				R=(1+gdp_gr)**(endyear-2013)*gdp_per_capita_2013*nb_people_exposed
				if urban_policy==0:
					pop_affected=(1+pop_gr)**(endyear-2013)*subdata.ix[notnull(subdata['share']),'Pop']
					losses_share=0.4
				elif urban_policy==1:
					pop_affected=subdata.ix[notnull(subdata['share']),'Pop']
					losses_share=0.2
				pop_multiplier=2.8*losses_share

				subdata=prepare_data(subdata,gdp_gr,gdp_per_capita_2013,pop_multiplier,pop_affected)

				option_values=calc_option_value(subdata,R)

				x2=DataFrame({'Popgr':[pop_gr]*len(option_values),'GDPgr':[gdp_gr]*len(option_values),'losses_share':[losses_share]*len(option_values)})
				alloptionvalues=alloptionvalues.append(concat([x2,option_values],axis=1),ignore_index=True)

	alloptionvalues.to_csv("all_option_values.csv",index=False)
