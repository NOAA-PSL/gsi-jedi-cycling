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
from modelVerticalpressure import ModelVerticalPressure

#=========================================================================
class PlotGaussian():
  def __init__(self, debug=0, output=0, fst=None, snd=None):
    self.debug = debug
    self.output = output
    self.fst = fst
    self.snd = snd

    if(self.debug):
      print('debug = ', debug)

    if(self.debug > 10):
      print('self.fst = ', self.fst)
      print('self.snd = ', self.snd)

    self.ncfst = netCDF4.Dataset(fst, 'r')
    self.ncsnd = netCDF4.Dataset(snd, 'r')

    self.lon = self.ncfst['lon'][:]
    self.lat = self.ncfst['lat'][:]
    self.hyai = self.ncfst['hyai'][:]
    self.hybi = self.ncfst['hybi'][:]
    self.nlon = len(self.lon)
    self.nlat = len(self.lat)
    self.nlev = len(self.hyai) - 1

  def get_latlon(self):
    return self.lat, self.lon

  def get_akbk(self):
    return self.hyai, self.hybi

  def get_var(self, ncfile, varname):
    var = ncfile.variables[varname][:, :, :]

    if(self.debug):
      msg = ('variable %s: (%s, %s).' % (varname, var.min(), var.max()))
      print(msg)

    return var

  def get_diff(self, varname):
    print('varname =', varname)

    fst = self.ncfst.variables[varname][:,:,:]
    snd = self.ncsnd.variables[varname][:,:,:]
    if(self.debug):
      msg = ('fst range for variable %s: (%s, %s).' % (varname, fst.min(), fst.max()))
      print(msg)
      msg = ('snd range for variable %s: (%s, %s).' % (varname, snd.min(), snd.max()))
      print(msg)

    diff = snd - fst

    return fst, snd, diff

#------------------------------------------------------------------------------
if __name__ == '__main__':
  debug = 1
  output = 0

  topdir = '/work2/noaa/da/weihuang/cycling/scripts/iasi-amsua/Data'
  fstfile = '%s/analysis.iasi_metop+n15+n18+n19/increment/interp2gaussian_grid.nc4' %(topdir)
  sndfile = '%s/analysis.iasi_metop+n15+n18+n19.separate_reinit_observer/increment/interp2gaussian_grid.nc4' %(topdir)

#=======================================================================================================================
  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=', 'fstfile=', 'sndfile='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--fstfile'):
      fstfile = a
    elif o in ('--sndfile'):
      sndfile = a
    else:
      assert False, 'unhandled option'

  print('debug = ', debug)
  print('output = ', output)

#=======================================================================================================================
  filename = 'akbk127.nc4'
  mvp = ModelVerticalPressure(debug=debug, filename=filename)
 #prs = mvp.get_pressure()
 #print('len(prs) = ', len(prs))
 #for n in range(len(prs)):
 #  print('Level %d pressure %f' %(n, prs[n]))
  logp = mvp.get_logp()
  markpres = mvp.get_markpres()
  marklogp = mvp.get_marklogp()

#=======================================================================================================================
  pg = PlotGaussian(debug=debug, output=output, fst=fstfile, snd=sndfile)
  fst, snd, var = pg.get_diff('T_inc')
  lat,lon = pg.get_latlon()

#=======================================================================================================================
  gp = genplot(debug=debug, output=output, lat=lat, lon=lon)

  gp.set_label('Temperature (K)')

 #imgprefix = 'JEDI_GSI_ps+sondes+amsua'
 #title_prefix = 'JEDI GSI ps+sondes+amsua'

  imgprefix = 'IASI_ps+sondes+iasi_SEPINT'
  title_prefix = 'JEDI GSI ps+sondes+iasi_SEPINT'

  levs = [30, 50, 70, 80, 90, 100, 110, 120]

  for lev in levs:
    pvar = fst[lev,:,:]
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
    gp.plot_meridional_section(pvar)
   #gp.plot_meridional_section_logp(pvar, logp, marklogp, markpres)

  lats = [-30, 0, 45, 70]

  for lat in lats:
    pvar = var[:,90+2*lat,:]
    imgname = '%s_lat_%d.png' %(imgprefix, lat)
    title = '%s latitude %d' %(title_prefix, lat)
    gp.set_imagename(imgname)
    gp.set_title(title)
    gp.plot_zonal_section(pvar)
   #gp.plot_zonal_section_logp(pvar, logp, marklogp, markpres)

