#=========================================================================
import os
import sys
import getopt

from mpi4py import MPI

import numpy as np
from netCDF4 import Dataset

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

    if(self.nmem != self.size):
      self.LOGFILE.write('MPI size: %d does not equal to nmem: %d. Terminating' %(self.size, self.nmem))
      sys.exit(-1)

    if(0 == self.rank):
      isExist = os.path.exists('logdir')
      if not isExist:
       #Create a new directory because it does not exist
        os.makedirs('logdir')

    self.comm.Barrier()

    logflnm='logdir/log.%s.%4.4d' %(self.obstype, self.rank)
    self.LOGFILE = open(logflnm, 'w')

    self.LOGFILE.write('debug: %d\n' %(self.debug))
    self.LOGFILE.write('rundir: %s\n' %(self.rundir))
    self.LOGFILE.write('datestr: %s\n' %(self.datestr))
    self.LOGFILE.write('nmem: %d\n' %(self.nmem))
    self.LOGFILE.write('MPI size: %d\n' %(self.size))
    self.LOGFILE.write('MY rank: %d\n' %(self.rank))

    self.LOGFILE.flush()

    self.comm.Barrier()

    self.setup()

#-----------------------------------------------------------------------------------------
  def setup(self):
    obsdir = '%s/%s/observer' %(self.rundir, self.datestr)
    filename = '%s_obs_%s.nc4' %(self.obstype, self.datestr)

    self.inputfile = '%s/mem%3.3d/%s' %(obsdir, self.rank, filename)
    self.outputfile = '%s/%s' %(obsdir, filename)

    self.LOGFILE.write('inputfile: %s\n' %(self.inputfile))
    self.LOGFILE.write('outputfile: %s\n' %(self.outputfile))

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

      self.LOGFILE.write('Create dimension: %s, no. dim: %d\n' %(name, len(dimension)))

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
      rv = ncout.createVariable(name, variable.datatype, variable.dimensions)
     #copy variable attributes all at once via dictionary
     #ncout.variables[name].setncatts(ncin.variables[name].__dict__)
      rv.setncatts(variable.__dict__)
      self.rootvardict[name] = rv

#-----------------------------------------------------------------------------------------
  def write_rootvar(self, ncin, ncout):
    self.LOGFILE.write('in write_rootvar on rank: %d\n' %(self.rank))
    self.LOGFILE.flush()
   #copy all var in root group.
    for name, variable in ncin.variables.items():
      self.LOGFILE.write('write rootvar: %s on rank: %d\n' %(name, self.rank))
     #self.rootvardict[name][:] = variable[:]
    self.LOGFILE.flush()

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
     #self.LOGFILE.write('var: %s has dimension: %d\n' %(varname, len(variable.dimensions)))
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
  def get_newname(self, name, n):
    item = name.split('_')
    item[-1] = '%d' %(n)
    newname = '_'.join(item)
   #self.LOGFILE.write('No %d name: %s, newname: %s\n' %(n, name, newname))
    return newname

#-----------------------------------------------------------------------------------------
  def create_grp2newname(self, name, n, group, ncout, grpdict):
    newname = self.get_newname(name, n)
    ncoutgroup = ncout.createGroup(newname)
    grpdict[newname] = {}
    self.create_var_in_group(group, ncoutgroup, grpdict[newname])

#-----------------------------------------------------------------------------------------
  def write_grp2newname(self, name, n, ncingroup, grpdict):
    newname = self.get_newname(name, n)
    self.LOGFILE.write('No %d name: %s, newname: %s\n' %(n, name, newname))

    for varname, variable in ncingroup.variables.items():
      if(1 == grpdict[newname][varname]['dim']):
        grpdict[newname][varname]['var'][:] = ncingroup.variables[varname][:]
      elif(2 == grpdict[newname][varname]['dim']):
        grpdict[newname][varname]['var'][:,:] = ncingroup.variables[varname][:,:]

