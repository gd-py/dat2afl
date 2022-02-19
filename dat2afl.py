import os, shutil
import subprocess
import numpy as np

def generate_polar_files(dat_file_name, alpha_i, alpha_f, alpha_step, Re, n_iter, sep=None, alpha_br=False): 
    if alpha_br:
        polar_file = rf"polar_files\polar_file_{Re}_{sep}.txt"
        input_file_name = f"input_file_{Re}_{sep}.in"
    else:
        polar_file = rf"polar_files\polar_file_{Re}.txt"
        input_file_name = f"input_file_{Re}.in"

    if os.path.exists(polar_file):
        os.remove(polar_file)

    with open(input_file_name, 'w') as input_file:
        input_file.write(f"LOAD {dat_file_name}\n")
        input_file.write("PANE\n")
        input_file.write("OPER\n")
        input_file.write(f"Visc {Re}\n")
        input_file.write("PACC\n")
        input_file.write(f"{polar_file}\n\n")
        input_file.write(f"ITER {n_iter}\n")
        input_file.write(f"ASeq {alpha_i} {alpha_f} {alpha_step}\n")
        input_file.write("\n\n")
        input_file.write("quit\n")

    subprocess.call(f"xfoil.exe < {input_file_name}", shell=True)
    os.remove(input_file_name)

def combine_polars(Re):
    with open(f'polar_files/polar_file_{Re}_0.txt', 'r') as fh:
        polar_1 = fh.readlines()
    with open(f'polar_files/polar_file_{Re}_1.txt', 'r') as fh:
        polar_2 = fh.readlines()
    contents_to_write = polar_1[:12] + polar_1[12:][::-1] + polar_2[13:]
    with open(f'polar_files/polar_file_{Re}.txt', 'w') as fh:
        for i in contents_to_write:
            fh.write(i)
    os.remove(f'polar_files/polar_file_{Re}_0.txt')
    os.remove(f'polar_files/polar_file_{Re}_1.txt')

def generate_afl_coordinates(dat_file_name):
    a = np.loadtxt(dat_file_name, skiprows=1)
    x_mul = 1
    x_shift = -0.25
    y_mul = 1
    y_shift = 0

    a[:,0], a[:,1] = a[:, 0]*x_mul+x_shift, a[:, 1]*y_mul+y_shift
    x_choices = [-0.25, -0.22, -0.15, 0, 0.2, 0.5, 0.75]
    results_list = []
    for s in range(2):
        result = {}
        for i in x_choices:
            _temp = 5
            result[i] = 0
            for j, k in a:
                if abs(j-i) < _temp and (k)*((-1)**s)>=0:
                    _temp = abs(j-i)
                    result[i] = (j, k)
        results_list.append(list(result.values()))
    final_coordinates = results_list[0]+results_list[1][::-1]
    return(np.array(final_coordinates), x_mul, y_mul)

def generate_afl_file(dat_file_name, ref_afl_file, polar_file, output_afl_file, Re, n_alpha=None, log_file=None):
    with open(ref_afl_file, 'r') as rf:
        lines = rf.readlines()

    with open(output_afl_file, 'w') as wf:
        wf.write('I $!Generated dynamically with dat2afl.py!\n')
        for i in lines[1:3]:
            wf.write(i)

    afl_coordinates, x_mul, y_mul = generate_afl_coordinates(dat_file_name)
    with open(output_afl_file, 'a') as fh:
        fh.write(f'{x_mul}\n{y_mul}\n')
    
    with open(output_afl_file, 'ab') as fh:
        np.savetxt(fh, afl_coordinates, fmt='%.4f')

    with open(output_afl_file, 'a') as fh:
        for i in lines[19:22]:
            fh.write(i)
    
    ref_data = np.loadtxt(ref_afl_file, skiprows=22, dtype=np.float)
    polar_data = np.loadtxt(polar_file, skiprows=12, usecols=(0,1,2,4), dtype=np.float)

    # logs
    if not polar_data.any():
        if log_file:
            log_file.write('ERROR!!! Empty polar file!\n')
            log_file.write('Continuing without writing afl file!\n')
        return 0
    
    m, n = np.shape(polar_data)
    i_0,  = np.where(np.isclose(ref_data[:,0], polar_data[0,0]))
    i_0, j_0 = int(i_0), 0
    i_n, j_n = i_0 + m, j_0 + n

    # logs
    if log_file and n_alpha:
        if m == n_alpha:
            log_file.write('Successfully written polar file for all values of alpha within specified range.\n')
            log_file.write('Successfully generated afl file for all values of alpha.\n')
        else:
            log_file.write('WARNING!!!\n')
            log_file.write("Couldn't converge for some values of alpha and they are left out.\n")
            log_file.write(f'Polar file written for this range: alpha=[{polar_data[0,0]}, {polar_data[m-1,0]}]\n')
            log_file.write('Also afl file will be generated only for this range of alpha.\n')

    afl_final = np.zeros(ref_data.shape)
    afl_final[i_0:i_n, j_0:j_n] = polar_data

    with open(output_afl_file, 'ab') as fh:
        np.savetxt(fh, afl_final, fmt='%.4f')

