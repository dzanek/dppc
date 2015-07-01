import sys
import numpy as np
import itertools
import numpy as np
import subprocess as sub
import matplotlib.pylab as pl
# take as input file with angle definitions, number of angles in first line, .gro for indexes of atom, xtc with trajectory



def mkNdx(ndx,fgro):
	#needs ndx-like file with name od dihedral and atom names
	#in whole gro finds indexes of such atoms 
	

	gro = [i for i in open(fgro,'r').readlines()[2:] if 'SOL' not in i]
	gro = [[i[9:15].strip(),i[15:22].strip()] for i in gro]
	thisNdx = [ndx.readline(),ndx.readline().split()]
	print gro	
	ndxs = []
	for i in thisNdx[1]:
		thisAtm = []
		for j in gro:
			if str(i) == str(j[0]):
				thisAtm.append(j[1])
		ndxs.append(thisAtm)
	readyNdx = [thisNdx[0]]
	for i in range(len(thisAtm)):
		readyNdx.append([ndxs[0][i],ndxs[1][i],ndxs[2][i],ndxs[3][i]])
	return readyNdx

def runGangle(fxtc,sndx,output):
	dirmk = 'mkdir '+output
	sub.call('rm -r '+output, shell=True)
	sub.call(dirmk.split())
	#runs subprocess of g_angle for certain
	for i in range(lipNo):
		print fxtc,sndx,output,output,i
		runCmd = 'g_angle -f %s -b 10000 -e 20000 -n %s.ndx -type dihedral -ov %s/%s_%s' %(fxtc,sndx,output,output,str(i))
		runner = sub.Popen(runCmd.split(), stdin=sub.PIPE)
		stdin_dat = runner.communicate(str(i))
		sub.call('rm \#*', shell=True)
	return 1

def mergeFiles(sndx):
	f1 = open('%s/%s_0.xvg' %(sndx,sndx),'r').readlines()
	f1 = [i.split() for i in f1 if i[0] not in '@#']
	f1 = zip(*f1)
	for i in range(lipNo)[1:]:
		fcont  = open('%s/%s_%i.xvg' %(sndx,sndx,i),'r').readlines()
		fcont = [i.split() for i in fcont if i[0] not in '@#']
		fcont = zip(*fcont)
		f1.append(fcont[1])

	valOnly = f1[1:]
	valOnly = list(itertools.chain(*valOnly))
	f1 = zip(*f1) #here 
	dump = open('%s_merged.xvg' %(sndx),'w')
	for i in f1:
		dump.write('\t'.join([str(k) for k in i])+'\n')
	dump.close()
	return [float(i) for i in valOnly]


def smoothData(data,window):
        data = list(data)
        smooth = []
        for i in range(len(data)):
                if np.isinf(data[i]) == True:
                        smooth.append(np.max([i for i in data if np.isinf(i) != True]))
                        continue
                if i < window/2:
                        smooth.append(np.mean([k for k in data[:i+(window/2)] if np.isinf(k) != True]))
                        continue
                else:
                        smooth.append(np.mean([k for k in data[i-window/2:i+window/2] if np.isinf(k) != True]))
                        continue
        return smooth

def mkHistogram(data,sndx):
	print type(data[2])
	histDat = pl.hist(data,360,normed=1,color='black',histtype='step',label='Angle %s' %(sndx))
	pl.legend()
	pl.xlim(-180,180)
	pl.xlabel('Angle [deg.]',fontsize=16)
	pl.ylabel('Probability density',fontsize=16)
	pl.xticks(fontsize=12)
	pl.yticks(fontsize=12)
	pl.savefig('%s_hist.pdf' %(sndx))
	pl.cla()
	return histDat # sp.histogram(data,360)

def mkProfile(hvals,sndx):
	xval = hvals[1][:-1]
	yval = hvals[0]
	yval = [-0.0019*float(300)*np.log(i) for i in yval]
	minVal = float(min(yval))
	yval = [i-minVal for i in yval]
	yvalS = smoothData(yval,10)
	pl.plot(xval,yval,'.',color='black',label='Calculated %s' %(sndx))
	pl.plot(xval,yvalS,'-',color='black',label='Smooth %s' %(sndx))
	pl.legend()
	pl.xlim(-180,180)
	pl.ylim(0,6)
        pl.xlabel('Angle [deg.]',fontsize=16)
        pl.ylabel('Energy [kcal/mol/deg2',fontsize=16)
	pl.xticks(fontsize=12)
        pl.yticks(fontsize=12)
        pl.savefig('%s_prof.pdf' %(sndx))
        pl.cla()



if __name__ == '__main__':
	fndx = sys.argv[1]
	fgro = sys.argv[2]
	fxtc = sys.argv[3]
	ndx = open(fndx,'r')
	dihNo = int(ndx.readline())
	dihNames = []
	for i in range(dihNo):
		data = mkNdx(ndx,fgro)
		lipNo = len(data[1:])
		dihNames.append(data[0])
		print data
		dump = open('%s.ndx' %(data[0][:-1]),'w')
		for k in data[1:]:
			dump.write('[ '+data[0][:-1]+' ]\n')
			dump.write(' '+' '.join([str(v) for v in k])+'\n')
			dump.flush()
	print lipNo
	print dihNames
#now You got ndx files for each of dih (stored in dihNames)
	for sndx in dihNames:
		sndx = sndx[:-1]
		runGangle(fxtc,sndx,sndx)
		vals = mergeFiles(sndx)
		hvals = mkHistogram(vals,sndx)
		mkProfile(hvals,sndx)
#	plot()

	
