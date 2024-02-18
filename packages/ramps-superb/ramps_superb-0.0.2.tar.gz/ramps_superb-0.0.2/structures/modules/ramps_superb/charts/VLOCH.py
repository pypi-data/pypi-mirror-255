

'''
	VLOCH
'''


'''
	import ramps_superb.charts.VLOCH as VLOCH
	chart = VLOCH.show (
		DF = DF
	)
	
	chart.show ()
'''

from datetime import datetime

import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots


'''
	https://stackoverflow.com/questions/64689342/plotly-how-to-add-volume-to-a-candlestick-chart
'''
'''
themes = [
	"plotly", "plotly_white", "plotly_dark", 
	"ggplot2", "seaborn", "simple_white", "none"
]:
'''
def show (
	#
	#	df
	#
	intervals = None,
	DF = None
):
	#
	#	Utilize the intervals as the DF if intervals is provided.
	#
	if (type (intervals) == list):
		df = pd.DataFrame.from_dict (intervals)
	else:
		df = DF;


	fig = make_subplots (
		rows = 2, 
		cols = 1, 
		shared_xaxes = True, 
		vertical_spacing = 0.03, 
		subplot_titles = ('', ''), 
		row_width = [ 
			0.3, 
			0.7
		]
	)
	

	candle_stick_chart = go.Candlestick (
		x = df ['date string'],
		
		open = df ['open'],
		high = df ['high'],
		low = df ['low'],
		close = df ['close']
	)


	fig.append_trace ( 
		candle_stick_chart,
		row = 1,
		col = 1
	)

	'''
	fig.add_trace (
		go.Bar (
			x = df ['date string'], 
			y = df ['ATR'], 
			showlegend = False
		), 
		row = 2, 
		col = 1
	)
	'''

	dark_mode = False;
	if (dark_mode):	
		fig.update_layout (template = 'plotly_dark')
	
	
	fig.update (layout_xaxis_rangeslider_visible = True)

	#fig.data[1].increasing.fillcolor = color_hi_fill
	#fig.data[1].decreasing.fillcolor = 'rgba(0,0,0,0)'

	fig.data [0].increasing.line.color = 'rgba (200,0,130,1)'
	fig.data [0].decreasing.line.color = 'rgba (200,130,0,1)'

	return fig;