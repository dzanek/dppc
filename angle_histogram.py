''' Tool for generating histograms of torsion dihedral distribution
Input:
 - xyz file to be converted to gro
 - gro/pdb/xtc file to be used directly in g_angle of gromacs

 - meta_ndx file to contain information about which angle to calculate
  this file should look line:
  [ name_of_angle ]
   1 2 3 4

  where 1, 2, 3 and 4 are numbers of atoms in FIRST molecule

 it will iterate creating new index file for every molecule
 and creating new res.xvg file for each molecule

 end of iteration will merge all molecules for selected angle and trajectory

 will produce histogram in text and png format
'''
import os
import sys
import shutil
import numpy as np
import matplotlib.pyplot as pl
import subprocess as s


class TrajFile:
    ''' '''
    def __init__(self, fname):
        ''' '''
        self.fname = fname
        self.extension = self.fname.split('.')[-1]
        self.fname_base = '.'.join(self.fname.split('.')[:-1])
        if os.path.exists('./{}'.format(self.fname_base)):
            shutil.rmtree(self.fname_base)
        os.makedirs(self.fname_base)

    def __str__(self):
        ''' '''
        return self.fname



    def to_gro(self):
        ''' '''
        self.gro_fname = self.fname_base+'.gro'
        print 'Will convert.'
        print 'obabel -i {} {} -o gro -O {}/{}'.format(self.extension, \
                                                     self.fname, \
                                                     self.fname_base, \
                                                     self.gro_fname)
        s.call('obabel -i {} {} -o gro -O {}/{}'.format(self.extension, \
                                                    self.fname, \
                                                     self.fname_base, \
                                                     self.gro_fname), \
                                                     shell=True)


    def get_mol_count(self):
        ''' '''
        mol_ids = []
        with open('{}/{}'.format(self.fname_base,self.gro_fname)) as fcont:
             for line in fcont:
                 ''' will iterate until first frame ends '''
                 if len(mol_ids) == 0 and line[0] != ' ':
                     continue
                 if line[0] != ' ':
                     break
                 else:
                     mol_ids.append(line.split()[0])

        return len(set(mol_ids)), mol_ids.count(mol_ids[0])

class Index:
    ''' builds indexes '''
    def __init__(self, fname, mol_size, fname_base):
        ''' '''
        self.fname_base = fname_base
        self.fname = fname
        self.mol_size = mol_size
        fcont = open(self.fname)
        self.id = fcont.readline()
        self.atoms = [int(i) for i in fcont.readline().split()]

    def build_index(self, mol_no):
        ''' '''
        self.new_atoms = [i+(mol_no*self.mol_size) for i in self.atoms]
        with open('{}/tmp.ndx'.format(self.fname_base),'w') as dump:
            dump.write(self.id)
            dump.write(' {} {} {} {}\n'.format(*self.new_atoms))


class Gangle:
    ''' '''
    def __init__(self, traj, mol_no):
        ''' '''
        self.fname_base = traj.fname_base
        self.gro_fname = traj.gro_fname
        self.mol_no = mol_no

    def run(self):
        s.call('gmx angle -f {}/{} -n {}/tmp.ndx -type dihedral -ov {}/res{}.xvg'.format(self.fname_base, \
                                                                                    self.gro_fname, \
                                                                                    self.fname_base,
                                                                                    self.fname_base,\
                                                                                    self.mol_no), \
                                                                                    shell=True)
        os.remove('angdist.xvg')
class Results:
    ''' '''
    def __init__(self, fname_base):
        ''' '''
        self.fname_base = fname_base

    def load_angles(self):
        ''' '''
        self.angle_vals = []
        res_list = ['{}/{}'.format(self.fname_base,i) for i in os.listdir(self.fname_base) if 'xvg' in i]
        for res_file in res_list:
            with open(res_file) as fcont:
                for lin in fcont:
                    if lin[0] in ['#','@']:
                        continue
                    else:
                        self.angle_vals.append(float(lin.split()[1]))
    def get_histogram(self, interval, angle_id):
        ''' '''
        pl.style.use('ggplot')
        pl.style.use('seaborn-poster')
        pl.rcParams['figure.figsize'] = 16,9
        yx = pl.hist(self.angle_vals, bins=np.linspace(-180,180,int(interval)), histtype='step', label=angle_id.split()[1])
        y, x = yx[0], yx[1]
        pl.xlim(-180,180)
        pl.xticks([-180,-90,0,90,180])
        ''' here is a part of visual side of histogram - tweak it '''
        pl.xlabel('Dihedral angle value [deg.]')
        pl.ylabel('Counts')
        pl.title('Histogram of angle distribution in simulation')
        pl.savefig('{}/{}.png'.format(self.fname_base,angle_id.split()[1]))

        with open('{}/{}.hist'.format(self.fname_base,angle_id.split()[1]),'w') as dump:
            dump.write('# histogram values for {}\n'.format(angle_id))
            for i in zip(x[:-1],y):
                dump.write('{}\t{}\n'.format(i[0],i[1]))

def main(trajectory_file, metaindex_file, interval):
    ''' runs stuff around :)
    takes trajectory_file_name as first argument
    takes metaindex_file_name as second argument'''
    traj = TrajFile(trajectory_file)
    traj.to_gro()

    mol_number, mol_size = traj.get_mol_count()
    for molecule in range(mol_number):
        ndx = Index(metaindex_file, mol_size, traj.fname_base)
        ndx.build_index(molecule)
        gangle = Gangle(traj, molecule)
        gangle.run()

    res = Results(traj.fname_base)
    res.load_angles()
    res.get_histogram(interval, ndx.id)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
