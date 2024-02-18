# Testing dielectric models and their surface loss function
import matplotlib.pyplot as plt
import numpy as np
from numpy import real, imag, sqrt
from scipy import constants


def doping2chargecarrierdensity(doping): #use doping in percentage by mass, not volume
    '''Returns the charge carrier density for a given doping in percentage of mass.'''
    return float(doping*3.31664067935517E+020*1E6) # doping[%] * charge carrier/cm^3 * 1E6 = n_e [m^-3] 

def doping2plasmaFrequency(doping,epsInfinity=1.): #use doping in percentage by mass, not volume
    '''Returns the plasma frequency for a given doping in percentage of mass.'''
    eps_0 = constants.value("vacuum electric permittivity")
    e = constants.value('elementary charge')
    m_e = constants.value('electron mass')
    c = constants.value('speed of light in vacuum') 
    eps_r = epsInfinity
    n_e = doping2chargecarrierdensity(doping)

    w_P = np.sqrt(n_e*e*e/(eps_r*eps_0*m_e)) #Hz
    w_P = w_P /1E+12 * 33.35641 #Hz -> THz -> cm^-1
    return w_P 
    

def doping2surfacePlasma(doping,epsInfinity=1.):
    '''Returns the surface plasma frequency in cm-1 for a doping 
       given by the argument in cm-3'''
    return np.sqrt(doping)*1.8817885780819758e-06/np.sqrt(1+epsInfinity)

def loss(eps):
    '''Returns the loss function for a given eps'''
    return np.imag(eps) #HHE changed former sign

def surfaceLoss(eps):
    '''Returns the surface loss function for a given eps'''
    return np.imag(-1/(1+eps)) #HHE changed former sign, according to Phd of FSc

def reflectivity(eps):  # IR reflectivity
    '''Returns the reflectivity for a given eps'''
    sq = np.sqrt(eps)
    a = np.abs((sq-1)/(sq+1))
    return a*a

def sigma(eps,w):       
    '''Returns the complex conductivity for a given eps'''
    return (eps-1)*w/1j

def plotDielectrics(x,eps, title=" ", plot_show=True):
    '''This method plots a given (x,eps)-dataset as Re/Im(eps), SurfaceLoss and Reflectivity 
    '''
    fig, axs = plt.subplots(3, 1, sharex=True)
    fig.suptitle(str(title), fontsize=16)
    axs[0].plot(x, np.imag(eps), label='Im( $\epsilon (\omega )$ )')
    axs[0].plot(x, np.real(eps), label='Re( $\epsilon (\omega )$ )')
    axs[0].legend()
    axs[0].set_ylabel('Dielectric Function')

    axs[1].plot(x, surfaceLoss(eps), lineStyle='-', label='Loss function')    
    axs[1].set_ylabel('Surface Loss Function')
    axs[1].set_ylim([-0.10,None])

    axs[2].plot(x, reflectivity(eps))
    axs[2].set_ylabel('Reflectivity')
    axs[2].set_xlabel('Frequency')
    axs[2].set_ylim([0.0,1])
    axs[0].set_xlim(left=0, right=max(x))

    if plot_show==True:
        plt.show()

class oscillator:
    '''This defines epsilon of an oscillator with a given (wTO, gTO, wLO, gLO)
    '''
    def __init__(self, wTO=177., gTO=20., wLO=184., gLO=20.):
        self.wTO = wTO
        self.wLO = wLO
        self.gammaTO = gTO
        self.gammaLO = gLO

    def eps(self,w):
        nom = self.wLO*self.wLO - w*w - 1j*w*self.gammaLO   #sign changed according to gervais paper, formular 2 -> neg im(eps), therefore changed back to lambins kurosawa
        denom = self.wTO*self.wTO - w*w - 1j*w*self.gammaTO #sign changed according to gervais paper, formular 2 -> neg im(eps), therefore changed back to lambins kurosawa
        return nom/denom

    def __call__(self, w):
        return self.eps(w)

class drude:
    '''This defines an additive Drude component to a dielectric function: 
    eps_drude = drude2(omega_p, gamma_p, gamma_0)
    ... eps(omega) + eps_drude(omega)
    '''
    def __init__(self, omega_p, gamma_p, gamma_0):

        self.omega_p = omega_p
        self.gamma_p = gamma_p
        self.gamma_0 = gamma_0

        print("called drude with w_P, g_P, g_0:", omega_p, gamma_p, gamma_0)
        

    def eps(self,w):
        newW = np.where(w==0, 0.000567894, w)   # Avoid zeros to avoid devision by zero 
        w = newW
        #print("Drude (x,y): ", w, -((self.omega_p**2 + 1j*w*(self.gamma_0-self.gamma_p))/(w*w + 1j*w*self.gamma_0)))

        nom = self.omega_p**2 + 1j*w*(self.gamma_0-self.gamma_p)
        denom = w*w + 1j*w*self.gamma_0 #sign changed according to Lambin notation

        return -(nom/denom) #HHE changed 

    def __call__(self, w):
        return self.eps(w)

    
