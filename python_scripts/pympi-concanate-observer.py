#=========================================================================
import os
import sys
import time
import getopt
import logging

import numpy as np
import netCDF4 as nc4

from mpi4py import MPI

#=========================================================================
class PyMPIConcatenateObserver():
  def __init__(self, debug=0, rundir=None, datestr=None,
               obstype='Unknown', nmem=81):
    self.debug = debug
    self.rundir = rundir
    self.datestr = datestr
    self.nmem = nmem

   #print("MPI.COMM_WORLD:", MPI.COMM_WORLD)
   #rank = MPI.COMM_WORLD.rank  # The process ID (integer 0-3 for 4-process run)
    self.comm = MPI.COMM_WORLD
    self.rank = self.comm.Get_rank()
    self.size = self.comm.Get_size()

    print('debug:', self.debug)
    print('rundir:', self.rundir)
    print('datestr:', self.datestr)
    print('nmem:', self.nmem)
    print('size:', self.size)
    print('rank:', self.rank)

    if(nmem != size):
      print('MPI size: %d does not equal to nmem: %d. Terminating' %(self.size, nmem))
      sys.exit(-1)

    self.setup_logging()

    self.set_obstype(obstype)

#-----------------------------------------------------------------------------------------
  def setup_logging(self):
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

#-----------------------------------------------------------------------------------------
  def setup(self):
    print('obstype:', self.obstype)
    print('rundir:', self.rundir)
    print('datestr:', self.datestr)
    print('nmem:', self.nmem)
    print('size:', self.size)
    obsdir = '%s/%s/observer' %(self.rundir, self.datestr)
    filename = '%s_obs_%s.nc4' %(self.obstype, self.datestr)

    self.inputfile = '%s/mem%3.3d/%s' %(obsdir, self.rank, filename)
    self.outputfile = '%s/%s' %(obsdir, filename)

    if(0 == rank):
      if(os.path.exists(self.outputfile)):
        os.remove(self.outputfile)

    self.comm.Barrier()

    try:
      self.IFILE = open(self.inputfile, 'r')
      self.OFILE = open(self.outputfile, 'w', parallel=True, comm=comm,
                        info=MPI.Info(), format=format)
      logging.info(f'Read data from {self.inputfile}')
      if(0 == rank):
        logging.info(f'Write data to {self.outputfile}')
    except Exception as e:
      logging.error(f'Error occurred when attempting to read from: {self.inputfile}, error: {e}')

   #self.IFILE.close()
   #self.OFILE.close()

#-----------------------------------------------------------------------------------------
  def set_obstype(self, obstype):
    self.obstype = obstype

    self.setup()

#-----------------------------------------------------------------------------------------
  def average(self, vlist):
    buf = np.zeros_like(vlist[0])
    nmem = len(vlist)
    for n in range(1, nmem):
      buf += vlist[n]
    buf /= (nmem-1)
    return buf

#-----------------------------------------------------------------------------------------
  def copy_dimension(self, ncin, ncout):
   #copy dimensions
    for name, dimension in ncin.dimensions.items():
     #ncout.createDimension(name, (len(dimension) if not dimension.isunlimited() else None))
      if dimension.isunlimited():
        ncout.createDimension(name, None)
      else:
        ncout.createDimension(name, len(dimension))

#-----------------------------------------------------------------------------------------
  def copy_attributes(self, ncin, ncout):
   #copy the global attributes to the new file
    inattrs = ncin.ncattrs()
    for attr in inattrs:
      if('_FillValue' != attr):
        ncout.setncattr(attr, ncin.getncattr(attr))

#-----------------------------------------------------------------------------------------
  def copy_rootvar(self, ncin, ncout):
   #copy all var in root group.
    for name, variable in ncin.variables.items():
      ncout.createVariable(name, variable.datatype, variable.dimensions)
     #copy variable attributes all at once via dictionary
      ncout[name].setncatts(ncin[name].__dict__)
      ncout[name][:] = ncin[name][:]

#-----------------------------------------------------------------------------------------
  def copy_var_in_group(self, ncingroup, ncoutgroup):
    fvname = '_FillValue'
   #copy all var in group.
    for varname, variable in ncingroup.variables.items():
      if(fvname in variable.__dict__):
        fill_value = variable.getncattr(fvname)
        newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions, fill_value=fill_value)
      else:
        newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions)
      copy_attributes(variable, newvar)
      newvar[:] = ncingroup[varname][:]

#-----------------------------------------------------------------------------------------
  def copy_grp2newname(self, name, n, group, ncout):
    item = name.split('_')
    item[-1] = '%d' %(n)
    newname = '_'.join(item)
    print('No %d name: %s, newname: %s' %(n, name, newname))
    ncoutgroup = ncout.createGroup(newname)
    self.copy_var_in_group(group, ncoutgroup)

