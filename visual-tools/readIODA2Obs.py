# =========================================================================
import os
import sys
import getopt
import math
import numpy as np
import netCDF4

#=========================================================================
class ReadIODA2Obs():
  def __init__(self, debug=0, filename=None):
    self.debug = debug
    self.filename = filename

    if(self.debug):
      print('debug = ', debug)
      print('filename = ', filename)

    self.ndatetime = 0
    self.nlocs = 0
    self.nstring = 0
    self.nvars = 0

    if(filename != None):
      self.set_vardims()

  def set_filename(self, filename=None):
    self.filename = filename

  def get_groupNvar_name(self, gvstr):
    np = gvstr.rfind('/')
    if (np < 0):
      gname = None
      vname = gvstr
    else:
      gname = gvstr[:np]
      vname = gvstr[np+1:]

   #if(self.debug):
   #  print('gname = ', gname)
   #  print('vname = ', vname)

    return gname, vname

  def ncdump(self, nc_fid, verb=True):
    '''
    ncdump outputs dimensions, variables and their attribute information.
    The information is similar to that of NCAR's ncdump utility.
    ncdump requires a valid instance of Dataset.

    Parameters
    ----------
    nc_fid : netCDF4.Dataset
        A netCDF4 dateset object
    verb : Boolean
        whether or not nc_attrs, nc_dims, and nc_vars are printed

    Returns
    -------
    nc_attrs : list
        A Python list of the NetCDF file global attributes
    nc_dims : list
        A Python list of the NetCDF file dimensions
    nc_vars : list
        A Python list of the NetCDF file variables
    '''
    def print_ncattr(key):
        """
        Prints the NetCDF file attributes for a given key

        Parameters
        ----------
        key : unicode
            a valid netCDF4.Dataset.variables key
        """
        try:
            print("\t\ttype:", repr(nc_fid.variables[key].dtype))
            for ncattr in nc_fid.variables[key].ncattrs():
                print('\t\t%s:' % ncattr,
                      repr(nc_fid.variables[key].getncattr(ncattr)))
        except KeyError:
            print("\t\tWARNING: %s does not contain variable attributes" % key)

    # NetCDF global attributes
    nc_attrs = nc_fid.ncattrs()
    if verb:
        print("NetCDF Global Attributes:")
        for nc_attr in nc_attrs:
            print('\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr)))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        print("NetCDF dimension information:")
        for dim in nc_dims:
            print("\tName:", dim)
            print("\t\tsize:", len(nc_fid.dimensions[dim]))
            if ('ndatetime' == dim):
                self.ndatetime = len(nc_fid.dimensions[dim])
            elif ('nlocs' == dim):
                self.nlocs = len(nc_fid.dimensions[dim])
            elif ('nstring' == dim):
                self.nstring = len(nc_fid.dimensions[dim])
            elif ('nvars' == dim):
                self.nvars = len(nc_fid.dimensions[dim])
            print_ncattr(dim)
    # Variable information.
    nc_vars = [var for var in nc_fid.variables]  # list of nc variables
    if verb:
        print("NetCDF variable information:")
        for var in nc_vars:
            if var not in nc_dims:
                print('\tName:', var)
                print("\t\tdimensions:", nc_fid.variables[var].dimensions)
                print("\t\tsize:", nc_fid.variables[var].size)
                print(ncattr(var))

        print('\tself.ndatetime:', self.ndatetime)
        print('\tself.nlocs:', self.nlocs)
        print('\tself.nstring:', self.nstring)
        print('\tself.nvars:', self.nvars)
    return nc_attrs, nc_dims, nc_vars

  def get_var(self, ncvarname):
    print('Processing FV3 file %s for variable %s.' % (self.filename, ncvarname))

    gname, vname = self.get_groupNvar_name(ncvarname)

   #print('gname = ', gname)
   #print('vname = ', vname)

    ncfile = netCDF4.Dataset(self.filename, 'r')
    if (gname is None):
      var = ncfile.variables[ncvarname][:]
    else:
     #print('gname = ', gname)
     #print('vname = ', vname)

      ncgroup = ncfile[gname]
      var = ncgroup.variables[vname][:]
    ncfile.close()
    return var

  def set_vardims(self):
    ncfile = netCDF4.Dataset(self.filename, 'r')
    if(self.debug > 1):
      print('ncpath = ', ncpath)
      print('self.filename = ', self.filename)
    nc_attrs, nc_dims, nc_vars = self.ncdump(ncfile, verb=True)
   #nc_attrs, nc_dims, nc_vars = self.ncdump(ncfile, verb=False)

   #print('nc_dims: ', nc_dims)
   #print('nc_vars: ', nc_vars)

    if(self.debug):
      print('nc_dims: ', nc_dims)
    ncfile.close()

  def get_latlon(self):
    lat = self.get_var('/MetaData/latitude')
    lon = self.get_var('/MetaData/longitude')

    return lat, lon

  def get_latlon_from_file(self, filename):
    ncfile = netCDF4.Dataset(filename, 'r')
    ncgroup = ncfile['MetaData']
    lat = ncgroup.variables['latitude'][:]
    lon = ncgroup.variables['longitude'][:]
    ncfile.close()

    lon = np.where(lon > 0, lon, lon+360.0)

    return lat, lon

  def get_latlon4var(self, varname=None):
    lat, lon = self.get_latlon()
    if(varname is None):
      return lat, lon

    var = self.get_var(varname)

   #print('len(lat) = ', len(lat))
   #print('len(var) = ', len(var))
   #print('var = ', var)

    mask = []

    for n in range(len(var)):
     #if(math.isnan(var[n]) or var[n] > 12):
     #  mask.append(n)
     #if(np.isnan(var[n])):
      if(math.isnan(var[n])):
        mask.append(n)
     #else:
     #  if((var[n] < -2000.0) or (var[n] > 2000.0)):
     #    mask.append(n)
     #else:
     #  print('var[%d] = %f' %(n, var[n]))

   #print('len(mask) = ', len(mask))

    short_lat = np.delete(lat, mask)
    short_lon = np.delete(lon, mask)
    short_var = np.delete(var, mask)

    print('len(short_lat) = ', len(short_lat))
    print('len(short_lon) = ', len(short_lon))

    return short_lat, short_lon, short_var

# ----
if __name__ == '__main__':
  debug = 1
  filename = '/work/noaa/gsienkf/weihuang/jedi/case_study/sondes/ioda_v2_data/obs/ncdiag.oper.ob.PT6H.sondes.2021-01-08T21:00:00Z.nc4'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'yaml_file='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--filename'):
      filename = a
   #else:
   #  assert False, 'unhandled option'

  print('debug = ', debug)
  print('filename = ', filename)

  rio = ReadIODA2Obs(debug=debug, filename=filename)
 #lat, lon = rio.get_latlon()
  lat, lon = rio.get_latlon4var(varname='/ObsValue/surface_pressure')
 
  print('lat = ', lat)
  print('lon = ', lon)

