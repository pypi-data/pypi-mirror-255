


'''
	description:
		This adds..
'''

'''
	import ramps_superb.victory_percentage.holding as superb_VP_holding
	superb_VP_holding.calc (data)
'''

from fractions import Fraction
def calc (DF):
	win_rate = 1

	previous_amount = None;
	previous_signal = None;
	
	last_sell_move_signal = None
	last_buy_move_signal = None
	
	bought_at = None
	sold_at = None
	
	'''
		find buy_move signal to sell_move signal multiplier.
	'''	
	for index, row in DF.iterrows ():
		signal = row ['superb direction']
		
		#print (signal, previous_signal)
		
		if (signal == "sell_move"):
			last_sell_move_signal = row ["close"]
			
			
		elif (signal == "buy_move"):
			last_buy_move_signal = row ["close"]
		
		
		if (signal == "buy_move" and previous_signal == "sell_move"):
			#print ("buy_move!", last_sell_move_signal)
			
			bought_at = Fraction (row ["close"])
			
			'''
			if (type (sold_at) == Fraction):
				multiplier = Fraction (row ["close"]) / Fraction (sold_at)	
				win_rate = win_rate * multiplier

				print ({
					"win rate": float (win_rate),
					"multiplier": float (multiplier),
					"span": [ float (bought_at), float (sold_at) ]
				})
			'''
			
		if (signal == "sell_move" and previous_signal == "buy_move"):
			#print ("sell_move!", last_buy_move_signal, type (bought_at))
			
			sold_at = Fraction (row ["close"])
			
			if (type (bought_at) == Fraction):
				multiplier = Fraction (row ["close"]) / Fraction (bought_at)	
				win_rate = win_rate * multiplier

				print ({
					"win rate": float (win_rate),
					"multiplier": float (multiplier),
					"span": [ float (bought_at), float (sold_at) ]
				})
			
			
		previous_signal = signal;
		
	
	actual_change = float (
		Fraction (DF ["close"].iloc [-1]) / Fraction (DF ["close"].iloc [0])
	)	
	
	print ()
	print ("win_rate of the superb tap:", float (win_rate))
	print ("actual change:", actual_change)
	
	
	return;