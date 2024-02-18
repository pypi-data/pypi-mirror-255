import matplotlib.pyplot as plt
a = []
fig,ax = plt.subplots(2,1)
for n in range(5):
	a.append(n)
	ax[0].cla()
	ax[1].cla()
	ax[0].plot(a,a,'o-')
	ax[1].plot(a,a,'o-')
	plt.show(block=False)
	plt.pause(1)