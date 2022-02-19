<h1> dat2afl <h1>

This file uses xfoil to generate polar files from given airfoil coordinates (.dat), scrapes Cl, Cd and Cm values 
from polar file and dumps them to .afl file in order. A series of afl files are generated based on range of Reynolds
Number provided.

1. Install python 3.*
2. Rename your .dat file (containing airfoil coordinates) as "coordinates.dat".
3. Paste here and replace existing "coordinates.dat" file.
4. run RunMe.bat
5. Specify prompted parameters
6. your afl files of specified Reynolds number range will be stored in "afl_files" folder
7. copy these afl files to some other directory else it will get deleted next time you run code.
        
Note* Donot give very low Re step or absurd values of alpha and Re or you will get stuck forever.
