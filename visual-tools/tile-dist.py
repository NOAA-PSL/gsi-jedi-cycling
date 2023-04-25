#########################################################################
#$Id: bld.py 28 2021-01-21 15:10:31Z whuang $
#$Revision: 28 $
#$HeadURL: file:///Users/whuang/.wei_svn_repository/trunk/jedi-build-tools/bld.py $
#$Date: 2021-01-21 08:10:31 -0700 (Thu, 21 Jan 2021) $
#$Author: whuang $
#########################################################################

import getopt
import os, sys
import types
import time
import datetime
import subprocess

import matplotlib.pyplot as plt
import numpy as np

import matplotlib
import matplotlib.pyplot

from matplotlib import cm
from mpl_toolkits.basemap import Basemap

def cmdout(command):
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    ostr = result.stdout
    return ostr.strip()

#=========================================================================
class GeneratePlot():
  def __init__(self, debug=0, output=0):
    self.debug = debug
    self.output = output

    self.set_default()

    self.precision = 1

  def set_precision(self, precision=1):
    self.precision = precision

  def set_grid(self, lat, lon):
    self.lat = np.array(lat)
    self.lon = np.array(lon)

  def set_default(self):
    self.image_name = 'sample.png'

   #cmapname = coolwarm, bwr, rainbow, jet, seismic
   #self.cmapname = 'bwr'
   #self.cmapname = 'coolwarm'
   #self.cmapname = 'rainbow'
    self.cmapname = 'jet'

    self.obslat = []
    self.obslon = []

   #self.clevs = np.arange(-0.2, 0.21, 0.01)
   #self.cblevs = np.arange(-0.2, 0.3, 0.1)

    self.extend = 'both'
    self.alpha = 0.5
    self.pad = 0.1
    self.orientation = 'horizontal'
    self.size = 'large'
    self.weight = 'bold'
    self.labelsize = 'medium'

    self.label = 'Distance (m)'
    self.title = 'Distance (m)'

  def set_clevs(self, clevs=[]):
    self.clevs = clevs

  def set_cblevs(self, cblevs=[]):
    self.cblevs = cblevs

  def set_imagename(self, imagename):
    self.image_name = imagename

  def set_cmapname(self, cmapname):
    self.cmapname = cmapname

  def set_label(self, label):
    self.label = label

  def set_title(self, title):
    self.title = title

  def build_basemap(self):
    basemap_dict = {'resolution': 'c', 'projection': 'cyl',
                    'llcrnrlat': -90.0, 'llcrnrlon': 0.0,
                    'urcrnrlat':  90.0, 'urcrnrlon': 360.0}
    basemap_dict['lat_0'] = 0.0
    basemap_dict['lon_0'] = 180.0

    basemap = Basemap(**basemap_dict)

    return basemap

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

  def plot(self, pvar):
    self.basemap = self.build_basemap()

    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    self.fig = self.plt.figure()
    self.ax = self.plt.subplot()

    msg = ('plot variable min: %s, max: %s' % (np.min(pvar), np.max(pvar)))
    print(msg)

    (self.x, self.y) = self.basemap(self.lon, self.lat)

    v1d = np.array(pvar)

    print('self.x.shape = ', self.x.shape)
    print('self.y.shape = ', self.y.shape)
    print('v1d.shape = ', v1d.shape)

   #contfill = self.basemap.contourf(self.x, self.y, v1d, tri=True,
   #                                 levels=self.clevs, extend=self.extend,
   #                                 alpha=self.alpha, cmap=self.cmapname)
    contfill = self.plt.tricontourf(self.x, self.y, v1d,
                                    alpha=self.alpha, cmap=self.cmapname)

    cb = self.fig.colorbar(contfill, orientation=self.orientation,
                           pad=self.pad)

    cb.set_label(label=self.label, size=self.size, weight=self.weight)

    cb.ax.tick_params(labelsize=self.labelsize)
   #if(self.precision == 0):
   #  cb.ax.set_xticklabels(['{:.0f}'.format(x) for x in self.cblevs], minor=False)
   #elif(self.precision == 1):
   #  cb.ax.set_xticklabels(['{:.1f}'.format(x) for x in self.cblevs], minor=False)
   #elif(self.precision == 2):
   #  cb.ax.set_xticklabels(['{:.2f}'.format(x) for x in self.cblevs], minor=False)
   #else:
   #  cb.ax.set_xticklabels(['{:.3f}'.format(x) for x in self.cblevs], minor=False)

    self.ax.set_title(self.title)

    self.plot_coast_lat_lon_line()

    self.display(output=self.output, image_name=self.image_name)

  def plot_coast_lat_lon_line(self):
   #https://matplotlib.org/basemap/users/geography.html
   #map.drawmapboundary(fill_color='aqua')
   #map.fillcontinents(color='#cc9955', lake_color='aqua')
   #map.drawcounties()
   #map.drawstates(color='0.5')

   #draw coastlines
    color = 'black'
    linewidth = 0.5
    self.basemap.drawcoastlines(color=color, linewidth=linewidth)

   #draw parallels
    color = 'green'
    linewidth = 0.5
    fontsize = 8
    dashes = [10, 10]
    circles = np.arange(-90,90,30)
    self.basemap.drawparallels(np.arange(-90,90,30),labels=[1,1,0,1],
                               color=color, linewidth=linewidth,
                               dashes=dashes, fontsize=fontsize)

   #draw meridians
    color = 'green'
    linewidth = 0.5
    fontsize = 8
    dashes = [10, 10]
    meridians = np.arange(0,360,30)
    self.basemap.drawmeridians(np.arange(0,360,30),labels=[1,1,0,1],
                               color=color, linewidth=linewidth,
                               dashes=dashes, fontsize=fontsize)

