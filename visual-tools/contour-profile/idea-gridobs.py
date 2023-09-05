import getopt
import os, sys
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable

import matplotlib.cm as cm

import cartopy.crs as ccrs
from cartopy import config
from cartopy.util import add_cyclic_point
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import cartopy.feature as cfeature
import cartopy.mpl.ticker as cticker

from netCDF4 import Dataset as netcdf_dataset

#=========================================================================
class GeneratePlot():
  def __init__(self, debug=0, output=0):
    self.debug = debug
    self.output = output

    self.set_default()

  def plot(self, lons, lats, data=[], obslon=[], obslat=[], omb=[],
           grdlon=[], grdlat=[]):
   #ax.coastlines(resolution='110m')
   #ax.gridlines()

    nrows = len(data)
    ncols = 1

   #set up the plot
    proj = ccrs.PlateCarree()

    fig, axs = plt.subplots(nrows=nrows,ncols=ncols,
                            subplot_kw=dict(projection=proj),
                            figsize=(11,8.5))
 
   #axs is a 2 dimensional array of `GeoAxes`. Flatten it into a 1-D array
    axs=axs.flatten()

    for i in range(len(axs)):
      axs[i].set_global()

      pvar = data[i]

     #print('Plot No. ', i)
     #print('\tpvar.shape = ', pvar.shape)

      cyclic_data, cyclic_lons = add_cyclic_point(pvar, coord=lons)

      cs=axs[i].contourf(cyclic_lons, lats, cyclic_data, transform=proj,
                         levels=self.clevs, extend=self.extend,
                         alpha=self.alpha, cmap=self.cmapname)
     #               cmap=self.cmapname, extend='both')
     #obsplot = axs[i].scatter(x, y, s=size, c=obsvar, cmap=self.cmapname, 
     #                             alpha=self.alpha)
      axs[i].autoscale(False) # To avoid that the scatter changes limits

     #colors = cm.rainbow(np.linspace(0, 1, len(obslon)))
     #print('colors = ', colors)
     #colors = colors[-1]

      obsplot = axs[i].scatter(obslon, obslat, s=10, zorder=1, c='green', marker='x')
      grdplot = axs[i].scatter(grdlon[i], grdlat[i], s=10, zorder=1, c='cyan', marker='o')

      axs[i].set_extent([-180, 180, -90, 90], crs=proj)
      axs[i].coastlines(resolution='auto', color='k')
      axs[i].gridlines(color='lightgrey', linestyle='-', draw_labels=True)

      axs[i].set_title(self.runname[i])

   #Adjust the location of the subplots on the page to make room for the colorbar
    fig.subplots_adjust(bottom=0.1, top=0.9, left=0.05, right=0.8,
                        wspace=0.02, hspace=0.02)

   #Add a colorbar axis at the bottom of the graph
    cbar_ax = fig.add_axes([0.85, 0.1, 0.05, 0.85])

   #Draw the colorbar
    cbar=fig.colorbar(cs, cax=cbar_ax, pad=self.pad, ticks=self.cblevs,
                      orientation='vertical')

    cbar.set_label(self.label, rotation=90)

   #Add a big title at the top
    plt.suptitle(self.title)

    fig.canvas.draw()
    plt.tight_layout()

    if(self.output):
      if(self.imagename is None):
        imagename = 't_aspect.png'
      else:
        imagename = self.imagename
      plt.savefig(imagename)
      plt.show()
      plt.close()
    else:
      plt.show()

  def set_default(self):
    self.imagename = 'sample.png'

    self.runname = ['LETKF2D', 'LETKF3D', 'LETKF3D - LETKF2D']

   #cmapname = coolwarm, bwr, rainbow, jet, seismic
    self.cmapname = 'bwr'
   #self.cmapname = 'coolwarm'
   #self.cmapname = 'rainbow'
   #self.cmapname = 'jet'

    self.clevs = np.arange(-0.2, 0.21, 0.01)
    self.cblevs = np.arange(-0.2, 0.3, 0.1)

    self.extend = 'both'
    self.alpha = 0.5
    self.pad = 0.1
    self.orientation = 'horizontal'
    self.size = 'large'
    self.weight = 'bold'
    self.labelsize = 'medium'

    self.label = 'Unit (C)'
    self.title = 'Temperature Increment'

  def set_runname(self, runname = ['REINIT', 'IASI', 'REINIT - IASI']):
    self.runname = runname

  def set_label(self, label='Unit (C)'):
    self.label = label

  def set_title(self, title='Temperature Increment'):
    self.title = title

  def set_clevs(self, clevs=[]):
    self.clevs = clevs

  def set_cblevs(self, cblevs=[]):
    self.cblevs = cblevs

  def set_imagename(self, imagename):
    self.imagename = imagename

  def set_cmapname(self, cmapname):
    self.cmapname = cmapname

