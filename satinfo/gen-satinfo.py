#########################################################################

import getopt
import os, sys
import types
import time
import datetime

import numpy as np

from ruamel.yaml import YAML

class INC:
  yaml_tag = u'!INC'
  def __init__(self, value, style=None):
    self.value = value
    self.style = style

  @classmethod
  def to_yaml(cls, representer, node):
    return representer.represent_scalar(cls.yaml_tag,
                                        u'{.value}'.format(node), node.style)

  @classmethod
  def from_yaml(cls, constructor, node):
    return cls(node.value, node.style)

#------------------------------------------------------------------
""" Build Satellite Information File """
class BuildSatelliteInfoFile:
  """ Constructor """
  def __init__(self, debug=0, satdir=None, datestr='1800010100'):
    """ Initialize class attributes """
    self.debug = debug
    self.satdir = satdir

    if(satdir is None):
      print('satdir not defined. Exit.')
      sys.exit(-1)

    if(os.path.exists(satdir)):
      print('satdir is %s.' %(satdir))
    else:
      print('satdir %s does not exist. Exit.' %(satdir))
      sys.exit(-1)

    self.yaml = YAML(typ='rt')
    self.yaml.register_class(INC)
    self.yaml.preserve_quotes = True

    self.header = []
    self.satinfo = []

    self.dt = self.get_time(datestr)

    self.select_satfile(self.satdir)

  def get_time(self, datestr):
    year = int(datestr[0:4])
    month = int(datestr[4:6])
    day = int(datestr[6:8])
    hour = int(datestr[8:10])

   #print('year: %d, month: %d, day: %d, hour: %d' %(year, month, day, hour))

    ct = datetime.datetime(year, month, day, hour, 0)

    print('ct = ', ct)

    return ct

  def select_satfile(self, workdir):
    self.filelist = []
    nc = 0
    for filename in os.listdir(workdir):
      f = os.path.join(workdir, filename)
     #checking if it is a file
      if os.path.isfile(f):
       #print(f)
        item = filename.split('.')
        if((3 == len(item)) and (item[0] == 'global_satinfo')):
          self.filelist.append(f)

    self.filelist.sort()

    for filename in self.filelist:
      item = filename.split('.')
      dt = self.get_time(item[-1])
      if(self.dt >= dt):
        self.satfile = filename

    print('Selected satfile: ', self.satfile)

    self.process()

  def process(self):
    self.headlines = []
    with open(self.satfile) as fh:
      lines = fh.readlines()
      num_lines = len(lines)
      if(self.debug):
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

          self.satinfo.append(item)
              
        nl += 1

  def get_channels(self, type):
    yamlfile = '%s.yaml' %(type)

    if(os.path.exists(yamlfile)):
      f = open(yamlfile, 'r')
      docs = self.yaml.load(f)
     #print(docs)

      obsspace = docs['obs space']
     #print('obsspace:', obsspace)

      channels = obsspace['channels']
    else:
      channels = []

   #print('channels:', channels)

    return channels

  def write(self, newsatfile, typelist=['']):
    self.OUTFILE = open(newsatfile, 'w')
    for line in self.headlines:
      self.OUTFILE.write(line)

    pretype = 'unknown'
    channels = []

    for n in range(len(self.satinfo)):
      li = self.satinfo[n]
      if(self.debug):
        print(li)

      type = li[0]
     #if(type != pretype):
     #  pretype = type
     #  channels = self.get_channels(type)

     #if(type in typelist):
     #  channel = li[1]
     #  if(channel in channels):
     #    li[2] = '  1'
     #  else:
     #    li[2] = ' -1'
     #else:
     #  li[2] = ' -1'
      if(type not in typelist):
        li[2] = ' -1'
      linfo = self.get_line(li)
      self.OUTFILE.write(linfo)

    self.OUTFILE.close()
    
  def get_line(self, li):
    linfo = ' %-16s %8s %3s %8s %8s' %(li[0], li[1], li[2], li[3], li[4])
    linfo = '%s %8s %8s %8s %6s' %(linfo, li[5], li[6], li[7], li[8])
    linfo = '%s %6s %6s\n' %(linfo, li[9], li[10])

    return linfo

#--------------------------------------------------------------------------------
class INC:
  yaml_tag = u'!INC'
  def __init__(self, value, style=None):
    self.value = value
    self.style = style

  @classmethod
  def to_yaml(cls, representer, node):
    return representer.represent_scalar(cls.yaml_tag,
                                        u'{.value}'.format(node), node.style)

  @classmethod
  def from_yaml(cls, constructor, node):
    return cls(node.value, node.style)

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 0
  outputfile = 'global_satinfo.txt'
  satdir = '/work2/noaa/da/weihuang/cycling/scripts/gdas-cycling/satinfo'
  datestr = '2020010106'
  type = 'amsua_n19'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'outputfile=', 'satdir=',
                                                'datestr=', 'type='])
  tl = []
  for opt, arg in opts:
    if opt in ('--debug'):
      debug = int(arg)
    elif opt in ('--outputfile'):
      outputfile = arg
    elif opt in ('--satdir'):
      satdir = arg
    elif opt in ('--datestr'):
      datestr = arg
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

  bsif = BuildSatelliteInfoFile(debug=debug, satdir=satdir, datestr=datestr)
  bsif.write(outputfile, typelist=typelist)

