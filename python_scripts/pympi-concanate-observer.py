import os, sys
import getopt
from mpi4py import MPI
import numpy as np
from netCDF4 import Dataset

#=========================================================================
class PyMPIConcatenateObserver():
  def __init__(self, debug=0, rundir=None, datestr=None, nmem=81):
    self.debug = debug
    self.datestr = datestr
    self.rundir = rundir
    self.nmem = nmem

    self.specgrps = ['hofx_y_mean_xb0', 'hofx0_1', 'ombg']
    self.format = 'NETCDF4'
   #self.format = 'NETCDF4_CLASS'

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
    for n in range(nmem):
      if(cnp == self.rank):
        self.memlist.append(n)
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
  def get_newname(self, name, n):
    item = name.split('_')
    item[-1] = '%d' %(n)
    newname = '_'.join(item)
   #self.LOGFILE.write('No %d name: %s, newname: %s\n' %(n, name, newname))
    return newname

#-----------------------------------------------------------------------------------------
  def create_var_in_group(self, ingroup, outgroup):
    self.copy_attributes(ingroup, outgroup)

    fvname = '_FillValue'
    vardict = {}

   #create all var in group.
    for varname, variable in ingroup.variables.items():
     #newvar = 'a variable'
     #if(fvname in variable.__dict__):
     #  fill_value = variable.getncattr(fvname)
     #  newvar = outgroup.createVariable(varname, variable.datatype, variable.dimensions,
     #                                   fill_value=fill_value)
     #else:
     #  newvar = outgroup.createVariable(varname, variable.datatype, variable.dimensions)
      newvar = outgroup.createVariable(varname, variable.datatype, variable.dimensions)
      if(self.debug):
        self.LOGFILE.write('\tcreate var: %s with %d dimension\n' %(varname, len(variable.dimensions)))

      vardict[varname] = {}
      vardict[varname]['var'] = newvar
      dimsize = len(variable.dimensions)
      vardict[varname]['dim'] = dimsize

    return vardict

#-----------------------------------------------------------------------------------------
  def get_varinfo(self, ingroup):
    varinfo = {}

   #create all var in group.
    for varname, variable in ingroup.variables.items():
      varinfo[varname] = variable

    return varinfo

#-----------------------------------------------------------------------------------------
  def read_var(self, name, variable):
    if(1 == len(variable.dimensions)):
      val = variable[:]
    elif(2 == len(variable.dimensions)):
      val = variable[:,:]
    elif(3 == len(variable.dimensions)):
      val = variable[:,:,:]

#-----------------------------------------------------------------------------------------
  def get_fileinfo(self):
    self.rootvarinfo = self.get_varinfo(self.RFILE)

    igroups = self.RFILE.groups

    self.grpinfo = []

    for grpname, group in igroups.items():
      self.grpinfo[grpname] = self.get_varinfo(group)

#-----------------------------------------------------------------------------------------
  def create_file(self, rootfile=None, outfile=None):
    self.rootfile = rootfile
    self.outfile = outfile

    if(0 == self.rank):
      if(os.path.exists(self.outfile)):
        os.remove(self.outfile)

    self.comm.Barrier()

    self.OFILE = Dataset(self.outfile, 'w', parallel=True, comm=self.comm,
                         info=MPI.Info(), format=self.format)

    self.RFILE = Dataset(self.rootfile, 'r')

    self.copy_dimensions(self.RFILE, self.OFILE)
    self.rootvardict = self.create_var_in_group(self.RFILE, self.OFILE)

    igroups = self.RFILE.groups

    self.ensvar = {}
    self.outdict = {}
    self.comgrps = []
    self.memgrps = []

    for grpname, group in igroups.items():
      if(grpname.find('hofx') < 0):
        self.comgrps.append(grpname)
      else:
        if('hofx_y_mean_xb0' == grpname):
          self.comgrps.append(grpname)
        else:
          self.memgrps.append(grpname)

        if(grpname in self.specgrps):
          self.ensvar[grpname] = {}
          for varname, variable in group.variables.items():
            self.ensvar[grpname][varname] = self.read_var(varname, variable)

    self.comdict = {}
    for grpname in self.comgrps:
      if(self.debug):
        self.LOGFILE.write('Create common group: %s\n' %(grpname))
        self.LOGFILE.flush()
      group = igroups[grpname]
      ogroup = self.OFILE.createGroup(grpname)
      for name in self.diminfo.keys():
        ogroup.createDimension(name, self.diminfo[name])
      vardict = self.create_var_in_group(group, ogroup)
      if(0 == self.rank):
        self.comdict[grpname] = vardict

    for mem in range(1, self.nmem):
      self.outdict[mem] = {}
      self.outdict[mem]['oldname'] = []
      self.outdict[mem]['newname'] = []
      self.outdict[mem]['vardict'] = []

    for grpname in self.memgrps:
      group = igroups[grpname]
      for mem in range(1, self.nmem):
        newname = self.get_newname(grpname, mem)
        ogroup = self.OFILE.createGroup(newname)

        if(self.debug):
          self.LOGFILE.write('Create group: %s from: %s\n' %(newname, grpname))
          self.LOGFILE.flush()

        for name in self.diminfo.keys():
          ogroup.createDimension(name, self.diminfo[name])
        vardict = self.create_var_in_group(group, ogroup)

        if(mem in self.memlist):
          self.outdict[mem]['oldname'].append(grpname)
          self.outdict[mem]['newname'].append(newname)
          self.outdict[mem]['vardict'].append(vardict)

    if(self.debug):
      self.LOGFILE.flush()

