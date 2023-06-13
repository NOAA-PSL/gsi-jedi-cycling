import os, sys
import getopt
import numpy as np
import netCDF4 as nc4

import threading 

#=========================================================================
class FillVariablesWithThreading():
  def __init__(self, debug=0, rundir=None, datestr=None, nmem=1, obstype=None):
    threading.Thread.__init__(self)
    self.debug = debug
    self.datestr = datestr
    self.rundir = rundir
    self.nmem = nmem
    self.obstype = obstype

    self.obsdir = '%s/%s/observer' %(self.rundir, self.datestr)
    self.filename = '%s_obs_%s.nc4' %(self.obstype, self.datestr)

#-----------------------------------------------------------------------------------------
  def process(self):
    self.outputfile = '%s/%s' %(self.obsdir, self.filename)

    self.OFILE = nc4.Dataset(self.outputfile, 'r+')

    threads = []
    for n in range(nmem):
      mem = n + 1
      thread = FillVariables(debug=self.debug, rundir=self.rundir, mem=mem,
                             datestr=datestr, obstype=self.obstype, OFILE=self.OFILE)
      threads.append(thread)
      thread.start()

    for thread in threads:
      thread.join()

    self.OFILE.close()

#=========================================================================
class FillVariables(threading.Thread):
  lock = threading.Lock()
  def __init__(self, debug=0, rundir=None, datestr=None, mem=1,
               obstype=None, OFILE=None):
    threading.Thread.__init__(self)
    self.debug = debug
    self.datestr = datestr
    self.rundir = rundir
    self.mem = mem
    self.obstype = obstype
    self.OFILE = OFILE

    self.obsdir = '%s/%s/observer' %(self.rundir, self.datestr)
    self.filename = '%s_obs_%s.nc4' %(self.obstype, self.datestr)

#-----------------------------------------------------------------------------------------
  def run(self):
    if(self.debug):
      logflnm='logdir/log.%s.%4.4d' %(self.obstype, self.mem)
      self.LOGFILE = open(logflnm, 'w')

      self.LOGFILE.flush()

    self.fill_variables()

    if(self.debug):
      self.LOGFILE.close()

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
  def write_var(self, var, val):
    dim = len(var.dimensions)
    if(1 == dim):
      var[:] = val[:]
    elif(2 == dim):
      var[:,:] = val[:,:]
    elif(3 == dim):
      var[:,:,:] = val[:,:,:]

#-----------------------------------------------------------------------------------------
  def write_var_in_group(self, ingroup, outgroup):
   #write all var in group.
    for varname, variable in ingroup.variables.items():
      val = self.read_var(varname, variable)

     #FillVariables.lock.acquire() 

      var = outgroup.variables[varname]

      self.write_var(var, val)

     #FillVariables.lock.release() 

      if(self.debug):
        self.LOGFILE.write('\twrite variable: %s\n' %(varname))

#-----------------------------------------------------------------------------------------
  def fill_variables(self):
    infile = '%s/mem%3.3d/%s' %(self.obsdir, self.mem, self.filename)
    IFILE = nc4.Dataset(infile, 'r')
    if(self.debug):
      self.LOGFILE.write('input file: %s\n' %(infile))
    igroups = IFILE.groups

    for grpname, group in igroups.items():
      if(grpname.find('hofx') < 0):
        continue
      if('hofx_y_mean_xb0' == grpname):
        continue

      newname = self.get_newname(grpname, self.mem)

      ogroup = self.OFILE.groups[newname]
      self.write_var_in_group(group, ogroup)
    
      if(self.debug):
        self.LOGFILE.write('write group %s from %s\n' %(newname, grpname))
        self.LOGFILE.flush()
 
    IFILE.close()

#=========================================================================================
if __name__== '__main__':
  debug = 1
  nmem = 80
  rundir = '/work2/noaa/da/weihuang/cycling/gdas-cycling'
  datestr = '2020010206'
  obstype = 'sondes'
  obstypelist = ['sfc_ps', 'sfcship_ps', 'sondes_ps',
                 'sondes', 'amsua_n15', 'amsua_n18', 'amsua_n19']

 #--------------------------------------------------------------------------------
  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'rundir=', 'obstype=',
                                                'nmem=', 'datestr='])
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
  fvwt = FillVariablesWithThreading(debug=debug, rundir=rundir, nmem=nmem,
                                      datestr=datestr, obstype=obstype)
  fvwt.process()

