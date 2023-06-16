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

      if(i == (len(axs) - 1)):
        clevs=self.incr_clevs
        cblevs=self.incr_cblevs
      else:
        clevs=self.clevs
        cblevs=self.cblevs

      pvar = data[i]

     #print('Plot No. ', i)
     #print('\tpvar.shape = ', pvar.shape)

      cyclic_data, cyclic_lons = add_cyclic_point(pvar, coord=lons)

      cs=axs[i].contourf(cyclic_lons, lats, cyclic_data, transform=proj,
                         levels=clevs, extend=self.extend,
                         alpha=self.alpha, cmap=self.cmapname)
     #               cmap=self.cmapname, extend='both')

      axs[i].set_extent([-180, 180, -90, 90], crs=proj)
      axs[i].coastlines(resolution='auto', color='k')
      axs[i].gridlines(color='lightgrey', linestyle='-', draw_labels=True)

      title = '%s min: %f, max: %f' %(self.runname[i], np.min(pvar), np.max(pvar))
      axs[i].set_title(title)
     #axs[i].set_title(self.runname[i])

      plt.colorbar(cs, ax=axs[i], pad=self.pad, ticks=cblevs,
                   orientation='vertical')

#For shared color-bar
#  #Adjust the location of the subplots on the page to make room for the colorbar
#   fig.subplots_adjust(bottom=0.1, top=0.9, left=0.05, right=0.8,
#                       wspace=0.02, hspace=0.02)

#  #Add a colorbar axis at the bottom of the graph
#   cbar_ax = fig.add_axes([0.85, 0.1, 0.05, 0.85])

#  #Draw the colorbar
#   cbar=fig.colorbar(cs, cax=cbar_ax, pad=self.pad, ticks=self.cblevs,
#                     orientation='vertical')

#   cbar.set_label(self.label, rotation=90)

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

  def set_runname(self, runname=['JEDI', 'ReInit', 'ReInit - JEDI']):
    self.runname = runname

  def set_default(self):
    self.imagename = 'sample.png'

    self.runname = ['JEDI', 'ReInit', 'ReInit - JEDI']

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

  def set_label(self, label='Unit (C)'):
    self.label = label

  def set_title(self, title='Temperature Increment'):
    self.title = title

  def set_clevs(self, clevs=[]):
    self.clevs = clevs

  def set_cblevs(self, cblevs=[]):
    self.cblevs = cblevs

  def set_incr_clevs(self, clevs=[]):
    self.incr_clevs = clevs

  def set_incr_cblevs(self, cblevs=[]):
    self.incr_cblevs = cblevs

  def set_imagename(self, imagename):
    self.imagename = imagename

  def set_cmapname(self, cmapname):
    self.cmapname = cmapname

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 0
  frtdir = '/work2/noaa/da/weihuang/cycling/sondes.gdas-cycling/2020010300'
  snddir = '/work2/noaa/da/weihuang/cycling/sepreint.jedi_C96_lgetkf_sondesonly/2020010300'

  frtfile = '%s/analysis/increment/xainc.20200103_000000z.nc4' %(frtdir)
  sndfile = '%s/analysis/increment/xainc.20200103_000000z.nc4' %(snddir)

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=',
                                                'sndfile=', 'frtfile='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--sndfile'):
      sndfile = a
    elif o in ('--frtfile'):
      frtfile = a
    else:
      assert False, 'unhandled option'

  gp = GeneratePlot(debug=debug, output=output)

  ncfrt = netcdf_dataset(frtfile)
  ncsnd = netcdf_dataset(sndfile)

  lats = ncfrt.variables['lat'][:]
  lons = ncfrt.variables['lon'][:]

#-----------------------------------------------------------------------------------------
  clevs = np.arange(-1.0, 1.02, 0.02)
  cblevs = np.arange(-1.0, 1.2, 0.2)

  gp.set_clevs(clevs=clevs)
  gp.set_cblevs(cblevs=cblevs)

#-----------------------------------------------------------------------------------------
  incr_clevs = np.arange(-0.1, 0.102, 0.002)
  incr_cblevs = np.arange(-0.1, 0.12, 0.02)

  gp.set_incr_clevs(clevs=incr_clevs)
  gp.set_incr_cblevs(cblevs=incr_cblevs)

#-----------------------------------------------------------------------------------------
  snd_varlist = ['T', 'ua', 'va', 'sphum', 'delp', 'DZ', 'o3mr']
  frt_varlist = ['T', 'ua', 'va', 'sphum', 'delp', 'DZ', 'o3mr']
 #snd_varlist = ['T', 'delp', 'sphum']
 #frt_varlist = ['T', 'delp', 'sphum']

  unitlist = ['Unit (C)', 'Unit (m/s)', 'Unit (m/s)',
              'Unit (kg/kg)', 'Unit (Pa', 'Unit (m', 'Unit (ppm)']

  runname = ['JEDI', 'ReInit', 'ReInit - JEDI']
  gp.set_runname(runname=runname)

#-----------------------------------------------------------------------------------------
  for n in range(len(snd_varlist)):
    sndvar = ncsnd.variables[snd_varlist[n]][0, :, :, :]
    frtvar = ncfrt.variables[frt_varlist[n]][0,:, :, :]

    nlev, nlat, nlon = sndvar.shape
    print('sndvar.shape = ', sndvar.shape)
    print('frtvar.shape = ', frtvar.shape)

    gp.set_label(unitlist[n])

    for lev in range(5, nlev, 10):
      v0 = frtvar[lev,:,:]
      v1 = sndvar[lev,:,:]
      v2 = v1 - v0

      data = [v0, v1, v2]

      title = '%s at Level %d' %(snd_varlist[n], lev)
      gp.set_title(title)

      print('Plotting ', title)
     #print('\tv0.shape = ', v0.shape)
     #print('\tv1.shape = ', v1.shape)
     #print('\tv2.shape = ', v2.shape)
 
      print('\t%s max: %f, min: %f' %(runname[0], np.max(v0), np.min(v0)))
      print('\t%s max: %f, min: %f' %(runname[1], np.max(v1), np.min(v1)))
      print('\t%s max: %f, min: %f' %(runname[2], np.max(v2), np.min(v2)))

      imagename = '%s_lev_%3.3d.png' %(snd_varlist[n], lev)
      gp.set_imagename(imagename)

      gp.plot(lons, lats, data=data)

#-----------------------------------------------------------------------------------------
  ncsnd.close()
  ncfrt.close()

