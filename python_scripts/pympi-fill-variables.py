import os, sys
import getopt
import numpy as np
import netCDF4 as nc4

from mpi4py import MPI

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
    for i in range(nmem):
      mem = i + 1
      if(cnp == self.rank):
        self.memlist.append(mem)
      cnp += 1
      if(cnp >= self.size):
        cnp = 0

#-----------------------------------------------------------------------------------------
  def get_newname(self, name, n):
    item = name.split('_')
    item[-1] = '%d' %(n)
    newname = '_'.join(item)
   #self.LOGFILE.write('No %d name: %s, newname: %s\n' %(n, name, newname))
    return newname

#-----------------------------------------------------------------------------------------
  def get_varinfo(self, ingroup):
    varinfo = {}

   #create all var in group.
    for varname, variable in ingroup.variables.items():
      varinfo[varname] = variable

    return varinfo

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
  def access_file(self, outfile=None):
    self.outfile = outfile

    self.OFILE = nc4.Dataset(self.outfile, 'r+', parallel=True, comm=self.comm,
                             info=MPI.Info(), format=self.format)

    self.specvars = {}

    for n in range(self.nmem):
      mem = n + 1
      self.specvars[mem] = {}
      for grpname in ['ombg', 'hofx_y_mean_xb0']:
        group = self.OFILE.groups[grpname]
        self.specvars[mem][grpname] = {}
        for varname, variable in group.variables.items():
          self.specvars[mem][grpname][varname] = self.read_var(varname, variable)

   #for grpname in ['ombg', 'hofx_y_mean_xb0']:
   #  group = self.OFILE.groups[grpname]
   #  for mem in self.memlist:
   #    self.specvars[mem][grpname] = {}
   #    for varname, variable in group.variables.items():
   #      self.specvars[mem][grpname][varname] = self.read_var(varname, variable)

    if(self.debug):
      self.LOGFILE.flush()

#-----------------------------------------------------------------------------------------
  def write_var(self, var, variable):
    dim = len(variable.dimensions)
    var.set_collective(True)
    if(1 == dim):
      var[:] = variable[:]
    elif(2 == dim):
      var[:,:] = variable[:,:]
    elif(3 == dim):
      var[:,:,:] = variable[:,:,:]

#-----------------------------------------------------------------------------------------
  def write_var_in_group(self, ingroup, outgroup):
   #write all var in group.
    for varname, variable in ingroup.variables.items():
      var = outgroup.variables[varname]
      self.write_var(var, variable)

      if(self.debug):
        self.LOGFILE.write('\twrite variable: %s\n' %(varname))

#-----------------------------------------------------------------------------------------
  def mpi_average(self, grpname, varlist):
    meanvars = {}

    for varname in varlist:
      nv = 0
      for mem in self.memlist:
        val = self.specvars[mem][grpname][varname]
        if(self.debug):
          self.LOGFILE.write('use specvars[%d][%s][%s]\n' %(mem, grpname, varname))
        if(0 == nv):
          buf = val
        else:
          buf += val
        nv += 1
    
      self.comm.Allreduce(buf, val, op=MPI.SUM)
      val /= self.nmem
      meanvars[varname] = val

    return meanvars

#-----------------------------------------------------------------------------------------
  def print_minmax(self, name, val):
    if(self.debug):
      self.LOGFILE.write('\t%s min: %f, max: %f\n' %(name, np.max(val), np.min(val)))

#-----------------------------------------------------------------------------------------
  def process_ombg(self):
    self.LOGFILE.write('processing for ombg on rank: %d\n' %(self.rank))
    self.LOGFILE.flush()

    mem = self.memlist[0]
    grpname = 'hofx0_1'
    varlist = self.specvars[mem][grpname].keys()

    self.LOGFILE.write('get avearge ombg\n')
    meanvars = self.mpi_average(grpname, varlist)

    if(self.rank):
      return

    grpname = 'ombg'
    for varname in varlist:
      val = self.specvars[mem]['ombg'][varname]
      val += self.specvars[mem]['hofx_y_mean_xb0'][varname]
      val -= meanvars[varname]

      var = self.OFILE.groups[grpname].variables[varname]
      dim = len(var.dimensions)
      if(1 == dim):
         var[:] = val
      elif(2 == dim):
         var[:,:] = val
      elif(3 == dim):
         var[:,:,:] = val

      self.print_minmax('hofx_y_mean_xb0', self.specvars[self.memlist[0]]['hofx_y_mean_xb0'][varname])
      self.print_minmax('old-ombg', self.specvars[self.memlist[0]]['ombg'][varname])
      self.print_minmax('new-ombg', val)

#-----------------------------------------------------------------------------------------
  def output_file(self):
    if(self.debug):
      self.LOGFILE.flush()

    self.vardimlen = {}

    for mem in self.memlist:
      if(self.debug):
        self.LOGFILE.write('write for mem: %d\n' %(mem))
      infile = '%s/mem%3.3d/%s' %(self.obsdir, mem, self.filename)
      IFILE = nc4.Dataset(infile, 'r')
      if(self.debug):
        self.LOGFILE.write('input file: %s\n' %(infile))
      igroups = IFILE.groups
  
      for grpname, group in igroups.items():
        if(grpname.find('hofx') < 0):
          continue
        if('hofx_y_mean_xb0' == grpname):
          continue

        if('hofx0_1' == grpname):
          self.specvars[mem][grpname] = {}
          for varname, variable in group.variables.items():
            self.specvars[mem][grpname][varname] = self.read_var(varname, variable)
            self.vardimlen[varname] = len(variable.dimensions)
            if(self.debug):
              self.LOGFILE.write('got specvars[%d][%s][%s]\n' %(mem, grpname, varname))
        newname = self.get_newname(grpname, mem)
        ogroup = self.OFILE.groups[newname]
        self.write_var_in_group(group, ogroup)
      
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

    self.outputfile = '%s/%s' %(self.obsdir, self.filename)

    if(self.debug):
      self.LOGFILE.write('outputfile: %s\n' %(self.outputfile))

    self.access_file(outfile=self.outputfile)

    self.debug = 1
    self.output_file()

    self.process_ombg()

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

