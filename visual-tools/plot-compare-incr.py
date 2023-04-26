import getopt
import os, sys
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable

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

  def plot(self, lons, lats, data=[]):
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

    self.runname = ['REINIT', 'IASI', 'REINIT - IASI']

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
  output = 0
  firstfile = '/work2/noaa/da/weihuang/cycling/scripts/iasi-amsua/Data/analysis.iasi_metop+n15+n18+n19/increment/interp2gaussian_grid.nc4'
  secondfile = '/work2/noaa/da/weihuang/cycling/scripts/iasi-amsua/Data/analysis.iasi_metop+n15+n18+n19.separate_reinit_observer/increment/interp2gaussian_grid.nc4'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=',
                                                'secondfile=', 'firstfile='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--secondfile'):
      secondfile = a
    elif o in ('--firstfile'):
      firstfile = a
    else:
      assert False, 'unhandled option'

  gp = GeneratePlot(debug=debug, output=output)

  ncsecond = netcdf_dataset(secondfile)
  ncfirst = netcdf_dataset(firstfile)
  lats = ncsecond.variables['lat'][:]
  lons = ncsecond.variables['lon'][:]

#-----------------------------------------------------------------------------------------
  clevs = np.arange(-1.0, 1.01, 0.01)
  cblevs = np.arange(-1.0, 1.1, 0.1)

  gp.set_clevs(clevs=clevs)
  gp.set_cblevs(cblevs=cblevs)

#-----------------------------------------------------------------------------------------
 #second_varlist = ['T_inc', 'u_inc', 'v_inc', 'sphum_inc', 'o3mr_inc']
 #first_varlist = ['T_inc', 'u_inc', 'v_inc', 'sphum_inc', 'o3mr_inc']
  second_varlist = ['T_inc', 'u_inc', 'v_inc', 'delz_inc', 'sphum_inc']
  first_varlist = ['T_inc', 'u_inc', 'v_inc', 'delz_inc', 'sphum_inc']

 #unitlist = ['Unit (C)', 'Unit (m/s)', 'Unit (m/s)',
 #            'Unit (kg/kg)', 'Unit (Pa', 'Unit (m', 'Unit (ppm)']
  unitlist = ['Unit (C)', 'Unit (m/s)', 'Unit (m/s)', 'Unit (m)', 'Unit (kg/kg)']

#-----------------------------------------------------------------------------------------
  for n in range(len(second_varlist)):
    secondvar = ncsecond.variables[second_varlist[n]][:, :, :]
    firstvar = ncfirst.variables[first_varlist[n]][:, :, :]

    nlev, nlat, nlon = secondvar.shape
    print('secondvar.shape = ', secondvar.shape)
    print('firstvar.shape = ', firstvar.shape)

    gp.set_label(unitlist[n])

    for lev in range(5, nlev, 10):
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

      gp.plot(lons, lats, data=data)

#-----------------------------------------------------------------------------------------
  ncsecond.close()
  ncfirst.close()

