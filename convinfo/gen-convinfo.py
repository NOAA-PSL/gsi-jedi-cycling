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
  def __init__(self, debug=0, convdir=None, datestr='1800010100'):
    """ Initialize class attributes """
    self.debug = debug
    self.convdir = convdir

    if(convdir is None):
      print('convdir not defined. Exit.')
      sys.exit(-1)

    if(os.path.exists(convdir)):
      print('convdir is %s.' %(convdir))
    else:
      print('convdir %s does not exist. Exit.' %(convdir))
      sys.exit(-1)

    self.header = []
    self.convinfo = []

    self.dt = self.get_time(datestr)

    self.select_convfile(self.convdir)

    self.process()

  def get_time(self, datestr):
    year = int(datestr[0:4])
    month = int(datestr[4:6])
    day = int(datestr[6:8])
    hour = int(datestr[8:10])

   #print('year: %d, month: %d, day: %d, hour: %d' %(year, month, day, hour))

    ct = datetime.datetime(year, month, day, hour, 0)

    if(self.debug):
      print('ct = ', ct)

    return ct

  def select_convfile(self, workdir):
    self.filelist = []
    nc = 0
    for filename in os.listdir(workdir):
      f = os.path.join(workdir, filename)
     #checking if it is a file
      if os.path.isfile(f):
       #print(f)
        item = filename.split('.')
        if((3 == len(item)) and (item[0] == 'global_convinfo')):
          self.filelist.append(f)

    self.filelist.sort()

    for filename in self.filelist:
      item = filename.split('.')
      dt = self.get_time(item[-1])
      if(self.dt >= dt):
        self.convfile = filename

    print('Selected convfile: ', self.convfile)

  def process(self):
    self.headlines = []
    with open(self.convfile) as fh:
      lines = fh.readlines()
      num_lines = len(lines)
      print('Total number of lines: ', num_lines)

      nl = 0
      for line in lines:
        if(self.debug):
          print('Line %d: %s' %(nl, line))

        if(line.find('!') >= 0):
          self.headlines.append(line)
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

  def write(self, newconvfile, typelist=['120'], otypelist=['ps']):
    self.OUTFILE = open(newconvfile, 'w')
    for line in self.headlines:
      self.OUTFILE.write(line)

    for n in range(len(self.convinfo)):
      li = self.convinfo[n]
      if(self.debug):
        print(li)
      otype = li[0]
      type = li[1]
      if((otype not in otypelist) or (type not in typelist)):
        li[3] = '  -1'
      linfo = self.get_line(li)
      self.OUTFILE.write(linfo)
    self.OUTFILE.close()
    
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
  convdir = '/work2/noaa/da/weihuang/cycling/scripts/gdas-cycling/convinfo'
  datestr = '2020010106'
  otype = 'ps'
  type = '120'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'outputfile=', 'convdir=',
                                                'datestr=', 'otype=', 'type='])

  tl = []
  otl = []
  for opt, arg in opts:
    if opt in ('--debug'):
      debug = int(arg)
    elif opt in ('--outputfile'):
      outputfile = arg
    elif opt in ('--convdir'):
      convdir = arg
    elif opt in ('--datestr'):
      datestr = arg
    elif opt in ('--type'):
      tl.append(arg)
    elif opt in ('--otype'):
      otl.append(arg)
    else:
      assert False, 'unhandled option'

  if(len(tl) > 0):
    typelist = tl
  else:
    typelist = [type]

 #if(debug):
  print('typelist:', typelist)

  if(len(otl) > 0):
    otypelist = otl
  else:
    otypelist = [otype]

 #if(debug):
  print('otypelist:', otypelist)

  bcif = BuildConventionalInfoFile(debug=debug, convdir=convdir, datestr=datestr)
  bcif.write(outputfile, typelist=typelist, otypelist=otypelist)

