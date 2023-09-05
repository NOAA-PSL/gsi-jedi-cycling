#########################################################################
import os, sys
import getopt
import netCDF4 as nc4

import numpy as np

#------------------------------------------------------------------
def compare_variables_in_group(grpname, basegroup, casegroup, diminfo):
 #print('\t%20s, %10s, %10s' %(' ', 'min', 'max'))
  infostr = []
  title = '\n%s' %(grpname)
  infostr.append(title)
  print(title)

  epsilon = 1.0e-20
  head = '\t%20s, %10s, %10s' %(' ', 'min', 'max')
  infostr.append(head)

  print_info = False
  for name, variable in basegroup.variables.items():
    title = '\t%s' %(name)
    print(title)
    if('stationIdentification' == name):
      continue
    if(1 == len(variable.dimensions)):
      baseval = variable[:]
      caseval = casegroup.variables[name][:]
    elif(2 == len(variable.dimensions)):
      baseval = variable[:,:]
      caseval = casegroup.variables[name][:,:]
    elif(3 == len(variable.dimensions)):
      baseval = variable[:,:,:]
      caseval = casegroup.variables[name][:,:,:]
    elif(3 < len(variable.dimensions)):
      print('len(variable.dimensions) is %d which is great than 3. Stop.' %(len(variable.dimensions)))
      sys.exit(-1)

    diff = caseval - baseval
    if(any(x is None for x in diff)):
      print('One of the variables %s has None' %(name))
    else:
     #print('\t%s, %10.4f, %10.4f' %(name, np.min(diff), np.max(diff)))
      if(epsilon < np.max(diff)):
        print_info = True
        prntstr = '\t%s, %10.4f, %10.4f' %(name, np.min(diff), np.max(diff))
        infostr.append(prntstr)
      
    if(print_info):
      for prntstr in infostr:
        print(prntstr)

      dimsize = []
      for n in range(len(variable.dimensions)):
        ds = diminfo[variable.dimensions[n]]
        dimsize.append(ds)

      print('dimsize:', dimsize)
      print('variable.dimensions:', variable.dimensions)
      print('variable.size:', variable.size)
      print('variable.name:', variable.name)
      if(1 == len(dimsize)):
        for n in range(dimsize[0]):
          if(epsilon < np.abs(diff[n])):
            print('No %d cv: %f, bv: %f, diff: %f' %(n, caseval[n], baseval[n], diff[n]))
      elif(2 == len(dimsize)):
        nj = dimsize[0]
        ni = dimsize[1]
        for i in range(ni):
          for j in range(nj):
            if(epsilon < np.abs(diff[j,i])):
              print('No [%d, %d] cv: %f, bv: %f, diff: %f' %(j, i, caseval[j,i], baseval[j,i], diff[j,i]))

#------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  basedir = '/work2/noaa/da/weihuang/EMC_cycling/jedi-cycling/2022011900/observer'
  casedir = '/work2/noaa/da/weihuang/EMC_cycling/jedi-cycling/2022011900/observer'

  obstype = 'amsua_n19'

 #baseflnm = '%s/%s_obs_2022011900.nc4.saved' %(basedir, obstype)
  baseflnm = '%s/%s_obs_2022011900.nc4.mpi' %(basedir, obstype)
  caseflnm = '%s/%s_obs_2022011900.nc4' %(casedir, obstype)

  userdefine = False
  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'baseflnm=', 'caseflnm=', 'obstype='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--baseflnm'):
      baseflnm = a
    elif o in ('--caseflnm'):
      caseflnm = a
    elif o in ('--obstype'):
      userdefine = True
      obstype = a
    else:
      print('option: ', a)
      assert False, 'unhandled option'

  if(userdefine):
    baseflnm = '%s/%s_obs_2020010206.nc4' %(basedir, obstype)
    caseflnm = '%s/%s_obs_2020010206.nc4' %(casedir, obstype)
  
 #------------------------------------------------------------------
  basencf =  nc4.Dataset(baseflnm, 'r')
  casencf =  nc4.Dataset(caseflnm, 'r')

  diminfo = {}
  for name, dimension in basencf.dimensions.items():
    diminfo[name] = dimension.size

  compare_variables_in_group('Root Group', basencf, casencf, diminfo)

  for grpname, basegroup in basencf.groups.items():
    casegroup = casencf.groups[grpname]
    compare_variables_in_group(grpname, basegroup, casegroup, diminfo)

