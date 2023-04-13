import getopt
import os, sys
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable

from matplotlib import rcParams
from scipy import stats

import netCDF4 as nc4

#=========================================================================
def plot_lines(frtrms, sndrms, output=0, lbl1='UNKOWN1', lbl2='UNKOWN2'):
  try:
    plt.close('all')
    plt.clf()
    plt.cla()
  except Exception:
    pass

  title = 'PS RMS'

 #print('frtrms = ', frtrms)
 #print('sndrms = ', sndrms)

  frtrms = 0.01*frtrms
  sndrms = 0.01*sndrms

  pmin = np.min(sndrms)
  gmin = np.min(frtrms)
  if(pmin > gmin):
    pmin = gmin

  pmax = np.max(sndrms)
  gmax = np.max(frtrms)
  if(pmax < gmax):
    pmax = gmax
 
  x = []
  xlabels = []
  for k in range(len(frtrms)):
    lbl = '%d' %(k)
    xlabels.append(lbl)
    x.append(k)

  yl = np.linspace(0,0.5,11)
  y = []
  ylabels = []
  for v in yl:
    if(v >= pmin and v <= pmax):
      lbl = '%5.3f' %(v)
      ylabels.append(lbl)
      y.append(v)

  fig = plt.figure()
  ax = plt.subplot()

  ax.plot(x, frtrms, color='blue', linewidth=2, alpha=0.9)
  ax.plot(x, sndrms, color='red', linewidth=2, alpha=0.9)

  plt.xscale('linear')
 #plt.xscale('log', base=2)
 #plt.yscale('log', base=2)
 #plt.yscale('log', base=10)
  plt.xticks(x, xlabels)
  plt.yticks(y, ylabels)

 #ax.plot(xd, yp, color='cyan', linewidth=2, alpha=0.9)

  plt.grid()

 #Same limits for everybody!
  plt.xlim(0, len(frtrms))
  plt.ylim(pmin, pmax)
 
 #general title
  title = '%s and %s PS rms' %(lbl1, lbl2)
  plt.suptitle(title, fontsize=16, fontweight=1, color='black')

 #Create a big subplot
  bs = fig.add_subplot(111, frameon=False)
  plt.subplots_adjust(bottom=0.2, right=0.70, top=0.8)

 #hide tick and tick label of the big axes
  plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')

 #bs.set_xlabel('(m/s)', labelpad=10)
  bs.set_ylabel('PS RMS (hPa)', labelpad=20)

  labels = [lbl1, lbl2]

 #Create the legend
  fig.legend(ax, labels=labels,
         loc="center right",   # Position of legend
         fontsize=8,
         borderpad=1.2,
         labelspacing=1.2,
         handlelength=1.5
         )

 #Adjust the scaling factor to fit your legend text completely outside the plot
 #(smaller value results in more space being made for the legend)

  imgname = 'ps_rms.png'

  if(output):
    plt.savefig(imgname)
  else:
    plt.show()

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  output = 0
  title = 'UNKNOW2 and UNKNOW1'
  region = 'Hem'
  lbl1 = 'GSI_PS'
  lbl2 = 'GDAS_PS'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'output=', 'title=',
                                                'region=', 'lbl1=', 'lbl2='])
  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--lbl1'):
      lbl1 = a
    elif o in ('--lbl2'):
      lbl2 = a
    elif o in ('--title'):
      title = a
    elif o in ('--region'):
      region = a
    else:
      assert False, 'unhandled option'

  frtrms = np.linspace(0.0,1.0,128)
  sndrms = 0.5125 + 0.5*(1.0-(frtrms-0.35)*(frtrms-0.35))
 #print('len(frtrms) = ', len(frtrms))
 #print('frtrms = ', frtrms)
  print('min(sndrms) = ', np.min(sndrms))
  print('max(sndrms) = ', np.max(sndrms))

  plot_lines(frtrms, sndrms, output=output, lbl1=lbl1, lbl2=lbl2)

