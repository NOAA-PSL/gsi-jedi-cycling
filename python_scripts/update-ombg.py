#=========================================================================
import os
import sys
import getopt
import netCDF4 as nc4
import time
import numpy as np

#-----------------------------------------------------------------------------------------
def read_var(self, name, variable):
  if(self.debug):
    self.LOGFILE.write('\tread var: %s with %d dimension\n' %(name, len(variable.dimensions)))
  if(1 == len(variable.dimensions)):
    val = variable[:]
  elif(2 == len(variable.dimensions)):
    val = variable[:,:]
  elif(3 == len(variable.dimensions)):
    val = variable[:,:,:]

  return val

#-----------------------------------------------------------------------------------------
def write_var(self, var, val):
  dim = len(var.dimensions)
  if(1 == dim):
    var[:] = val[:]
  elif(2 == dim):
    var[:,:] = val[:,:]
  elif(3 == dim):
    var[:,:,:] = val[:,:,:]

#-----------------------------------------------------------------------------------------
def process(ncinlist, ncout):
  ombggroup = ncout.groups['ombg']
  hofxgroup = ncout.groups['hofx_y_mean_xb0']
  ensvarinfo = {}

  ombgdict = {}
  hofxdict = {}

  for varname, variable in ombggroup.variables.items():
    ombgdict[varname] = self.read_var(varname, variable)

  for varname, variable in hofxgroup.variables.items():
    hofxdict[varname] = self.read_var(varname, variable)

  buf = {}
  for n in range(self.nmem):
    mem = n + 1
    hofx0group = ncinlist[n].groups['hofx0_1']
    for varname, variable in hofx0group.variables.items():
      val = self.read_var(varname, variable)
      if(n < 1):
        buf[varname] = val
      else:
        buf[varname] += val

  for varname, variable in ombggroup.variables.items():
    val = ombgdict[varname] + hofxdict[varname] - buf[varname]/self.nmem
    self.write_var(variable, val)

#-----------------------------------------------------------------------------------------
def update_ombg(filelist, outfile):
  ncinlist = []
  for infile in filelist:
    if(os.path.exists(infile)):
     #print('infile: ', infile)
      ncin = nc4.Dataset(infile, 'r')
      ncinlist.append(ncin)
    else:
      print('infile: %s does not exist.' %(infile))
      sys.exit(-1)

  if(os.path.exists(outfile)):
    os.remove(outfile)
    print('outfile: ', outfile)
 #else:
 #  print('outfile: %s does not exist.' %(outfile))

  print('len(ncinlist) = ', len(ncinlist))

  ncout = nc4.Dataset(outfile, 'r+')

  process(ncinlist, ncout)
 
  for ncin in ncinlist:
    ncin.close()
  ncout.close()

#-----------------------------------------------------------------------------------------
debug = 1
nmem = 81

rundir = '/work2/noaa/da/weihuang/cycling/gdas-cycling'
datestr = '2020010106'
obstype = 'sondes'

#-----------------------------------------------------------------------------------------
opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'rundir=',
                                              'datestr=', 'obstype=', 'nmem='])
for o, a in opts:
  if o in ('--debug'):
    debug = int(a)
  elif o in ('--rundir'):
    rundir = a
  elif o in ('--datestr'):
    datestr = a
  elif o in ('--obstype'):
    obstype = a
  elif o in ('--nmem'):
    nmem = int(a)
  else:
    assert False, 'unhandled option'

#-----------------------------------------------------------------------------------------
filelist = []
for n in range(nmem):
  mem = n + 1
  flnm = '%s/observer/mem%3.3d/%s_obs_%s.nc4' %(rundir, mem, obstype, datestr)
  filelist.append(flnm)
outfile = '%s/observer/%s_obs_%s.nc4' %(rundir, datestr, obstype, datestr)

update_ombg(filelist, outfile)