#-----------------------------------------------------------------------------------------
  def write_var(self, var, dim, varname, ingroup):
    if(1 == dim):
      var[:] = ingroup.variables[varname][:]
    elif(2 == dim):
      var[:,:] = ingroup.variables[varname][:,:]
    elif(3 == dim):
      var[:,:,:] = ingroup.variables[varname][:,:,:]
    if(self.debug):
      self.LOGFILE.write('\twrite variable: %s with dim: %d\n' %(varname, dim))

#-----------------------------------------------------------------------------------------
  def write_var_in_group(self, ingroup, vardict):
   #write all var in group.
    for varname in vardict.keys():
      var = vardict[varname]['var']
      dim = vardict[varname]['dim']
      if(self.debug):
        self.LOGFILE.write('\twrite variable: %s with dim: %d\n' %(varname, dim))
      self.write_var(var, dim, varname, ingroup)

#-----------------------------------------------------------------------------------------
  def output_file(self):
    if(0 == self.rank):
      if(self.debug):
        self.LOGFILE.write('write root variables\n')
      self.write_var_in_group(self.RFILE, self.rootvardict)
      igroups = self.RFILE.groups
      for grpname in self.comgrps:
        if(self.debug):
          self.LOGFILE.write('write group: %s\n' %(grpname))
        group = igroups[grpname]
        self.write_var_in_group(group, self.comdict[grpname])

    if(self.debug):
      self.LOGFILE.flush()

    for mem in self.memlist:
      if(0 == mem):
        continue

      if(self.debug):
        self.LOGFILE.write('write for mem: %d\n' %(mem))
      infile = '%s/mem%3.3d/%s' %(self.obsdir, mem, self.filename)
      IFILE = Dataset(infile, 'r')
      if(self.debug):
        self.LOGFILE.write('input file: %s\n' %(infile))
      igroups = IFILE.groups
      if(self.debug):
        self.LOGFILE.write('length of self.outdict[mem]["oldname"]: %d\n' %(len(self.outdict[mem]['oldname'])))
      for n in range(len(self.outdict[mem]['oldname'])):
        grpname = self.outdict[mem]['oldname'][n]
        newname = self.outdict[mem]['newname'][n]
        group = igroups[grpname]
        vardict = self.outdict[mem]['vardict'][n]
        self.write_var_in_group(group, vardict)
      
        if(self.debug):
          self.LOGFILE.write('write group %s from %s\n' %(newname, grpname))
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

    self.obsdir = '%s/%s/observer' %(self.rundir, self.datestr)
    self.filename = '%s_obs_%s.nc4' %(self.obstype, self.datestr)

    self.rootfile = '%s/mem000/%s' %(self.obsdir, self.filename)
    self.outputfile = '%s/%s' %(self.obsdir, self.filename)

    if(self.debug):
      self.LOGFILE.write('rootfile: %s\n' %(self.rootfile))
      self.LOGFILE.write('outputfile: %s\n' %(self.outputfile))

    self.create_file(rootfile=self.rootfile, outfile=self.outputfile)

    self.debug = 1
    self.output_file()

    self.RFILE.close()
    self.OFILE.close()

#=========================================================================================
if __name__== '__main__':
  debug = 0
  nmem = 81
  rundir = '/work2/noaa/da/weihuang/cycling/gdas-cycling'
  datestr = '2020010200'
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
  pyconcatenater = PyMPIConcatenateObserver(debug=debug, rundir=rundir,
                                            nmem=nmem, datestr=datestr)
  pyconcatenater.process(obstype)

