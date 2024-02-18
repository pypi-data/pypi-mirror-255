




from ._clique import clique





'''
	import ramps_superb
	enhanced_trend_DF = superb.calc ([{
		"high": "",
		"low": "",
		"open": "",
		"close": ""
	}])	
'''

'''
	description:
		yields:
			superb direction
'''

def calc (
	data,
	
	period = 14,
	multiplier = 3
):
	
	# reverse the DF
	#data = data.iloc[::-1]
	#data = data [::-1].reset_index (drop = True)
	#print ("data retrieved reversed", data)

	data ['tr0'] = abs (data ["high"] - data ["low"])
	data ['tr1'] = abs (data ["high"] - data ["close"].shift(1))
	data ['tr2'] = abs (data ["low"]- data ["close"].shift(1))
	data ["TR"] = round (data [['tr0', 'tr1', 'tr2']].max(axis=1),2)
	
	data ["ATR"] = 0.00
	
	'''
		Basic and Final
	
		UB & LB:
			upper band and lower band?
	'''
	data ['BUB'] = 0.00
	data ["BLB"] = 0.00
	data ["FUB"] = 0.00
	data ["FLB"] = 0.00
	
	data ["superb line"] = 0.00
	
	# Calculating ATR 
	for i, row in data.iterrows ():
		if i == 0:
			data.loc [i,'ATR'] = 0.00 
			#data['ATR'].iat[0]
		else:
			data.loc[i,'ATR'] = ((data.loc[i-1,'ATR'] * (period - 1))+data.loc[i,'TR'])/ period


	'''
		# Calculate SuperTrend
		upper_band = (high + low) / 2 + multiplier * atr
		lower_band = (high + low) / 2 - multiplier * atr
	'''
	'''
		round to 2 decimal places..
	'''
	data ['BUB'] = round (
		((data ["high"] + data ["low"]) / 2) + 
		(multiplier * data ["ATR"]),
		
		2
	)
	
	
	data['BLB'] = round (
		((data ["high"] + data ["low"]) / 2) - (multiplier * data ["ATR"]),
		
		2
	)


	# FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous close > Previous FINAL UPPERBAND))
	#                     THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)


	for i, row in data.iterrows ():
		if i==0:
			data.loc[i,"FUB"]=0.00
		else:
			if (data.loc[i,"BUB"]<data.loc[i-1,"FUB"])|(data.loc[i-1,"close"]>data.loc[i-1,"FUB"]):
				data.loc[i,"FUB"]=data.loc[i,"BUB"]
			else:
				data.loc[i,"FUB"]=data.loc[i-1,"FUB"]

	# FINAL LOWERBAND = IF( (Current BASIC LOWERBAND > Previous FINAL LOWERBAND) or (Previous close < Previous FINAL LOWERBAND)) 
	#                     THEN (Current BASIC LOWERBAND) ELSE Previous FINAL LOWERBAND)

	for i, row in data.iterrows():
		if i==0:
			data.loc[i,"FLB"]=0.00
		else:
			if (data.loc[i,"BLB"]>data.loc[i-1,"FLB"])|(data.loc[i-1,"close"]<data.loc[i-1,"FLB"]):
				data.loc[i,"FLB"]=data.loc[i,"BLB"]
			else:
				data.loc[i,"FLB"]=data.loc[i-1,"FLB"]



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


	for i, row in data.iterrows():
		if i==0:
			data.loc[i,"superb line"]=0.00
		elif (data.loc[i-1,"superb line"]==data.loc[i-1,"FUB"]) & (data.loc[i,"close"]<=data.loc[i,"FUB"]):
			data.loc[i,"superb line"]=data.loc[i,"FUB"]
		
		elif (data.loc[i-1,"superb line"]==data.loc[i-1,"FUB"])&(data.loc[i,"close"]>data.loc[i,"FUB"]):
			data.loc[i,"superb line"]=data.loc[i,"FLB"]
		
		elif (data.loc[i-1,"superb line"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]>=data.loc[i,"FLB"]):
			data.loc[i,"superb line"]=data.loc[i,"FLB"]
		
		elif (data.loc[i-1,"superb line"]==data.loc[i-1,"FLB"])&(data.loc[i,"close"]<data.loc[i,"FLB"]):
			data.loc[i,"superb line"]=data.loc[i,"FUB"]

	# buy_move sell_move Indicator
	for i, row in data.iterrows():
		if i==0:
			data["superb direction"]="NA"
		elif (data.loc[i,"superb line"]<data.loc[i,"close"]) :
			data.loc[i,"superb direction"]="buy_move"
		else:
			data.loc[i,"superb direction"]="sell_move"
			
	return data;