#-----------------------------------------------------------------------------------------
  def process(self, grplist):
    grpnamelist = []
    hofxgrps = []
    commongrps = []
    ensvarinfo = {}

   #check groups
    for grpname, group in self.IFILE.groups.items():
      print('grpname: ', grpname)
      grpnamelist.append(grpname)
      if(grpname in grplist):
        ensvarinfo[grpname] = {}
        if(grpname == 'hofx0_1'):
          for varname, variable in group.variables.items():
           #val = group[varname][:]
            ensvarinfo[grpname][varname] = []
           #ensvarinfo[grpname][varname].append(val)
        else:
          if(grpname == 'hofx_y_mean_xb0'):
            ncoutgroup = ncout.createGroup(grpname)
            copy_var_in_group(group, ncoutgroup)

          for varname, variable in group.variables.items():
            val = group[varname][:]
            ensvarinfo[grpname][varname] = val
      else:
        if(grpname.find('hofx') < 0):
          commongrps.append(grpname)
          ncoutgroup = ncout.createGroup(grpname)
          copy_var_in_group(group, ncoutgroup)
        else:
          hofxgrps.append(grpname)

    print('len(grpnamelist) = %d, len(commongrps) = %d, len(hofxgrps) = %d' %(len(grpnamelist), len(commongrps), len(hofxgrps)))

    grpname = 'hofx0_1'
    for n in range(1, len(ncinlist)):
      ncin = ncinlist[n]
      for name in hofxgrps:
        group = ncin.groups[name]
        self.copy_grp2newname(name, n, group, ncout)

      group = ncin.groups[grpname]
      self.copy_grp2newname(grpname, n, group, ncout)

      for varname, variable in group.variables.items():
        val = group[varname][:]
        ensvarinfo[grpname][varname].append(val)

    varlist = ensvarinfo['hofx0_1'].keys()
   #print('varlist = ', varlist)
    meanvars = {}
    ncoutgroup = ncout.createGroup(grpname)
    for varname in varlist:
      meanval = average(ensvarinfo[grpname][varname])
      print('get avearge for varname = ', varname)
     #print('meanval.shape = ', meanval.shape)
     #print('meanval.size = ', meanval.size)
      meanvars[varname] = meanval

    grpname = 'ombg'
    ncingroup = ncinlist[0].groups[grpname]
    ncoutgroup = ncout.createGroup(grpname)
    fvname = '_FillValue'
   #copy all var in group.
    for varname, variable in ncingroup.variables.items():
      if(fvname in variable.__dict__):
        fill_value = variable.getncattr(fvname)
        newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions, fill_value=fill_value)
      else:
        newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions)
      copy_attributes(variable, newvar)
      val = ensvarinfo[grpname][varname] + ensvarinfo['hofx_y_mean_xb0'][varname] - meanvars[varname]
      print('\told-ombg.max: %f, old-ombg.min: %f' %(np.max(ensvarinfo[grpname][varname]), np.min(ensvarinfo[grpname][varname])))
      print('\thofx_y_mean_zb0.max: %f, hofx_y_mean_zb0.min: %f' %(np.max(ensvarinfo['hofx_y_mean_xb0'][varname]), np.min(ensvarinfo['hofx_y_mean_xb0'][varname])))
      print('\tmeanvars.max: %f, meanvars.min: %f' %(np.max(meanvars[varname]), np.min(meanvars[varname])))
      print('\tnew-ombg.max: %f, new-ombg.min: %f' %(np.max(val), np.min(val)))
     #val = ensvarinfo[grpname][varname]
      newvar[:] = val[:]

#-----------------------------------------------------------------------------------------
  def concatenate(self, grplist):
   #copy global attributes all at once via dictionary
   #ncout.setncatts(ncin.__dict__)
    self.OFILE.source='JEDI observer only ouptut, each with only one member'
    self.OFILE.comment = 'updated variable hofx_y_mean_xb0 and ombg from all observer files'

   #copy attributes
    for name in self.IFILE.ncattrs():
      self.OFILE.setncattr(name, self.IFILE.getncattr(name))

    self.copy_dimension(self.IFILE, ncout)

    if(0 == self.rank):
      self.copy_rootvar(self.IFILE, ncout)

    self.process(grplist)
 
    self.IFILE.close()
    self.OFILE.close()

#-----------------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  rundir = '/work2/noaa/da/weihuang/cycling/gdas-cycling'
  datestr = '2020010200'
  nmem = 81
  obstype = 'sondes'
  obstypelist = ['sfc_ps', 'sfcship_ps', 'sondes_ps',
                 'sondes', 'amsua_n15', 'amsua_n18', 'amsua_n19']

 #--------------------------------------------------------------------------------
  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'rundir=', 'obstype=',
                                                'nmem=', 'datestr='])
  print('opts = ', opts)
  print('args = ', args)

  for o, a in opts:
    print('o: <%s>' %(o))
    print('a: <%s>' %(a))
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--obsdir'):
      obsdir = a
    elif o in ('--obstype'):
      obstype = a
    elif o in ('--datestr'):
      datestr = a
    elif o in ('--nmem'):
      nmem = int(a)
    else:
      print('o: <%s>' %(o))
      print('a: <%s>' %(a))
      assert False, 'unhandled option'

 #--------------------------------------------------------------------------------
  pyconcatenater = PyMPIConcatenateObserver(debug=debug, rundir=rundir, obstype=obstype,
                                            nmem=neme, datestr=datestr)
  grplist = ['hofx_y_mean_xb0', 'hofx0_1', 'ombg']
  pyconcatenater.concatenate(grplist)