#------------------------------------------------------------------
""" DataTile """
class DataTile:
  """ Constructor """
  def __init__(self, debug=0, workdir=None):
    """ Initialize class attributes """
    self.debug = debug
    self.workdir = workdir

    if(workdir is None):
      print('workdir not defined. Exit.')
      sys.exit(-1)

    nc = 0
    search_more = True
    self.filelist = []
    while(search_more):
      filename = '%s/stdout.%8.8d' %(workdir, nc)
      if(os.path.exists(filename)):
       #print('File No %d: %s' %(nc, filename))
        self.filelist.append(filename)
        nc += 1
      else:
        search_more = False

   #self.filelist.sort()
    print('filelist: ', self.filelist)

  def process(self):
    self.lon = []
    self.lat = []
    self.dist = []

    nc = 0
    for flnm in self.filelist:
      nc += 1
      if(self.debug):
        print('Processing case ' + str(nc) + ': ' + flnm)
      lon, lat, dist = self.get_stats(flnm)
     #print('len(lon) = ', len(lon))
     #print('len(lat) = ', len(lat))
     #print('len(dist) = ', len(dist))
      self.lon.extend(lon)
      self.lat.extend(lat)
      self.dist.extend(dist)

    print('len(self.lon) = ', len(self.lon))
    print('len(self.lat) = ', len(self.lat))
    print('len(self.dist) = ', len(self.dist))

  def get_data(self):
    return np.array(self.lat), np.array(self.lon), np.array(self.dist)

  def get_stats(self, flnm):
    lon = []
    lat = []
    dist = []

    with open(flnm) as fh:
      lines = fh.readlines()
      num_lines = len(lines)
     #print('Total number of lines: ', num_lines)

      nl = 0
      while(nl < num_lines):
       #print('Line[%d]: %s' %(nl, lines[nl].strip()))
        if(lines[nl].find('Longitude: ') >= 0):
         #print('Line[%d]: %s' %(nl, lines[nl].strip()))
          istr = lines[nl]
         #istr = istr.replace(',', ' ')
          item = istr.split(': ')
         #for n in range(len(item)):
         #  print('item[%d]: %s' %(n, item[n]))
          lonstr = item[1].split(', ')
          lonval = float(lonstr[0])
          lon.append(lonval)
          latstr = item[2].split(', ')
          latval = float(latstr[0])
          lat.append(latval)
          distval = float(item[3])
          dist.append(distval)
         #break
        nl += 1

    return lon, lat, dist

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 0
  iamgename = 'dist.png'
 #workdir = '/work2/noaa/gsienkf/weihuang/jedi/per_core_timing/run/surf/run_80.40t1n_36p/stdoutNerr'
 #workdir = '/work2/noaa/gsienkf/weihuang/jedi/run/run_80.40t8n_312p/stdoutNerr'
 #workdir = '/scratch2/BMC/gsienkf/Wei.Huang/jedi/dev/build/intel/fv3-jedi/test/stdoutNerr'
  workdir = '/work2/noaa/gsienkf/weihuang/jedi/case_study/sondes/run_80.40t1n_36p/stdoutNerr'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=', 'workdir=', 'imagename='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--workdir'):
      workdir = a
    elif o in ('--imagename'):
      imagename = a
    else:
      assert False, 'unhandled option'

  dt = DataTile(debug=debug, workdir=workdir)
  dt.process()
  lat, lon, dist = dt.get_data()

  gp = GeneratePlot(debug=debug, output=output)
  gp.set_grid(lat, lon)

  gp.set_imagename(imagename)
  title = 'Distance to Patch Center (Unit: m)'
  gp.set_title(title)
  gp.plot(dist)

