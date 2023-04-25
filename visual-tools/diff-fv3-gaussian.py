#=========================================================================
import os
import sys
import types
import getopt
import netCDF4
import matplotlib

import numpy as np
import matplotlib.pyplot

from matplotlib import cm
from mpl_toolkits.basemap import Basemap

from genplot import GeneratePlot as genplot
from scipy_regridder import RegridFV3 as regridder
from modelVerticalpressure import ModelVerticalPressure

#=========================================================================
class PlotGaussian():
  def __init__(self, debug=0, output=0, bkg=None, anl=None):
    self.debug = debug
    self.output = output
    self.bkg = bkg
    self.anl = anl

    if(self.debug):
      print('debug = ', debug)

    if(self.debug > 10):
      print('self.bkg = ', self.bkg)
      print('self.anl = ', self.anl)

    self.has_snd_file = 0
    self.snd_file = None

  def set_snd_file(self, filename):
    self.has_snd_file = 1
    self.snd_file = filename

  def get_vardims(self, filename, varname):
    if(self.debug > 1):
      print('varname = ', varname)
      print('filename = ', filename)
    ncfile = netCDF4.Dataset(filename, 'r')
    dimids = ncfile.variables[varname].dimensions

    if(self.debug > 1):
      print('dimids = ', dimids)

    self.nx = 0
    self.ny = 0
    self.nz = 0
    self.ntime = 0

    print('dimids = ', dimids)

    for dimname in dimids:
      if(self.debug > 1):
        print('dimname:', dimname)
      if(dimname == 'time'):
        self.ntime = len(ncfile.dimensions[dimname])
      elif(dimname == 'pfull'):
        self.nz = len(ncfile.dimensions[dimname])
      elif(dimname == 'grid_yt'):
        self.ny = len(ncfile.dimensions[dimname])
      elif(dimname == 'grid_xt'):
        self.nx = len(ncfile.dimensions[dimname])

    if(self.debug):
      print('self.nx = ', self.nx)
      print('self.ny = ', self.ny)
      print('self.nz = ', self.nz)
      print('self.ntime = ', self.ntime)

  def get_var(self, varname):
    print('varname =', varname)

    self.get_vardims(self.bkg, varname)

    lat = np.zeros((self.ny, self.nx))
    lon = np.zeros((self.ny, self.nx))

    anl = np.zeros((self.nz, self.ny, self.nx))
    bkg = np.zeros((self.nz, self.ny, self.nx))

    anl_file = netCDF4.Dataset(self.anl, 'r')
    lat = anl_file.variables['lat'][:, :]
    lon = anl_file.variables['lon'][:, :]
    anl = anl_file.variables[varname][0, :, :, :]
    anl_file.close()

    self.lats = lat.flatten()
    self.lons = lon.flatten()

    bkg_file = netCDF4.Dataset(self.bkg, 'r')
    bkg = bkg_file.variables[varname][0, :, :, :]
    bkg_file.close()

    if(self.debug):
      msg = ('analy range for variable %s: (%s, %s).' % (varname, anl.min(), anl.max()))
      print(msg)
      msg = ('bkgrd range for variable %s: (%s, %s).' % (varname, bkg.min(), bkg.max()))
      print(msg)

    incr = anl - bkg

   #print('incr = ', incr)

    return self.lons, self.lats, incr

  def get_diff(self, varname):
    print('varname =', varname)

    self.get_vardims(self.anl, varname)

    lat = np.zeros((self.ny, self.nx))
    lon = np.zeros((self.ny, self.nx))

    fst = np.zeros((self.nz, self.ny, self.nx))
    snd = np.zeros((self.nz, self.ny, self.nx))

    fst_file = netCDF4.Dataset(self.anl, 'r')
    lat = fst_file.variables['lat'][:, :]
    lon = fst_file.variables['lon'][:, :]
    fst = fst_file.variables[varname][0, :, :, :]
    fst_file.close()

    self.lats = lat.flatten()
    self.lons = lon.flatten()

    snd_file = netCDF4.Dataset(self.snd_file, 'r')
    snd = snd_file.variables[varname][0, :, :, :]
    snd_file.close()

    if(self.debug):
      msg = ('fst range for variable %s: (%s, %s).' % (varname, fst.min(), fst.max()))
      print(msg)
      msg = ('snd range for variable %s: (%s, %s).' % (varname, snd.min(), snd.max()))
      print(msg)

    diff = snd - fst

   #print('incr = ', incr)

    return self.lons, self.lats, diff

#------------------------------------------------------------------------------
if __name__ == '__main__':
  debug = 1
  output = 0

  uvOnly = 0

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=', 'uvOnly='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--uvOnly'):
      uvOnly = int(a)
   #else:
   #  assert False, 'unhandled option'

  print('debug = ', debug)
  print('output = ', output)
  print('uvOnly = ', uvOnly)

