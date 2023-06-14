#########################################################################
import os, sys
import getopt
import netCDF4 as nc4

import numpy as np

#------------------------------------------------------------------
def compare_variables_in_group(basegroup, casegroup):
  print('\t%20s, %10s, %10s' %(' ', 'min', 'max'))
  for name, variable in basegroup.variables.items():
    if(1 == len(variable)):
      baseval = variables[:]
      caseval = casegroup.variables[name][:]

      diff = caseval - baseval

      print('\t%20s, %10.4f, %10.4f' %(name, np.min(diff), np.max(diff)))

#------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  basedir = '/work2/noaa/da/weihuang/cycling/gdas-cycling/2020010206/observer/seqobs'
  casedir = '/work2/noaa/da/weihuang/cycling/gdas-cycling/2020010206/observer/mpiobs'

  baseflnm = '%s/sondes_obs_2020010206.nc4' %(basedir)
  caseflnm = '%s/sondes_obs_2020010206.nc4' %(casedir)

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'baseflnm=', 'caseflnm='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--baseflnm'):
      baseflnm = a
    elif o in ('--caseflnm'):
      caseflnm = a
    else:
      print('option: ', a)
      assert False, 'unhandled option'

 #------------------------------------------------------------------
  basencf =  nc4.Dataset(baseflnm, 'r')
  casencf =  nc4.Dataset(caseflnm, 'r')

  print('\nRoot Group')
  compare_variables_in_group(basencf, casencf)

  for name, basegroup in basencf.groups.items():
    casegroup = basenc.groups[name]
    print('\n%s' %(name))
    compare_variables_in_group(basegroup, casegroup)

