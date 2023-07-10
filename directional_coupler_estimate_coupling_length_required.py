import numpy as np
import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import imp
import os
#importlibutil

#-------------------functions------------

def calcLc(Pcoupled_in_percentage,deltan,wavelength):
    Lc = (wavelength/(np.pi*deltan))*np.arcsin(np.sqrt(Pcoupled_in_percentage))
    return(Lc)

#--------------------Main code starts------------

wavelength_center = 1.3e-6
gap_width='200nmGap_310nmWide'
lumapi=imp.load_source("lumapi", "C:\\Program Files\\Lumerical\\v212\\api\\python\\lumapi.py")
#os.add_dll_directory("C:\\Program Files\\Lumerical\\v212\\api\\python")

lmd = lumapi.MODE('wg_coupling_sims_Si_'+str(gap_width)+'.lms')
#mode.addvarfdtd()

lmd.select("FDE")
lmd.set("wavelength",wavelength_center)
lmd.select("FineMesh")
lmd.set("z span",0.4e-6)

lmd.run()
lmd.findmodes()

mode1 = "mode1"
mode2 = "mode2"

# Get neff for the required modes
neff1_c  = lmd.getresult(mode1,"neff"); neff1 = np.real(neff1_c[0,0]);
neff2_c  = lmd.getresult(mode2,"neff"); neff2 = np.real(neff2_c[0,0]);


df = pd.DataFrame(columns=['neff1','neff2','deltan','Lc1', 'Lc10', 'Lc50','Lc90','Lc99', 'Lc100'])
# Calculate coupling length needed for 100%, 50%, 90%, 1% power
deltan = neff1 - neff2
P1=0.01; P10=0.1; P50=0.5; P90=0.9; P99=0.99; P100 = 1;
Lc1 = calcLc(P1,deltan,wavelength_center)
Lc10 = calcLc(P10,deltan,wavelength_center)
Lc50 = calcLc(P50,deltan,wavelength_center)
Lc90 = calcLc(P90,deltan,wavelength_center)
Lc99 = calcLc(P99,deltan,wavelength_center)
Lc100 = calcLc(P100,deltan,wavelength_center)

df.loc[0] = [neff1,neff2,deltan,Lc1,Lc10,Lc50,Lc90,Lc99,Lc100]
df.to_csv(str(wavelength_center*1e9)+'nm_wavelength_'+str(gap_width)+'.csv', index=False)