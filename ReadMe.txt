dat2afl

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
