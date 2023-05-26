#=========================================================================
import os
import sys
import time
import getopt
import logging

import numpy as np
from netCDF4 import Dataset

from mpi4py import MPI

#=========================================================================
class PyMPIConcatenateObserver():
  def __init__(self, debug=0, rundir=None, datestr=None,
               obstype='unknown', nmem=81):
    self.debug = debug
    self.rundir = rundir
    self.datestr = datestr
    self.obstype = obstype
    self.nmem = nmem

   #print("MPI.COMM_WORLD:", MPI.COMM_WORLD)
   #rank = MPI.COMM_WORLD.rank  # The process ID (integer 0-3 for 4-process run)
    self.comm = MPI.COMM_WORLD
    self.rank = self.comm.Get_rank()
    self.size = self.comm.Get_size()

    self.setup_logging()

    logging.debug('debug: %d' %(self.debug))
    logging.debug('rundir: %s' %(self.rundir))
    logging.debug('datestr: %s' %(self.datestr))
    logging.debug('nmem: %d' %(self.nmem))
    logging.warning('MPI size: %d' %(self.size))
    logging.warning('MY rank: %d' %(self.rank))

    if(self.nmem != self.size):
      logging.error('MPI size: %d does not equal to nmem: %d. Terminating' %(self.size, self.nmem))
      sys.exit(-1)

    self.setup()

#-----------------------------------------------------------------------------------------
  def setup_logging(self):
   #https://docs.python.org/3/howto/logging.html
   #logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
   #                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logflnm='log.%s.%4.4d' %(self.obstype, self.rank)
   #logging.basicConfig(filename=logflnm, format='%(asctime)s:%(levelname)s:%(message)s',
   #                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.basicConfig(filename=logflnm, filemode='w', level=logging.DEBUG)
    logging.debug('Start logging')
   #logging.info('So should this')
   #logging.warning('And this, too')
   #logging.error('And non-ASCII stuff, too, like Øresund and Malmö')

#-----------------------------------------------------------------------------------------
  def setup(self):
    obsdir = '%s/%s/observer' %(self.rundir, self.datestr)
    filename = '%s_obs_%s.nc4' %(self.obstype, self.datestr)

    self.inputfile = '%s/mem%3.3d/%s' %(obsdir, self.rank, filename)
    self.outputfile = '%s/%s' %(obsdir, filename)

    logging.debug('inputfile: %s' %(self.inputfile))
    logging.debug('outputfile: %s' %(self.outputfile))

    if(0 == self.rank):
      if(os.path.exists(self.outputfile)):
        os.remove(self.outputfile)

    self.comm.Barrier()

#-----------------------------------------------------------------------------------------
  def set_obstype(self, obstype):
    self.obstype = obstype
    self.setup_logging()
    self.setup()

#-----------------------------------------------------------------------------------------
  def mpi_average(self, varr):
    buf = np.zeros_like(varr)
    if(0 == self.rank):
      varr = 0.0
    
    self.comm.Allreduce(varr, buf, op=MPI.SUM)
    buf /= (self.nmem-1)

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
  def create_rootvar(self, ncin, ncout):
   #create all var in root group.
    for name, variable in ncin.variables.items():
      ncout.createVariable(name, variable.datatype, variable.dimensions)
     #copy variable attributes all at once via dictionary
      ncout[name].setncatts(ncin[name].__dict__)

#-----------------------------------------------------------------------------------------
  def write_rootvar(self, ncin, ncout):
   #copy all var in root group.
    for name, variable in ncin.variables.items():
      ncout.variables[name][:] = ncin.variables[name][:]

#-----------------------------------------------------------------------------------------
  def create_var_in_group(self, ncingroup, ncoutgroup, grpdict):
    fvname = '_FillValue'
   #create all var in group.
    for varname, variable in ncingroup.variables.items():
      if(fvname in variable.__dict__):
        fill_value = variable.getncattr(fvname)
        newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions, fill_value=fill_value)
      else:
        newvar = ncoutgroup.createVariable(varname, variable.datatype, variable.dimensions)
      self.copy_attributes(variable, newvar)
     #print('var: %s has dimension: %d' %(varname, len(variable.dimensions)))
      grpdict[varname] = {}
      grpdict[varname]['var'] = newvar
      grpdict[varname]['dim'] = len(variable.dimensions)

#-----------------------------------------------------------------------------------------
  def write_var_in_group(self, ncingroup, grpdict):
   #write all var in group.
    for varname, variable in ncingroup.variables.items():
      if(1 == grpdict[varname]['dim']):
        grpdict[varname]['var'][:] = ncingroup.variables[varname][:]
      elif(2 == grpdict[varname]['dim']):
        grpdict[varname]['var'][:,:] = ncingroup.variables[varname][:,:]

#-----------------------------------------------------------------------------------------
  def create_grp2newname(self, name, n, group, ncout, grpdict):
    item = name.split('_')
    item[-1] = '%d' %(n)
    newname = '_'.join(item)
   #print('No %d name: %s, newname: %s' %(n, name, newname))
    ncoutgroup = ncout.createGroup(newname)
    grpdict[newname] = {}
    self.create_var_in_group(group, ncoutgroup, grpdict[newname])

