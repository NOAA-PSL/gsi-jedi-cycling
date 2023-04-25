#########################################################################
#$Id: bld.py 28 2021-01-21 15:10:31Z whuang $
#$Revision: 28 $
#$HeadURL: file:///Users/whuang/.wei_svn_repository/trunk/jedi-build-tools/bld.py $
#$Date: 2021-01-21 08:10:31 -0700 (Thu, 21 Jan 2021) $
#$Author: whuang $
#########################################################################

import getopt
import os, sys
import types
import time
import datetime
import subprocess
import netCDF4

import numpy as np

#------------------------------------------------------------------
def compare_variable(basedir, casedir, type, varname, prefix=None, nt=0):
  print('Compare variable: ', varname)
  print('%10s, %10s' %('min', 'max'))
  for ntile in range(1,7,1):
    if(prefix is None):
      basefile = '%s/%s.res.tile%d.nc' %(basedir, type, ntile)
      casefile = '%s/%s.res.tile%d.nc' %(casedir, type, ntile)
    else:
      basefile = '%s/%s%s.res.tile%d.nc' %(basedir, prefix, type, ntile)
      casefile = '%s/%s%s.res.tile%d.nc' %(casedir, prefix, type, ntile)

    if(not os.path.exists(basefile)):
      print('basefile: %s does not exist, stop' %(basefile))
      sys.exit(-1)
    if(not os.path.exists(casefile)):
      print('casefile: %s does not exist, stop' %(casefile))
      sys.exit(-1)

    ncbase = netCDF4.Dataset(basefile)
    nccase = netCDF4.Dataset(casefile)

    baseval = ncbase.variables[varname][nt,:,:,:]
    caseval = nccase.variables[varname][nt,:,:,:]

    diff = caseval - baseval

    print('tile %d, %10.4f, %10.4f' %(ntile, np.min(diff), np.max(diff)))

    ncbase.close()
    nccase.close()

#------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 0
  runtype = 'run_80.36t1n_36p'
  runname = 'allobs_JEDI_full_run'
  rundir = '/work2/noaa/gsienkf/weihuang/jedi/case_study'
  basename = 'develop'
  caselist = ['anna1', 'anna2']
  casename = 'anna1'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=', 'casename='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--casename'):
      casename = a
    else:
      print('option: ', a)
      assert False, 'unhandled option'

  core_namelist = ['u', 'v', 'T', 'delp', 'DZ']
  tracer_namelist = ['sphum', 'o3mr']

  basedir = '%s/%s_%s/%s/analysis/increment' %(rundir, runname, basename, runtype)
  print('\nruntype %s: ' %(runtype))
  for casename in caselist:
    print('\nDifferene of %s to %s for %s' %(casename, basename, runtype))
    casedir = '%s/%s_%s/%s/analysis/increment' %(rundir, runname, casename, runtype)

    type = 'fv_core'
    for varname in core_namelist:
      compare_variable(basedir, casedir, type, varname, prefix='20200110.030000.', nt=0)

    type = 'fv_tracer'
    for varname in tracer_namelist:
      compare_variable(basedir, casedir, type, varname, prefix='20200110.030000.', nt=0)

