import numpy as np
import os, sys
import getopt

from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
from datetime import timedelta

from pygw.template import Template
from pygw.yaml_file import YAMLFile

#=========================================================================
class GenerateConfig():
  def __init__(self, debug=0, template='config.template',
               nmem_enkf=80, fcstfreq=6,
               year=2020, month=1, day=1, hour=0, interval=3):
    self.debug = debug
    self.yaml_in = template
    self.yaml_out = 'config.yaml'
    self.nmem_enkf = nmem_enkf
    self.fcstfreq = fcstfreq
    self.year = year
    self.month = month
    self.day = day
    self.hour = hour
    self.interval = interval
    self.st = datetime(self.year, self.month, self.day, self.hour, 0, 0)
    self.ymdh = '%4.4d%2.2d%2.2d%2.2d' %(self.year, self.month, self.day, self.hour)
 
  def get_ymdh(self, ct):
    year = ct.year
    month = ct.month
    day = ct.day
    hour = ct.hour

    return year, month, day, hour

  def get_advancedate(self, cur_datetime, intval):
    dt = timedelta(hours=intval)
    ct = cur_datetime + dt
    return ct

  def get_timestring(self, ct):
    ts = ct.strftime("%Y-%m-%dT%H:00:00Z")
    return ts

  def genYAML(self, intval=3):
    yaml_file = YAMLFile(path=self.yaml_in)
   #print('yaml_file = ', yaml_file)
    bgn_intv = self.interval + 1
    win_bgn_datetime = self.get_advancedate(self.st, -bgn_intv)
    yaml_file['executable options']['ATM_WINDOW_BEGIN'] = self.get_timestring(win_bgn_datetime)
    win_end_datetime = self.get_advancedate(self.st, self.interval)
    yaml_file['executable options']['ATM_WINDOW_END'] = self.get_timestring(win_end_datetime)
    yaml_file['executable options']['ATM_WINDOW_CENTER'] = self.get_timestring(self.st)
    yaml_file['executable options']['NMEM_ENKF'] = self.nmem_enkf
    yaml_file['executable options']['YYYYMMDDHH'] = self.ymdh

    bkg_datetime = self.get_advancedate(self.st, -self.fcstfreq)
    year, month, day, hour = self.get_ymdh(bkg_datetime)
    ymd = '%4.4d%2.2d%2.2d' %(year, month, day)
    ymdh = '%s%2.2d' %(ymd, hour)
    yaml_file['executable options']['BKGDIR'] = '../%s' %(ymdh)

    bgn_datetime = self.get_advancedate(self.st, -self.interval)
    year, month, day, hour = self.get_ymdh(bgn_datetime)
    ymd = '%4.4d%2.2d%2.2d' %(year, month, day)
    ymdh = '%s%2.2d' %(ymd, hour)
    yaml_file['executable options']['ATM_BGN_TIME'] = self.get_timestring(bgn_datetime)
    yaml_file['executable options']['ATM_BGN_YYYYMMDDHH'] = ymdh
    yaml_file['executable options']['ATM_BGN_YYYYMMDD'] = ymd
    yaml_file['executable options']['ATM_BGN_HH'] = '%2.2d' %(hour)

    end_datetime = self.get_advancedate(self.st, self.interval)
    year, month, day, hour = self.get_ymdh(end_datetime)
    ymd = '%4.4d%2.2d%2.2d' %(year, month, day)
    ymdh = '%s%2.2d' %(ymd, hour)
    yaml_file['executable options']['ATM_END_TIME'] = self.get_timestring(end_datetime)
    yaml_file['executable options']['ATM_END_YYYYMMDDHH'] = ymdh
    yaml_file['executable options']['ATM_END_YYYYMMDD'] = ymd
    yaml_file['executable options']['ATM_END_HH'] = '%2.2d' %(hour)

    yaml_file.save(self.yaml_out)

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  template = 'config.template'
  nmem_enkf = 80
  fcstfreq = 6
  year = 2020
  month = 1
  day = 2
  hour = 0
  intv = 3

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'template=',
                                                'nmem_enkf=', 'fcstfreq=',
                                                'year=', 'month=',
                                                'day=', 'hour=', 'intv='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--template'):
      template = a
    elif o in ('--year'):
      year = int(a)
    elif o in ('--nmem_enkf'):
      nmem_enkf = int(a)
    elif o in ('--fcstfreq'):
      fcstfreq = int(a)
    elif o in ('--month'):
      month = int(a)
    elif o in ('--day'):
      day = int(a)
    elif o in ('--hour'):
      hour = int(a)
    elif o in ('--intv'):
      intv = int(a)
    else:
      assert False, 'unhandled option'

 #-------------------------------------------------------------------------------
  gc = GenerateConfig(debug=debug, template=template,
                      nmem_enkf=nmem_enkf, fcstfreq=fcstfreq,
                      year=year, month=month, day=day, hour=hour,
                      interval=intv)
  gc.genYAML()
