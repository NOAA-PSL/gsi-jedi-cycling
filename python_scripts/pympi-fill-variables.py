import os, sys
import getopt
from mpi4py import MPI
import numpy as np
import netCDF4 as nc4

#=========================================================================
class PyMPIFillVariables():
  def __init__(self, debug=0, rundir=None, datestr=None, startmem=1, endmem=30):
    self.debug = debug
    self.datestr = datestr
    self.rundir = rundir
    self.startmem = startmem
    self.endmem = endmem

   #self.format = 'NETCDF4_CLASS'
    self.format = 'NETCDF4'

   #print("MPI.COMM_WORLD:", MPI.COMM_WORLD)
    self.comm = MPI.COMM_WORLD
    self.rank = self.comm.Get_rank()
    self.size = self.comm.Get_size()

    if(0 == self.rank):
      isExist = os.path.exists('logdir')
      if not isExist:
       #Create a new directory because it does not exist
        os.makedirs('logdir')

    self.comm.Barrier()
    
    self.setup()

    self.LOGFILE = None

  def setup(self):
    cnp = 0
    self.memlist = []
    for n inrange(self.nmem):
      mem = n + 1
      if(cnp == self.rank):
        self.memlist.append(mem)
      cnp += 1
      if(cnp >= self.size):
        cnp = 0

#-----------------------------------------------------------------------------------------
  def copy_dimensions(self, ncin, ncout):
    self.diminfo = {}
    for name, dimension in ncin.dimensions.items():
      if(self.debug):
        self.LOGFILE.write('dimension: %s has size: %d\n' %(name, dimension.size))
      ncout.createDimension(name, dimension.size)

      self.diminfo[name] = dimension.size

      if(self.debug):
        self.LOGFILE.write('Create dimension: %s, no. dim: %d\n' %(name, len(dimension)))

#-----------------------------------------------------------------------------------------
  def copy_attributes(self, ncin, ncout):
    inattrs = ncin.ncattrs()
    for attr in inattrs:
      if('_FillValue' != attr):
        ncout.setncattr(attr, ncin.getncattr(attr))

#-----------------------------------------------------------------------------------------
  def create_var_in_group(self, ingroup, outgroup):
    self.copy_attributes(ingroup, outgroup)

    fvname = '_FillValue'

   #create all var in group.
    for varname, variable in ingroup.variables.items():
      if(fvname in variable.__dict__):
        fill_value = variable.getncattr(fvname)
        newvar = outgroup.createVariable(varname, variable.datatype, variable.dimensions,
                                         fill_value=fill_value)
      else:
        newvar = outgroup.createVariable(varname, variable.datatype, variable.dimensions)

      self.copy_attributes(variable, newvar)

      if(self.debug):
        self.LOGFILE.write('\tcreate var: %s with %d dimension\n' %(varname, len(variable.dimensions)))

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
  def create_groups(self):
    obsdir = '%s/%s/observer' %(self.rundir, self.datestr)
    filename = '%s_obs_%s.nc4' %(self.obstype, self.datestr)

    outputfile = '%s/%s' %(obsdir, filename)

    if(self.debug):
      self.LOGFILE.write('outputfile: %s\n' %(outputfile))

    self.OFILE = nc4.Dataset(outputfile, 'a', parallel=True, comm=self.comm,
                             info=MPI.Info(), format=self.format)

    igroup = self.OFILE.groups['ombg']

    for m in range(self.nmem):
      mem = m + 1
      grpname = 'hofx0_%d' %(mem)
      ogroup = self.OFILE.createGroup(grpname)
      self.create_var_in_group(igroup, ogroup)
      for n in range(20):
        nv = n + 1
        grpname = 'hofxm0_%d_%d' %(nv, mem)
        ogroup = self.OFILE.createGroup(grpname)
        self.create_var_in_group(igroup, ogroup)
      mem += 1

    if(self.debug):
      self.LOGFILE.flush()

#-----------------------------------------------------------------------------------------
  def write_var_in_group(self, igroup, ogroup):
   #write all var in group.
    for name, ivar in igroup.variables.items():
      ovar = ogroup.variables[name]
      dim = len(ivar.dimensions)

      if(1 == dim):
        ovar[:] = ivar[:]
      elif(2 == dim):
        ovar[:,:] = ivar[:,:]
      elif(3 == dim):
        ovar[:,:,:] = ivar[:,:,:]

    if(self.debug):
      self.LOGFILE.write('\twrite variable: %s with dim: %d\n' %(name, dim))

#-----------------------------------------------------------------------------------------
  def output_file(self):
    for mem in self.memlist:
      if(self.debug):
        self.LOGFILE.write('write for mem: %d\n' %(mem))
      infile = '%s/mem%3.3d/%s' %(self.obsdir, mem, self.filename)
      IFILE = nc4.Dataset(infile, 'r')
      if(self.debug):
        self.LOGFILE.write('input file: %s\n' %(infile))
      igroup = IFILE.groups['hofx0_1']
      grpname = 'hofx0_%d' %(mem)
      ogroup = self.OFILE.createGroup(grpname)
      self.write_var_in_group(igroup, ogroup)

      for n in range(20):
        nv = n + 1
        igrpname = 'hofxm0_%d_1' %(nv)
        igroup = IFILE.groups[igrpname]
        ogrpname = 'hofxm0_%d_%d' %(nv, mem)
        ogroup = self.OFILE.groups[grpname]
        self.write_var_in_group(igroup, ogroup)
      
        if(self.debug):
          self.LOGFILE.write('write group %s from %s\n' %(ogrpname, igrpname))
          self.LOGFILE.flush()
 
      IFILE.close()

    if(self.debug):
      self.LOGFILE.flush()

#-----------------------------------------------------------------------------------------
  def process(self, obstype):
    self.obstype = obstype

    if(self.LOGFILE is not None):
      self.LOGFILE.close()

    logflnm='logdir/log.%s.%4.4d' %(self.obstype, self.rank)
    self.LOGFILE = open(logflnm, 'w')

    self.LOGFILE.write('size: %d\n' %(self.size))
    self.LOGFILE.write('rank: %d\n' %(self.rank))

    self.create_groups()

    self.debug = 1
    self.output_groups()

    self.RFILE.close()
    self.OFILE.close()

#=========================================================================================
if __name__== '__main__':
  debug = 0
  nmem = 80
  rundir = '/work2/noaa/da/weihuang/cycling/gdas-cycling'
  datestr = '2020010206'
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
  pyfv = PyMPIFillVariables(debug=debug, rundir=rundir,
                            nmem=nmem, datestr=datestr)
  pyfv.process(obstype)

