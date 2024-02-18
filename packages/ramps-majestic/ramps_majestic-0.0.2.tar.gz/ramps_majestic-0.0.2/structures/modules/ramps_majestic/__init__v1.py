

'''
	based on:
		https://stackoverflow.com/questions/44935269/supertrend-code-using-pandas-python
'''


from ._clique import clique



'''
	import ramps_majestic
	enhanced_trend_DF = majestic.calc ([{
		"high": "",
		"low": "",
		"open": "",
		"close": ""
	}])	
'''

'''
	description:
		yields:
			majestic estimate
'''

def calc (
	DF,
	
	period = 14,
	multiplier = 3
):

	DF ['TR 1'] = abs (DF ["high"] - DF ["low"])
	DF ['TR 2'] = abs (DF ["high"] - DF ["close"].shift (1))
	DF ['TR 3'] = abs (DF ["low"]- DF ["close"].shift (1))
	DF ["TR"] = round (DF [[ 'TR 1', 'TR 2', 'TR 3' ]].max (axis = 1), 2)
	
	DF ["ATR"] = 0.00
	
	'''
		Basic and Final
	
		UB & LB:
			upper band and lower band?
	'''
	DF ['BUB'] = 0.00
	DF ["BLB"] = 0.00
	DF ["FUB"] = 0.00
	DF ["FLB"] = 0.00
	
	DF ["majestic line"] = 0.00
	
	# Calculating ATR 
	for i, row in DF.iterrows ():
		if i == 0:
			DF.loc [ i, 'ATR' ] = 0.00 
			#DF['ATR'].iat[0]
		else:
			DF.loc [ i, 'ATR'] = ((DF.loc[i-1,'ATR'] * (period - 1))+DF.loc[i,'TR'])/ period


	'''
		# Calculate SuperTrend
		upper_band = (high + low) / 2 + multiplier * atr
		lower_band = (high + low) / 2 - multiplier * atr
	'''
	'''
		round to 2 decimal places..
	'''
	DF ['BUB'] = round (
		((DF ["high"] + DF ["low"]) / 2) + (multiplier * DF ["ATR"]),
		2
	)
	DF ['BLB'] = round (
		((DF ["high"] + DF ["low"]) / 2) - (multiplier * DF ["ATR"]),
		
		2
	)



	'''
		https://pandas.pyDF.org/pandas-docs/stable/reference/api/pandas.DFFrame.loc.html
	'''
	for i, row in DF.iterrows ():
		if i == 0:
			DF.loc [ i, "FUB"] = 0.00
		else:
			if (DF.loc [ i, "BUB" ] < DF.loc[i-1,"FUB"])|(DF.loc[i-1,"close"]>DF.loc[i-1,"FUB"]):
				DF.loc [ i, "FUB" ] = DF.loc[i,"BUB"]
			else:
				DF.loc [ i, "FUB" ] = DF.loc[i-1,"FUB"]


	for i, row in DF.iterrows ():
		if i == 0:
			DF.loc [ i, "FLB" ]=0.00
		else:
			if (DF.loc[i,"BLB"]>DF.loc[i-1,"FLB"])|(DF.loc[i-1,"close"]<DF.loc[i-1,"FLB"]):
				DF.loc[i,"FLB"]=DF.loc[i,"BLB"]
			else:
				DF.loc[i,"FLB"]=DF.loc[i-1,"FLB"]



	# SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current close <= Current FINAL UPPERBAND)) THEN
	#                 Current FINAL UPPERBAND
	#             ELSE
	#                 IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current close > Current FINAL UPPERBAND)) THEN
	#                     Current FINAL LOWERBAND
	#                 ELSE
	#                     IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current close >= Current FINAL LOWERBAND)) THEN
	#                         Current FINAL LOWERBAND
	#                     ELSE
	#                         IF((Previous SUPERTREND = Previous FINAL LOWERBAND) and (Current close < Current FINAL LOWERBAND)) THEN
	#                             Current FINAL UPPERBAND


	for i, row in DF.iterrows ():
		if i==0:
			DF.loc[i,"majestic line"]=0.00
		elif (DF.loc[i-1,"majestic line"]==DF.loc[i-1,"FUB"]) & (DF.loc[i,"close"]<=DF.loc[i,"FUB"]):
			DF.loc[i,"majestic line"]=DF.loc[i,"FUB"]
		
		elif (DF.loc[i-1,"majestic line"]==DF.loc[i-1,"FUB"])&(DF.loc[i,"close"]>DF.loc[i,"FUB"]):
			DF.loc[i,"majestic line"]=DF.loc[i,"FLB"]
		
		elif (DF.loc[i-1,"majestic line"]==DF.loc[i-1,"FLB"])&(DF.loc[i,"close"]>=DF.loc[i,"FLB"]):
			DF.loc[i,"majestic line"]=DF.loc[i,"FLB"]
		
		elif (DF.loc[i-1,"majestic line"]==DF.loc[i-1,"FLB"])&(DF.loc[i,"close"]<DF.loc[i,"FLB"]):
			DF.loc[i,"majestic line"]=DF.loc[i,"FUB"]


	multiplier = 1;
	fee = 0

	trend = "NA"
	pivot = "no"
	inventory = 0;
	

	'''
		This figures out the indicators
		
		{
			"open": 22757.267578,
			"high": 23310.974609,
			"low": 22756.257813,
			"close": 23264.291016,
			"volume": "27187964471",
			"unadjusted close": "23264.291016",
			"date string": "2023-02-07",
			"majestic line": 0.0,
			"multiplier": 1.0,
			"inventory": "0",
			"majestic estimate": "NA"
		  },
		  {
			"open": 23263.416016,
			"high": 23367.958984,
			"low": 22731.097656,
			"close": 22939.398438,
			"volume": "25371367758",
			"unadjusted close": "22939.398438",
			"date string": "2023-02-08",
			"majestic line": 23186.0,
			"multiplier": 1.0,
			"inventory": "0",
			"majestic estimate": "decline_move"
		  }
  
		NA no 23264.291016
		NA no 22939.398438
		decline no 21819.039063
		decline no 21651.183594
		
	'''
	for i, row in DF.iterrows ():	
		if (pivot == "yes"):
			pivot = "no"
	
		if i == 0:
			DF ["majestic estimate"] = "NA_move"
			trend = "NA_move"
			
			if (trend != "NA_move"):
				pivot = "yes"
			
		elif (DF.loc [ i, "majestic line" ] < DF.loc [ i, "close" ]):
			DF.loc [ i, "majestic estimate" ] = "incline_move"
			
			if (trend != "incline_move"):
				pivot = "yes"
			
			trend = "incline_move"
			
			
		else:
			DF.loc[ i, "majestic estimate" ] = "decline_move"
			
			if (trend != "decline_move"):
				pivot = "yes"
			
			trend = "decline_move"
		
		DF.loc [ i, "pivot" ] = pivot
		
		
		
	'''
	for i, row in DF.iterrows ():
		DF.loc [ i, "multiplier" ] = multiplier
	
		print (trend, pivot, DF.loc [ i, "close" ])
	
		if (trend == "incline"):
			DF.loc [ i, "inventory" ] = "1"
			inventory = "1"
			
			if (pivot != "yes"):			
				DF.loc [ i, "multiplier" ] = (
					DF.loc [ i, "close" ] / 
					DF.loc [ i - 1, "close" ]
				)
					
	'''
		
			
	DF = DF.drop (columns = [
		'TR 1', 'TR 2', 'TR 3',
		'TR',
		'ATR',
		"BUB", "BLB", "FUB", "FLB"
	])		
			
	return DF;