#-----------------------------------------------------------------------------------------
  def create_all_variables(self, grplist):
    self.grpnamelist = []
    self.hofxgrps = []
    self.commongrps = []
    self.ensvarinfo = {}

    self.newvardict = {}

    self.rootvardict = {}

   #copy attributes
    for name in self.IFILE.ncattrs():
      self.OFILE.setncattr(name, self.IFILE.getncattr(name))

    self.copy_dimension(self.IFILE, self.OFILE)

    self.create_rootvar(self.IFILE, self.OFILE)

   #check groups
    for grpname, group in self.IFILE.groups.items():
      self.LOGFILE.write('create grpname: %s on rank: %d\n' %(grpname, self.rank))
      if(grpname in grplist):
        self.ensvarinfo[grpname] = {}
        for varname, variable in group.variables.items():
          if(1 == len(variable.dimensions)):
            self.ensvarinfo[grpname][varname] = group.variables[varname][:]
          elif(2 == len(variable.dimensions)):
            self.ensvarinfo[grpname][varname] = group.variables[varname][:,:]

        if('hofx0_1' == grpname):
          for n in range(1, self.size):
            newgrpname = self.get_newname(grpname, n)
            self.newvardict[newgrpname] = {}
            ncoutgroup = self.OFILE.createGroup(newgrpname)
            self.create_var_in_group(group, ncoutgroup, self.newvardict[newgrpname])
            if(n == self.rank):
              self.grpnamelist.append(newgrpname)
        else:
          self.newvardict[grpname] = {}
          ncoutgroup = self.OFILE.createGroup(grpname)
          self.create_var_in_group(group, ncoutgroup, self.newvardict[grpname])
          self.grpnamelist.append(grpname)
      else:
        if(grpname.find('hofx') < 0):
          self.commongrps.append(grpname)
          ncoutgroup = self.OFILE.createGroup(grpname)
          self.newvardict[grpname] = {}
          self.create_var_in_group(group, ncoutgroup, self.newvardict[grpname])
          self.grpnamelist.append(grpname)
        else:
          self.hofxgrps.append(grpname)
          for n in range(1, self.size):
            self.create_grp2newname(grpname, n, group, self.OFILE, self.newvardict)
            newgrpname = self.get_newname(grpname, n)
            if(n == self.rank):
              self.grpnamelist.append(newgrpname)

    self.LOGFILE.write('len(self.grpnamelist) = %d\n' %(len(self.grpnamelist)))
    self.LOGFILE.write('len(self.commongrps) = %d\n' %(len(self.commongrps)))
    self.LOGFILE.write('len(self.hofxgrps) = %d\n' %(len(self.hofxgrps)))

    self.LOGFILE.write('finished create group on rank: %4.4d.\n' %(self.rank))

    self.LOGFILE.flush()

   #self.comm.Barrier()

#-----------------------------------------------------------------------------------------
  def print_minmax(self, name, val):
    self.LOGFILE.write('\t%s min: %f, max: %f\n' %(np.max(val), np.min(val)))

