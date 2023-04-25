#=========================================================================
import os
import sys
import time
import types
import getopt
import netCDF4

import numpy as np

#=========================================================================
class ModelVerticalPressure():
  def __init__(self, debug=0, filename=None):
    self.debug = debug

    flnm = 'pressure.txt'
    if(os.path.exists(flnm)):
      self.readdata(flnm)
    else:
      self.gen_pressure(filename)
      self.writedata(flnm)

   #self.markpres = [1000.0, 850.0, 700.0, 500.0, 200.0, 100.0,
    self.markpres = [1000.0, 700.0, 500.0, 200.0, 100.0,
                     50.0, 30.0, 20.0, 10.0, 5.0, 3.0, 2.0, 1.0]

  def gen_pressure(self, filename):
    ncfile = netCDF4.Dataset(filename)
    ak = ncfile.variables['ak'][:]
    bk = ncfile.variables['bk'][:]
    ncfile.close()

   #print('ak = ', ak)
   #print('bk = ', bk)

    print('len(ak) = ', len(ak))
    print('len(bk) = ', len(bk))

    nlevs = len(ak)

   #constants
    rd = 2.8705e+2
    cp = 1.0046e+3
    kap = rd/cp
    kapr = cp/rd
    kap1 = kap + 1.0

   #set mean surface pressure (has to be a global constant)
    psgmean = 1.e5

    self.fullpres = np.empty((nlevs), 'd')  # interface pressure
    self.halfpres = np.empty((nlevs-1), 'd')  # mid-layer pressure

    for k in range(nlevs):
      self.fullpres[k] = ak[k] + bk[k]*psgmean
    for k in range(nlevs-1):
     #phillips vertical interpolation from guess_grids.F90 in GSI (used for global model)
      self.halfpres[k] = ((self.fullpres[k]**kap1-self.fullpres[k+1]**kap1)
                         /(kap1*(self.fullpres[k]-self.fullpres[k+1])))**kapr
     #simple average of interface pressures (used by fv3_regional in GSI)
     #halfpres[k] = 0.5*(fullpres[k]+fullpres[k+1])
     #linear in logp interpolation from interface pressures
     #halfpres[k] = np.exp(0.5*(np.log(fullpres[k])+np.log(fullpres[k+1])))
  
    self.logp = -np.log(self.halfpres) # (ranges from -2 to -11)

    print('self.fullpres = ', self.fullpres)
    print('self.halfpres = ', self.halfpres)
    print('self.logp = ', self.logp)
    print('len(self.logp) = ', len(self.logp))

  def get_pressure(self):
    return self.halfpres

  def get_fullpressure(self):
    return self.fullpres

  def get_logp(self):
    return self.logp

  def get_markpres(self):
    return self.markpres

  def set_markpres(self, markpres=[]):
      self.markpres = markpres

  def get_marklogp(self, mp=None):
    if(mp is None):
      markpres = np.empty((len(self.markpres)), 'f')
      for n in range(len(self.markpres)):
        markpres[n] = 100.0*self.markpres[n]
    else:
      markpres = 100.0*mp
      
    marklogp = -np.log(markpres)
    return marklogp

  def writedata(self, flnm):
    OF = open(flnm, 'w')
    for n in range(len(self.halfpres)):
      OF.write("%f, %f\n" %(self.fullpres[n], self.halfpres[n]))
    OF.write("%f, %f\n" %(self.fullpres[-1], -1))
    OF.close()

  def readdata(self, flnm):
    self.halfpres = []
    self.fullpres = []
    INF = open(flnm, 'r')
    lines = INF.readlines()
    for line in lines:
      item = line.split(', ')
      self.fullpres.append(float(item[0]))
      if(float(item[1]) > 0):
        self.halfpres.append(float(item[1]))
    INF.close()
  
    self.logp = -np.log(self.halfpres) # (ranges from -2 to -11)

#------------------------------------------------------------------------------
if __name__ == '__main__':
  debug = 1
 #filename = '/work/noaa/gsienkf/weihuang/jedi/case_study/sondes/Data/bkg/fv_core.res.nc'
  filename = '/work2/noaa/gsienkf/weihuang/jedi/singleobs/Data/ens/mem001/RESTART/20151205.030000.fv_core.res.nc'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'filename='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--filename'):
      filename = a
   #else:
   #  assert False, 'unhandled option'

  print('debug = ', debug)
  print('filename = ', filename)

  mvp = ModelVerticalPressure(debug=debug, filename=filename)

  prs = mvp.gen_pressure(filename=filename)
  prs = mvp.get_pressure()
  print('len(prs) = ', len(prs))
  for n in range(len(prs)):
    print('Level %d pressure %f' %(n, prs[n]))

  print('prs = ', prs)

  prs = mvp.writedata('pressure.txt')