#=======================================================================================================================
  fv3_griddir = '/work/noaa/gsienkf/weihuang/tools/UFS-RNR-tools/JEDI.FV3-increments/grid/C48/'

  if(uvOnly):
    gsi_bkg = '/work/noaa/gsienkf/weihuang/jedi/case_study/sondes/jeff-gsi-run/uv-only/sfg_2021010900_fhr06_ensmean'
    gsi_anl = '/work/noaa/gsienkf/weihuang/jedi/case_study/sondes/jeff-gsi-run/uv-only/sanl_2021010900_fhr06_ensmean.uv'

    datadir = '/work/noaa/gsienkf/weihuang/jedi/case_study/sondes/analysis.getkf.80members.36procs.uvOnly/increment/'
  else:
    gsi_bkg = '/work/noaa/gsienkf/weihuang/jedi/vis_tools/jeff-run/sfg_2021010900_fhr06_ensmean'
    gsi_anl = '/work/noaa/gsienkf/weihuang/jedi/vis_tools/jeff-run/sanl_2021010900_fhr06_ensmean'

   #datadir = '/work/noaa/gsienkf/weihuang/jedi/case_study/sondes/analysis.getkf.80members.36procs.all/increment/'
    datadir = '/work/noaa/gsienkf/weihuang/jedi/case_study/sondes/analysis.getkf.80members.36procs.uvTq/increment/'

  datafiles = []
  gridspecfiles = []
  for ntile in range(1,7,1):
    gridfile = '%sC48_grid.tile%s.nc' %(fv3_griddir, ntile)
    gridspecfiles.append(gridfile)

    datafile = '%s20210109.000000.fv_core.res.tile%s.nc' %(datadir, ntile)
    datafiles.append(datafile)

#=======================================================================================================================
  filename = '/work/noaa/gsienkf/weihuang/jedi/case_study/sondes/Data/bkg/fv_core.res.nc'
  mvp = ModelVerticalPressure(debug=debug, filename=filename)
 #prs = mvp.get_pressure()
 #print('len(prs) = ', len(prs))
 #for n in range(len(prs)):
 #  print('Level %d pressure %f' %(n, prs[n]))
  logp = mvp.get_logp()
  markpres = mvp.get_markpres()
  marklogp = mvp.get_marklogp()

#=======================================================================================================================
  nlon = 360
  nlat = nlon/2 + 1
  dlon = 360.0/nlon
  dlat = 180.0/(nlat - 1)
  lon = np.arange(0.0, 360.0, dlon)
  lat = np.arange(-90.0, 90.0+dlat, dlat)

#=======================================================================================================================
  pg = PlotGaussian(debug=debug, output=output, bkg=gsi_bkg, anl=gsi_anl)
  lon1d, lat1d, var1d = pg.get_var('tmp')

  regrid_gsi = regridder(debug=debug, datafiles=[], gridspecfiles=[])
  gsi_var = regrid_gsi.interp2latlon_data(lon1d, lat1d, var1d, nlon=nlon, nlat=nlat, method='linear')

#=======================================================================================================================
  regrid_getkf = regridder(debug=debug, datafiles=datafiles, gridspecfiles=gridspecfiles)

  varname = 'T'
  getkf_var = regrid_getkf.get_latlon_data(varname, nlon=nlon, nlat=nlat, method='linear')

 #print('var.ndim = ', var.ndim)
 #print('var.shape = ', var.shape)

#=======================================================================================================================
  var = getkf_var - gsi_var

#=======================================================================================================================
  gp = genplot(debug=debug, output=output, lat=lat, lon=lon)

  gp.set_label('Temperature (K)')

  if(uvOnly):
    imgprefix = 'uvOnly_getkf-gsi_sondes'
    title_prefix = 'uvOnly GETKF-GSI Sondes Temperature at'
  else:
    imgprefix = 'uvTq_getkf-gsi_sondes'
    title_prefix = 'uvTq GETKF-GSI Sondes Temperature at'

  levs = [10, 23, 30, 52]

  for lev in levs:
    pvar = var[lev,:,:]
    imgname = '%s_lev_%d.png' %(imgprefix, lev)
    title = '%s level %d' %(title_prefix, lev)
    gp.set_imagename(imgname)
    gp.set_title(title)
    gp.plot(pvar)

  lons = [40, 105, 170, 270, 300]

  for lon in lons:
    pvar = var[:,:,lon]
    imgname = '%s_lon_%d.png' %(imgprefix, lon)
    title = '%s longitude %d' %(title_prefix, lon)
    gp.set_imagename(imgname)
    gp.set_title(title)
   #gp.plot_meridional_section(pvar)
    gp.plot_meridional_section_logp(pvar, logp, marklogp, markpres)

  lats = [-30, 0, 45, 70]

  for lat in lats:
    pvar = var[:,90+lat,:]
    imgname = '%s_lat_%d.png' %(imgprefix, lat)
    title = '%s latitude %d' %(title_prefix, lat)
    gp.set_imagename(imgname)
    gp.set_title(title)
   #gp.plot_zonal_section(pvar)
    gp.plot_zonal_section_logp(pvar, logp, marklogp, markpres)

