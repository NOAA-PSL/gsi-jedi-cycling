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

    self.label = 'Time (sec)'
    self.title = 'Time (sec)'

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
""" TimingTile """
class TimingTile:
  """ Constructor """
  def __init__(self, debug=0, workdir=None):
    """ Initialize class attributes """
    self.debug = debug
    self.workdir = workdir

    if(workdir is None):
      print('workdir not defined. Exit.')
      sys.exit(-1)

   #nc = 0
   #self.filelist = []
   #for root, dirs, files in os.walk(workdir):
   #  for filename in files:
   #    if(filename.find('stderr') >= 0):
   #      continue
   #   #print('File No %d: %s' %(nc, filename))
   #    self.filelist.append(filename)
   #    nc += 1

   #self.filelist.sort()
   #print('filelist: ', self.filelist)

    search_more = True
    self.filelist = []
    nc = 0
    while(search_more):
      flnm = '%s/stdout.%8.8d' %(workdir, nc)
      nc += 1
      if(os.path.exists(flnm)):
        print('File No %d: %s' %(nc, flnm))
        self.filelist.append(flnm)
      else:
        search_more = False

  def process(self):
    self.lon = []
    self.lat = []
    self.loc = []
    self.stats = []

    nc = 0
    for flnm in self.filelist:
      nc += 1
      if(self.debug):
        print('Processing case ' + str(nc) + ': ' + flnm)
      lon, lat, stats = self.get_stats(flnm)
      loc = {}
      loc['lon'] = lon
      loc['lat'] = lat
      self.loc.append(loc)
      self.stats.append(stats)
      self.lon.extend(lon)
      self.lat.extend(lat)

  def get_latlon(self):
    return self.lat, self.lon

  def get_val(self, name):
   #val = np.zeros(len(self.lon), dtype=float)
   #val = np.linspace(1, len(self.lon), len(self.lon))
    val = []
    idx = self.get_idx(name)
    i = 0
    for n in range(len(idx)):
      if(idx[n] >= 0):
        t = 0.001*self.stats[n][idx[n]]['time']
      else:
        t = 0.0

      print('Tile %d time %f, name: %s' %(n, t, name))

      ni = len(self.loc[n]['lon'])
      for k in range(ni):
        val.append(t)
        i += 1

    print('len(self.lon) = ', len(self.lon))
    print('len(val) = ', len(val))

    return val
      
  def get_stats(self, flnm):
    lon = []
    lat = []
    time = []

    with open(flnm) as fh:
      lines = fh.readlines()
      num_lines = len(lines)
     #print('Total number of lines: ', num_lines)

      nl = 0
      while(nl < num_lines):
        if(lines[nl].find('Longitude:') > 0):
          item = lines[nl].split(':')
          lonitem = item[1].split(',')
          lonval = float(lonitem[0].strip())
          latval = float(item[2].strip())
         #print('lon: %f, lat: %f' %(lonval, latval))
          if(lonval < 0.0):
            lonval += 360.0
          lon.append(lonval)
          lat.append(latval)
       #if(lines[nl].find('Longitude:') > 0):
       #  item = lines[nl].split(':')
       #  lonval = float(item[1].strip())
       # #print('lon: %f' %(lonval))
       #  lon.append(lonval)
       #elif(lines[nl].find('Latitude:') > 0):
       #  item = lines[nl].split(':')
       #  latval = float(item[1].strip())
       # #print('lat: %f' %(latval))
       #  lat.append(latval)
        elif(lines[nl].find('Timing Statistics') > 0):
          if(lines[nl].find('OOPS_STATS ') >= 0):
            nl += 1
            continue
         #if(self.debug):
         #  print('Start Timing Statistics')
          nl, stats = self.time_stats(lines, nl)
          nl += num_lines
        nl += 1

    return lon, lat, stats

  def time_stats(self, lines, nl):
    stats = {}
    going = 1
    idx = 0
   #print('lines[nl]:', lines[nl])

    ns = nl + 3
   #print('2. lines[nl]:', lines[nl])

    while(going):
      line = lines[ns].strip()
      ns += 1
      if(line.find('Timing Statistics') > 0):
        going = 0
        break
      if(line.find('OOPS_STATS') >= 0):
        continue

     #print('Line ' + str(ns) + ': ' + line)
      item = line.split(': ')
     #print('item=', item)
      name = item[0].strip()

      tstr = item[1].strip()
      while(tstr.find('  ') > 0):
        tstr = tstr.replace('  ', ' ')
      nlist = tstr.split(' ')
     #print('nlist=', nlist)

      tinfo = {}
      tinfo['name'] = name
      if(len(nlist) < 3):
        tinfo['time'] = float(nlist[0][0:-8])
        tinfo['call'] = int(nlist[0][-8:])
       #print('tinfo=', tinfo)
       #sys.exit(-1)
      else:
        tinfo['time'] = float(nlist[0])
        tinfo['call'] = int(nlist[1])

      stats[idx] = tinfo

     #pinfo = '\t%50s%10.2f%8d' %(stats[idx]['name'], stats[idx]['time'], stats[idx]['call'])
     #print(pinfo)

      idx += 1

    return ns, stats

  def get_idx(self, name):
    index = []
    for n in range(len(self.stats)):
      stats = self.stats[n]
      idx = -1
      for k in stats.keys():
       #if(n == 0):
       #  print('No %d name: %s' %(k, stats[k]['name']))
        if(stats[k]['name'] == name):
          idx = k
          break
      index.append(idx)

    return index

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 0
  workdir = '/work2/noaa/da/weihuang/cycling/gdas-cycling/2020010212/stdoutNerr'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=', 'workdir='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--workdir'):
      workdir = a
    else:
      assert False, 'unhandled option'

  tt = TimingTile(debug=debug, workdir=workdir)
  tt.process()
  lat, lon = tt.get_latlon()

  gp = GeneratePlot(debug=debug, output=output)
  gp.set_grid(lat, lon)

  namelist = ['oops::GETKFSolver::applyWeights',
              'oops::GETKFSolver::computeHofX',
              'oops::GETKFSolver::computeWeights',
              'oops::GETKFSolver::measurementUpdate',
              'oops::ObsSpace::ObsSpace',
              'oops::Geometry::Geometry',
              'oops::State::State',
              'oops::State::write',
              'util::Timers::Total',
              'util::Timers::measured']

  for name in namelist:
    print('processing: ', name)
    val = tt.get_val(name)
    namestr = name.replace('::', '_')
    namestr = namestr.replace(' ', '_')
    gp.set_imagename(namestr)
    gp.set_title(name)
    gp.plot(val)

