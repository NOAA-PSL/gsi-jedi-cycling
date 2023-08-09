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
   #self.plotarea = [-180, 180, -30, 30]
    self.resolution = 'auto'

    self.extend = 'both'

  def showit(self):
    plt.title(self.title)
    plt.savefig(self.imgname)
   #if sys.flags.interactive:
    plt.show()

  def set_title(self, title):
    self.title = title

  def set_imgname(self, imgname):
    self.imgname = imgname

  def set_clevs(self, clevs):
    self.clevs = clevs

  def set_cblevs(self, cblevs):
    self.cblevs = cblevs

  def set_cmapname(self, cmapname):
    self.cmapname = cmapname

 #---------------------------------------------------------
  def plotit(self, x, y, z, title, imgname):
    self.proj = ccrs.PlateCarree()
    self.fig = plt.figure(figsize=(10, 5))
   #self.ax = self.fig.add_subplot(1, 1, 1, projection=slef.proj)
    self.ax = self.fig.add_subplot(1, 1, 1)

    print('Plotting ', title)
   
   #                      transform=self.proj,
    cs = self.ax.contourf(x, y, z, levels=self.clevs, extend=self.extend,
                          cmap=self.cmapname)
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
  def get_region(self, lines):
    self.nxs = 99999999
    self.nxe = -1
    self.nys = 99999999
    self.nye = -1

    notl = len(lines)
    n = 0
    while (n < notl):
      line = lines[n]
      n += 1

      if(line.find('iindex=') > 0):
        item = line.split(',')
       #print('line: ', line)
       #print('item: ', item)
        iflag, iidx = self.get_val(item[0])
        jflag, jidx = self.get_val(item[1])

        i = int(iidx)
        j = int(jidx)

        if(i > self.nxe):
          self.nxe = i
        if(i < self.nxs):
          self.nxs = i

        if(j > self.nye):
          self.nye = j
        if(j < self.nys):
          self.nys = j

 #-----------------------------------------------------------------------------------------
  def get_var(self, filename):
    fin = open(filename,'r')
    lines = fin.readlines()
    fin.close()

    self.get_region(lines)
    nx = self.nxe - self.nxs + 1
    ny = self.nye - self.nys + 1

    self.ovar = np.zeros((ny, nx))
    self.pvar = np.zeros((ny, nx))
    self.xidx = np.zeros((ny, nx))
    self.yidx = np.zeros((ny, nx))

    npass = 1
    kpass = 1
    kidx = -1
    notl = len(lines)
    n = 0
    while (n < notl):
      line = lines[n]
      n += 1

      if(line.find('iindex=') > 0):
        item = line.split(',')
       #print('line: ', line)
       #print('item: ', item)
        iflag, iidx = self.get_val(item[0])
        jflag, jidx = self.get_val(item[1])
        xflag, vidx = self.get_val(item[2])
        vflag, fval = self.get_val(item[3])

        i = int(iidx) - self.nxs
        j = int(jidx) - self.nys
        if(vflag == 'oro'):
          if(kidx > j):
            print('n: ', n)
            print('line: ', line)
            print('item: ', item)
            kpass += 1
            kidx = -1
            if(kpass > npass):
              break

          self.xidx[j,i] = float(i)
          self.yidx[j,i] = float(j)
          self.ovar[j,i] = float(fval)

         #print('self.xidx[%d,%d] = %s, kidx = %d ' %(j, i, iidx, kidx))
         #print('self.yidx[%d,%d] = %s ' %(j, i, jidx))
         #print('self.ovar[%d,%d] = %f ' %(j, i, self.ovar[j,i]))
        else:
          self.pvar[j,i] = float(fval)

        kidx = j

    return self.ovar

 #-----------------------------------------------------------------------------------------
  def process(self, datadir=None, flnm=None):
    path = '%s/%s' %(datadir, flnm)
    pvar = self.get_var(path)

    print('self.xidx = ', self.xidx)
    print('self.xidx.shape = ', self.xidx.shape)
    print('self.yidx = ', self.yidx)
    print('self.yidx.shape = ', self.yidx.shape)
    print('pvar = ', pvar)
    print('pvar.shape = ', pvar.shape)

    clevs = np.arange(0.0, 4010.0, 10.0)
    cblevs = np.arange(0.0, 4500.0, 500.0)

   #clevs = np.arange(-10.0, 0.1, 0.1)
   #cblevs = np.arange(-10.0, 1.0, 1.0)

    self.gp.set_clevs(clevs)
    self.gp.set_cblevs(cblevs)

    title = flnm.replace('.', ' ')
    imgname = '%s.png' %(flnm)
    print('%s min: %f, max: %f' %(flnm, np.min(pvar), np.max(pvar)))
    self.gp.plotit(self.xidx, self.yidx, pvar, title, imgname)

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

