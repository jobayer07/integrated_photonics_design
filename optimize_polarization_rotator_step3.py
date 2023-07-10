from __future__ import division
import numpy
import matplotlib.cm as cm
import matplotlib.pyplot as plt
#import imp
import os,sys
import numpy as np
#importlibutil

#from scipy.optimize import minimize
from scipy.optimize import basinhopping

import random
import math

micron=1e-6
sys.path.append("/opt/lumerical/v212/api/python")
import lumapi
#lumapi=imp.load_source("lumapi", "C:\\Program Files\\Lumerical\\v212\\api\\python\\lumapi.py")
base_file = "base_rotator.fsp"
        
#--- COST FUNCTION ------------------------------------------------------------+

# function we are attempting to optimize (minimize)
def func1(x):
    if os.path.exists(base_file):
        with lumapi.FDTD(filename=base_file, hide='TRUE') as fdtd: #hide='TRUE'
            x1=x[0]*micron
            w1=x[1]*micron
            w2=x[2]*micron

            print('x1:', x[0], ', w1:', x[1], ', w2:', x[2])
            fdtd.switchtolayout()
            
            fdtd.select("Left_of_Top")
            Vlt=fdtd.get("vertices")
            Vlt[0, 1] = -w1/2
            Vlt[1, 1] = w1/2
            Vlt[2, 0]=x1
            Vlt[3, 0]=x1
            fdtd.set("vertices", Vlt)

            fdtd.select("Top_left_stabilize")
            Vtls=fdtd.get("vertices")
            Vtls[0, 1] = -w1/2
            Vtls[1, 1] = w1/2
            Vtls[2, 1]= w1/2
            Vtls[3, 1]= -w1/2
            fdtd.set("vertices", Vtls)

            fdtd.select("Top")
            Vt=fdtd.get("vertices")
            Vt[2, 1]= w1/2
            Vt[3, 1]= -w1/2
            fdtd.set("vertices", Vt)

            #--------------Bottom--------------------
            
            fdtd.select("Left_of_Bottom")
            Vlb=fdtd.get("vertices")
            Vlb[0, 1] = -w2/2
            Vlb[1, 1] = w2/2
            fdtd.set("vertices", Vlb)

            fdtd.select("Bottom_left_stabilize")
            Vbls=fdtd.get("vertices")
            Vbls[0, 1] = -w2/2
            Vbls[1, 1] = w2/2
            Vbls[2, 1]= w2/2
            Vbls[3, 1]= -w2/2
            fdtd.set("vertices", Vbls)

            fdtd.select("Bottom")
            Vb=fdtd.get("vertices")
            Vb[2, 1]= w2/2
            Vb[3, 1]= -w2/2
            fdtd.set("vertices", Vb)
            
            fdtd.save()
            fdtd.run()
            
            bot_monitor=fdtd.getresult("monitor_bottom", "E")
            E_abs=abs(bot_monitor["E"])
            P=E_abs**2
            
            i1,i2,i3,i4,i5=np.shape(P)
            
            line_pow=P[i1-5, :, 0, 0, 1] #P[xindex, yindex all, 0, 0, Y polarization]
            p_target=np.max(line_pow)
            print('P_TE:', p_target)
    else:
        print("base file doesn't exist...")
    return -p_target


#--- RUN ----------------------------------------------------------------------+
#initial=[-139.5, 1.86, 0.8]               # initial starting location [x1,x2...]
bounds=[(-145, -135), (1.65, 2.2), (0.65, 1.2)]  # input bounds [(x1_min,x1_max),(x2_min,x2_max)...]
#minimize(fun=func1, x0=initial, method='L-BFGS-B', bounds=bounds, options={'eps': 1, 'maxiter': 5})
#basinhopping(func=func1, x0=initial, niter=5, T=1.0, stepsize=0.5, minimizer_kwargs={'method': 'L-BFGS-B', 'bounds': bounds}, take_step=None, accept_test=None, callback=None, interval=50, disp=False, niter_success=None, seed=None, target_accept_rate=0.5, stepwise_factor=0.9)

initial_optimized=[-139.55, 1.8, 0.66]
res=func1(initial_optimized) #18.9%
print(res)