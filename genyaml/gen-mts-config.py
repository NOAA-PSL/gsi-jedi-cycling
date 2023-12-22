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
  def __init__(self, debug=0, topdir='./', template='config.template',
               nmem_enkf=80, year=2020, month=1, day=1, hour=0, interval=3):
    self.debug = debug
    self.topdir = topdir
    self.yaml_in = template
    self.yaml_out = 'config.yaml'
    self.nmem_enkf = nmem_enkf
    self.year = year
    self.month = month
    self.day = day
    self.hour = hour
    self.interval = interval
    self.st = datetime(self.year, self.month, self.day, self.hour, 0, 0)
    self.ymdh = '%d%2.2d%2.2d%2.2d' %(self.year, self.month, self.day, self.hour)

    self.bgn_datetime = self.get_advancedate(-self.interval)
    self.bgn_year, self.bgn_month, self.bgn_day, self.bgn_hour = self.get_ymdh(self.bgn_datetime)
    self.bgn_ymdh = '%d%2.2d%2.2d%2.2d' %(self.bgn_year, self.bgn_month, self.bgn_day, self.bgn_hour)

    self.end_datetime = self.get_advancedate(self.interval)
    self.end_year, self.end_month, self.end_day, self.end_hour = self.get_ymdh(self.end_datetime)
    self.end_ymdh = '%d%2.2d%2.2d%2.2d' %(self.end_year, self.end_month, self.end_day, self.end_hour)
 
  def get_ymdh(self, ct):
    year = ct.year
    month = ct.month
    day = ct.day
    hour = ct.hour

    return year, month, day, hour

  def get_advancedate(self, intval):
    dt = timedelta(hours=intval)
    ct = self.st + dt
    return ct

  def advancedate(self, intval):
    dt = timedelta(hours=intval)
    ct = self.st + dt

    ts = ct.strftime("%Y-%m-%dT%H:00:00Z")

   #print('st = ', st)
   #print('dt = ', dt)
   #print('ct = ', ct)
   #print('ts = ', ts)

    return ts

  def genYAML(self, intval=3):
    yaml_file = YAMLFile(path=self.yaml_in)
    print('yaml_file = ', yaml_file)
    bgn_intv = self.interval + 1
    yaml_file['executable options']['ATM_WINDOW_BEGIN'] = self.advancedate(-bgn_intv)
    yaml_file['executable options']['ATM_WINDOW_END'] = self.advancedate(self.interval)
    yaml_file['executable options']['ATM_WINDOW_CENTER'] = self.advancedate(0)
    yaml_file['executable options']['NMEM_ENKF'] = self.nmem_enkf
    yaml_file['executable options']['YYYYMMDDHH'] = self.ymdh

    yaml_file['executable options']['TOPDIR'] = self.topdir
    yaml_file['executable options']['ATM_BGN_TIME'] = self.advancedate(-self.interval)
    yaml_file['executable options']['ATM_BGN_YYYYMMDDHH'] = self.bgn_ymdh
    yaml_file['executable options']['ATM_BGN_YYYYMMDD'] = '%d%2.2d%2.2d' %(self.bgn_year, self.bgn_month, self.bgn_day)
    yaml_file['executable options']['ATM_BGN_HH'] = '%2.2d' %(self.bgn_hour)

   #yaml_file['executable options']['ATM_CNT_TIME'] = self.advancedate(0)

    yaml_file['executable options']['ATM_END_TIME'] = self.advancedate(self.interval)
    yaml_file['executable options']['ATM_END_YYYYMMDDHH'] = self.end_ymdh
    yaml_file['executable options']['ATM_END_YYYYMMDD'] = '%d%2.2d%2.2d' %(self.end_year, self.end_month, self.end_day)
    yaml_file['executable options']['ATM_END_HH'] = '%2.2d' %(self.end_hour)

   #yaml_file['executable options']['CTR_CNT_TIME'] = self.advancedate(0)

    yaml_file.save(self.yaml_out)

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  topdir = '/work2/noaa/da/weihuang/EMC_cycling/jedi-cycling'
  template = 'config.template'
  nmem_enkf = 80
  year = 2020
  month = 1
  day = 2
  hour = 0
  intv = 3

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'topdir', 'template=',
                                                'nmem_enkf=', 'year=', 'month=',
                                                'day=', 'hour=', 'intv='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--topdir'):
      topdir = a
    elif o in ('--template'):
      template = a
    elif o in ('--year'):
      year = int(a)
    elif o in ('--nmem_enkf'):
      nmem_enkf = int(a)
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
  gc = GenerateConfig(debug=debug, topdir=topdir, template=template, nmem_enkf=nmem_enkf,
                      year=year, month=month, day=day, hour=hour,
                      interval=intv)
  gc.genYAML()
  tstr = gc.advancedate(-intv)
  print(tstr)

