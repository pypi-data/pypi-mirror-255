#!/usr/bin/env python3
import numpy as np
import json
import sys, re, os
from libhreels.HREELS import myPath
from copy import deepcopy

import scipy.integrate as integrate

libDir = os.path.dirname(os.path.realpath(__file__)) 

if not (sys.version.startswith('3.6') or sys.version.startswith('3.8')):
    print('''Make sure the Fortran routines 'myEels20' and 'myBoson' 
    have been complied with the proper f2py3 for the right 
    python version!!''') 
try:
    from libhreels import myEels20 as LambinEELS   # wrapper for myEels20.f90
    from libhreels import myBoson as LambinBoson  # wrapper for myBoson.f90
except:
    print('myEels20 and MyBoson are not available here (Check your version)')			

# Experimental setup as dictionary:
setup = {
    "e0": 4.0,
    "theta": 60.,
    "phia": 0.33,
    "phib": 2.0,
    "temperature": 298.,
    "debug": False
}
# Instrumental function describing elastic peak shape:
instrument = {
    "width": 18.,
    "intensity": 100000.,
    "asym": 0.01,
    "gauss": 0.88
}

	
def importMaterials(string='', path=libDir):
    ''' Returns a dictionary with all phonon parameters for the material provided 
    as string argument. If the string is empty or not matching, a list of all available 
    materials is printed.
    '''
    file = os.path.join(myPath(path),'materials20.json')
    with open(file) as json_file:
        materials = json.load(json_file)
        try:
            mat = materials[string]

            #Following if-case for preventing old material data to be used in  wrong terminology
            if mat["wLO"][0]==1 and mat["gLO"][0]==1 and mat["wTO"][0]<0 and mat["gTO"][0]<0:
                print('It seems you are trying to load a Material from an older version. Parameter will be altered to fit the current Version.')
                wTO = 0
                gTO = -mat["gTO"][0]                
                wLO = -mat["wTO"][0]
                gLO = -mat["gTO"][0]        
                mat["wTO"][0] = wTO
                mat["gTO"][0] = gTO
                mat["wLO"][0] = wLO
                mat["gLO"][0] = gLO
        except:
            print('No data for material >>{}<< found in {} materials.json!!'.format(string, path))
            print('Available materials:\n{}\n'.format(materials.keys()))
            mat = 'None'
    return mat

def addDrude(wLOPlasma, gLOPlasma, material, gTOPlasma='None'):
    ''' Adds a generalized Drude response to the materials properties (which are provided 
    as last argument) and returns a new materials dictionary with all phonon parameters. Note 
    that at least the eps_infinity has to given before.
    '''
    if gTOPlasma == 'none':
        gTOPlasma = gLOPlasma
    newMaterial = deepcopy(material)
    # To select the Drude response, the Lambin Fortran code requires a negative first oscillator frequency
    # which is then interpreted as plasma frequency.
    # The values of the former LO parameter are irrelevant (but need to be provided). 
    try:
        if len(newMaterial['wTO']) > 0:
            newMaterial['wTO'] += [0.]
            newMaterial['gTO'] += [gTOPlasma]
            newMaterial['wLO'] += [wLOPlasma]
            newMaterial['gLO'] += [gLOPlasma]
            return newMaterial
    except:
        print('Cannot add Drude to material',material)
    return material

################################################################################
################################################################################
class lambin:
    def __init__(self, film, setup=setup, instrument=instrument):
        self.e0 = setup['e0']
        self.theta = setup['theta']
        self.phia = setup['phia']
        self.phib = setup['phib']
        self.temperature = setup['temperature']
        self.debug = setup['debug']
        self.width = instrument['width']
        self.gauss = instrument['gauss']
        self.intensity = instrument['intensity']
        self.asym = instrument['asym']
        self.layers = len(film)          # number of layers
        self.neps = self.layers
        # name_size = self.layers
        self.name = []; self.thick=[]; self.listNOsci=[]; self.epsinf =[]; Q = []
        allTO=[]; allgTO=[];  allgLO=[]; nDrude=0
        name2 = []
        for layer in film:
            try:
                a = layer[0]['name']
            except:
                a = 'None'
            self.name.append('{:<10}'.format(a[:10]))        # film name and material
            name2.append(a)
            try:
                a = layer[1]
            except:
                a = 10000.
            self.thick.append(a)
            self.epsinf.append(layer[0]['eps'])
            nTO = 2 * len(layer[0]['wTO'])
            allTO.extend(layer[0]['wTO'])
            allgTO.extend(layer[0]['gTO'])
            allTO.extend(layer[0]['wLO'])
            allgTO.extend(layer[0]['gLO'])
            Q.extend(2*len(layer[0]['wTO'])*[10.])
            self.listNOsci.append(nTO)
        
        if len(allTO)!=sum(self.listNOsci) or len(allgTO)!=sum(self.listNOsci):
            print('Error in materials: ', layer[0])
        self.wOsc = np.array(allTO)
        self.gOsc = np.array(allgTO)
        self.osc = np.array([self.wOsc, np.array(Q), self.gOsc])
        return

    def calcSurfaceLoss(self,x):
        ''' Calculate the surface loss spectrum for the array of x, which needs to be an equidistant array. 
        All parameters are defined in the class __init__() call.'''
        wmin = min(x)
        wmax = max(x)-0.001
        dw = (wmax-wmin)/(len(x)-1)     # assumes that x is an equidistant array
        wn_array_size = len(x)     # size of array for x and epsilon (wn_array, loss_array)
        nper = 1.
        contrl = '{:<10}'.format('None'[:10])   # Can be 'image' to include image charge
        mode = '{:<10}'.format('kurosawa'[:10])           
        wn_array,loss_array = LambinEELS.mod_doeels.doeels(self.e0,self.theta,self.phia,self.phib,
            wmin,wmax,dw,self.layers,self.neps,nper,self.name,
            self.thick,self.epsinf,self.listNOsci,self.osc,contrl,mode,wn_array_size)
        i=0
        for item in wn_array:
            if item > 0: break
            i += 1
        return wn_array[i-1:], loss_array[i-1:]

    def calcHREELS(self,x, normalized=True, areanormalized=False):
        emin = min(x)
        emax = max(x)-0.001
        norm = 1
        xLoss,loss_array = self.calcSurfaceLoss(x)
        wmin = min(xLoss)
        wmax = max(xLoss)
        xOut,spectrum,n = LambinBoson.doboson3(self.temperature,self.width,self.gauss,self.asym,
            emin,emax,wmin,wmax,loss_array,self.debug,len(loss_array))
        if normalized:
            norm = max(spectrum[:n])
            if areanormalized: #edit by HHE
                try:                    
                    areanormalize_xstart = np.argmin(abs(x+100.)) #seems to be oddly complicated, but is way more stable than x.index(-100.) or where()
                except:
                    areanormalize_xstart = 0
                try:
                    areanormalize_xend = np.argmin(abs(x-1000.))
                except:
                    areanormalize_xend = len(x)
                cropped_spectra=spectrum[areanormalize_xstart:areanormalize_xend]
                cropped_x=x[areanormalize_xstart:areanormalize_xend]

                norm=integrate.simps(cropped_spectra, dx=x[areanormalize_xstart+1]-x[areanormalize_xstart])

        else:
            print("not normalized")
        return xOut[:len(x)], spectrum[:len(x)]/norm

    def calcEps(self, x):
        epsArray = []
        nOsci = len(self.wOsc)
        for wn in x:
            yn = LambinEELS.mod_doeels.seteps(self.listNOsci,nOsci,self.osc,self.epsinf,wn,self.layers)
            epsArray.append(yn)
        return np.transpose(np.array(epsArray))