def main():
    with open('ReadMe.txt', 'w') as fh:
        fh.write(
'''<h1> dat2afl <h1>

This file uses xfoil to generate polar files from given airfoil coordinates (.dat), scrapes Cl, Cd and Cm values 
from polar file and dumps them to .afl file in order. A series of afl files are generated based on range of Reynolds
Number provided.

> Install python 3.*
> Rename your .dat file (containing airfoil coordinates) as "coordinates.dat".
> Paste here and replace existing "coordinates.dat" file.
> run RunMe.bat
> Specify prompted parameters
> your afl files of specified Reynolds number range will be stored in "afl_files" folder
> copy these afl files to some other directory else it will get deleted next time you run code.
        
Note* Donot give very low Re step or absurd values of alpha and Re or you will get stuck forever.
''')
    with open('requirements.txt', 'w') as fh:
        fh.write('numpy == 1.19.4')

    if not os.path.isdir('polar_files'):
        os.mkdir('polar_files')
    else:
        shutil.rmtree('polar_files')
        os.mkdir('polar_files')

    if not os.path.isdir('afl_files'):
        os.mkdir('afl_files')
    else:
        shutil.rmtree('afl_files')
        os.mkdir('afl_files')

    dat_file_name = 'coordinates.dat'
    with open(dat_file_name, 'r') as file:
        file_contents = file.read()

    log_file = open('logs.txt', 'w')

    airfoil_name = file_contents.split('\n', 1)[0].strip()
    while True:
        alpha_i = input("Enter initial value of alpha (should be integer and in range(-20, 20)!): ")
        alpha_f = input("Enter final value of alpha (should be integer and in range(-20, 20)!): ")
        alpha_step = 0.1
        Re_i = input("Enter starting Re (should be integer!): ")
        Re_f = input("Enter final Re (should be integer!): ")
        Re_step = input("Enter Re step (should be integer!): ")
        n_iter = 100
        try:
            alpha_i = int(alpha_i)
            alpha_f = int(alpha_f)
            alpha_step = float(alpha_step)
            Re_i = int(Re_i)
            Re_f = int(Re_f)
            Re_step = int(Re_step)
            break
        except:
            print("\nInput data type error!!")
            input("Press any key to continue!")
            print('\n')
    
    n_alpha = int((alpha_f - alpha_i)/alpha_step)

    # logs
    log_file.write(f'Generated for airfoil: {airfoil_name}\n\n')
    log_file.write('Input data:\n')
    log_file.write(f'alpha range: [{alpha_i}, {alpha_f}]\n')
    log_file.write(f'alpha step: {alpha_step}\n')
    log_file.write(f'Reynolds Number range: [{Re_i}, {Re_f}]\n')
    log_file.write(f'Reynolds Number step: {Re_step}\n')
    log_file.write(f'Used total iteration value: {n_iter}\n')
    log_file.write('Used Ncrit value: 9\n\n')

    sep = 1
    alpha_br = False
    if alpha_i*alpha_f < 0:
        alpha_f = [alpha_i, alpha_f]
        alpha_i = [0, 0]
        sep = 2
        alpha_br = True
        log_file.write('INFO!! Found negative to positive alpha transition!\n')
        log_file.write(f'Alpha range is re-arranged as [0, {alpha_f[0]}] and [0, {alpha_f[1]}] for better convergence.\n\n')
    else: 
        alpha_i = [alpha_i]
        alpha_f = [alpha_f]

    for Re in range(Re_i, Re_f+1, Re_step):
        # logs
        log_file.write('*'*100)
        log_file.write('\n')

        for i in range(sep):
            generate_polar_files(dat_file_name, alpha_i[i], alpha_f[i], alpha_step, Re, n_iter, sep=i, alpha_br=alpha_br)
        
        if alpha_br:
            combine_polars(Re)
        ref_afl_file = 'ref_afl_file.afl'
        polar_file = f'polar_files/polar_file_{Re}.txt'
        output_afl_file = f'afl_files/afl_file_{Re}.afl'

        # logs
        log_file.write(f'Logs for Re={Re}\n')
        log_file.write(f'polar file name: {polar_file}\n')
        log_file.write(f'output afl file name: {output_afl_file}\n')

        generate_afl_file(dat_file_name, ref_afl_file, polar_file, output_afl_file, Re, n_alpha=n_alpha, log_file=log_file)
        Re = Re + 100000
        log_file.write('\n')
    log_file.close()
    print("\n\n\n\nPlease check log-file for details: logs.txt")
    input('Enter any key to exit!')

if __name__ == '__main__':
    main()
