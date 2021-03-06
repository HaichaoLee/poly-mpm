import os
from numpy import pi,array,dot,tan,zeros,eye,cumsum,outer,sum,trace,exp,linspace
from numpy import random,ones
import matplotlib.pyplot as plt

class Params():
    def __init__(self,mode):
        self.dt = 1e-2 # timestep (s)
        self.t = 0. # physical time (s)
        self.tstep = 0
        self.savetime = .1
        self.t_f = self.dt#0.5 # final time (s)
        self.nt = int(self.t_f/self.dt) # number of timesteps
        self.save = 0 # save counter
        self.M_tol = 1e-10 # very small mass (kg)
        self.max_g = 0. # gravity (ms^-2)
        self.max_q = 1.
        self.theta = 0.*pi/180. # slope angle (degrees)
        self.update_forces()
        self.G = Grid_Params()
        self.B = Boundary_Params()
        self.S = Solid_Params(self.G)
        self.O = Output_Params(self.nt,self.S.n)
        self.check_positions = False
        self.has_yielded = False
        self.damping = True
        self.mode = mode

    def update_forces(self):
        self.g = self.max_g
        self.q = 1.+self.max_q*self.t/0.1
        

class Grid_Params():
    def __init__(self):
        self.x_m = 0.0 # (m)
        self.x_M = 1.0 # (m)
        self.y_m = 0.0 # (m)
        self.y_M = 1.0 # (m)
        self.thickness = 1. # (m) into page
        self.nx = 2
        self.ny = 2
        
class Boundary_Params():
    def __init__(self):
        self.wall = False
        self.has_top = False
        self.has_bottom = False
        self.has_right = True
        self.has_left = True
        self.outlet_left = False
        self.outlet_bottom = False
        self.vertical_force = True
        self.horizontal_force = False
        self.roughness = False

class Solid_Params():
    def __init__(self,G):
        self.X = []
        self.Y = []
        self.x = 3#(10*2-1)*2 # particles in x direction
        self.y = 3#(5*2-1)*2-4 # particles in y direction
        self.n = 0
        self.sizes = linspace(0.5,1,3)

#        self.law = 'elastic'
        self.law = 'dp'
        self.rho = 2650. # density (kg/m^3)
        
        self.E = 1.e5 # elastic modulus (Pa)
        self.nu = 0.3 # poisson's ratio
        self.K = self.E/(3.*(1.-2.*self.nu)) # bulk modulus (Pa)
        self.G = self.E/(2.*(1.+self.nu)) # shear modulus (Pa)

        self.beta = 1.
        self.mu = 10.
        self.s = 0.5

        self.L = 0.7
        self.W = 0.7
        for x in linspace(0.5-self.L/2.,0.5+self.L/2.,self.x):
            for y in linspace(0.5-self.W/2.,0.5+self.W/2.,self.y):
                self.X.append(x)
                self.Y.append(y)
                self.n += 1

        self.A = (G.x_M-G.x_m)*(G.y_M-G.y_m)/self.n # area (m^2)

class Output_Params():
    def __init__(self,nt,n):
        self.measure_energy = True
        self.plot_continuum = False
        self.plot_material_points = False
        self.measure_stiffness = False
        self.check_positions = False
        self.plot_fluid = False
        self.energy = zeros((nt*10+1,4)) # energy
        self.p = zeros((nt*10+10,n))
        self.q = zeros((nt*10+10,n))
        
    def measure_E(self,P,L):
        print 'Measuring macro and micro stress/strain for each material point... '
        for i in xrange(P.S.n):
            original_position = array((P.S.X[i],P.S.Y[i],0))
            macro_strain = (original_position-L.S[i].x)/array((P.S.L,P.S.W,1.)) #original_position
            macro_stress = P.max_q/2.
            print 'From macroscopic stress/strain:'
            print macro_stress/macro_strain/P.S.E
            print 'From microscopic stress/strain:'
            print L.S[i].dstress/L.S[i].dstrain/P.S.E

    def store_p_q(self,P,G,L,tstep):
        for i in xrange(P.S.n):
            self.p[tstep,i] = L.S[i].p
            self.q[tstep,i] = L.S[i].q
            
    def draw_p_q(self,P,G,L,plot,tstep):
        x = zeros((P.S.n,3))
        v = zeros((P.S.n,3))
        plt.figure()
        for i in xrange(P.S.n):
            plt.clf()
            plt.xlabel(r"$p$")
            plt.ylabel(r"$q$",rotation='horizontal')
            plt.plot(self.p[:tstep-1,i],self.q[:tstep-1,i])
            plot.savefig(P,str(i))
        #print (self.q[tstep-1,0]-self.q[1,0])/(self.p[tstep-1,0]-self.p[1,0])
