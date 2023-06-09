#=========================================================================
import os
import sys
import getopt
import netCDF4 as nc4
import numpy as np

#-----------------------------------------------------------------------------------------
def average(vlist):
  buf = np.zeros_like(vlist[0])
  nmem = len(vlist)
  for n in range(1, nmem):
    buf += vlist[n]
  buf /= (nmem-1)
  return buf

#-----------------------------------------------------------------------------------------
def copy_dimension(ncin, ncout):
 #copy dimensions
  for name, dimension in ncin.dimensions.items():
   #ncout.createDimension(name, (len(dimension) if not dimension.isunlimited() else None))
    if dimension.isunlimited():
      ncout.createDimension(name, None)
    else:
      ncout.createDimension(name, len(dimension))

#-----------------------------------------------------------------------------------------
def copy_attributes(ncin, ncout):
 #copy the global attributes to the new file
  inattrs = ncin.ncattrs()
  for attr in inattrs:
    if('_FillValue' != attr):
      ncout.setncattr(attr, ncin.getncattr(attr))

#-----------------------------------------------------------------------------------------
def copy_rootvar(ncin, ncout):
 #copy all var in root group.
  for name, variable in ncin.variables.items():
    ncout.createVariable(name, variable.datatype, variable.dimensions)
   #copy variable attributes all at once via dictionary
    ncout[name].setncatts(ncin[name].__dict__)

    if(1 == len(variable.dimensions)):
      ncout[name][:] = ncin[name][:]
    elif(2 == len(variable.dimensions)):
      ncout[name][:,:] = ncin[name][:,:]
    elif(3 == len(variable.dimensions)):
      ncout[name][:,:,:] = ncin[name][:,:,:]

#-----------------------------------------------------------------------------------------
def copy_var_in_group(ncingroup, ncoutgroup):
  fvname = '_FillValue'
 #copy all var in group.
  for varname, variable in ncingroup.variables.items():
    if(fvname in variable.__dict__):
      fill_value = variable.getncattr(fvname)
      newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions, fill_value=fill_value)
    else:
      newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions)
    copy_attributes(variable, newvar)

    if(1 == len(variable.dimensions)):
      newvar[:] = variable[:]
    elif(2 == len(variable.dimensions)):
      newvar[:,:] = variable[:,:]
    elif(3 == len(variable.dimensions)):
      newvar[:,:,:] = variable[:,:,:]

#-----------------------------------------------------------------------------------------
def create_var_in_group(ncingroup, ncoutgroup):
  fvname = '_FillValue'
 #copy all var in group.
  for varname, variable in ncingroup.variables.items():
    if(fvname in variable.__dict__):
      fill_value = variable.getncattr(fvname)
      newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions, fill_value=fill_value)
    else:
      newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions)
    copy_attributes(variable, newvar)

#-----------------------------------------------------------------------------------------
def copy_grp2newname(name, n, group, ncin, ncout):
  item = name.split('_')
  item[-1] = '%d' %(n)
  newname = '_'.join(item)
  print('create No %d from variable: %s, as: %s' %(n, name, newname))
  ncoutgroup = ncout.createGroup(newname)
 #copy_dimension(ncin, ncoutgroup)
  create_var_in_group(group, ncoutgroup)

#-----------------------------------------------------------------------------------------
def process(ncin, ncout, nmem):
  grplist = ['hofx_y_mean_xb0', 'ombg']

 #check groups
  for grpname, group in ncin.groups.items():
    print('grpname: ', grpname)
    if(grpname.find('hofx') < 0):
      ncoutgroup = ncout.createGroup(grpname)
     #copy_dimension(ncin, ncoutgroup)
      copy_var_in_group(group, ncoutgroup)
    else:
      if(grpname == 'hofx_y_mean_xb0'):
        ncoutgroup = ncout.createGroup(grpname)
       #copy_dimension(ncin, ncoutgroup)
        copy_var_in_group(group, ncoutgroup)
      else:
        for i in range(nmem):
          n = i + 1
          copy_grp2newname(grpname, n, group, ncin, ncout)

#-----------------------------------------------------------------------------------------
def create_file(infile, outfile, nmem):
  if(os.path.exists(infile)):
   #print('infile: ', infile)
    ncin = nc4.Dataset(infile, 'r')
  else:
    print('infile: %s does not exist.' %(infile))
    sys.exit(-1)

  if(os.path.exists(outfile)):
    os.remove(outfile)
    print('outfile: ', outfile)
 #else:
 #  print('outfile: %s does not exist.' %(outfile))

  ncout = nc4.Dataset(outfile, 'w')
 #ncout = nc4.Dataset(outfile, 'w', parallel=True, comm=comm,
 #                    info=MPI.Info(), format=format)

 #copy global attributes all at once via dictionary
 #ncout.setncatts(ncin.__dict__)
  ncout.source='JEDI observer only ouptut, each with only one member'
  ncout.comment = 'updated variable hofx_y_mean_xb0 and ombg from all observer files'

 #copy attributes
  for name in ncin.ncattrs():
    ncout.setncattr(name, ncin.getncattr(name))

  copy_dimension(ncin, ncout)
  copy_rootvar(ncin, ncout)

  process(ncin, ncout, nmem)
 
  ncin.close()
  ncout.close()

#-----------------------------------------------------------------------------------------
debug = 1
nmem = 80

rundir = '/work2/noaa/da/weihuang/cycling/gdas-cycling'
datestr = '2020010206'
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
infile = '%s/%s/observer/mem000/%s_obs_%s.nc4' %(rundir, datestr, obstype, datestr)
outfile = '%s/%s/observer/%s_obs_%s.nc4' %(rundir, datestr, obstype, datestr)

create_file(infile, outfile, nmem)

