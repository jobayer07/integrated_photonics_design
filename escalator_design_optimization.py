from __future__ import division
import numpy
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import imp
import os
import numpy as np
#importlibutil

import random
import math

micron=1e-6

lumapi=imp.load_source("lumapi", "C:\\Program Files\\Lumerical\\v212\\api\\python\\lumapi.py")
base_file = "escalator_base_optimize_fdtd_file.fsp"
        
#--- COST FUNCTION ------------------------------------------------------------+

if os.path.exists(base_file):
    print('exists')

# function we are attempting to optimize (minimize)
def func1(x):
    if os.path.exists(base_file):
        with lumapi.FDTD(filename=base_file) as fdtd: #hide='TRUE'
            fdtd.switchtolayout()
            
            PN=fdtd.select("PN")
            V1=fdtd.get("vertices")
            V1[0, 0]=x[0]*micron
            V1[1, 0]=x[0]*micron
            V1[0, 1]=-micron*x[1]/2
            V1[1, 1]=micron*x[1]/2
            fdtd.set("vertices", V1)
            VN1=fdtd.get("vertices")
            
            SN=fdtd.select("SN")
            V2=fdtd.get("vertices")
            V2[2, 0]=x[2]*micron
            V2[3, 0]=x[2]*micron
            V2[2, 1]=micron*x[3]/2
            V2[3, 1]=-micron*x[3]/2
            fdtd.set("vertices", V2)
            VN2=fdtd.get("vertices")
            print('PN right-top:', VN1[1, :]/micron, ', SN left-bottom:', VN2[2, :]/micron)
            
            #fdtd.save()    #saves file
            fdtd.run()
            
            port2=fdtd.getresult("FDTD::ports::port 2", "T")
            #lam=port2['lambda']
            T=port2['T']
            print('T:', T)
    else:
        print("base file doesn't exist...")
    return -T

#--- MAIN ---------------------------------------------------------------------+

class Particle:
    def __init__(self,x0):
        self.position_i=[]          # particle position
        self.velocity_i=[]          # particle velocity
        self.pos_best_i=[]          # best position individual
        self.err_best_i=-1          # best error individual
        self.err_i=-1               # error individual

        for i in range(0,num_dimensions):
            self.velocity_i.append(random.uniform(-1,1)) #up to 4 decimal place
            self.position_i.append(x0[i])

    # evaluate current fitness
    def evaluate(self,costFunc):
        self.err_i=costFunc(self.position_i)

        # check to see if the current position is an individual best
        if self.err_i < self.err_best_i or self.err_best_i==-1:
            self.pos_best_i=self.position_i
            self.err_best_i=self.err_i

    # update new particle velocity
    def update_velocity(self,pos_best_g):
        w=0.5       # constant inertia weight (how much to weigh the previous velocity)
        c1=1        # cognative constant
        c2=2        # social constant

        for i in range(0,num_dimensions):
            r1=random.random()
            r2=random.random()

            vel_cognitive=c1*r1*(self.pos_best_i[i]-self.position_i[i])
            vel_social=c2*r2*(pos_best_g[i]-self.position_i[i])
            self.velocity_i[i]=w*self.velocity_i[i]+vel_cognitive+vel_social

    # update the particle position based off new velocity updates
    def update_position(self,bounds):
        for i in range(0,num_dimensions):
            self.position_i[i]=self.position_i[i]+self.velocity_i[i]

            # adjust maximum position if necessary
            if self.position_i[i]>bounds[i][1]:
                self.position_i[i]=bounds[i][1]

            # adjust minimum position if neseccary
            if self.position_i[i] < bounds[i][0]:
                self.position_i[i]=bounds[i][0]
                
class PSO():
    def __init__(self,costFunc,x0,bounds,num_particles,maxiter):
        global num_dimensions

        num_dimensions=len(x0)
        err_best_g=-1                   # best error for group
        pos_best_g=[]                   # best position for group

        # establish the swarm
        swarm=[]
        for i in range(0,num_particles):
            swarm.append(Particle(x0))

        # begin optimization loop
        i=0
        while i < maxiter:
            #print i,err_best_g
            # cycle through particles in swarm and evaluate fitness
            for j in range(0,num_particles):
                print ('Swarm=', i, ', Particle=', j)
                swarm[j].evaluate(costFunc)

                # determine if current particle is the best (globally)
                if swarm[j].err_i < err_best_g or err_best_g == -1:
                    pos_best_g=list(swarm[j].position_i)
                    err_best_g=float(swarm[j].err_i)

            # cycle through swarm and update velocities and position
            for j in range(0,num_particles):
                swarm[j].update_velocity(pos_best_g)
                swarm[j].update_position(bounds)
            i+=1

        # print final results
        print ('FINAL:')
        print (pos_best_g)
        print (err_best_g)
        

#--- RUN ----------------------------------------------------------------------+
initial=[33, 0.1, -33, 0.628]               # initial starting location [x1,x2...]
bounds=[(-20, 33), (0.1, 0.8), (-33, 20), (0.1,1.2)]  # input bounds [(x1_min,x1_max),(x2_min,x2_max)...]
PSO(func1,initial,bounds,num_particles=40,maxiter=20)


