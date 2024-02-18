import numpy as np 
import matplotlib.pyplot as plt 
import _pickle as pickle 
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
import matplotlib as mpl
from magnelPy import statFunc

#####################################################################
# First version, I will put detailed comments soon - Balsa
#################################################################
def oneplot(plot_dict, fig):

	x=plot_dict['x']
	y=plot_dict['y']
	xlim=plot_dict["xlim"]
	ylim=plot_dict["ylim"]
	xscale=plot_dict["xscale"]
	yscale=plot_dict["yscale"]
	label=plot_dict["label"]
	linestyle=plot_dict["linestyle"]
	color=plot_dict["color"]
	marker=plot_dict["marker"]
	#dashes=plot_dict["dashes"]
	try:
		ax = plt.gca()
	except:
		ax = fig.add_subplot(1, 1, 1)

	plot_line=ax.plot(x,y,label=label,linestyle=linestyle,color=color, marker=marker)#,dashes=dashes
	leftx, rightx = plt.xlim()
	# if leftx > xlim[0]: # RVC : issue as this overwrites the command
	leftx=xlim[0]
	# elif rightx<xlim[1]:
	rightx=xlim[1]
	plt.xlim((leftx, rightx))
	# lefty, righty = plt.ylim()
	
	# # if lefty > ylim[0]:
	# lefty=ylim[0]
		
		
	# # if righty < ylim[1]:
	# righty=ylim[1]
	
		
	# plt.ylim((lefty, righty))
	plt.xscale(xscale)
	plt.yscale(yscale)
	ax.xaxis.set_minor_locator(AutoMinorLocator(5))

	#ax.yaxis.set_minor_locator(MultipleLocator(5))
	plt.legend(handlelength=4,framealpha=1,fontsize=12)
	#ax.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
	ax.tick_params(axis='both',pad=10,labelsize=12, length=5) # mod conform legend and axis titles
	#ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,g}'))

	return plot_line
def create_plot_dictionary(x,y, xlim=0, ylim=0, xscale=0, yscale=0,linestyle=0, label=0, color=0,marker=0):
	
	if xlim == 0:
		xlength=np.max(x)-np.min(x)
		xlim=(np.min(x)-0.1*xlength,np.max(x)+0.1*xlength)
	if ylim == 0:
		ylength=np.max(y)-np.min(y)
		ylim=(np.min(y)-0.1*ylength,np.max(y)+0.1*ylength)
	if xscale == 0:
		xscale='linear'
	if yscale == 0:
		yscale='linear'
	if label == 0:
		label=''
	if color == 0:
		color='black'
	if marker == 0:
		marker='None'
	if linestyle == 0:
		linestyle='-'




	plot_dict={
	"x":x,
	"y":y,
	"xlim":xlim,
	"ylim":ylim,
	"xscale":xscale,
	"yscale":yscale,
	"label":label,
	"linestyle":linestyle,
	"color":color,
	"marker":marker
	
	}
	return plot_dict
	
	
def color_list(num):
	color_list=['black', 'r', "blue",'green', 'orange',  'm', 'c', 'grey', 'brown','pink','olive']
	color=color_list[num]
	return color

def marker_list(num):
	marker_list=["o","x","s","+","^","D","."]
	marker=marker_list[num]
	return marker

def linestyle_list(num):
	#Dodaj jos linije crtica pomocu recnika preko prve reci
	linestyle_list = ['-', (1,(1,1)),(0,(3,2,1,2)),(0,(5,5)),(0,(5,10)),(0,(3,2,1,2,1,2)) ] 
	linestyle=linestyle_list[num]
	return linestyle

def ploty_cdf(data, names=0,figname=0,BW=False,fig=0,linestyle=0,cdftype='both'):
	
	#################################################################
	#CDF plotting function
	#	data - 		input array where a seperate CDF will be drawn for every column
	#	names - 	list of names for every column
	#	figename - 	name of the pickle file where the figure will be saved (if = 0 no saveing)
	#
	#	type - 		type of visulization : 'cdf', 'ccdf', 'both'
	#################################################################
	try:
		data[0,0]
	except:
		data=data.reshape((len(data), 1))
	cdf=data*0
	for num in np.arange(len(data[0,:])):
		cdf[:,num]=np.sort(data[:,num])
	if names == 0:
		names=[None]*len(cdf[0,:]) 
	if linestyle == 0:
		linestyle='-'
	if fig == 0:
		fig=plt.figure(figsize=(8.0,6.0))
	plot_dicts=[]
	n=len(cdf[:,num])
	for num in np.arange(len(cdf[0,:])):
		if BW: # RVC : linestyle is overwritten
			if cdftype=='both' or cdftype=='cdf': plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=np.arange(0+1/n/2,1,1/len(cdf[:,num])),label=names[num],yscale='Log', linestyle=linestyle))
			if cdftype=='both': plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=1-np.arange(0+1/n/2,1,1/len(cdf[:,num])),yscale='Log',linestyle=linestyle))
			if cdftype=='ccdf': plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=1-np.arange(0+1/n/2,1,1/len(cdf[:,num])),label=names[num],yscale='Log',linestyle=linestyle))
		else:
			if cdftype=='both' or cdftype=='cdf': plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=np.arange(0+1/n/2,1,1/len(cdf[:,num])),color=color_list(num),label=names[num],yscale='Log',linestyle=linestyle ))
			if cdftype=='both': plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=1-np.arange(0+1/n/2,1,1/len(cdf[:,num])),color=color_list(num),yscale='Log',linestyle=linestyle))
			if cdftype=='ccdf': plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=1-np.arange(0+1/n/2,1,1/len(cdf[:,num])),color=color_list(num),label=names[num],yscale='Log',linestyle=linestyle))
	for num in np.arange(len(plot_dicts)):
		oneplot(plot_dicts[num],fig)
	# plt.ylim((1/len(cdf[:,0]/2),1))
	fig.show()
	

	if figname !=0:
		#print(figname)
		pickle.dump(fig,open(figname,'wb'))
	return fig

