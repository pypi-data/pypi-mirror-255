



def start (DF):
	#data = data.iloc[::-1]

	DF = DF [::-1].reset_index (drop = True)
	print ("data retrieved reversed", DF)