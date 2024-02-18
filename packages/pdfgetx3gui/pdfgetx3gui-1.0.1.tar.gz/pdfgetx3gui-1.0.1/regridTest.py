import numpy as np

import time
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

file = r'C:\Users\kenneth1a\Documents\beamlineData\May2023\measurements\C60\xrd\average\xye/C60_0p3mm_001_average_gainCorrected.xye'
x,y = np.loadtxt(file,unpack=True,usecols=(0,1))
q = 4*np.pi*np.sin(x*np.pi/(2*180))/(0.24032)

def qRebin(q, intensity, method = 'linear',power = 1, exponent = 0.0005):
	t0 = time.time()
	if method == 'none':
		return q, intensity
	
	qspacing = (q[-1] - q[0])/(len(q)-1)
	qovergrid = np.arange(q[0],q[-1], qspacing/20)
	regridfunc = interp1d(q,intensity) #from scipy
	intovergrid = regridfunc(qovergrid)

	if method == 'linear':
		gradient = 1.1
		newq = np.array([qn*gradient for qn in q if qn*gradient < q[-1]])



	elif method == 'exponential':
		exponent = 0.0005
		newq = np.array([qn*np.exp((exponent*i)**power) for i,qn in enumerate(q) if qn*np.exp((exponent*i)**power) < q[-1]])
	elif method == 'exponential2':
		exponent = 0.0005
		newq = np.array([qn*np.exp((exponent*i)**2) for i,qn in enumerate(q) if qn*np.exp((exponent*i)**2) < q[-1]])

	newint = np.array([])
	for n in range(len(newq)):
		if n == 0:
			qminval = newq[n]
		else:
			qminval = (newq[n] + newq[n-1])/2
		if n == len(newq)-1:
			qmaxval = newq[n]
		else:
			qmaxval = (newq[n+1] + newq[n])/2
		qominindex = np.abs(qovergrid - qminval).argmin()
		qomaxindex = np.abs(qovergrid - qmaxval).argmin()

		intensityn = np.average(intovergrid[qominindex:qomaxindex],axis = 0)
		newint = np.append(newint,intensityn)
	newqmaxindex = np.abs(q-newq[-1]).argmin()
	regridfunc2 = interp1d(newq,newint)
	newintRG = regridfunc2(q[:newqmaxindex])
	print('rebin time:', time.time() - t0)
	return q[:newqmaxindex], newintRG, qovergrid, intovergrid

def qRebin2(q, intensity, method = 'linear'):
	t0 = time.time()
	if method == 'none':
		return q, intensity
	

	regridfunc = interp1d(q,intensity) #from scipy


	if method == 'linear':
		gradient = 1.1
		newq = np.array([qn*gradient for qn in q if qn*gradient < q[-1]])




	elif method == 'exponential':
		exponent = 0.0005
		newq = np.array([qn*np.exp(exponent*i) for i,qn in enumerate(q) if qn*np.exp(exponent*i) < q[-1]])

	newint = np.array([])
	for n in range(len(newq)):
		if n == 0:
			qminval = newq[n]
		else:
			qminval = (newq[n] + newq[n-1])/2
		if n == len(newq)-1:
			qmaxval = newq[n]
		else:
			qmaxval = (newq[n+1] + newq[n])/2
		intav0 = regridfunc(qminval)
		intavend = regridfunc(qmaxval)
		intavmid = [intensity[i] for i in range(len(q)) if q[i] > qminval and q[i] < qmaxval]
		intrange = np.array([intav0]+ intavmid + [intavend])
		intensityn = np.average(intrange,axis = 0)
		newint = np.append(newint,intensityn)
	print('rebin2 time:', time.time() - t0)
	return newq, newint

def qRegrid(q, intensity, method = 'linear', power = 1):
	if method == 'none':
		return q, intensity
	
	regridfunc = interp1d(q,intensity) #from scipy


	if method == 'linear':
		gradient = 1.1
		newq = np.array([qn*gradient for qn in q if qn*gradient < q[-1]])

	elif method == 'exponential':
		exponent = 0.0005
		newq = np.array([qn*np.exp((exponent*i)**power) for i,qn in enumerate(q) if qn*np.exp((exponent*i)**power) < q[-1]])
	newint = regridfunc(newq)
	return newq, newint



xrebin,yrebin, xovergrid, yovergrid = qRebin(x,y,'exponential')
xrebin2,yrebin2,_,_  = qRebin(x,y,'exponential', power= 2)
xregrid,yregrid = qRegrid(x,y,'exponential')
qnew = 4*np.pi*np.sin(xrebin*np.pi/(2*180))/(0.24032)

plt.figure()
plt.plot(x,y, 'o-', label = 'original',markersize = 2)
plt.plot(xrebin,yrebin, 'o-',linewidth = 2, label = 'rebin',markersize = 3)
plt.plot(xrebin2,yrebin2,'o-',linewidth = 2, label = 'rebin2', markersize = 3)
#plt.plot(xovergrid,yovergrid, 'o-',label = 'overgrided', markersize = 2)
#plt.plot(xregrid,yregrid,linewidth = 2, label = 'regrid')
plt.legend()
plt.show()
