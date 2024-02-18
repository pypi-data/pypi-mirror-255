


'''
	description:
		This adds..
'''

'''
	agenda: 
		{
			"ramp victory percentage": "",
			"hold victory percentage": ""
		}
'''

'''
	import ramps_majestic.victory_multiplier.holding as majestic_VM_holding
	majestic_VP_holding.calc (data)
'''

from fractions import Fraction
def calc (DF):
	win_rate = 1

	previous_amount = None;
	previous_signal = None;
	
	last_decline_move_signal = None
	last_incline_move_signal = None
	
	bought_at = None
	sold_at = None
	
	'''
		find incline_move signal to decline_move signal multiplier.
	'''	
	for index, row in DF.iterrows ():
		signal = row ['majestic estimate']
			
		'''
			.. maybe this gets the most recent
			move signals...
		'''
		if (signal == "decline_move"):
			last_decline_move_signal = row ["close"]
			
		elif (signal == "incline_move"):
			last_incline_move_signal = row ["close"]
		
		else:
			print ("?")
		
		
		
		'''
			pivot calculations
		'''
		if (signal == "incline_move" and previous_signal == "decline_move"):	
			bought_at = Fraction (row ["close"])
			
			'''
				Description:
					The defacto here is that you weren't holding the
					asset and then you purchased the asset.
			'''
			
			
		if (signal == "decline_move" and previous_signal == "incline_move"):			
			sold_at = Fraction (row ["close"])
			
			if (type (bought_at) == Fraction):
				multiplier = Fraction (row ["close"]) / Fraction (bought_at)	
				win_rate = win_rate * multiplier

				print ({
					"win rate": float (win_rate),
					"multiplier": float (multiplier),
					"span": [ float (bought_at), float (sold_at) ]
				})
				
			else:
				print ("The type of bought at could not be determined")
			
			
		previous_signal = signal;
		
	
	actual_change = float (
		Fraction (DF ["close"].iloc [-1]) / 
		Fraction (DF ["close"].iloc [0])
	)	
	

	return {
		"ramp victory multiplier": float (win_rate),
		"hold victory multiplier": float (actual_change)
	}