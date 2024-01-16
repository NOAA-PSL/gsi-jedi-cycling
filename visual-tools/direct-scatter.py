#=========================================================================
import os
import sys
import types
import getopt

import numpy as np
import matplotlib
import matplotlib.pyplot

import matplotlib.cm as cm

#from matplotlib.colors import Normalize
#from matplotlib.ticker import MultipleLocator

from matplotlib import colors
from matplotlib.ticker import PercentFormatter

import netCDF4

#=========================================================================
class ScatterPlotsFor2Runs():
  def __init__(self, debug=0, output=0):
    self.debug = debug
    self.output = output

    self.set_default()

    self.precision = 1

  def set_precision(self, precision=1):
    self.precision = precision

  def set_default(self):
    self.image_name = 'sample.png'

   #cmapname = coolwarm, bwr, rainbow, jet, seismic
    self.cmapname = 'bwr'
   #self.cmapname = 'rainbow'
   #self.cmapname = 'seismic'

    self.extend = 'both'
    self.alpha = 0.5
    self.pad = 0.1
    self.orientation = 'horizontal'
    self.size = 'large'
    self.weight = 'bold'
    self.labelsize = 'medium'

    self.label = 'JEDI vs GSI'
    self.title = 'JEDI vs GSI Scatter Plot'

  def set_imagename(self, imagename):
    self.image_name = imagename

  def set_cmapname(self, cmapname):
    self.cmapname = cmapname

  def set_label(self, label):
    self.label = label

  def set_title(self, title):
    self.title = title

  def create_image(self, plt_obj, savename):
    msg = ('Saving image as %s.' % savename)
    print(msg)
    kwargs = {'transparent': True, 'dpi': 500}
    plt_obj.savefig(savename, **kwargs)

  def display(self, output=False, image_name=None):
    if(output):
      if(image_name is None):
        image_name=self.image_name
      self.plt.tight_layout()
      kwargs = {'plt_obj': self.plt, 'savename': image_name}
      self.create_image(**kwargs)
    else:
      self.plt.show()

  def scatter_plot(self, x, y, varname=None):
    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    self.fig = self.plt.figure()
    self.ax = self.plt.subplot()

    print('self.cmapname = ', self.cmapname)
   #scatterplot = self.plt.scatter(x, y, s=10, c='blue', alpha=self.alpha)
    scatterplot = self.plt.scatter(x, y, c='blue', alpha=self.alpha)

    self.ax.set_title(self.title)

    if(varname == 'surface_pressure'):
      self.plt.xlim((-7, 7))
      self.plt.ylim((-7, 7))
    elif(varname == 'airTemperature'):
      self.plt.xlim((-10, 10))
      self.plt.ylim((-10, 10))
    elif(varname == 'eastward_wind' or varname == 'northward_wind'):
      self.plt.xlim((-10, 10))
      self.plt.ylim((-10, 10))
    elif(varname == 'specific_humidity'):
      self.plt.xlim((-5, 5))
      self.plt.ylim((-5, 5))

    self.plt.xlabel('JEDI_omb', fontsize=14)
    self.plt.ylabel('GSI_omb', fontsize=14)
    self.plt.grid(True)

    ax = self.plt.gca()
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    self.display(output=self.output, image_name=self.image_name)

#----------------------------------------------------------------------
if __name__ == '__main__':
  debug = 1
  output = 0
  topdir = '/work2/noaa/da/weihuang/EMC_cycling'

  datestr = '2022010900'
  varname = 't'
  case1 = 'jedi'
  case2 = 'gsi'

  datadir1 = '%s/%s-cycling/%s' %(topdir, case1, datestr)
  f1 = '%s/diag_conv_%s_ges.%s_ensmean.nc4' %(datadir1, varname, datestr)

  datadir2 = '%s/%s-cycling/%s' %(topdir, case2, datestr)
  f2 = '%s/diag_conv_%s_ges.%s_ensmean.nc4' %(datadir2, varname, datestr)

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=',
                                                'f1=', 'f2=', 'varname='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--f1'):
      f1 = a
    elif o in ('--f2'):
      f2 = a
    elif o in ('--varname'):
      varname = a
    else:
      assert False, 'unhandled option'

  print('debug = ', debug)
  print('output = ', output)
  print('f1 = ', f1)
  print('f2 = ', f2)
  print('varname = ', varname)

  ncf1 = netCDF4.Dataset(f1, 'r')
  lat1 = ncf1['Latitude'][:]
  lon1 = ncf1['Longitude'][:]
  v1 = ncf1['Obs_Minus_Forecast_adjusted']
  len1 = len(lat1)

  ncf2 = netCDF4.Dataset(f2, 'r')
  lat2 = ncf2['Latitude'][:]
  lon2 = ncf2['Longitude'][:]
  v2 = ncf2['Obs_Minus_Forecast_adjusted']
 #v2 = ncf2['u_Obs_Minus_Forecast_unadjusted']
  len2 = len(lat2)

  print('len1 = %d, len2 = %d' %(len1, len2))

  sp42r = ScatterPlotsFor2Runs(debug=debug, output=output)
  sp42r.scatter_plot(v1[::10], v2[::10], varname=varname)