#-----------------------------------------------------------------------------------------
  def write_grp2newname(self, name, n, ncingroup, grpdict):
    if(n != self.rank):
      return

    item = name.split('_')
    item[-1] = '%d' %(n)
    newname = '_'.join(item)
   #print('No %d name: %s, newname: %s' %(n, name, newname))
    for varname, variable in ncingroup.variables.items():
      if(1 == grpdict[varname]['dim']):
        grpdict[newname][varname]['var'][:] = ncingroup.variables[varname][:]
      elif(2 == grpdict[varname]['dim']):
        grpdict[newname][varname]['var'][:,:] = ncingroup.variables[varname][:,:]

#-----------------------------------------------------------------------------------------
  def create_all_variables(self, grplist):
    self.grpnamelist = []
    self.hofxgrps = []
    self.commongrps = []
    self.ensvarinfo = {}

    self.newvardict = {}

    self.create_rootvar(self.IFILE, self.OFILE)

   #check groups
    for grpname, group in self.IFILE.groups.items():
     #print('grpname: ', grpname)
      self.grpnamelist.append(grpname)
      if(grpname in grplist):
        self.newvardict[grpname] = {}
        self.ensvarinfo[grpname] = {}
        for varname, variable in group.variables.items():
          self.ensvarinfo[grpname][varname] = group[varname][:]

        ncoutgroup = self.OFILE.createGroup(grpname)
        self.create_var_in_group(group, ncoutgroup, self.newvardict[grpname])
      else:
        if(grpname.find('hofx') < 0):
          self.commongrps.append(grpname)
          ncoutgroup = self.OFILE.createGroup(grpname)
          self.newvardict[grpname] = {}
          self.create_var_in_group(group, ncoutgroup, self.newvardict[grpname])
        else:
          self.hofxgrps.append(grpname)
          self.newvardict[grpname] = {}
          for n in range(1, self.size):
            self.create_grp2newname(grpname, n, group, self.OFILE, self.newvardict)

    print('len(self.grpnamelist) = %d' %(len(self.grpnamelist)))
    print('len(self.commongrps) = %d' %(len(self.commongrps)))
    print('len(self.hofxgrps) = %d' %(len(self.hofxgrps)))

#-----------------------------------------------------------------------------------------
  def print_minmax(self, name, val):
    print('\t%s min: %f, max: %f' %(np.max(val), np.min(val)))

#-----------------------------------------------------------------------------------------
  def process(self, grplist):
    self.create_all_variables(grplist)

    if(0 == self.rank):
      self.write_rootvar(self.IFILE, self.OFILE)

    for grpname in self.grpnamelist:
     #print('grpname: ', grpname)
      ncoutgroup = self.OFILE.groups[grpname]
      if(grpname in grplist):
        varlist = self.ensvarinfo[grpname].keys()
       #print('varlist = ', varlist)
        if('hofx0_1' == grpname):
          self.meanvars = {}
          for varname in varlist:
            print('get avearge for varname = ', varname)
            self.meanvars[varname] = self.mpi_average(self.ensvarinfo[grpname][varname])

          if(0 == self.rank):
            for varname in varlist:
              self.newvardict[grpname][varname][:] = self.meanvars[varname]
        elif('ombg' == grpname):
          if(0 == self.rank):
            for varname, variable in ncingroup.variables.items():
              val = self.ensvarinfo['ombg'][varname]
              val += self.ensvarinfo['hofx_y_mean_xb0'][varname]
              val -= self.meanvars[varname]
              self.newvardict[grpname][varname][:] = val

              self.print_minmax('hofx_y_mean_xb0', self.ensvarinfo['hofx_y_mean_xb0'][varname])
              self.print_minmax('old-ombg', self.ensvarinfo['ombg'][varname])
              self.print_minmax('new-ombg', val)
        elif('ombg' == grpname):
          if(0 == self.rank):
            for varname, variable in ncingroup.variables.items():
              self.newvardict[grpname][varname][:] = self.ensvarinfo[grpname][:]
        else:
          if(0 < self.rank):
            if(grpname.find('hofx') < 0):
              self.commongrps.append(grpname)
              self.write_var_in_group(group, self.newvardict[grpname])
            else:
              for n in range(1, self.size):
                self.write_grp2newname(grpname, n, group, self.newvardict)

#-----------------------------------------------------------------------------------------
  def concatenate(self, grplist):
    try:
      self.IFILE = Dataset(self.inputfile, 'r')
    except Exception as e:
      logging.error(f'Error occurred when attempting to read from: {self.inputfile}, error: {e}')

   #format = 'NETCDF4_CLASSIC'
    format = 'NETCDF4'

    self.OFILE = Dataset(self.outputfile, 'w', parallel=True, comm=self.comm,
                         info=MPI.Info(), format=format)
    logging.debug(f'Read data from {self.inputfile}')
    if(0 == self.rank):
      logging.debug(f'Write data to {self.outputfile}')

   #copy global attributes all at once via dictionary
   #ncout.setncatts(self.IFILE.__dict__)
    self.OFILE.source='JEDI observer only ouptut, each with only one member'
    self.OFILE.comment = 'updated variable hofx_y_mean_xb0 and ombg from all observer files'

   #copy attributes
    for name in self.IFILE.ncattrs():
      self.OFILE.setncattr(name, self.IFILE.getncattr(name))

    self.copy_dimension(self.IFILE, self.OFILE)

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
 #print('opts = ', opts)
 #print('args = ', args)

  for o, a in opts:
   #print('o: <%s>' %(o))
   #print('a: <%s>' %(a))
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--rundir'):
      rundir = a
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
                                            nmem=nmem, datestr=datestr)
  grplist = ['hofx_y_mean_xb0', 'hofx0_1', 'ombg']
  pyconcatenater.concatenate(grplist)

