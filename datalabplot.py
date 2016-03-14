import matplotlib.pyplot as plt
#import seaborn as sns

def LabDataPlot(headers, datas, errors):

	font = {'family' : 'serif',
        'color'  : 'darkred',
        'weight' : 'normal',
        'size'   : 16,
        }

	#with plt.xkcd():

	plt.title('Damped exponential decay', fontdict=font)
	plt.xlabel('time (s)', fontdict=font)
	plt.ylabel('voltage (mV)', fontdict=font)
	#plt.grid(True)

	for i in range(len(datas)):

		#Grab above and below x errors
		belowpts1 = []
		abovepts1 = []
		belowpts2 = []
		abovepts2 = []

		belowx = [a - b for a, b in zip(datas[i][0], errors[i][0])]
		abovex = [a + b for a, b in zip(datas[i][0], errors[i][0])]

		belowy = [a - b for a, b in zip(datas[i][1], errors[i][1])]
		abovey = [a + b for a, b in zip(datas[i][1], errors[i][1])]


		for pts in zip(belowx,datas[i][0]):
			belowpts1 += list(pts)

		for pts in zip(datas[i][1],abovey):
			abovepts1 += list(pts)

		for pts in zip(datas[i][0],abovex):
			belowpts2 += list(pts)

		for pts in zip(belowy,datas[i][1]):
			abovepts2 += list(pts)

		plt.plot(datas[i][0],datas[i][1])
		plt.plot(belowpts1,abovepts1)
		plt.plot(belowpts2,abovepts2)

		plt.errorbar(datas[i][0], datas[i][1], xerr=errors[i][0], yerr=errors[i][1])
		plt.fill_between(belowpts1,abovepts1,abovepts2,linewidth=0.0,color='darkgreen', alpha='0.5')
		plt.fill_betweenx(abovepts2,belowpts1,belowpts2,linewidth=0.0,color='darkgreen', alpha='0.5')

	plt.savefig('myfig.pdf')

#END
