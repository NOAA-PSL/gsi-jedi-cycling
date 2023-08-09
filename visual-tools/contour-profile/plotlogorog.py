#=========================================================================
import os, sys
import getopt
import numpy as np
import netCDF4 as nc4

from datetime import datetime, timezone, timedelta
import matplotlib
import matplotlib.pyplot as plt

import cartopy.crs as ccrs

import tkinter
import matplotlib

#if sys.flags.interactive:
matplotlib.use('TkAgg')

#=========================================================================
class GeneratePlot():
  def __init__(self, debug=0, title='Unknown', imgname='sample'):
    self.debug = debug
    self.title = title
    self.imgname = imgname

    self.setup_default()

  def setup_default(self):
   #cmapname = coolwarm, bwr, rainbow, jet, seismic, nipy_spectral
    self.cmapname = 'jet'

    self.clevs = np.arange(950.0, 1051.0, 1.0)
    self.cblevs = np.arange(950.0, 1060, 10.0)

    self.orientation = 'horizontal'
    self.pad = 0.1
    self.fraction = 0.06

    self.plotarea = [-180, 180, -90, 90]
    self.resolution = 'auto'

    self.extend = 'both'

 #---------------------------------------------------------
  def showit(self):
    plt.title(self.title)
    plt.savefig(self.imgname)
   #if sys.flags.interactive:
    plt.show()

 #---------------------------------------------------------
  def set_title(self, title):
    self.title = title

 #---------------------------------------------------------
  def set_imgname(self, imgname):
    self.imgname = imgname

 #---------------------------------------------------------
  def set_clevs(self, clevs):
    self.clevs = clevs

 #---------------------------------------------------------
  def set_cblevs(self, cblevs):
    self.cblevs = cblevs

 #---------------------------------------------------------
  def set_cmapname(self, cmapname):
    self.cmapname = cmapname

 #---------------------------------------------------------
  def add_coastline(self):
    self.ax.set_extent(self.plotarea, crs=self.proj)
   #self.ax.coastlines(resolution=self.resolution, color='k')
    self.ax.gridlines(color='lightgrey', linestyle='-', draw_labels=True)
   #self.ax.set_global()

 #---------------------------------------------------------
  def plotit(self, x, y, z, title, imgname):
    self.proj = ccrs.PlateCarree()
    self.fig = plt.figure(figsize=(10, 5))
    self.ax = self.fig.add_subplot(1, 1, 1, projection=self.proj)

    print('Plotting ', title)
   
    cs = self.ax.tricontourf(x, y, z, levels=self.clevs, extend=self.extend,
                             transform=self.proj, cmap=self.cmapname)
    cbar = plt.colorbar(cs, ax=self.ax, orientation=self.orientation,
                        ticks=self.cblevs,
                        pad=self.pad, fraction=self.fraction)

    self.set_title(title)
    self.set_imgname(imgname)

    self.showit()

#=========================================================================
class PlotVariable():
  def __init__(self, debug=0):
    self.debug = debug
    self.monthname = ['NonExist', 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
                      'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

    print('debug: ', debug)

    self.gp = GeneratePlot(debug)

 #-----------------------------------------------------------------------------------------
  def get_val(self, item):
    info = item.split('=')
    flg = info[0].strip()
    val = info[1].strip()

    return flg, val

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

    self.oro = []
    self.lat = []
    self.lon = []

    notl = len(lines)
    n = 0
    while (n < notl):
      line = lines[n]
      n += 1

      if(line.find('geoiter=GeometryIterator') > 0):
        item = line.split(' / ')
       #print('line: ', line)
       #print('item: ', item)
        headlat = item[0].split(':')
       #print('headlat: ', headlat)
        lat = float(headlat[1].strip())
        lon = float(item[1].strip())
        if(lon > 180.0):
          lon -= 360.0
        self.lat.append(lat)
        self.lon.append(lon)

        line = lines[n]
        n += 1

        item = line.split('=')
       #print('line: ', line)
       #print('item: ', item)
        if(item[1].find('nsp') >= 0):
          oplist = item[1].split(' ')
          oro = float(oplist[0])
        else:
          oro = float(item[1])
        self.oro.append(oro)

       #print('lat: %f, lon: %f, org: %f' %(lat, lon, oro))

    self.set_region()

    return self.oro

 #-----------------------------------------------------------------------------------------
  def process(self, datadir=None, flnm=None):
    path = '%s/%s' %(datadir, flnm)
    pvar = self.get_var(path)

   #print('pvar = ', pvar)
    print('len(pvar) = ', len(pvar))

    clevs = np.arange(0.0, 2010.0, 10.0)
    cblevs = np.arange(0.0, 2500.0, 500.0)

   #clevs = np.arange(-10.0, 0.1, 0.1)
   #cblevs = np.arange(-10.0, 1.0, 1.0)

    self.gp.set_clevs(clevs)
    self.gp.set_cblevs(cblevs)

    title = flnm.replace('.', ' ')
    imgname = '%s.png' %(flnm)
    print('%s min: %f, max: %f' %(flnm, np.min(pvar), np.max(pvar)))
    self.gp.plotit(self.lon, self.lat, pvar, title, imgname)

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 0

  datadir = '/scratch2/BMC/gsienkf/Wei.Huang/jedi/jedi_test2/stdoutNerr'
  flnm = 'stdout.00000051'

 #-----------------------------------------------------------------------------------------
  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'datadir=', 'flnm='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--datadir'):
      datadir = a
    elif o in ('--flnm'):
      flnm = a
    else:
      assert False, 'unhandled option'

 #-----------------------------------------------------------------------------------------
  pv = PlotVariable(debug=debug)
  pv.process(datadir=datadir, flnm=flnm)

