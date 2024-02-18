
'''
	import ramps_majestic.charts.majestic_line as majestic_line
	majestic_line.attach (
		chart = chart,
		DF = enhanced_trend_DF
	)	
'''

import plotly.graph_objects as GO
def attach (
	chart, 
	DF, 
	line_name = "majestic line", 
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