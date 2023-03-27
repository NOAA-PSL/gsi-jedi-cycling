import numpy as np
import os, sys
import getopt

from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
from datetime import timedelta
from netCDF4 import Dataset

#=========================================================================
def get_dates(sdate, edate, intv):
  sdatestr = '%sT%s0000' %(sdate[0:8], sdate[8:10])
  edatestr = '%sT%s0000' %(edate[0:8], edate[8:10])

  hourly = list(rrule(HOURLY, interval=intv,
                dtstart=parse(sdatestr),
                until=parse(edatestr)))

 #print('hourly = ', hourly)

  dtlist = []
  for hd in hourly:
    ds = hd.strftime("%Y%m%d%H")
    dtlist.append(ds)

 #print('dtlist = ', dtlist)

  return dtlist

#=========================================================================
def cal_datetohrs(date):
  year = int(date[0:4])
  month = int(date[4:6])
  day = int(date[6:8])
  hour = int(date[8:10])
  ct = datetime(year, month, day, hour, 0, 0)
  st = datetime(1970, 1, 1, 0, 0, 0)
  dt = ct - st
  hour = dt / timedelta(hours=1)

 #print('st = ', st)
 #print('ct = ', ct)
 #print('dt = ', dt)
 #print('hour = ', hour)

  return float(hour)

#=========================================================================
class DiagObFit():
  def __init__(self, debug=0, output=0, sdate=None, edate=None,
               runid=None, hem='HS', psonly=True, interval=6,
               noair=False, aironly=False, latbound=30):
    msg = 'sdate edate runid hem'
    if(sdate is None or edate is None):
      print(msg)
      raise SystemExit

    self.sdate = sdate
    self.edate = edate
    self.runid = runid
    self.hem = hem

   #if psonly False, aircraft, pibals and surface data included also
   #self.psonly = False # use only 120,132,220,221,232 (sondes,pibals,drops)
    self.psonly = psonly
    self.noair = noair
    self.aironly = aironly
    self.latbound = latbound

    self.dates = get_dates(sdate, edate, interval)

    self.set_default()

 #def __del__(self):
 #  self.ncout.close()

  def set_default(self):
    self.deltap = 50.

  def process(self, datapath, outfile):
    ncout = Dataset(outfile, 'w')

    times = ncout.createDimension('time',len(self.dates))
    times = ncout.createVariable('times',np.float64,'time')
    times.units = 'hours since 1970-01-01'
    ps_rms = ncout.createVariable('omf_rmsps',float, ('time'))
    ps_cnt = ncout.createVariable('ps_obcounts',int, ('time'))

    hours = []
    for date in self.dates:
      h = cal_datetohrs(date)
      hours.append(h)

    print(hours)

    ndate = 0
    for date in self.dates:
      times[ndate] = cal_datetohrs(date)
      if self.runid != '': 
        obsfile_ps = os.path.join(datapath,'%s/diag_conv_ps_ges.%s_%s.nc4' % (date,date,runid))
      else:
        obsfile_ps = os.path.join(datapath,'%s/diag_conv_ps_ges.%s.nc4' % (date,date))

      nc_ps = Dataset(obsfile_ps)

      ps_code = nc_ps['Observation_Type'][:]
      ps_used = nc_ps['Analysis_Use_Flag'][:]
      ps_oberrinv = nc_ps['Errinv_Final'][:]
      ps_press = nc_ps['Pressure'][:]
      ps_lon = nc_ps['Longitude'][:]
      ps_lat = nc_ps['Latitude'][:]
      omf_ps = nc_ps['Obs_Minus_Forecast_unadjusted'][:]

     #print(omf_ps)

      if self.psonly:
        insitu_ps = np.logical_or(ps_code == 180,
                                  ps_code == 181, #sfc
                                  ps_code == 183) #sfc
      else:
        insitu_ps = np.logical_or(ps_code == 120, # sondes
                                  ps_code == 132) # drops

     #print(insitu_ps)

     #consider this of if used flag is 1, inverse oberr is < 1.e-5 and a valid pressure level is included
      ps_used = ps_used == 1
      ps_used = np.logical_and(ps_used, np.isfinite(ps_press))
      insitu_ps = np.logical_and(insitu_ps,ps_used)

      print(insitu_ps)

      if self.hem == 'NH':
        ps_latcond = ps_lat > self.latbound 
      elif self.hem == 'SH':
        ps_latcond = ps_lat < -self.latbound
      elif self.hem == 'TR':
        ps_latcond = np.logical_and(ps_lat <= self.latbound,ps_lat >= -self.latbound)

      if self.hem in ['NH','TR','SH']:
        indxps = np.logical_and(insitu_ps,ps_latcond)
      else:
        indxps = insitu_ps

      omf_ps = omf_ps[indxps]
      ps_rms[ndate] = np.sqrt((omf_ps**2).mean())
      ps_cnt[ndate] = len(omf_ps)
      ndate += 1
  
    ncout.close()

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 0

  interval = 12
  sdate = '2020010112'
  edate = '2020011218'
  dir1 = 'gsi_C96_lgetkf_psonly'
  dir2 = 'gdas-cycling'
  datadir = '/work2/noaa/da/weihuang/cycling'
  runid = 'ensmean'
  hem = 'NH'
  lbl1 = 'GSI_PS'
  lbl2 = 'GDAS_PS'

  psonly=True
  noair=False
  aironly=False
  latbound=30

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=', 'sdate=', 'edate=',
                                                'datadir=', 'runid=', 'hem=',
                                                'dir1=', 'dir2=', 'interval=',
                                                'lbl1=', 'lbl2='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--sdate'):
      sdate = a
    elif o in ('--edate'):
      edate = a
    elif o in ('--datadir'):
      datadir = a
    elif o in ('--runid'):
      runid = a
    elif o in ('--hem'):
      hem = a
    elif o in ('--dir1'):
      dir1 = a
    elif o in ('--dir2'):
      dir2 = a
    elif o in ('--interval'):
      interval = int(a)
    elif o in ('--lbl1'):
      lbl1 = a
    elif o in ('--lbl2'):
      lbl2 = a
    else:
      assert False, 'unhandled option'

#-----------------------------------------------------------------------------------------

  dof = DiagObFit(debug=debug, output=output, sdate=sdate, edate=edate,
                  runid=runid, hem=hem, psonly=psonly, interval=interval,
                  noair=noair, aironly=aironly, latbound=latbound)

  lbllist = [lbl1, lbl2]
  dirlist = [dir1, dir2]
  for n in range(len(dirlist)):
    datapath = '%s/%s' %(datadir, dirlist[n])
    outfile = 'ps_stats_%s.nc' %(lbllist[n])
    dof.process(datapath, outfile)

