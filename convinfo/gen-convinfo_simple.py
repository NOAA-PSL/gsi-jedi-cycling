#########################################################################

import getopt
import os, sys
import types
import time
import datetime

import numpy as np

#------------------------------------------------------------------
""" Build Conventional Information File """
class BuildConventionalInfoFile:
  """ Constructor """
  def __init__(self, debug=0, convfile=None):
    """ Initialize class attributes """
    self.debug = debug
    self.convfile = convfile

    if(convfile is None):
      print('convfile not defined. Exit.')
      sys.exit(-1)

    if(os.path.exists(convfile)):
      print('convfile is %s.' %(convfile))
    else:
      print('convfile %s does not exist. Exit.' %(convfile))
      sys.exit(-1)

    self.header = []
    self.convinfo = []

  def write(self, newconvfile, typelist=[120], exceptotypelist=[]):
    self.OUTFILE = open(newconvfile, 'w')
    with open(self.convfile) as fh:
      lines = fh.readlines()
      num_lines = len(lines)
      print('Total number of lines: ', num_lines)

      nl = 0
      for line in lines:
        if(self.debug):
          print('Line %d: %s' %(nl, line))

        if(line.find('!') >= 0):
          self.OUTFILE.write(line)
          if(line.find('!otype ') >= 0):
            if(self.debug):
              print('Line %d: %s' %(nl, line))
            while(line.find('  ') >= 0):
              line = line.replace('  ', ' ')
            item = line[1:].split(' ')
            for name in item:
              self.header.append(name)
            if(self.debug):
              print('header: ', self.header)
        else:
          line = line.strip()
          while(line.find('  ') >= 0):
            line = line.replace('  ', ' ')
          item = line.split(' ')

          self.convinfo.append(item)
              
        nl += 1
    for n in range(len(self.convinfo)):
      li = self.convinfo[n]
      if(self.debug):
        print(li)
      litype = int(li[1])
      for type in typelist:
        if(type == litype):
          need_write = 1
          for otype in exceptotypelist:
            if(otype == li[0]):
              need_write = 0
              break

          if(need_write):
            linfo = self.get_line(li)
            self.OUTFILE.write(linfo)
    
  def get_line(self, li):
    linfo = ' %-5s %6s %4s %4s %7s' %(li[0], li[1], li[2], li[3], li[4])
    linfo = '%s %6s %6s %6s %5s' %(linfo, li[5], li[6], li[7], li[8])
    linfo = '%s %5s %5s %5s %9s' %(linfo, li[9], li[10], li[11], li[12])
    linfo = '%s %5s %5s %6s %6s' %(linfo, li[13], li[14], li[15], li[16])
    linfo = '%s %5s %6s %4s %4s\n' %(linfo, li[17], li[18], li[19], li[20])

    return linfo

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  outputfile = 'global_convinfo.txt'
  convfile = 'global_convinfo.txt.2019021900'
  typelist = [120, 220]
  exceptotypelist = ['ps']

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'outputfile=', 'convfile='])

  for o, a in opts:
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--outputfile'):
      outputfile = a
    elif o in ('--convfile'):
      convfile = a
    else:
      assert False, 'unhandled option'

  bcif = BuildConventionalInfoFile(debug=debug, convfile=convfile)
  bcif.write(outputfile, typelist=typelist, exceptotypelist=exceptotypelist)