####################################################################################
def myMain():
    import matplotlib.pyplot as plt
    import numpy as np
    import os

    x = np.linspace(-100.,1000,400)
    x2 = np.linspace(-100.,1000,2400)
    

    material = {'eps': 4.,
                'wTO': [0],  'gTO': [20], 'wLO': [598.7], 'gLO': [20],
                }
    
    print("Ag imported as: ", importMaterials('Ag'))

    film1 = lambin(film=[[material,10000.]])
    film1.temperature = 100
    #xs, spectrum = film1.calcSurfaceLoss(x)
    xs, spectrum = film1.calcHREELS(x,normalized=False,areanormalized=False)
    xs1, spectrum1 = film1.calcHREELS(x2,normalized=False,areanormalized=False)
    xs2, spectrum2 = film1.calcHREELS(x,areanormalized=True)
    xs3, spectrum3 = film1.calcHREELS(x2,areanormalized=True)

    norm_test=integrate.simps(spectrum, dx=xs[2]-xs[1])/(max(xs)-min(xs))
    norm_test1=integrate.simps(spectrum1, dx=xs1[2]-xs1[1])/(max(xs1)-min(xs1))
    norm_test2=integrate.simps(spectrum2, dx=xs2[2]-xs2[1])/(max(xs2)-min(xs2))
    norm_test3=integrate.simps(spectrum3, dx=xs3[2]-xs3[1])/(max(xs3)-min(xs3))
    print(norm_test,norm_test1,norm_test2,norm_test3)
    print(xs[2]-xs[1],xs1[2]-xs1[1],xs2[2]-xs2[1],xs3[2]-xs3[1])
    
    plt.plot(xs[:-1],spectrum[:-1], label='normalized=Flase, '+str(len(x))+' points, E0 at '+str(max(spectrum)))
    plt.plot(xs1[:-2],spectrum1[:-2], label='normalized=Flase, '+str(len(x2))+' points, E0 at '+str(max(spectrum1)))
    plt.plot(xs2[:-10],spectrum2[:-10],label='area normalized=True, '+str(len(x))+' points, E0 at '+str(max(spectrum2)))
    plt.plot(xs3[:-20],spectrum3[:-20],label='area normalized=True, '+str(len(x2))+' points, E0 at '+str(max(spectrum3)))

    print('spec2/spec0=', max(spectrum2)/max(spectrum))
    print('spec3/spec0=', max(spectrum3)/max(spectrum))
    print('spec0/spec2=', max(spectrum)/max(spectrum2))
    print('spec0/spec3=', max(spectrum)/max(spectrum3))

    # pureDrude = {'eps': 4.,
    #             'wTO': [-400],  'gTO': [-20], 'wLO': [0], 'gLO': [0],
    #             }
    # film2 = lambin(film=[[pureDrude,10000.]])
    # film2.temperature = 100
    # xs, spectrum = film2.calcSurfaceLoss(x)
    # plt.plot(xs,spectrum,'g-.', label='pure Drude 400')


    plt.ylabel('Surface Loss')
    plt.xlabel('Energy Loss (cm$^{-1}$)')
    plt.legend(title=r'Plasma frequency')

    plt.text(0.99, 0.01,os.path.basename(__file__), fontsize=10, ha='right', va='bottom', transform=plt.gcf().transFigure)
    output_filename = os.path.splitext(__file__)[0] + '.png'
    plt.savefig(output_filename)

    plt.show()


if __name__ == '__main__':
	myMain()