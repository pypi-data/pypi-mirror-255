
'''
	import ramps_superb.charts.superb_line as superb_line
	superb_line.attach (
		chart = chart,
		DF = enhanced_trend_DF
	)	
'''

import plotly.graph_objects as GO
def attach (
	chart, 
	DF, 
	line_name = "superb line", 
	color = "purple"
):
	chart.add_trace (
		GO.Scatter (
			x = DF ['date string'], 
			y = DF [ line_name ], 
			line = dict (
				color = color, 
				width = 3
			)
		),
		row = 1,
		col = 1
	)