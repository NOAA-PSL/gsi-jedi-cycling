#=========================================================================
import os
import sys
import getopt
import netCDF4 as nc4
import time
import numpy as np
import inspect, logging

#-----------------------------------------------------------------------------------------
def average(vlist):
  buf = np.zeros_like(vlist[0])
  nmem = len(vlist)
  for n in range(1, nmem):
    buf += vlist[n]
  buf /= (nmem-1)
  return buf

#=========================================================================
class ConcanateObservations():
  def __init__(self, debug=0, nmem=81, run_dir=None, datestr=None, obstype=None):
    self.nmem = nmem
    self.debug = debug

    self.grplist = ['hofx_y_mean_xb0', 'hofx0_1', 'ombg']
    self.filelist = []
    for n in range(nmem):
     #flnm = '%s/mem%3.3d/%s_obs_%s.nc4' %(run_dir, n, obstype, datestr)
      flnm = '%s/mem%3.3d/%s_hofx_%s.nc4' %(run_dir, n, obstype, datestr)
      self.filelist.append(flnm)
    self.outfile = '%s/%s_obs_%s.nc4' %(run_dir, obstype, datestr)

    self.identstr = ''

 #-----------------------------------------------------------------------------------------
  def logger(self, message):
   #Automatically log the current function details.
   #Get the previous frame in the stack, otherwise it would
   #be this function!!!
    func = inspect.currentframe().f_back.f_code
   #Dump the message + the name of this function to the log.
    if(message == 'Enter'):
      self.identstr += '    '
    if(self.debug):
      print("%s %s %s at line %i in %s" % (self.identstr, message, 
        func.co_name, func.co_firstlineno, func.co_filename))
    if(message == 'Leave'):
      newidentstr = self.identstr[:-4]
      self.identstr = newidentstr

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
      outvar = ncout.createVariable(name, variable.datatype, variable.dimensions)
      invar = ncin[name]
      self.copy_var2var(invar, outvar)

 #-----------------------------------------------------------------------------------------
  def copy_var2var(self, invar, outvar):
   #copy variable attributes all at once via dictionary
    outvar.setncatts(invar.__dict__)
    nd = len(invar.dimensions)
    if(nd == 1):
      outvar[:] = invar[:]
    elif(nd == 2):
      outvar[:,:] = invar[:,:]
    elif(nd == 3):
      outvar[:,:,:] = invar[:,:,:]
    elif(nd == 4):
      outvar[:,:,:,:] = invar[:,:,:,:]
    else:
      msg = 'Do not know how to handle nd = %i' %(nd)
      self.logger(msg)
      print(msg)
      sys.exit(-1)

 #-----------------------------------------------------------------------------------------
  def read_val(self, invar):
    nd = len(invar.dimensions)
    if(nd == 1):
      val = invar[:]
    elif(nd == 2):
      val = invar[:,:]
    elif(nd == 3):
      val = invar[:,:,:]
    elif(nd == 4):
      val = invar[:,:,:,:]
    else:
      msg = 'Do not know how to handle nd = %i' %(nd)
      self.logger(msg)
      print(msg)
      sys.exit(-1)

    return val

 #-----------------------------------------------------------------------------------------
  def write_val2var(self, val, outvar):
    nd = len(outvar.dimensions)
    if(nd == 1):
      outvar[:] = val[:]
    elif(nd == 2):
      outvar[:,:] = val[:,:]
    elif(nd == 3):
      outvar[:,:,:] = val[:,:,:]
    elif(nd == 4):
      outvar[:,:,:,:] = val[:,:,:,:]
    else:
      msg = 'Do not know how to handle nd = %i' %(nd)
      self.logger(msg)
      print(msg)
      sys.exit(-1)

 #-----------------------------------------------------------------------------------------
  def copy_group2group(self, ncingroup, ncoutgroup):
    self.logger('Enter')
    fvname = '_FillValue'
   #copy all var in group.
    for varname, variable in ncingroup.variables.items():
     #self.logger('  working on var: ' + varname)
     #print('  working on var: ' + varname)
      if(fvname in variable.__dict__):
        fill_value = variable.getncattr(fvname)
        newvar = ncoutgroup.createVariable(varname, variable.datatype,
                                           variable.dimensions, fill_value=fill_value)
      else:
        newvar = ncoutgroup.createVariable(varname, variable.datatype,
                                           variable.dimensions)
      self.copy_var2var(variable, newvar)

   #print('ncingroup.groups=', ncingroup.groups)
   #print('ncingroup.groups.values()=', ncingroup.groups.values())
   #print('ncingroup.groups.keys()=', ncingroup.groups.keys())

   #copy group in group
    for grpname in ncingroup.groups.keys():
      group = ncingroup.groups[grpname]
      newoutgroup = ncoutgroup.createGroup(grpname)
      self.copy_group2group(group, newoutgroup)

    self.logger('Leave')

 #-----------------------------------------------------------------------------------------
  def copy_grp2newname(self, name, n, group, ncout):
    self.logger('Enter')
    item = name.split('_')
    item[-1] = '%d' %(n)
    newname = '_'.join(item)
   #print('No %d name: %s, newname: %s' %(n, name, newname))
    ncoutgroup = ncout.createGroup(newname)
    self.copy_group2group(group, ncoutgroup)
    self.logger('Leave')

