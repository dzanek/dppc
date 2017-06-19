import sys
import subprocess as s

class Trajectory:
    ''' '''


    def _to_gro(self):
        ''' '''
        new_name = '.'.join(self.fname.split('.')[:-1])+'.gro'
        s.call('obabel -i {} {} -o gro -O {}'.format(self.extension, self.fname, new_name), shell=True)
        return new_name

    def __init__(self, f_traj):
        ''' '''
        self.fname = f_traj
        self.extension = f_traj.split(',')[-1]
        if not self.extension == 'gro':
            self.fname = self._to_gro()


    def count_molecules(self):
        ''' '''
        with open(self.fname) as fcont:
            self.molecules = {}
            for line in fcont:
                if line[0] != ' ' and len(self.molecules) != 0:
                    continue
                if line[0] != ' ':
                    break
                else:
                    line = line.split()
                    try:
                        self.molecules[line[0]].append(line[2])
                    except KeyError:
                        self.molecules[line[0]] = [line[2]]


    def build_matrix(self):
        ''' '''
        for mol1 in self.molecules:
            self._write_index(mol1)
            for mol2 in self.molecules:
                self._write_index(mol2)
                self._run_g_dist(mol1,mol2)




def main(f_traj, min_neighbour):
    ''' '''
    traj = Trajectory(f_traj)
    traj.count_molecules()
    traj.build_matrix()
    traj.get_surrounded()

if __name__ == '__main__':
    ''' '''
    f_traj = sys.argv[1]
    min_neighbour = int(sys.argv[2])
    main(f_traj, min_neighbour)
