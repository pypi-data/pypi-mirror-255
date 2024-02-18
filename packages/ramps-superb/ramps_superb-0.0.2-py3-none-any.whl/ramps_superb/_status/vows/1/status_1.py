


'''
	https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
'''

import json

def relative_path (path):
	import pathlib
	from os.path import dirname, join, normpath
	import sys

	this_directory_path = pathlib.Path (__file__).parent.resolve ()	

	return str (normpath (join (this_directory_path, path)))

def read_CSV ():
	csv_path = relative_path ("yahoo-finance--BTC-USD.CSV")

	trend = []

	import csv
	with open (csv_path) as csv_file:
		csv_reader = csv.reader (csv_file, delimiter = ',')
		line_count = 0
		#for row in csv_reader:
		#	print (row)
			
		headers = next (csv_reader)
		headers = [ s.lower () for s in headers ]
		print ("headers:", headers)
		
		for row in csv_reader:
			trend.append (dict (zip (headers, row)))

	'''
		2023-02[Feb]-09
	'''
	for line in trend:
		line ["unadjusted close"] = line ["adj close"]
		line ["close"] = float (line ["adj close"])
		del line ['adj close']
		
		line ["date string"] = line ["date"]
		del line ['date']
		
		line ["open"] = float (line ["open"])
		line ["high"] = float (line ["high"])
		line ["low"] = float (line ["low"])
		

	print (json.dumps (trend, indent = 4))
	
	return trend;

import pandas
import ramps_superb
import ramps_superb.victory_percentage.holding as superb_VP_holding
import rich	
	
import plotly.graph_objects as go
def plot_1_venture (chart, OHLCV_DF, venture, color = "white"):
	chart.add_trace (
		go.Scatter (
			x = OHLCV_DF ['UTC date string'], 
			y = OHLCV_DF [ venture ], 
			line = dict (
				color = color, 
				width = 3
			)
		),
		row = 1,
		col = 1
	)
	

	
def check_1 ():
	trend = read_CSV ()
	trend_DF = pandas.DataFrame (trend)	
	
	enhanced_trend_DF = ramps_superb.calc (
		trend_DF,
		period = 14,
		multiplier = 3
	)
	
	
	#enhanced_list = enhanced_trend_DF.to_dict ('records')
	#print (enhanced_list)
	
	
	superb_VP_holding.calc (enhanced_trend_DF)
	enhanced_list = enhanced_trend_DF.to_dict ('records')
	
	rich.print_json (data = enhanced_list)
	
	
	import ramps_superb.charts.VLOCH as VLOCH
	chart = VLOCH.show (
		DF = enhanced_trend_DF
	)
	
	import ramps_superb.charts.trend_side_circles as trend_side_circles
	trend_side_circles.attach (
		chart = chart,
		DF = enhanced_trend_DF
	)
	
	import ramps_superb.charts.superb_line as superb_line
	superb_line.attach (
		chart = chart,
		DF = enhanced_trend_DF
	)	
		
	chart.show ()
	
checks = {
	"check 1": check_1
}