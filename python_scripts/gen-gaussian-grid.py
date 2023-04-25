#=========================================================================
import os
import sys
import getopt
import netCDF4 as nc4
import time
import numpy as np
import inspect, logging
import cdms2

#=========================================================================
class GenerateGaussianGrid():
  def __init__(self, debug=0, nlats=192, nlons=384, basefile=None):
    self.debug = debug
    self.nlats = nlats
    self.nlons = nlons
    self.basefile = basefile

    self.outfile = 'gaussian_grid_C%d.nc4' %(nlats/2)
    self.ncin = nc4.Dataset(basefile, 'r')

    self.identstr = ''

 #-----------------------------------------------------------------------------------------
  def logger(self, message):
   #Automatically log the current function details.
   #Get the previous frame in the stack, otherwise it would
   #be this function!!!
    func = inspect.currentframe().f_back.f_code
   #Dump the message + the name of this function to the log.
    if(message == 'Enter'):
      self.identstr += '    '
    if(self.debug):
      print("%s %s %s at line %i in %s" % (self.identstr, message, 
        func.co_name, func.co_firstlineno, func.co_filename))
    if(message == 'Leave'):
      newidentstr = self.identstr[:-4]
      self.identstr = newidentstr

 #-----------------------------------------------------------------------------------------
  def create_dimension(self, name, dimlen, ncout):
    if(dimlen <= 0):
      ncout.createDimension(name, None)
    else:
      ncout.createDimension(name, dimlen)

 #-----------------------------------------------------------------------------------------
  def create_attributes(self, name, attr, ncout):
    ncout.setncattr(name, attr)

 #-----------------------------------------------------------------------------------------
  def write_val2var(self, val, outvar):
    nd = len(outvar.dimensions)
    if(nd == 1):
      outvar[:] = val[:]
    elif(nd == 2):
      outvar[:,:] = val[:,:]
    elif(nd == 3):
      outvar[:,:,:] = val[:,:,:]
    elif(nd == 4):
      outvar[:,:,:,:] = val[:,:,:,:]
    else:
      msg = 'Do not know how to handle nd = %i' %(nd)
      self.logger(msg)
      print(msg)
      sys.exit(-1)

#-----------------------------------------------------------------------------------------
  def generate(self):
    self.logger('Enter')

    if(os.path.exists(self.outfile)):
      os.remove(outfile)

    print('outfile: ', self.outfile)

    self.ncout = nc4.Dataset(outfile, 'w')

    ak = self.ncin['ak'][:]
    bk = self.ncin['bk'][:]

    print('ak = ', ak)
    print('bk = ', bk)

    self.nlevs = len(ak) - 1
    self.ilev = len(bk)

   #global attributes
    self.ncout.source='Generate from running: gen-gaussian-grid.py'
    self.ncout.comment = 'Gaussian grid of (nlon: %d, nlat: %d) ' %(self.nlons, self.nlats)

    dlat = self.create_dimension('lat', self.nlats, self.ncout)
    dlon = self.create_dimension('lon', self.nlons, self.ncout)
    dlev = self.create_dimension('lev', self.nlevs, self.ncout)
    dilev = self.create_dimension('ilev', self.ilev, self.ncout)
  
    lat = self.ncout.createVariable('lat', float, dlat)
    lon = self.ncout.createVariable('lon', float, dlon)
    lev = self.ncout.createVariable('lev', float, dlev)
    hyai = self.ncout.createVariable('hyai', float, dilev)
    hybi = self.ncout.createVariable('hybi', float, dilev)

    lat[:] = cdms2.createGaussianAxis(nlats)
    lon[:] = np.linespace(0, 360, self.nlons)
    lev[:] = range(1, self.ilev)
    hyai[:] = ak
    hybi[:] = bk

    grid = cdms2.createGaussianGrid(128)
    print('grid = ', grid)

    self.ncin.close()
    self.ncout.close()

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 0

  basefile = 'akbk127.nc4'
  nlats = 192

  #-----------------------------------------------------------------------------------------
  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'basefile=', 'nlats='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--basefile'):
      basefile = a
    elif o in ('--nlats'):
      nlats = int(a)
    else:
      assert False, 'unhandled option'

  nlons = 2*nlats

  #-----------------------------------------------------------------------------------------
  ggg = GenerateGaussianGrid(debug=debug, nlats=nlats, nlons=nlons, basefile=basefile)
  ggg.generate()

