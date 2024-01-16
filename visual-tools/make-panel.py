import os, sys
import matplotlib.pyplot as plt
from matplotlib import image
import numpy as np
import getopt

import matplotlib as mpl
mpl.rcParams['figure.dpi']= 500

#=========================================================================
class MakePanelPlot():
  def __init__(self, debug=0, output=0, imglist=[]):
    self.debug = debug
    self.output = output
    self.imglist = imglist

    if(self.debug):
      print('debug = ', debug)

    if(self.debug > 10):
      print('self.imglist = ', self.imglist)

    self.genit()

  def genit(self):
   #initialise grid of axes
   #fig, axes = plt.subplots(2, 2, constrained_layout=True)
    fig, axes = plt.subplots(2, 2)
    axes = axes.ravel()

   #iterate over axes
    for i, ax in enumerate(axes):
      im = image.imread(self.imglist[i])
      ax.axis('off')
      ax.imshow(im)

   #plt.subplots_adjust(left=0.05, bottom=0.05,
   #                    right=0.95, top=0.95,
   #                    wspace=0.05, hspace=0.05)
   #The parameter meanings (and suggested defaults) are:
   #left  = 0.125  # the left side of the subplots of the figure
   #right = 0.9    # the right side of the subplots of the figure
   #bottom = 0.1   # the bottom of the subplots of the figure
   #top = 0.9      # the top of the subplots of the figure
   #wspace = 0.2   # the amount of width reserved for blank space between subplots
   #hspace = 0.2   # the amount of height reserved for white space between subplots

    plt.tight_layout()

    imgname = 'panel-plot'
   #fig.savefig(imgname, dpi=300, bbox_inches="tight")
    fig.savefig(imgname, bbox_inches="tight", quality=100)
    plt.show()

#------------------------------------------------------------------------------
if __name__ == '__main__':
  debug = 1
  output = 0
  imglist = ['trim_MTS-GSI-omb_MTS-JEDI-omb_airTemperature.png',
             'trim_STS-JEDI-omb_MTS-JEDI-omb_airTemperature.png',
             'trim_STS-GSI-omb_MTS-GSI-omb_airTemperature.png',
             'trim_STS-GSI-omb_STS-JEDI-omb_airTemperature.png']

  opts, args = getopt.getopt(sys.argv[1:], '',
               ['debug=', 'output=', 'imglist='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--output'):
      output = int(a)
    elif o in ('--imglist'):
      imglist = a
   #else:
   #  assert False, 'unhandled option'

  print('debug = ', debug)
  print('output = ', output)

  mpp = MakePanelPlot(debug=debug, output=output,
                      imglist=imglist)