class cole_davidson:
    '''This defines an additive Cole-Davidson component to a dielectric function: 
    eps_cole_davidson = cole_davidson(omega_p, gamma_p, gamma_0)
    ... eps(omega) + eps_drude(omega)
    '''
    def __init__(self, omega_p, gamma_p, gamma_0, beta):

        self.omega_p = omega_p
        self.gamma_p = gamma_p
        self.gamma_0 = gamma_0
        self.beta = beta

        print("called coledavidson with w_P, g_P, g_0, beta:", omega_p, gamma_p, gamma_0, beta)
    

    def eps(self,w):
        newW = np.where(w==0, 0.000567894, w)   # Avoid zeros to avoid devision by zero 
        w = newW
        #print("Drude (x,y): ", w, -((self.omega_p**2 + 1j*w*(self.gamma_0-self.gamma_p))/(w*w + 1j*w*self.gamma_0)))
        #return -((self.omega_p**2 + 1j*w*(self.gamma_0-self.gamma_p))/(w*w + 1j*w*self.gamma_0)) #HHE changed 
        
        #nom = self.omega_p**2 + 1j*w*(self.gamma_0-self.gamma_p) #very simple approach by just putting an exponent to denominator (works only for gamma_0=gamma_P)
        #denom = (w*w - 1j*w*self.gamma_0)**self.beta  #sign changed according to gervais paper, formular 7

        hilf = 1j * w * self.gamma_0 * (1-1j*w*(1/self.gamma_0))**(self.beta)

        nom = self.omega_p**2 - 1j*w*(self.gamma_p) - w*w + hilf #unfortunately also the nominator changes due to cole-davidson
        denom = hilf   #sign changed according to gervais paper, formular 7 -> did not match, changed back to lambin formularism


        return -(nom/denom)

    def __call__(self, w):
        return self.eps(w)

class cole_cole:
    '''This defines an additive Cole-Davidson component to a dielectric function: 
    eps_cole_cole = cole_cole(omega_p, gamma_p, gamma_0, beta)
    ... 
    '''
    def __init__(self, omega_p, gamma_p, gamma_0, beta):

        self.omega_p = omega_p
        self.gamma_p = gamma_p
        self.gamma_0 = gamma_0
        self.beta = beta

        print("called colecole with w_P, g_P, g_0, beta:", omega_p, gamma_p, gamma_0, beta)

    def eps(self,w):
        newW = np.where(w==0, 0.000567894, w)   # Avoid zeros to avoid devision by zero 
        w = newW
        #nom = self.omega_p**2 + 1j*w*(self.gamma_0-self.gamma_p) #very simple approach by just putting an exponent to denominator (works only for gamma_0=gamma_P)
        #denom = w*w + w*(1j*self.gamma_0)**self.beta

        hilf = 1j**(self.beta+1) * w**(self.beta+1) * self.gamma_0**(1-self.beta)

        nom = self.omega_p**2 + 1j*w*(self.gamma_0-self.gamma_p) - w*w - hilf #unfortunately also the nominator changes due to cole-cole 
        denom = 1j*w*(self.gamma_0) - hilf   #sign changed according to lambin formularism

        return -(nom/denom)

    def __call__(self, w):
        return self.eps(w)


class simpleOscillator(oscillator):
    '''This defines epsilon of an oscillator with a given (wPl, Q and gTO)
    '''
    def __init__(self, wPl, Q, gTO=20):
        self.wPl = wPl
        self.Q = Q
        self.gammaTO = gTO

    def eps(self,w):
        nom = self.wPl*self.wPl*self.Q
        denom = self.wPl*self.wPl - w*w - 1j*self.gammaTO*w #HHE changed, wrong sign of Im
        return nom/denom

class simpleDrude:
    '''This defines epsilon of an oscillator with a given (wPl, gamma). gamma = gammaTO = gammaLO
    '''
    def __init__(self, wPL, gamma):
        self.wPL = wPL
        self.gamma = gamma

    def eps(self,w):
        return -(self.wPL*self.wPL)/(w*w-1j*w*self.gamma) #HHE changed 

    def __call__(self, w):
        return self.eps(w)



def myMain():
    # BaTiO3
    simple_data = [
        [178.6, 8.02, 3.09800E-02],
        [270.6, 24.00, 10.0800E-02],
        [522.9, 1.20, 6.97200E-02]]

    data = [
        [177.4 , 1.9262 , 184.003 , 9.718],
        [272.84 , 93.3091 , 470.972 ,  14.31 ],
        [506.379 , 42.60 , 739.651 , 33.044],
    ]  
        
    x = np.linspace(0,1000,num=1200)
    epsInfinity = 5.25

    simpleoscis = [simpleOscillator(TO, Q, f*TO) for (TO, Q, f) in simple_data]
    eps = epsInfinity
    for each in simpleoscis:
        eps += each(x) #sum
    plotDielectrics(x, eps, title="Eps of BaTiO calced with simpleOscillator", plot_show=False)

    oscis = [oscillator(wTO=a, wLO=c, gTO=b, gLO=d) for (a, b, c, d) in data]
    eps2 = epsInfinity
    for each in oscis:
        eps2 *= each(x) #kurosawa
    plotDielectrics(x, eps2, title="Eps of BaTiO calced with oscillator", plot_show=False)

    plt.show()

if __name__ == '__main__':
    myMain()
