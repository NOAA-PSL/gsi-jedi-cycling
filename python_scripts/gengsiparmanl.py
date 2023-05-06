#########################################################################

import getopt
import os, sys
import types
import time
import datetime

import numpy as np

#------------------------------------------------------------------
""" Build obs input file """
class BuildObsInpuFile:
  """ Constructor """
  def __init__(self, debug=0, textdir=None):
    """ Initialize class attributes """
    self.debug = debug
    self.textdir = textdir

    if(textdir is None):
      print('textdir not defined. Exit.')
      sys.exit(-1)

    if(os.path.exists(textdir)):
      print('textdir is %s.' %(textdir))
    else:
      print('textdir %s does not exist. Exit.' %(textdir))
      sys.exit(-1)

    self.head = self.get_lines('gsiparm.anl.head')
    self.body = self.get_lines('gsiparm.anl.template')
    self.tail = self.get_lines('gsiparm.anl.tail')

  def get_lines(self, filename):
    fn = '%s/%s' %(self.textdir, filename)
    hf = open(fn, 'r')
    lines = hf.readlines()
    return lines

  def write(self, newfile, typelist=['']):
    if(os.path.exists(newfile)):
      os.remove(newfile)

    dflist = []
    dplist = []
    dtlist = []
    dslist = []

    for type in typelist:
      item = type.split(',')
      dflist.append(item[0])
      dtlist.append(item[1])
      dplist.append(item[2])
      dslist.append(item[3])
     #print('item: ', item)

    print('typelist: ', typelist)
    print('dflist: ', dflist)
    print('dplist: ', dplist)
    print('dtlist: ', dtlist)
    print('dslist: ', dslist)

    self.OUTFILE = open(newfile, 'w')
    for line in self.head:
      self.OUTFILE.write(line)

    for line in self.body:
      textline = ' '.join(line.split())
      item = textline.split()
     #print('textline: ', textline)
     #print('item: ', item)
      dfile = item[0]
      dtype = item[1]
      dplat = item[2]
      dsis = item[3]
      for n in range(len(dflist)):
       #print('dfile: %s, dflist[%d]: %s' %(dfile, n, dflist[n]))
       #print('dtype: %s, dtlist[%d]: %s' %(dtype, n, dtlist[n]))
       #print('dplat: %s, dplist[%d]: %s' %(dplat, n, dplist[n]))
       #print('dsis : %s, dslist[%d]: %s' %(dsis , n, dslist[n]))
        if((dfile == dflist[n]) and (dtype == dtlist[n]) and
          (dplat == dplist[n]) and (dsis == dslist[n])):
          print('line: ', line)
          self.OUTFILE.write(line)
          break

    for line in self.tail:
      self.OUTFILE.write(line)

    self.OUTFILE.close()
    
#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 0
  outputfile = 'gsiparm.anl'
  textdir = '/work2/noaa/da/weihuang/cycling/scripts/gdas-cycling/textinfo'
  type = 'prepbufr,t,null,t'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'outputfile=', 'textdir=',
                                                'type='])
  tl = []
  for opt, arg in opts:
    if opt in ('--debug'):
      debug = int(arg)
    elif opt in ('--outputfile'):
      outputfile = arg
    elif opt in ('--textdir'):
      textdir = arg
    elif opt in ('--type'):
      tl.append(arg)
     #print(opt + ': ' + arg)
     #print('tl: ', tl)
    else:
      assert False, 'unhandled option'

  if(len(tl) > 0):
    typelist = tl
  else:
    typelist = [type]
  print('typelist:', typelist)

  boif = BuildObsInpuFile(debug=debug, textdir=textdir)
  boif.write(outputfile, typelist=typelist)

