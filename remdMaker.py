import sys
import subprocess as s
import os
import numpy

def genSystem(conf,topol,mdpInit,equilInput,initTemp=300,finalTemp=1000,interval=8):	
	"""
	generates exponential temperatures, generate set of directories, generate mdp filese and prints smiling face of joy
	"""
#calculate temperatures
	tempSpace = finalTemp - initTemp

	temps = [initTemp]
	for i in range(1,interval+1):
#		addit = ((i+1)*(1./interval))**(2)
#		temps.append(initTemp + (tempSpace)*addit)
		temps.append(temps[-1]+tempSpace/interval)
	temps = [300.00, 367.62, 434.04, 510.62, 598.98, 699.98, 815.98, 1005.98]		# it is a better idea to use generated temperatures instead - just paste here
	temps = [300.00, 305.65, 311.37, 317.17, 323.11, 329.07, 335.10, 341.22, 347.43, 353.71, 360.08, 366.53, 373.07, 379.70, 386.42, 393.27, 400.19, 408.19, 415.31, 422.52, 429.82, 437.21, 444.72, 452.34]
	print 'Temperatures are: ',temps
	#make directories
	#populate dirs with configuration, topology and changed mdp files
	
	for i in temps:
		tempDir = str(temps.index(i))
		s.call('rm %s/*' %(tempDir),shell=True)
		if not os.path.exists('%s' %(tempDir)): os.makedirs('%s' %(tempDir))
		s.call('cp %s %s/%s' %(conf,tempDir,conf), shell=True)	
		for k in topol:
			s.call('cp %s %s/%s' %(k,tempDir,k),shell=True)
		mdFiles = [mdpInit,equilInput]
		for mdFile in mdFiles:
			thisFile = open(mdFile,'r').readlines()
			mdFileNew = [';;mdp file for %f temperature\n' %(i)]
			for line in thisFile:
				if 'ref_t' in line or 'ref-t' in line:
					mdFileNew.append('ref_t               =  %f\n' %(i))
				elif 'gen_temp' in line:
					mdFileNew.append('gen_temp               =  %f\n' %(i))

				elif 'ref_t' not in line and 'ref-t' not in line and 'gen_temp' not in line:
					mdFileNew.append(line)
			dumpFile = open('%s/%s' %(tempDir,mdFile),'a')
			for line in mdFileNew:
				dumpFile.write(line)
			dumpFile.close()

	return [str(i)[:3] for i in temps]
		


def replicaPrep(conf,topol,mdpInit,equilInput,temps):
	"""
	equilibrates each repllica
	"""

#grompps each eq
	for i in temps:
                tempDir = str(temps.index(i))
		s.call('grompp -f %s/%s -c %s/%s -p %s/%s -maxwarn 10 -o %s/equil%s' %(tempDir,equilInput,tempDir,conf,tempDir,topol[0],tempDir,tempDir),shell=True)
#mdruns each eq
		s.call('mdrun -v -deffnm %s/equil%s' %(tempDir,tempDir),shell=True)	

def replicaRunner(conf,topol,mdpInit,temps,interval=8,replex=500):
#grompps each md
        for i in temps:
                tempDir = str(temps.index(i))

		s.call('grompp -f %s/%s -c %s/equil%s -p %s/%s -maxwarn 10 -o replica_%s' %(tempDir,mdpInit,tempDir,tempDir,tempDir,topol[0],tempDir),shell=True)

	"""
	runs replica simulation, mdrun -s prefix_.tpr -multi $numberOfReplicas -replex $stepsOfChanges50ps output options
	"""
	s.call('mpirun -np %i mdrun_mpi -s replica_.tpr -multi %i -replex %i' %(interval,interval,replex),shell=True)   #crucial part - runs REMD simulation

def analize():
	"""
	takes data from output
	"""
#for future work should include histo and profile maker here

########################## a c t u a l   r u  n n i n g   p a r t  ################################

if __name__ == '__main__':
	topol = []
	confID = sys.argv.index('-c')
	topID = sys.argv.index('-t')
	mdID = sys.argv.index('-md')
	eqID = sys.argv.index('-eq')
	for i in sys.argv:
		if sys.argv.index(i) == confID+1: conf = i
		elif sys.argv.index(i) > topID and sys.argv.index(i) < mdID: topol.append(i)
		elif sys.argv.index(i) == mdID+1: md = i
		elif sys.argv.index(i) == eqID+1: eq = i
	temps = genSystem(conf,topol,md,eq)
	replicaPrep(conf,topol,md,eq,temps)
	replicaRunner(conf,topol,md,temps)