#-----------------------------------------------------------------------------------------
  def process(self, grplist):
    self.create_all_variables(grplist)

    self.LOGFILE.write('Before writing root var on rank: %d\n' %(self.rank))
    self.LOGFILE.flush()

    if(0 == self.rank):
      self.write_rootvar(self.IFILE, self.OFILE)

    self.LOGFILE.write('After writing root var on rank: %d\n' %(self.rank))
    self.LOGFILE.flush()

    for grpname in self.grpnamelist:
      self.LOGFILE.write('writing grpname: %s on rank: %d\n' %(grpname, self.rank))
      ncoutgroup = self.OFILE.groups[grpname]
      if(grpname in grplist):
        varlist = self.ensvarinfo[grpname].keys()
        if('hofx0_1' == grpname):
          self.meanvars = {}
          for varname in varlist:
            self.LOGFILE.write('get avearge for varname: %s\n' %(varname))
            self.meanvars[varname] = self.mpi_average(self.ensvarinfo[grpname][varname])

          if(0 < self.rank):
            newgrpname = self.get_newname(grpname, self.rank)
            for varname in varlist:
              if(1 == self.newvardict[newgrpname][varname]['dim']):
                self.newvardict[newgrpname][varname][:] = self.meanvars[varname]
              elif(2 == self.newvardict[newgrpname][varname]['dim']):
                self.newvardict[newgrpname][varname][:,:] = self.meanvars[varname]
        elif('ombg' == grpname):
          if(0 == self.rank):
            ncingroup = self.IFILE.groups[grpname]
            for varname, variable in ncingroup.variables.items():
              val = self.ensvarinfo['ombg'][varname]
              val += self.ensvarinfo['hofx_y_mean_xb0'][varname]
              val -= self.meanvars[varname]
              if(1 == self.newvardict[grpname][varname]['dim']):
                 self.newvardict[grpname][varname]['var'][:] = val
              elif(2 == self.newvardict[grpname][varname]['dim']):
                 self.newvardict[grpname][varname]['var'][:,:] = val

              self.print_minmax('hofx_y_mean_xb0', self.ensvarinfo['hofx_y_mean_xb0'][varname])
              self.print_minmax('old-ombg', self.ensvarinfo['ombg'][varname])
              self.print_minmax('new-ombg', val)
        elif('hofx_y_mean_xb0' == grpname):
          if(0 == self.rank):
            ncingroup = self.IFILE.groups[grpname]
            for varname, variable in ncingroup.variables.items():
              if(1 == self.newvardict[grpname][varname]['dim']):
                 self.newvardict[grpname][varname]['var'][:] = self.ensvarinfo[grpname][varname]
              elif(2 == self.newvardict[grpname][varname]['dim']):
                 self.newvardict[grpname][varname]['var'][:,:] = self.ensvarinfo[grpname][varname]
        else:
          if(0 < self.rank):
            if(grpname.find('hofx') < 0):
              self.write_var_in_group(group, self.newvardict[grpname])
            else:
              self.write_grp2newname(grpname, self.rank, group, self.newvardict)

#-----------------------------------------------------------------------------------------
  def concatenate(self, grplist):
    try:
      self.IFILE = Dataset(self.inputfile, 'r')
    except Exception as e:
      self.LOGFILE.write(f'Error occurred when attempting to read from: {self.inputfile}, error: {e}\n')

   #format = 'NETCDF4_CLASSIC'
    format = 'NETCDF4'

    self.OFILE = Dataset(self.outputfile, 'w', parallel=True, comm=self.comm,
                         info=MPI.Info(), format=format)

    self.LOGFILE.write(f'Read data from {self.inputfile}\n')
    self.LOGFILE.write(f'Write data to {self.outputfile}\n')

   #copy global attributes all at once via dictionary
   #ncout.setncatts(self.IFILE.__dict__)
    self.OFILE.source='JEDI observer only ouptut, each with only one member'
    self.OFILE.comment = 'updated variable hofx_y_mean_xb0 and ombg from all observer files'

    self.process(grplist)
 
    self.comm.Barrier()
    self.IFILE.close()

    self.comm.Barrier()
    self.LOGFILE.write('before close OFILE on rank: %4.4d.\n' %(self.rank))

    self.OFILE.close()

    self.LOGFILE.write('after close OFILE on rank: %4.4d.\n' %(self.rank))
    self.comm.Barrier()

    self.LOGFILE.close()

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
   #self.LOGFILE.write('o: <%s>\n' %(o))
   #self.LOGFILE.write('a: <%s>\n' %(a))
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
      self.LOGFILE.write('o: <%s>\n' %(o))
      self.LOGFILE.write('a: <%s>\n' %(a))
      assert False, 'unhandled option'

 #--------------------------------------------------------------------------------
  pyconcatenater = PyMPIConcatenateObserver(debug=debug, rundir=rundir, obstype=obstype,
                                            nmem=nmem, datestr=datestr)
  grplist = ['hofx_y_mean_xb0', 'hofx0_1', 'ombg']
  pyconcatenater.concatenate(grplist)

