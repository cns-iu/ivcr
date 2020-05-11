"""
forcasting skill trend tracked by the time series appearance data
required package: 
	- statsmodels
	- sktime (optional) 
reference: 
	- https://machinelearningmastery.com/time-series-forecasting-methods-in-python-cheat-sheet/
	- https://github.com/MaxBenChrist/awesome_time_series_in_python
"""
from random import random
import pandas as pd 
import heapq

from statsmodels.tsa.ar_model import AR
from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.holtwinters import ExponentialSmoothing

'''load data into tuple list [(skill, vector),...]'''
def load_data(input_file):
	data = []
	df = pd.read_csv(input_file).values.tolist() 
	for row in df: 
		if row != None:
			skill = row[0] 
			vector = [float(row[i]) for i in range(5,len(row))]
			vector = [v/sum(vector) for v in vector] #normalized vector
			data.append((skill,vector))  
	return data 

'''forcasting model to predict next time step value'''
def forcasting_model(data):
	trend_l = [] # store predicted value in a tuple list (value, skill)
	for (skill, vector) in data:
		# fit model
		#AR model 
		# model = AR(vector)
		# model_fit = model.fit()
		# yhat = model_fit.predict(len(vector), len(vector))

		#MA model
		# model = ARMA(vector, order=(0, 1))
		# model_fit = model.fit(disp=False)
		# yhat = model_fit.predict(len(vector), len(vector))

		# #ARMA model
		# model = ARMA(vector, order=(3, 3))
		# model_fit = model.fit(disp=False)
		# yhat = model_fit.predict(len(vector), len(vector))

		#Simple Smoothing
		model = SimpleExpSmoothing(vector)
		model_fit = model.fit() 
		yhat = model_fit.predict(len(vector), len(vector))

		#Exponential Smoothing
		model = ExponentialSmoothing(vector)
		model_fit = model.fit()
		yhat = model_fit.predict(len(vector), len(vector))

		# #ARIMA model
		# model = ARIMA(vector, order=(10, 0, 1))
		# model_fit = model.fit(disp=False)
		# yhat = model_fit.predict(len(vector), len(vector),typ='levels')

		# print(yhat)
		trend_l.append((yhat,skill))
		# break
	return trend_l

'''get the outliers with largest & smallest predicted value'''
def get_outlier(trend_l, output_file):
	topK = 10 #int(len(trend_l)*0.05)
	bw = open(output_file, 'w')

	largest_skills = heapq.nlargest(topK, trend_l)
	bw.write("Top increasing skills: \n")
	for [value,skill] in largest_skills:
		bw.write(skill + ":" + str(value[0]) + ", ")

	smallest_skills = heapq.nsmallest(topK, trend_l)
	bw.write("\nTop decreasing skills: \n")
	for [value,skill] in smallest_skills:
		bw.write(skill + ":" + str(value[0]) + ", ")

	bw.close()
if __name__ == "__main__": 
	data = load_data("../data/skills-monthly-counts-1600-test.csv")
	# print(len(data),data[:3])
	trend_l = forcasting_model(data)
	get_outlier(trend_l, "../result/trend/Exponential_trend.txt")
	