def ploty_pdf(data, names=0,nbins=50,figname=0,fig=0,linestyle=0):
	
	#################################################################
	#PDF plotting function
	#	data - 		input array where a seperate PDF will be drawn for every column
	#	names - 	list of names for every column
	#	nbins - 	total number of bins for the whole graph (each PDF will have the same bin width)
	#	figename - 	name of the pickle file where the figure will be saved (if = 0 no saveing)
	#
	#################################################################
	try:
		data[0,0]
	except:
		data=data.reshape((len(data), 1))

	my_bins=np.arange(0.9*np.min(data),1.1*np.max(data),(1.1*np.max(data)-0.9*np.min(data))/nbins)
	bwidth=(1.1*np.max(data)-0.9*np.min(data))/nbins
	Histy=np.zeros((len(my_bins),len(data[0,:])))
	Histx=np.zeros((len(my_bins)+1,len(data[0,:])))

	if names == 0:
		names=['']*len(data[0,:])
	if linestyle == 0:
		linestyle='-'
	if fig == 0:
		fig=plt.figure(figsize=(18,10))
	plot_dicts=[]
	for num in np.arange(len(data[0,:])):
		Histy[1:,num],Histx[1:,num]=np.histogram(data[:,num],bins=my_bins)
		Histx[0,num]=Histx[1,num]
		plot_dicts.append(create_plot_dictionary(x=(Histx[:-1,num]+Histx[1:,num])/2,y=Histy[:,num]/len(data[:,num])/bwidth,color=color_list(num),label=names[num],linestyle=linestyle))
	for num in np.arange(len(plot_dicts)):
		oneplot(plot_dicts[num],fig)
	if figname !=0:
		pickle.dump(fig,open(figname,'wb'))
	lefty, righty = plt.ylim()
	plt.ylim((0, righty))

	fig.show()
	return fig

def ploty_cdf_approx(m,s,fig,dist_type):
	
	leftx, rightx = plt.xlim()
	cdfx=np.arange(leftx,rightx,(rightx-leftx)/100)
	plot_dicts=[]
	for num in np.arange(len(m)):

		if dist_type == "N":
			cdfy=statFunc.F_Normal(cdfx,m[num],s[num])
		elif dist_type == 'LN':
			cdfy=statFunc.F_Lognormal(cdfx,m[num],s[num])
		elif dist_type == 'Gamma':
			cdfy=statFunc.F_Gamma(cdfx,m[num],s[num])	
		elif dist_type == 'Gumbel':
			cdfy=statFunc.F_Gumbel(cdfx,m[num],s[num])
		plot_dicts.append(create_plot_dictionary(x=cdfx,y=cdfy,color=color_list(num),yscale='Log' ,linestyle=':'))
		plot_dicts.append(create_plot_dictionary(x=cdfx,y=1-cdfy,color=color_list(num),yscale='Log',linestyle=':'))
	for num in np.arange(len(plot_dicts)):
		oneplot(plot_dicts[num],fig)

	return fig

def ploty_pdf_approx(m,s,fig,dist_type):
	
	leftx, rightx = plt.xlim()
	pdfx=np.arange(leftx,rightx,(rightx-leftx)/100)
	plot_dicts=[]
	for num in np.arange(len(m)):

		if dist_type == "N":
			pdfy=statFunc.f_Normal(pdfx,m[num],s[num])
		elif dist_type == 'LN':
			pdfy=statFunc.f_Lognormal(pdfx,m[num],s[num])
		elif dist_type == 'Gamma':
			pdfy=statFunc.f_Gamma(pdfx,m[num],s[num])	
		elif dist_type == 'Gumbel':
			pdfy=statFunc.f_Gumbel(pdfx,m[num],s[num])
		plot_dicts.append(create_plot_dictionary(x=pdfx,y=pdfy,color=color_list(num) ,linestyle=':'))
		
	for num in np.arange(len(plot_dicts)):
		oneplot(plot_dicts[num],fig)
	lefty, righty = plt.ylim()
	plt.ylim((0, righty))

	return fig

