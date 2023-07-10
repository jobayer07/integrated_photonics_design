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
            xmax=x[0]*micron
            ymin_bot=x[1]*micron
            w_bot=x[2]*micron
            
            ymin_top=-x[3]*micron
            ymax_top=x[3]*micron
            
            print('xmax:', x[0], ', ymin_bot:', x[1], ', w_bot:', x[2], ', ymin_top:', -x[3])
            fdtd.switchtolayout()
            
            fdtd.select("Bottom")
            Vbot=fdtd.get("vertices")
            Vbot[0, 0]=xmax
            Vbot[0, 1]=ymin_bot
            Vbot[1, 0]=xmax
            Vbot[1, 1]=ymin_bot+w_bot
            fdtd.set("vertices", Vbot)
            
            fdtd.select("Top")
            Vtop=fdtd.get("vertices")
            Vtop[0, 0]=xmax
            Vtop[0, 1]=ymin_top
            Vtop[1, 0]=xmax
            Vtop[1, 1]=ymax_top
            fdtd.set("vertices", Vtop)
            
            fdtd.select("FDTD")
            fdtd.set("x max", xmax-0.5e-6)

            fdtd.select("DFTmonitor_output")
            fdtd.set("x", xmax-0.6e-6)
            fdtd.set("y min", ymin_bot-0.2e-6)
            fdtd.set("y max", ymin_bot+w_bot+0.2e-6)
            
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
initial=[50.39, 0.91, 0.65, 0.73]               # initial starting location [x1,x2...]
bounds=[(45, 55), (0.8, 1), (0.55, 0.75), (0.6,0.9)]  # input bounds [(x1_min,x1_max),(x2_min,x2_max)...]
res=basinhopping(func=func1, x0=initial, niter=5, T=1.0, stepsize=0.5, minimizer_kwargs={'method': 'L-BFGS-B', 'bounds': bounds}, take_step=None, accept_test=None, callback=None, interval=50, disp=False, niter_success=3, seed=None, target_accept_rate=0.5, stepwise_factor=0.9)
#minimize(fun=func1, x0=initial, method='L-BFGS-B', bounds=bounds, options={'eps': 1e-01, 'maxiter': 5})
#initial_optimized=[50.39, 0.91, 0.65, 0.73]
#res=func1(initial_optimized) #18.9%
print(res)

