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

def prepare_data(subdata):

	subdata.ix[notnull(subdata['share']),'cost']=subdata.ix[notnull(subdata['share']),'Pop']
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
	subdata['popestimated']=np.exp(subdata['costlog'])
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