def ploty_cdf_CONFAB(data, names=0,figname=0,BW=False,fig=0):
	
	#################################################################
	#CDF plotting function
	#	data - 		input array where a seperate CDF will be drawn for every column
	#	names - 	list of names for every column
	#	figename - 	name of the pickle file where the figure will be saved (if = 0 no saveing)
	#
	#################################################################
	try:
		data[0,0]
	except:
		data=data.reshape((len(data), 1))
	cdf=data*0
	for num in np.arange(len(data[0,:])):
		cdf[:,num]=np.sort(data[:,num])
	if names ==0:
		names=[None]*len(cdf[0,:])
	if fig == 0:
		fig=plt.figure(figsize=(12,9))
	plot_dicts=[]
	for num in np.arange(len(cdf[0,:])):
		if BW:
			plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=np.arange(0,1,1/len(cdf[:,num])),label=names[num],yscale='Log', linestyle=linestyle_list(num)))
			plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=1-np.arange(0,1,1/len(cdf[:,num])),yscale='Log',linestyle=linestyle_list(num)))
		else:
			plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=np.arange(0,1,1/len(cdf[:,num])),color=color_list(int(num/3)),linestyle=linestyle_list(num % 3),label=names[num],yscale='Log' ))
			plot_dicts.append(create_plot_dictionary(x=cdf[:,num],y=1-np.arange(0,1,1/len(cdf[:,num])),color=color_list(int(num/3)),linestyle=linestyle_list(num % 3),yscale='Log'))
	for num in np.arange(len(plot_dicts)):
		oneplot(plot_dicts[num],fig)
	plt.ylim((1/len(cdf[:,0]),1))
	#fig.show()
	

	if figname !=0:
		print(figname)
		pickle.dump(fig,open(figname,'wb'))
	return fig
def ploty_pdf_CONFAB(data, names=0,nbins=50,figname=0,fig=0,color=0):
	
	#################################################################
	#PDF plotting function
	#	data - 		input array where a seperate PDF will be drawn for every column
	#	names - 	list of names for every column
	#	nbins - 	total number of bins for the whole graph (each PDF will have the same bin width)
	#	figename - 	name of the pickle file where the figure will be saved (if = 0 no saveing)
	#
	#################################################################
	try:
		data[0,0]
	except:
		data=data.reshape((len(data), 1))

	my_bins=np.arange(0.9*np.min(data),1.1*np.max(data),(1.1*np.max(data)-0.9*np.min(data))/nbins)
	bwidth=(1.1*np.max(data)-0.9*np.min(data))/nbins
	Histy=np.zeros((len(my_bins),len(data[0,:])))
	Histx=np.zeros((len(my_bins)+1,len(data[0,:])))

	if names == 0:
		names=['']*len(data[0,:])
	if fig == 0:
		fig=plt.figure(figsize=(12,9))
	plot_dicts=[]
	for num in np.arange(len(data[0,:])):
		Histy[1:,num],Histx[1:,num]=np.histogram(data[:,num],bins=my_bins)
		Histx[0,num]=Histx[1,num]
		plot_dicts.append(create_plot_dictionary(x=(Histx[:-1,num]+Histx[1:,num])/2,y=Histy[:,num]/len(data[:,num])/bwidth,color=color_list(color),linestyle=linestyle_list(num % 3),label=names[num]))
	for num in np.arange(len(plot_dicts)):
		oneplot(plot_dicts[num],fig)
	if figname !=0:
		pickle.dump(fig,open(figname,'wb'))
	lefty, righty = plt.ylim()
	plt.ylim((0, righty))
	fig.show()
	return fig




if __name__ == "__main__":
	
	print('Test')
	Pn_input =np.load("Pn8.npy")
	names=[r'$E_{Confab}$',r'$E_{H&S}$',r'$E_{Iqbal}$',r'$E_{Confab}$',r'$E_{H&S}$',r'$E_{Iqbal}$',r'$E_{Confab}$',r'$E_{H&S}$']
	#ploty_pdf(Pn_input[:,:3],names)
	ploty_cdf(Pn_input[:,:6],names,BW=True,figname='blabla')
	plt.show()

	
	# fig=plt.figure()

	# plot1=create_plot_dictornary(x=np.sort(Pn_input[:,0]),y=np.arange(0,1,1/len(Pn_input[:,0])),label='prvi',color='blue',yscale='log')
	# plot2=create_plot_dictornary(x=np.sort(Pn_input[:,1]),y=np.arange(0,1,1/len(Pn_input[:,1])),label='drugi',color='red',yscale='log')
	# plot1c=create_plot_dictornary(x=np.sort(Pn_input[:,0]),y=1-np.arange(0,1,1/len(Pn_input[:,0])),color='blue',yscale='log')
	# plot2c=create_plot_dictornary(x=np.sort(Pn_input[:,1]),y=1-np.arange(0,1,1/len(Pn_input[:,1])),color='red',yscale='log')

	# oneplot(plot1,fig)
	# oneplot(plot2,fig)
	# oneplot(plot1c,fig)
	# oneplot(plot2c,fig)
	# plt.xlim((0,1.1*np.max(Pn_input[:,0])))

	# plt.draw()
	# plt.show()