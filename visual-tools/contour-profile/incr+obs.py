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

  def plot(self, lons, lats, data=[], obslon=[], obslat=[], omb=[]):
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

      obsplot = axs[i].scatter(obslon, obslat, zorder=1, c='green')

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

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 1
  firstfile = 'letkf2d/xainc.20201215_000000z.nc4'
  secondfile = 'letkf3d/xainc.20201215_000000z.nc4'

 #firstobs  = 'letkf2d/sfc_letkf-gfs_2020121500_s.nc4'
 #secondobs  = 'letkf3d/sfc_letkf-gfs_2020121500_s.nc4'

  firstobs  = 'letkf2d/scatwind_letkf-gfs_2020121500_s.nc4'
  secondobs  = 'letkf3d/scatwind_letkf-gfs_2020121500_s.nc4'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=',
                                                'secondfile=', 'firstfile=',
                                                'secondobs=', 'firstobs='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--secondfile'):
      secondfile = a
    elif o in ('--firstfile'):
      firstfile = a
    elif o in ('--secondobs'):
      secondobs = a
    elif o in ('--firstobs'):
      firstobs = a
    else:
      assert False, 'unhandled option'

  gp = GeneratePlot(debug=debug, output=output)

  ncsecond = netcdf_dataset(secondfile)
  ncfirst = netcdf_dataset(firstfile)
  lats = ncsecond.variables['lat'][:]
  lons = ncsecond.variables['lon'][:]

#-----------------------------------------------------------------------------------------
  ncsecondobs = netcdf_dataset(secondobs)
  group = ncsecondobs.groups['MetaData']
  secondobslat = group.variables['latitude'][:]
  secondobslon = group.variables['longitude'][:]
  group = ncsecondobs.groups['ombg']
 #secondombg = group.variables['stationPressure'][:]
  secondombg = group.variables['windEastward'][:]

#-----------------------------------------------------------------------------------------
  ncfirstobs = netcdf_dataset(firstobs)
  group = ncfirstobs.groups['MetaData']
  firstobslat = group.variables['latitude'][:]
  firstobslon = group.variables['longitude'][:]
  group = ncfirstobs.groups['ombg']
 #firstombg = group.variables['stationPressure'][:]
  firstombg = group.variables['windNorthward'][:]

#-----------------------------------------------------------------------------------------
  ncsecondobs.close()
  ncfirstobs.close()

#-----------------------------------------------------------------------------------------
  clevs = np.arange(-1.0, 1.01, 0.01)
  cblevs = np.arange(-1.0, 1.1, 0.1)

  clevs = 0.1*clevs
  cblevs = 0.1*cblevs

  gp.set_clevs(clevs=clevs)
  gp.set_cblevs(cblevs=cblevs)

#-----------------------------------------------------------------------------------------
  second_varlist = ['T', 'ua', 'va', 'DELP', 'sphum']
  first_varlist = ['T', 'ua', 'va', 'DELP', 'sphum']

  unitlist = ['Unit (C)', 'Unit (m/s)', 'Unit (m/s)', 'Unit (pa)', 'Unit (kg/kg)']

#-----------------------------------------------------------------------------------------
  for n in range(len(second_varlist)):
    secondvar = ncsecond.variables[second_varlist[n]][0, :, :, :]
    firstvar = ncfirst.variables[first_varlist[n]][0, :, :, :]

    print('second_varlist[%d]: %s' %(n, second_varlist[n]))
    print('secondvar.shape = ', secondvar.shape)

    nlev, nlat, nlon = secondvar.shape
    print('secondvar.shape = ', secondvar.shape)
    print('firstvar.shape = ', firstvar.shape)

    gp.set_label(unitlist[n])

    for lev in range(50, nlev, 20):
      v0 = firstvar[lev,:,:]
      v1 = secondvar[lev,:,:]
      v2 = v1 - v0

      data = [v0, v1, v2]

      title = '%s at Level %d' %(second_varlist[n], lev)
      gp.set_title(title)

      print('Plotting ', title)
      print('\tv0.shape = ', v0.shape)
      print('\tv1.shape = ', v1.shape)
      print('\tv2.shape = ', v2.shape)
 
      print('\tv0.max: %f, v0.min: %f' %(np.max(v0), np.min(v0)))
      print('\tv1.max: %f, v1.min: %f' %(np.max(v1), np.min(v1)))
      print('\tv2.max: %f, v2.min: %f' %(np.max(v2), np.min(v2)))

      imagename = '%s_lev_%3.3d.png' %(second_varlist[n], lev)
      gp.set_imagename(imagename)

      gp.plot(lons, lats, data=data, obslon=secondobslon, obslat=secondobslat, omb=secondombg)

#-----------------------------------------------------------------------------------------
  ncsecond.close()
  ncfirst.close()