#=========================================================================
class ProcessGeometry():
  def __init__(self, debug=0):
    self.debug = debug

 #-----------------------------------------------------------------------------------------
  def set_region(self):
    self.minlat = np.min(self.lat)
    self.maxlat = np.max(self.lat)

    self.minlon = np.min(self.lon)
    self.maxlon = np.max(self.lon)

    self.plotarea = [self.minlon, self.maxlon, self.minlat, self.maxlat]

 #-----------------------------------------------------------------------------------------
  def get_var(self, filename):
    fin = open(filename,'r')
    lines = fin.readlines()
    fin.close()

    self.dist = []
    self.lat = []
    self.lon = []

    notl = len(lines)
    n = 0
    while (n < notl):
      line = lines[n]
      n += 1

      if(line.find('OOPS_DEBUG') >= 0 and line.find('Longitude') > 0):
        item = line.split(': ')
       #print('line: ', line)
       #print('item: ', item)
        headlon = item[1].split(', ')
       #print('headlon: ', headlon)
        lon = float(headlon[0].strip())
        if(lon > 180.0):
          lon -= 360.0
        headlat = item[2].split(', ')
       #print('headlat: ', headlat)
        lat = float(headlat[0].strip())
        self.lat.append(lat)
        self.lon.append(lon)
        self.dist.append(item[3])

       #print('lat: %f, lon: %f, org: %f' %(lat, lon, dist))

   #self.set_region()

    return self.lon, self.lat, self.dist

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 1
  datadir = '/work2/noaa/gsienkf/weihuang/jedi/per_core_timing/build/fv3-jedi/test'
  anlfile = '%s/Data/analysis/letkf/gfs/mem000/xainc.20201215_000000z.nc4' %(datadir)
 #obsfile  = '%s/Data/obs/testinput_tier_1/sondes_obs_2020121500_m.nc4' %(datadir)
 #obsfile  = '%s/Data/hofx/sondes_letkf-gfs_2020121500_m.nc4'  %(datadir)
 #obsfile  = '%s/Data/hofx/scatwind_letkf-gfs_2020121500_m.nc4'  %(datadir)
 #obsfile  = '%s/Data/hofx/satwind_letkf-gfs_2020121500_m.nc4'  %(datadir)
 #obsfile  = '%s/Data/hofx/sfc_letkf-gfs_2020121500_m.nc4'  %(datadir)
  obsfile  = '%s/Data/hofx/aircraft_letkf-gfs_2020121500_m.nc4'  %(datadir)
  dbgfile  = '%s/stdoutNerr/stdout.00000004'  %(datadir)

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=',
                                                'anlfile=', 'obsfile=', 'dbgfile='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--anlfile'):
      anlfile = a
    elif o in ('--obsfile'):
      obsfile = a
    elif o in ('--dbgfile'):
      dbgfile = a
    else:
      assert False, 'unhandled option'

#-----------------------------------------------------------------------------------------
  ncobs = netcdf_dataset(obsfile)
  group = ncobs.groups['MetaData']
  obslat = group.variables['latitude'][:]
  obslon = group.variables['longitude'][:]
  group = ncobs.groups['ObsValue']
 #obsval = group.variables['airTemperature'][:]
  obsval = group.variables['windEastward'][:]
  ncobs.close()

#-----------------------------------------------------------------------------------------
  gridlonlist = []
  gridlatlist = []
  pg = ProcessGeometry(debug=debug)

  for n in range(6):
    dbgfile  = '%s/stdoutNerr/stdout.0000000%d' %(datadir, n)
    grdlon, grdlat, dist = pg.get_var(dbgfile)
    gridlonlist.append(grdlon)
    gridlatlist.append(grdlat)

#-----------------------------------------------------------------------------------------
  gp = GeneratePlot(debug=debug, output=output)

  clevs = np.arange(-1.0, 1.01, 0.01)
  cblevs = np.arange(-1.0, 1.1, 0.1)

  clevs = 2.0*clevs
  cblevs = 2.0*cblevs

 #clevs = 0.1*clevs
 #cblevs = 0.1*cblevs

  gp.set_clevs(clevs=clevs)
  gp.set_cblevs(cblevs=cblevs)

#-----------------------------------------------------------------------------------------
  varlist = ['T', 'ua', 'va', 'DELP', 'sphum']

  unitlist = ['Unit (C)', 'Unit (m/s)', 'Unit (m/s)', 'Unit (pa)', 'Unit (kg/kg)']

#-----------------------------------------------------------------------------------------
  ncf = netcdf_dataset(anlfile)
  lats = ncf.variables['lat'][:]
  lons = ncf.variables['lon'][:]

#-----------------------------------------------------------------------------------------
  m = 0
  for n in range(len(varlist)):
    var = ncf.variables[varlist[n]][0, :, :, :]

    print('varlist[%d]: %s' %(n, varlist[n]))
    print('var.shape = ', var.shape)

    nlev, nlat, nlon = var.shape
    print('var.shape = ', var.shape)

    gp.set_label(unitlist[n])

    lev0 = 63
    lev1 = 125
    v0 = var[lev0,:,:]
    v1 = var[lev1,:,:]

    data = [v0, v1]

    title = '%s at Level %d & %d' %(varlist[n], lev0, lev1)
    gp.set_title(title)

    print('Plotting ', title)
    print('\tv0.shape = ', v0.shape)
    print('\tv1.shape = ', v1.shape)
    print('\tv0.max: %f, v0.min: %f' %(np.max(v0), np.min(v0)))
    print('\tv1.max: %f, v1.min: %f' %(np.max(v1), np.min(v1)))

    imagename = '%s_lev_%3.3d_%3.3d.png' %(varlist[n], lev0, lev1)
    gp.set_imagename(imagename)

    if(m >= 6):
      m -= 6
    gp.plot(lons, lats, data=data, obslon=obslon, obslat=obslat, omb=obsval,
            grdlon=gridlonlist[m:m+2], grdlat=gridlatlist[m:m+2])
    m += 2

#-----------------------------------------------------------------------------------------
  ncf.close()

