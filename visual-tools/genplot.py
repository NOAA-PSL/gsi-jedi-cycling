#=========================================================================
import os
import sys
import types
import getopt

import numpy as np
import matplotlib
import matplotlib.pyplot

from matplotlib import cm
from mpl_toolkits.basemap import Basemap
from matplotlib.ticker import MultipleLocator
from modelVerticalpressure import ModelVerticalPressure

#=========================================================================
class GeneratePlot():
  def __init__(self, debug=0, output=0, lat=[], lon=[]):
    self.debug = debug
    self.output = output

    self.set_default()
    self.set_grid(lat, lon)

   #------------------------------------------------------------------------------
    filename = '/work/noaa/gsienkf/weihuang/jedi/case_study/sondes/Data/bkg/fv_core.res.nc'
    self.mvp = ModelVerticalPressure(debug=debug, filename=filename)
   #prs = self.mvp.get_pressure()
   #print('len(prs) = ', len(prs))
   #for n in range(len(prs)):
   #  print('Level %d pressure %f' %(n, prs[n]))
    self.logp = self.mvp.get_logp()
    self.markpres = self.mvp.get_markpres()
    self.marklogp = self.mvp.get_marklogp()

    self.precision = 1

  def set_precision(self, precision=1):
    self.precision = precision

  def get_markpres(self):
    return self.markpres

  def set_markpres(self, markpres=[]):
    self.markpres = markpres
    self.mvp.set_markpres(markpres = markpres)
    self.marklogp = self.mvp.get_marklogp()

  def set_default(self):
    self.image_name = 'sample.png'

   #self.basemap = self.build_basemap()

   #self.plt = matplotlib.pyplot
   #try:
   #  self.plt.close('all')
   #  self.plt.clf()
   #except Exception:
   #  pass

   #self.fig = self.plt.figure()
   #self.ax = self.plt.subplot()

   #cmapname = coolwarm, bwr, rainbow, jet, seismic
    self.cmapname = 'bwr'

    self.clevs = np.arange(-2.0, 2.05, 0.05)
    self.cblevs = np.arange(-2.0, 2.5, 0.5)

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

    self.label = 'Distance (km)'
    self.title = 'Distance to Patch/Tile Center'

  def set_clevs(self, clevs=[]):
    self.clevs = clevs

  def set_cblevs(self, cblevs=[]):
    self.cblevs = cblevs

  def set_obs_latlon(self, obslat=[], obslon=[]):
    self.obslat = obslat
    self.obslon = obslon

  def set_imagename(self, imagename):
    self.image_name = imagename

  def set_cmapname(self, cmapname):
    self.cmapname = cmapname

  def set_label(self, label):
    self.label = label

  def set_title(self, title):
    self.title = title

  def set_grid(self, lat, lon):
    self.nlat = len(lat)
    self.nlon = len(lon)

    print('self.nlat = ', self.nlat)
    print('self.nlon = ', self.nlon)

    lon2d = np.zeros((self.nlat, self.nlon), dtype=float)
    lat2d = np.zeros((self.nlat, self.nlon), dtype=float)

    for n in range(self.nlat):
      lon2d[n, :] = lon[:]
    for n in range(self.nlon):
      lat2d[:, n] = lat[:]

    self.lon1d = np.reshape(lon2d, (lon2d.size, ))
    self.lat1d = np.reshape(lat2d, (lat2d.size, ))

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

  def plot(self, pvar, addmark=0, marker='x', size=3, color='green'):
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
    print('pvar.shape = ', pvar.shape)
    print('pvar.size = ', pvar.size)

    (self.x, self.y) = self.basemap(self.lon1d, self.lat1d)
   #(self.x, self.y) = np.meshgrid(lon1d, lat1d)
    v1d = np.reshape(pvar, (pvar.size, ))

    contfill = self.basemap.contourf(self.x, self.y, v1d, tri=True,
                                     levels=self.clevs, extend=self.extend,
                                     alpha=self.alpha, cmap=self.cmapname)

    cb = self.fig.colorbar(contfill, orientation=self.orientation,
                           pad=self.pad, ticks=self.cblevs)

    cb.set_label(label=self.label, size=self.size, weight=self.weight)

    cb.ax.tick_params(labelsize=self.labelsize)
    if(self.precision == 0):
      cb.ax.set_xticklabels(['{:.0f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 1):
      cb.ax.set_xticklabels(['{:.1f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 2):
      cb.ax.set_xticklabels(['{:.2f}'.format(x) for x in self.cblevs], minor=False)
    else:
      cb.ax.set_xticklabels(['{:.3f}'.format(x) for x in self.cblevs], minor=False)

    self.ax.set_title(self.title)

    self.plot_coast_lat_lon_line()

    if(addmark):
      self.add_obs_marker(marker=marker, size=size, color=color)

    self.display(output=self.output, image_name=self.image_name)

  def plot_without_marker(self, pvar):
    self.basemap = self.build_basemap()

    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    self.fig = self.plt.figure()
    self.ax = self.plt.subplot()

    msg = ('plot variable min: %s, max: %s' % (pvar.min(), pvar.max()))
    print(msg)

    (self.x, self.y) = self.basemap(self.lon1d, self.lat1d)
   #(self.x, self.y) = np.meshgrid(lon1d, lat1d)
    v1d = np.reshape(pvar, (pvar.size, ))

    contfill = self.basemap.contourf(self.x, self.y, v1d, tri=True,
                                     levels=self.clevs, extend=self.extend,
                                     alpha=self.alpha, cmap=self.cmapname)

    cb = self.fig.colorbar(contfill, orientation=self.orientation,
                           pad=self.pad, ticks=self.cblevs)

    cb.set_label(label=self.label, size=self.size, weight=self.weight)

    cb.ax.tick_params(labelsize=self.labelsize)
    if(self.precision == 0):
      cb.ax.set_xticklabels(['{:.0f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 1):
      cb.ax.set_xticklabels(['{:.1f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 2):
      cb.ax.set_xticklabels(['{:.2f}'.format(x) for x in self.cblevs], minor=False)
    else:
      cb.ax.set_xticklabels(['{:.3f}'.format(x) for x in self.cblevs], minor=False)

    self.ax.set_title(self.title)

    self.plot_coast_lat_lon_line()

  def obsonly(self, obslat, obslon, obsvar):
    self.basemap = self.build_basemap()

    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    self.fig = self.plt.figure()
    self.ax = self.plt.subplot()

    msg = ('plot variable min: %s, max: %s' % (np.min(obsvar), np.max(obsvar)))
    print(msg)

   #print('len(obslon) = ', len(obslon))
   #print('len(obslat) = ', len(obslat))
   #print('len(obsvar) = ', len(obsvar))

    x, y = self.basemap(obslon, obslat)
   #norm = self.plt.Normalize(np.min(obsvar), np.max(obsvar))
   #obsplot = self.basemap.scatter(x, y, c=obsvar, cmap='viridis', alpha=self.alpha)

    vm = abs(np.min(obsvar))
    bm = abs(np.max(obsvar))
    if(bm > vm):
      vm = bm
  
    if(vm < 1.0e-6):
      vm = 1.0
    size = np.zeros((len(obsvar)), dtype=float)
    for n in range(len(size)):
      size[n] = 1.0 + abs(obsvar[n])/vm
     #size[n] = 1.0 + 500.0*abs(obsvar[n])/vm
   #obsplot = self.basemap.scatter(x, y, s=size, c=size, cmap=self.cmapname, 
    obsplot = self.basemap.scatter(x, y, s=size, c=obsvar, cmap=self.cmapname, 
                                   alpha=self.alpha)

    cb = self.plt.colorbar(orientation=self.orientation,
                           pad=self.pad, ticks=self.cblevs)

    cb.set_label(label=self.label, size=self.size, weight=self.weight)

    cb.ax.tick_params(labelsize=self.labelsize)
    if(self.precision == 0):
      cb.ax.set_xticklabels(['{:.0f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 1):
      cb.ax.set_xticklabels(['{:.1f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 2):
      cb.ax.set_xticklabels(['{:.2f}'.format(x) for x in self.cblevs], minor=False)
    else:
      cb.ax.set_xticklabels(['{:.3f}'.format(x) for x in self.cblevs], minor=False)

    self.ax.set_title(self.title)

    self.plot_coast_lat_lon_line()

    self.display(output=self.output, image_name=self.image_name)

  def add_obs_marker(self, marker='x', size=3, color='green'):
    if(len(self.obslon) > 0):
      x, y = self.basemap(self.obslon, self.obslat)
     #adding dotes:
     #dotes = self.basemap.plot(x, y, 'bo', markersize=12)
     #dotes = self.basemap.plot(x, y, 'bo', markersize=6)
      dotes = self.basemap.scatter(x, y, marker=marker, s=size, color=color)

  def plot_meridional_section(self, pvar):
    nlev, nlat = pvar.shape

    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    lev = np.arange(0.0, float(nlev), 1.0)
    dlat = 180.0/(nlat-1)
    lat = np.arange(-90.0, 90.0+dlat, dlat)

    self.fig = self.plt.figure()
    self.ax = self.plt.subplot()

   #contfill = self.ax.contourf(lat, lev, pvar, tri=True,
    contfill = self.ax.contourf(lat, -lev[::-1], pvar[::-1,:], tri=True,
                                levels=self.clevs, extend=self.extend,
                                alpha=self.alpha, cmap=self.cmapname)

    cb = self.fig.colorbar(contfill, orientation=self.orientation,
                           pad=self.pad, ticks=self.cblevs)

    cb.set_label(label=self.label, size=self.size, weight=self.weight)

    cb.ax.tick_params(labelsize=self.labelsize)
    if(self.precision == 0):
      cb.ax.set_xticklabels(['{:.0f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 1):
      cb.ax.set_xticklabels(['{:.1f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 2):
      cb.ax.set_xticklabels(['{:.2f}'.format(x) for x in self.cblevs], minor=False)
    else:
      cb.ax.set_xticklabels(['{:.3f}'.format(x) for x in self.cblevs], minor=False)

    self.ax.set_title(self.title)

    major_ticks_top=np.linspace(-90,90,7)
    self.ax.set_xticks(major_ticks_top)

    intv = int(1+nlev/10)
   #major_ticks_top=np.linspace(0,nlev,intv)
   #major_ticks_top=np.linspace(0,60,7)
    major_ticks_top=np.linspace(-60,0,7)
    self.ax.set_yticks(major_ticks_top)

    minor_ticks_top=np.linspace(-90,90,19)
    self.ax.set_xticks(minor_ticks_top,minor=True)

   #minor_ticks_top=np.linspace(0,60,13)
    minor_ticks_top=np.linspace(-60,0,13)
    self.ax.set_yticks(minor_ticks_top,minor=True)

    self.ax.grid(b=True, which='major', color='green', linestyle='-', alpha=0.5)
    self.ax.grid(b=True, which='minor', color='green', linestyle='dotted', alpha=0.2)

    self.display(output=self.output, image_name=self.image_name)

  def plot_meridional_section_logp(self, pvar):
    nlev, nlat = pvar.shape

    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    lev = np.arange(0.0, float(nlev), 1.0)
    dlat = 180.0/(nlat-1)
    lat = np.arange(-90.0, 90.0+dlat, dlat)

    self.fig = self.plt.figure()
    self.ax = self.plt.subplot()

    contfill = self.ax.contourf(lat, self.logp[::-1], pvar[::-1,:], tri=True,
                                levels=self.clevs, extend=self.extend,
                                alpha=self.alpha, cmap=self.cmapname)

    cb = self.fig.colorbar(contfill, orientation=self.orientation,
                           pad=self.pad, ticks=self.cblevs)

    cb.set_label(label=self.label, size=self.size, weight=self.weight)

    cb.ax.tick_params(labelsize=self.labelsize)
    if(self.precision == 0):
      cb.ax.set_xticklabels(['{:.0f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 1):
      cb.ax.set_xticklabels(['{:.1f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 2):
      cb.ax.set_xticklabels(['{:.2f}'.format(x) for x in self.cblevs], minor=False)
    else:
      cb.ax.set_xticklabels(['{:.3f}'.format(x) for x in self.cblevs], minor=False)

    self.ax.set_title(self.title)

    major_ticks_top=np.linspace(-90,90,7)
    self.ax.set_xticks(major_ticks_top)

    minor_ticks_top=np.linspace(-90,90,19)
    self.ax.set_xticks(minor_ticks_top,minor=True)
    self.ax.set_xlabel('Latitude')

    self.ax.set_yticks(self.marklogp)
    self.ax.set_ylabel('Unit: hPa')

    yticklabels = []
    for p in self.markpres:
      lbl = '%d' %(int(p+0.1))
      yticklabels.append(lbl)
    self.ax.set_yticklabels(yticklabels)

    self.ax.grid(b=True, which='major', color='green', linestyle='-', alpha=0.5)
    self.ax.grid(b=True, axis='x', which='minor', color='green', linestyle='dotted', alpha=0.2)

    self.display(output=self.output, image_name=self.image_name)

  def plot_zonal_section(self, pvar):
    nlev, nlon = pvar.shape

    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    lev = np.arange(0.0, float(nlev), 1.0)
   #lev = -lev[::-1]
    dlon = 360.0/nlon
    lon = np.arange(0.0, 360, dlon)

    self.fig = self.plt.figure()
    self.ax = self.plt.subplot()

   #contfill = self.ax.contourf(lon, lev, pvar, tri=True,
    contfill = self.ax.contourf(lon, -lev[::-1], pvar[::-1,:], tri=True,
                                levels=self.clevs, extend=self.extend,
                                alpha=self.alpha, cmap=self.cmapname)

    cb = self.fig.colorbar(contfill, orientation=self.orientation,
                           pad=self.pad, ticks=self.cblevs)

    cb.set_label(label=self.label, size=self.size, weight=self.weight)

    cb.ax.tick_params(labelsize=self.labelsize)
    if(self.precision == 0):
      cb.ax.set_xticklabels(['{:.0f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 1):
      cb.ax.set_xticklabels(['{:.1f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 2):
      cb.ax.set_xticklabels(['{:.2f}'.format(x) for x in self.cblevs], minor=False)
    else:
      cb.ax.set_xticklabels(['{:.3f}'.format(x) for x in self.cblevs], minor=False)

    self.ax.set_title(self.title)

    major_ticks_top=np.linspace(0,360,13)
    self.ax.set_xticks(major_ticks_top)

    intv = int(1+nlev/10)
   #major_ticks_top=np.linspace(0,nlev,intv)
   #major_ticks_top=np.linspace(0,60,7)
    major_ticks_top=np.linspace(-60,0,7)
    self.ax.set_yticks(major_ticks_top)

    self.ax.grid(b=True, which='major', color='green', linestyle='-', alpha=0.5)

    minor_ticks_top=np.linspace(0,360,37)
    self.ax.set_xticks(minor_ticks_top,minor=True)

    intv = int(1+nlev/5)
   #minor_ticks_top=np.linspace(0,nlev,intv)
   #minor_ticks_top=np.linspace(0,60,13)
    minor_ticks_top=np.linspace(-60,0,13)
    self.ax.set_yticks(minor_ticks_top,minor=True)

    self.ax.grid(b=True, which='minor', color='green', linestyle='dotted', alpha=0.2)

    self.display(output=self.output, image_name=self.image_name)

  def plot_zonal_section_logp(self, pvar):
    nlev, nlon = pvar.shape

    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    lev = np.arange(0.0, float(nlev), 1.0)
    dlon = 360.0/nlon
    lon = np.linspace(0.5*dlon, 360.0-0.5*dlon, nlon, endpoint=True)

    self.fig = self.plt.figure()
    self.ax = self.plt.subplot()

    contfill = self.ax.contourf(lon, self.logp[::-1], pvar[::-1,:], tri=True,
                                levels=self.clevs, extend=self.extend,
                                alpha=self.alpha, cmap=self.cmapname)

    cb = self.fig.colorbar(contfill, orientation=self.orientation,
                           pad=self.pad, ticks=self.cblevs)

    cb.set_label(label=self.label, size=self.size, weight=self.weight)

    cb.ax.tick_params(labelsize=self.labelsize)
    if(self.precision == 0):
      cb.ax.set_xticklabels(['{:.0f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 1):
      cb.ax.set_xticklabels(['{:.1f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 2):
      cb.ax.set_xticklabels(['{:.2f}'.format(x) for x in self.cblevs], minor=False)
    else:
      cb.ax.set_xticklabels(['{:.3f}'.format(x) for x in self.cblevs], minor=False)

    self.ax.set_title(self.title)

    major_ticks_top=np.linspace(0,360,13,endpoint=True)
    self.ax.set_xticks(major_ticks_top)

    minor_ticks_top=np.linspace(0,360,37,endpoint=True)
    self.ax.set_xticks(minor_ticks_top,minor=True)
    self.ax.set_xlabel('Longitude')

    self.ax.set_yticks(self.marklogp)
    self.ax.set_ylabel('Unit: hPa')

    yticklabels = []
    for p in self.markpres:
      lbl = '%d' %(int(p+0.1))
      yticklabels.append(lbl)
    self.ax.set_yticklabels(yticklabels)

    self.ax.grid(b=True, which='major', color='green', linestyle='-', alpha=0.5)
    self.ax.grid(b=True, axis='x', which='minor', color='green', linestyle='dotted', alpha=0.2)

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

  def plot_with_obs(self, pvar, obslist):
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
    print('pvar.shape = ', pvar.shape)
    print('pvar.size = ', pvar.size)

    (self.x, self.y) = self.basemap(self.lon1d, self.lat1d)
    v1d = np.reshape(pvar, (pvar.size, ))

    contfill = self.basemap.contourf(self.x, self.y, v1d, tri=True,
                                     levels=self.clevs, extend=self.extend,
                                     alpha=self.alpha, cmap=self.cmapname)

    cb = self.fig.colorbar(contfill, orientation=self.orientation,
                           pad=self.pad, ticks=self.cblevs)

    cb.set_label(label=self.label, size=self.size, weight=self.weight)

    cb.ax.tick_params(labelsize=self.labelsize)
    if(self.precision == 0):
      cb.ax.set_xticklabels(['{:.0f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 1):
      cb.ax.set_xticklabels(['{:.1f}'.format(x) for x in self.cblevs], minor=False)
    elif(self.precision == 2):
      cb.ax.set_xticklabels(['{:.2f}'.format(x) for x in self.cblevs], minor=False)
    else:
      cb.ax.set_xticklabels(['{:.3f}'.format(x) for x in self.cblevs], minor=False)

    self.ax.set_title(self.title)

    self.plot_coast_lat_lon_line()

    self.obscolorlist = ['greenyellow', 'lawngreen', 'darkseagreen', 'palegreen',
                         'forestgreen', 'limegreen', 'darkgreen', 'green',
                         'lime', 'seagreen', 'springgreen', 'mediumseagreen',
                         'lightgreen', 'turquoise', 'darkcyan', 'yellowgreen',
                         'aquamarine', 'teal', 'cyan', 'aqua', 'deepskyblue']
   #https://matplotlib.org/stable/api/markers_api.html
    self.obsmarklist = ['o', 'v', '^', '<', '>', '1', '2', '3', '4',
                        '8', 's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X',
                        'D', 'd', '|', '-']

    nm = 0
    markersize=1
    for obs in obslist:
      obslon = obs[0]
      obslat = obs[1]
      self.add_obs_marker_at_latlon(obs[0], obs[1], marker=self.obsmarklist[nm],
                                    size=markersize, color=self.obscolorlist[nm])
      nm += 1

    self.display(output=self.output, image_name=self.image_name)

  def add_obs_marker_at_latlon(self, obslon, obslat, marker='x', size=3, color='green'):
    if(len(obslon) > 0):
      x, y = self.basemap(obslon, obslat)
     #adding dotes:
     #dotes = self.basemap.plot(x, y, 'bo', markersize=12)
     #dotes = self.basemap.plot(x, y, 'bo', markersize=6)
      dotes = self.basemap.scatter(x, y, marker=marker, s=size, color=color)
# ----
if __name__ == '__main__':
  debug = 1
  output = 0

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
   #else:
   #  assert False, 'unhandled option'

  print('debug = ', debug)
  print('output = ', output)

 #gp = GeneratePlot(debug=debug, output=output, lat=lat, lon=lon)
 #gp.plot(pvar)