#-----------------------------------------------------------------------------------------
  def process_basegroup(self, ncin, ncout, grplist):
    self.logger('Enter')

    self.grpnamelist = []
    self.hofxgrps = []
    self.commongrps = []
    self.ensvarinfo = {}
  
   #check groups
    ng = 0
    for grpname, group in ncin.groups.items():
      ng += 1
     #print('grpname No %d: %s' %(ng, grpname))
      self.grpnamelist.append(grpname)
      if(grpname in grplist):
        self.ensvarinfo[grpname] = {}
        if(grpname == 'hofx0_1'):
          for varname, variable in group.variables.items():
           #val = group[varname][:]
            self.ensvarinfo[grpname][varname] = []
           #self.ensvarinfo[grpname][varname].append(val)
        else:
          if(grpname == 'hofx_y_mean_xb0'):
            ncoutgroup = ncout.createGroup(grpname)
            self.copy_group2group(group, ncoutgroup)

          for varname, variable in group.variables.items():
            val = self.read_val(variable)
            self.ensvarinfo[grpname][varname] = val
      else:
       #print('grpname: ', grpname)
        if(grpname.find('hofx') < 0):
          self.commongrps.append(grpname)
          ncoutgroup = ncout.createGroup(grpname)
          self.copy_group2group(group, ncoutgroup)
        else:
          self.hofxgrps.append(grpname)

    print('len(self.grpnamelist) = %d' %(len(self.grpnamelist)))
    print('len(self.commongrps) = %d' %(len(self.commongrps))) 
    print('len(self.hofxgrps) = %d' %(len(self.hofxgrps)))

    self.logger('Leave')

#-----------------------------------------------------------------------------------------
  def process(self, ncinlist, ncout, grplist):
    grpname = 'hofx0_1'
    for n in range(1, len(ncinlist)):
      ncin = ncinlist[n]
      for name in self.hofxgrps:
        group = ncin.groups[name]
        self.copy_grp2newname(name, n, group, ncout)

      group = ncin.groups[grpname]
      self.copy_grp2newname(grpname, n, group, ncout)

      for varname, variable in group.variables.items():
        val = self.read_val(variable)
        self.ensvarinfo[grpname][varname].append(val)

    varlist = self.ensvarinfo['hofx0_1'].keys()
   #print('varlist = ', varlist)
    meanvars = {}
    ncoutgroup = ncout.createGroup(grpname)
    for varname in varlist:
      meanval = average(self.ensvarinfo[grpname][varname])
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
        newvar = ncoutgroup.createVariable(varname, variable.datatype,
                                           variable.dimensions, fill_value=fill_value)
      else:
        newvar = ncoutgroup.createVariable(varname, variable.datatype,
                                           variable.dimensions)
      self.copy_attributes(variable, newvar)
      val = self.ensvarinfo[grpname][varname] + self.ensvarinfo['hofx_y_mean_xb0'][varname] - meanvars[varname]
      print('\thofx_y_mean_zb0.min: %f' %(np.min(self.ensvarinfo['hofx_y_mean_xb0'][varname])))
      print('\thofx_y_mean_zb0.max: %f' %(np.max(self.ensvarinfo['hofx_y_mean_xb0'][varname])))
      print('\told-ombg.min: %f' %(np.min(self.ensvarinfo[grpname][varname])))
      print('\told-ombg.max: %f' %(np.max(self.ensvarinfo[grpname][varname])))
      print('\tnew-ombg.min: %f' %(np.min(val)))
      print('\tnew-ombg.max: %f' %(np.max(val)))
      print('\tmeanvars.min: %f' %(np.min(meanvars[varname])))
      print('\tmeanvars.max: %f' %(np.max(meanvars[varname])))
     #val = self.ensvarinfo[grpname][varname]
      self.write_val2var(val, newvar)

 #-----------------------------------------------------------------------------------------
  def replace_var(self):
    self.ncinlist = []
    for infile in self.filelist:
      if(os.path.exists(infile)):
        print('infile: ', infile)
        ncin = nc4.Dataset(infile, 'r')
        self.ncinlist.append(ncin)
      else:
        print('infile: %s does not exist.' %(infile))
        sys.exit(-1)

    if(os.path.exists(self.outfile)):
      os.remove(self.outfile)

    print('len(self.ncinlist) = ', len(self.ncinlist))
    print('outfile: ', self.outfile)

    self.ncout = nc4.Dataset(self.outfile, 'w')

   #copy global attributes all at once via dictionary
   #self.ncout.setncatts(ncin.__dict__)
    self.ncout.source='JEDI observer only ouptut, each with only one member'
    self.ncout.comment = 'updated variable hofx_y_mean_xb0 and ombg from all observer files'

   #copy attributes
    for name in self.ncinlist[0].ncattrs():
      self.ncout.setncattr(name, self.ncinlist[0].getncattr(name))

    self.copy_dimension(self.ncinlist[0], self.ncout)
    self.copy_rootvar(self.ncinlist[0], self.ncout)
  
    self.process_basegroup(self.ncinlist[0], self.ncout, self.grplist)

    self.process(self.ncinlist, self.ncout, self.grplist)
 
    for ncin in self.ncinlist:
      ncin.close()
    self.ncout.close()

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 0
  nmem = 81

  run_dir = '/work2/noaa/da/weihuang/cycling/scripts/iasi-amsua/Data/obsout'
  datestr = '2022030312'
  obstype = 'amsua_n15'

  #-----------------------------------------------------------------------------------------
  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'run_dir=',
                                                'datestr=', 'obstype=', 'nmem='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--run_dir'):
      run_dir = a
    elif o in ('--datestr'):
      datestr = a
    elif o in ('--obstype'):
      obstype = a
    elif o in ('--nmem'):
      nmem = int(a)
    else:
      assert False, 'unhandled option'

  #-----------------------------------------------------------------------------------------
  co = ConcanateObservations(debug=debug, nmem=nmem, run_dir=run_dir,
                             datestr=datestr, obstype=obstype)
  co.replace_var()
