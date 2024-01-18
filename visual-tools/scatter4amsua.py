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

from readIODA2Obs import ReadIODA2Obs

#=========================================================================
class ScatterPlotsFor2Runs():
  def __init__(self, debug=0):
    self.debug = debug

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

    self.xlabel = 'MTS-JEDI'
    self.ylabel = 'MTS-GSI'

    self.title = '%s vs %s Scatter Plot' %(self.xlabel, self.ylabel)

  def set_imagename(self, imagename):
    self.image_name = imagename

  def set_cmapname(self, cmapname):
    self.cmapname = cmapname

  def set_label(self, xlabel, ylabel, varname, datestr=None, obstype=None):
    self.xlabel = xlabel
    self.ylabel = ylabel

    self.title = '%s vs %s: %s Scatter Plot' %(xlabel, ylabel, varname)
    imagename = '%s_%s_%s' %(xlabel, ylabel, varname)
    if(datestr is not None):
      self.title = '%s, %s' %(self.title, datestr)
      imagename = '%s_%s' %(imagename, datestr)
    if(obstype is not None):
      self.title = '%s, %s' %(self.title, obstype)
      imagename = '%s_%s' %(imagename, obstype)
    self.set_imagename(imagename)

  def set_title(self, title):
    self.title = title

  def create_image(self, plt_obj, savename):
    msg = ('Saving image as %s.' % savename)
    print(msg)
    kwargs = {'transparent': True, 'dpi': 500}
    plt_obj.savefig(savename, **kwargs)

  def display(self, image_name=None):
    if(image_name is None):
      image_name=self.image_name
    self.plt.tight_layout()
    kwargs = {'plt_obj': self.plt, 'savename': image_name}
    self.create_image(**kwargs)

    if(self.debug):
      self.plt.show()

  def scatter_plot(self, x, y, varname):
    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    self.fig = self.plt.figure()
    self.ax = self.plt.subplot()

    scatterplot = self.plt.scatter(x, y, c='blue', alpha=self.alpha)

    self.ax.set_title(self.title)

    if(varname == 'surface_pressure'):
      self.plt.xlim((-7, 7))
      self.plt.ylim((-7, 7))
    elif(varname == 'airTemperature' or varname == 'virtualTemperature'
      or varname == 'brightnessTemperature'):
      self.plt.xlim((-10, 10))
      self.plt.ylim((-10, 10))
    elif(varname == 'eastward_wind' or varname == 'northward_wind'):
      self.plt.xlim((-10, 10))
      self.plt.ylim((-10, 10))
    elif(varname == 'specific_humidity'):
      self.plt.xlim((-5, 5))
      self.plt.ylim((-5, 5))
    else:
      self.plt.xlim((-10, 10))
      self.plt.ylim((-10, 10))

    self.plt.xlabel(self.xlabel, fontsize=14)
    self.plt.ylabel(self.ylabel, fontsize=14)
    self.plt.grid(True)

    ax = self.plt.gca()
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    self.display(image_name=self.image_name)

def reorder(latx, lonx, hgtx, laty, lony, hgty, varyin):
  varyout = varyin[:]
  nv = len(latx)
  idx = [i for i in range(nv)]
  dlt = 0.0000001
  for n in range(nv):
    k = -1
    i = 0
    while (i < len(idx)):
      if(abs(latx[n]-laty[i]) < dlt):
        if(abs(lonx[n]-lony[i]) < dlt):
          if(abs(hgtx[n]-hgty[i]) < dlt):
            varyout[n] = varyin[i]
            k = i
            i = len(idx)
      i += 1;
    if(k >= 0):
      del idx[k]
  return varyout

#----------------------------------------------------------------------
if __name__ == '__main__':
  debug = 0
  topdir = '/work2/noaa/da/weihuang/EMC_cycling'
 #obstype = 'sondes'
  obstype = 'amsua_n19'
  datestr = '2022010512'

  xflist = ['mts.gsi', 'sts.gsi', 'sts.gsi', 'sts.jedi']
  yflist = ['mts.jedi', 'mts.gsi', 'sts.jedi', 'mts.jedi']

  xslist = ['MTS-GSI', 'STS-GSI', 'STS-GSI', 'STS-JEDI']
  yslist = ['MTS-JEDI', 'MTS-GSI', 'STS-JEDI', 'MTS-JEDI']

  for n in range(len(xflist)):
    datadir = '%s/%s-cycling/%s/ioda_v2_data' %(topdir, xflist[n], datestr)
    xflist[n] = '%s/%s_obs_%s.nc4' %(datadir, obstype, datestr)
    datadir = '%s/%s-cycling/%s/ioda_v2_data' %(topdir, yflist[n], datestr)
    yflist[n] = '%s/%s_obs_%s.nc4' %(datadir, obstype, datestr)

    if(os.path.exists(xflist[n])):
      print('xflist[%d] = %s' %(n, xflist[n]))
    else:
      print('xflist[%d] = %s, does not exist. Exit.' %(n, xflist[n]))
    if(os.path.exists(yflist[n])):
      print('yflist[%d] = %s' %(n, yflist[n]))
    else:
      print('yflist[%d] = %s, does not exist. Exit.' %(n, yflist[n]))

 #sys.exit(0)

#-----------------------------------------------------------------------
  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'xf=', 'yf='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--xf'):
      xf = a
    elif o in ('--yf'):
      yf = a
    else:
      assert False, 'unhandled option'

  print('debug = ', debug)
 #print('xflist = ', xflist)
 #print('yflist = ', yflist)
 #print('xslist = ', xslist)
 #print('yslist = ', yslist)

 #varname = 'airTemperature'
  varname = 'brightnessTemperature'

  for n in range(len(xflist)):
    xf = xflist[n]
    yf = yflist[n]
    xlabel = xslist[n]
    ylabel = yslist[n]

    ncxf = ReadIODA2Obs(debug=debug, filename=xf)
    latx, lonx = ncxf.get_latlon()
    hgtx = ncxf.get_var('/MetaData/heightOfSurface')
    gsix = ncxf.get_var_2d('/GsiHofXBc/brightnessTemperature')
    obsx = ncxf.get_var_2d('/ObsValue/brightnessTemperature')
    varx = obsx - gsix
    lenx = len(latx)

    ncyf = ReadIODA2Obs(debug=debug, filename=yf)
    laty, lony = ncyf.get_latlon()
    hgty = ncyf.get_var('/MetaData/heightOfSurface')
    gsiy = ncyf.get_var_2d('/GsiHofXBc/brightnessTemperature')
    obsy = ncyf.get_var_2d('/ObsValue/brightnessTemperature')
    vary = obsy - gsiy
    leny = len(laty)

    print('lenx = %d, leny = %d' %(lenx, leny))

   #for n in range(lenx):
   #  print('No %d: lat: %f, %f, lon: %f, %f, hgt: %f, %f' %(n, latx[n], laty[n], lonx[n], lony[n], hgtx[n], hgty[n]))

    channel = 1

    newvary = reorder(latx[::10], lonx[::10], hgtx[::10], laty[::10], lony[::10], hgty[::10], vary[::10, channel])
    sp42r = ScatterPlotsFor2Runs(debug=debug)

    sp42r.set_label(xlabel, ylabel, varname, datestr=datestr, obstype=obstype)
    sp42r.scatter_plot(varx[::10, channel], newvary, varname)

