
'''
	python3 status.proc.py "_status/vows/1/status_1.py"
'''

'''
	https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
'''

import json


import pandas
import rich	


import ramps_majestic
import ramps_majestic.victory_multiplier.ramp as majestic_VM_ramp	
import ramps_majestic.furniture.CSV.read as read_CSV

def relative_path (path):
	import pathlib
	from os.path import dirname, join, normpath
	import sys

	this_directory_path = pathlib.Path (__file__).parent.resolve ()	
	return str (normpath (join (this_directory_path, path)))
	

	
def check_1 ():
	trend = read_CSV.start (relative_path ("yahoo-finance--BTC-USD.CSV"))
	trend_DF = pandas.DataFrame (trend)	
	
	enhanced_trend_DF = ramps_majestic.calc (
		trend_DF,
		period = 14,
		multiplier = 3
	)
	
	
	#enhanced_list = enhanced_trend_DF.to_dict ('records')
	#print (enhanced_list)
	
	
	multipliers = majestic_VM_ramp.calc (enhanced_trend_DF)
	rich.print_json (data = multipliers)	
	assert (multipliers ["ramp victory multiplier"] == 1.7190292640816087)
	assert (multipliers ["hold victory multiplier"] == 1.9002342058305688)
	
	enhanced_list = enhanced_trend_DF.to_dict ('records')
	
	rich.print_json (data = enhanced_list)
	
	
	import ramps_majestic.charts.VLOCH as VLOCH
	chart = VLOCH.show (
		DF = enhanced_trend_DF
	)
	
	import ramps_majestic.charts.trend_side_circles as trend_side_circles
	trend_side_circles.attach (
		chart = chart,
		DF = enhanced_trend_DF
	)
	
	import ramps_majestic.charts.majestic_line as majestic_line
	majestic_line.attach (
		chart = chart,
		DF = enhanced_trend_DF
	)	
		
	chart.show ()
	
checks = {
	"check 1": check_1
}