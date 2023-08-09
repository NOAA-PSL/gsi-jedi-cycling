#=========================================================================
import os
import sys
import types
import getopt

import numpy as np
import matplotlib.pyplot as plt

import netCDF4 as nc4

#=========================================================================
def plotit(lev, imgname, label, title, data):
 #print('lev = ', lev)

  z = []
  ftop = np.log2(10.0)
  for n in range(len(lev)):
    fact = 20.0*(np.log2(1000.0/lev[n])/ftop)
   #print('Level %d prs = %f, z = %f' %(n, lev[n], fact))
    z.append(fact)

 #print('z = ', z)
  ns = 43

  linestyles = ['--', 'dotted', 'solid']
  legends = ['2D Iterator', '3D Iterator']

  nrows = 1
  ncols = len(data)

  fig, axs = plt.subplots(nrows=nrows,ncols=ncols, figsize=(11,8.5))

 #axs is a 2 dimensional array of `GeoAxes`. Flatten it into a 1-D array
  axs=axs.flatten()

  for i in range(len(axs)):
    pv = data[i]

    v0 = pv[0]
    v1 = pv[1]

    if(2 > i):
      p0 = axs[i].plot(v0[ns:], z[ns:], color='blue',
           linewidth=1.5, linestyle=linestyles[i])
      p1 = axs[i].plot(v1[ns:], z[ns:], color='red',
           linewidth=1.5, linestyle=linestyles[i])
    else:
      p0 = axs[i].plot(v0[ns:], z[ns:], color='blue',
           linewidth=2.0)
      p1 = axs[i].plot(v1[ns:], z[ns:], color='red',
           linewidth=2.0)

    axs[i].set_title(label[i])

   #axs[i].set_xlim((0, 0.50))  
    axs[i].set_ylim((0, 20.0))

   #axs[i]. = plt.gca()
   #axs[i].xaxis.set_ticks_position('bottom')
   #axs[i].yaxis.set_ticks_position('left')

    axs[i].set_title(label[i], fontsize=20)
    axs[i].set_ylabel('Height (Km)', fontsize=15)
    axs[i].grid(True)

    axs[i].legend(legends)

 #Add a big title at the top
  fig.suptitle(title)

  fig.canvas.draw()
  plt.tight_layout()

  pngname = '%s.png' %(imgname)
  plt.savefig(pngname)

  plt.show()

  plt.close()
 #plt.clf()

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 0
  firstfile = 'letkf2d/xainc.20201215_000000z.nc4'
  secondfile = 'letkf3d/xainc.20201215_000000z.nc4'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=',
                                                'secondfile=', 'firstfile='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--secondfile'):
      secondfile = a
    elif o in ('--firstfile'):
      firstfile = a
    else:
      assert False, 'unhandled option'

 #--------------------------------------------------------------------------------
  ncsecond = nc4.Dataset(secondfile, 'r')
  ncfirst = nc4.Dataset(firstfile, 'r')
  lats = ncsecond.variables['lat'][:]
  lons = ncsecond.variables['lon'][:]
  levs = [0.0128, 0.0203, 0.0318, 
    0.0488, 0.0736, 0.1093, 
    0.1595, 0.2293, 0.3245, 
    0.4523, 0.6214, 0.8416, 
    1.1244, 1.4822, 1.9289, 2.4790, 
    3.1478, 3.9507, 4.9032, 6.0200, 
    7.3150, 8.8007, 10.488, 12.385, 
    14.500, 16.836, 19.397, 22.187, 
    25.191, 28.422, 31.871, 35.537, 
    39.415, 43.506, 47.810, 52.331, 
    57.075, 62.054, 67.284, 72.786, 
    78.579, 84.676, 91.087, 97.823, 
    104.90, 112.32, 120.10, 128.24, 
    136.76, 145.66, 154.96, 164.66, 
    174.75, 185.26, 196.18, 207.51, 
    219.25, 231.39, 243.95, 256.90, 
    270.25, 283.98, 298.08, 312.53, 
    327.32, 342.43, 357.84, 373.53, 
    389.47, 405.63, 421.99, 438.52, 
    455.18, 471.95, 488.78, 505.65, 
    522.53, 539.37, 556.15, 572.83, 
    589.38, 605.77, 621.97, 637.94, 
    653.67, 669.13, 684.29, 699.14, 
    713.65, 727.80, 741.59, 755.00, 
    768.02, 780.64, 792.86, 804.66, 
    816.06, 827.04, 837.61, 847.79, 
    857.54, 866.90, 875.87, 884.45, 
    892.66, 900.50, 907.97, 915.10, 
    921.89, 928.35, 934.50, 940.34, 
    945.89, 951.15, 956.15, 960.88, 
    965.37, 969.61, 973.63, 977.43, 
    981.02, 984.42, 987.63, 990.66, 
    993.52, 996.22, 998.76]

 #print('lats: ', lats)
 #print('lons: ', lons)
 #print('levs: ', levs)

  nlon = len(lons)
  nlat = len(lats)

  print('nlat = ', nlat)
  print('nlon = ', nlon)

  nlons = 0
  nlats = 0

  nlone = nlon - 40
  nlate = 2

 #t = ncfirst.variables['T'][0,101,nlats:nlate,nlons:nlone]

 #print('t = ', t)

 #nlon = int((nlons + nlone)/2)
 #nlat = int((nlats + nlate)/2)

  labels = ['U-Component', 'V-component', 'Temperature']

 #for nlon in [0, 1, nlon - 2, nlon - 1]:
  for nlon in [0, nlon - 1]:
    lon = lons[nlon]
    for nlat in range(8):
      lat = lats[nlat]

      u1 = ncfirst.variables['ua'][0,:,nlat,nlon]
      v1 = ncfirst.variables['va'][0,:,nlat,nlon]
      t1 = ncfirst.variables['T'][0,:,nlat,nlon]

      u2 = ncsecond.variables['ua'][0,:,nlat,nlon]
      v2 = ncsecond.variables['va'][0,:,nlat,nlon]
      t2 = ncsecond.variables['T'][0,:,nlat,nlon]

      ud = [u1, u2]
      vd = [v1, v2]
      td = [t1, t2]

      data = [ud, vd, td]

      title = 'Increments at (lat, lon): (%f, %f)' %(lat, lon)
      name = 'profile_at_lat%f_lon%f' %(lat, lon)
      plotit(levs, name, labels, title, data)

