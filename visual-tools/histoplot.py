import os, sys
import getopt

# importing the required module
import datetime
import calendar

import numpy as np
import matplotlib
import matplotlib.pyplot

import matplotlib.cm as cm

#from matplotlib.colors import Normalize
#from matplotlib.ticker import MultipleLocator

from matplotlib import colors
from matplotlib.ticker import PercentFormatter

from readIODA2Obs import ReadIODA2Obs

#=========================================================================
class PlotTimeHistogram():
  def __init__(self, debug=0, output=0, cntdatetime=None, obsfile=None):
    self.debug = debug
    self.output = output

    self.set_default()

    if(cntdatetime is None):
      print('Need to input cntdatetime')
      raise SystemExit

    self.cntdatetime = cntdatetime

    if(obsfile is None):
      print('Need to input obsfile')
      raise SystemExit
    else:
      if(os.path.exists(obsfile)):
        print('obsfile: %s' %(obsfile))
      else:
        print('obsfile: %s does not exist. Exit.' %(obsfile))

    self.obsfile = obsfile

    self.nbins = 8

    tcnt = self.datetime2seconds(self.cntdatetime)

    print('tcnt = ', tcnt)

    self.pbins = np.zeros(self.nbins, float)
    for n in range(self.nbins):
      self.pbins[n] = float(n - int(self.nbins/2) + 0.5)

    ncf = ReadIODA2Obs(debug=debug, filename=self.obsfile)
    isnd = ncf.get_var('/MetaData/dateTime')

    isnd -= tcnt

    fsnd = isnd/3600.0

    print('fsnd = ', fsnd)

    self.plot_histo(fsnd)

#group: MetaData {
#  variables:
#        int64 dateTime(Location) ;
#                dateTime:_FillValue = -9223372036854775806LL ;
#                string dateTime:units = "seconds since 1970-01-01T00:00:00Z" ;

  def datetime2seconds(self, datestr):
    year = int(datestr[0:4])
    month = int(datestr[4:6])
    day = int(datestr[6:8])
    hour = int(datestr[8:10])
    t = datetime.datetime(year, month, day, hour, 0, 0)
    ts = calendar.timegm(t.timetuple())

    print('t = ', t)
    print('ts = ', ts)

   #datetime.datetime.utcfromtimestamp(1347517370).strftime('%Y-%m-%d %H:%M:%S')
   #'2012-09-13 06:22:50'

    return ts

  def set_default(self):
    self.image_name = 'histo.png'

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

    self.xlabel = 'Hours'
    self.ylabel = 'Count'

    self.title = 'Obs Time Histo'

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

  def plot_histo(self, var):
    self.plt = matplotlib.pyplot
    try:
      self.plt.close('all')
      self.plt.clf()
    except Exception:
      pass

    hist, bins = np.histogram(var, self.pbins)
    print('hist: ', hist)
    print('bins: ', bins)

    self.fig, self.axs = self.plt.subplots(1, 1, tight_layout=True)

   #Set the number of bins with the *bins* keyword argument.
    self.axs.hist(var)

   #self.plt.title(self.title)

   #self.plt.xlabel(self.xlabel, fontsize=14)
   #self.plt.ylabel(self.ylabel, fontsize=14)

    self.display(image_name=self.image_name)

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 0

  cntdatetime = '2022010512'

  varname = 'amsua_n19'
  datadir = '/work2/noaa/da/weihuang/EMC_cycling/sts.gsi-cycling/%s' %(cntdatetime)
  obsfile = '%s/ioda_v2_data/%s_obs_%s.nc4' %(datadir, varname, cntdatetime)

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=', 'cntdatetime=',
                                                'obsfile='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--cntdatetime'):
      cntdatetime = a
    elif o in ('--obsfile'):
      obsfile = a
    else:
      assert False, 'unhandled option'

#-----------------------------------------------------------------------------------------

  print('cntdatetime = ', cntdatetime)
  print('obsfile = ', obsfile)

  pth = PlotTimeHistogram(debug=debug, output=output,
                          cntdatetime=cntdatetime,
                          obsfile=obsfile)

