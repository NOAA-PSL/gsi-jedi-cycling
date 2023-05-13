#########################################################################
import getopt
import os, sys
import types
import time
import datetime

import numpy as np

from ruamel.yaml import YAML

#------------------------------------------------------------------
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
    self.channels = []

    self.selected_use_flag = None
    self.selected_obserr_bound_max = None
    self.selected_error_parameter_vector = None

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

      obs_space = docs['obs space']
     #print('obs_space:', obss_pace)

      channels = obs_space['channels']
    else:
      channels = []

   #print('channels:', channels)

    newyamlfile = 'new_%s' %(yamlfile)
    yaml.dump(docs, newyamlfile)
   #yaml.dump(docs, sys.stdout, transform=tr)

    return channels

  def write(self, newsatfile, typelist=['']):
    self.OUTFILE = open(newsatfile, 'w')
    for line in self.headlines:
      self.OUTFILE.write(line)

    pretype = 'unknown'

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
      if(type in typelist):
        channel = int(li[1])
        flag = int(li[2])
        if(flag > 0):
          self.channels.append(channel)
      else:
        li[2] = ' -1'
      linfo = self.get_line(li)
      self.OUTFILE.write(linfo)

    self.OUTFILE.close()
    
  def get_line(self, li):
    linfo = ' %-16s %8s %3s %8s %8s' %(li[0], li[1], li[2], li[3], li[4])
    linfo = '%s %8s %8s %8s %6s' %(linfo, li[5], li[6], li[7], li[8])
    linfo = '%s %6s %6s\n' %(linfo, li[9], li[10])

    return linfo

  def get_strlist(self, in_channels):
   #print('in_channels:', in_channels)
    tmpstr = in_channels.replace(' ', '')
    tmpstr = tmpstr.replace('\n', '')
    str_channels = tmpstr.split(',')
   #print('str_channels:', str_channels)
   #print('str_channels length:', len(str_channels))

    return str_channels

  def get_string(self, inlist):
    separator = ', '
    astr = separator.join(inlist)
    return astr

  def get_selected_string(self, inlist):
    slist = inlist[self.index]
    separator = ', '
    astr = separator.join(slist)
    return astr

  def update_obs_space(self, docs):
    obs_space = docs['obs space']
   #print('obs_space:', obs_space)

    channels = obs_space['channels']
   #print('obs channels length:', len(channels))

    str_channels = self.get_strlist(channels)

    self.new_channels = []
    self.index = []
    n = 0
    for chnl in str_channels:
     #print('Channel %d: <%s>' %(n, chnl))
      idx = int(chnl)
     #print('Channel %d: <%s> as %d' %(n, chnl, idx))
      if(idx in self.channels):
        self.new_channels.append(chnl)
        self.index.append(n)
      n += 1

    print('new obs channels length:', len(self.new_channels))

    self.new_channelstring = self.get_string(self.new_channels)
    obs_space['channels'] = self.new_channelstring

   #obs_space = docs['obs space']
   #print('obs_space:', obs_space)

   #channels = obs_space['channels']
   #print('obs channels length:', len(channels))

  def update_obs_prior_filters(self, docs):
    obs_prior_filters = docs['obs prior filters']
   #print('obs_prior_filters:', obs_prior_filters)
    print('len(obs_prior_filters):', len(obs_prior_filters))
   #print('obs_prior_filters.items():', list(obs_prior_filters.items()))

    n = 0
    for n in range(len(obs_prior_filters)):
      opf = obs_prior_filters[n]
     #print('opf no %d:' %(n))
     #print('opf:', opf)
      print('opf.keys():', list(opf.keys()))

      filter_variables = opf['filter variables']
     #filter_variables['channels'] = self.new_channelstring
     #docs['obs prior filters'][n]['filter variables']['channels'] = self.new_channelstring
     #print("filter_variables['channels']:", filter_variables['channels'])
     #docs['obs prior filters'][n]['filter variables']['channels'] = self.new_channels
    
      action = opf['action']
      print('action.keys():', list(action.keys()))
      error_parameter_vector = action['error parameter vector']
     #i = 0
     #for epv in error_parameter_vector:
     #  print('Epv %d: %s' %(i, epv))
     #  i += 1
     #print('error_parameter_vector:', error_parameter_vector)
      
     #str_epv = self.get_strlist(error_parameter_vector)
     #sel_epv = self.get_selected_string(str_epv)
     #sel_epv = self.get_selected_string(error_parameter_vector)

      sel_epv = []
      for i in self.index:
       #print('error_parameter_vector[%d] = %s' %(i, error_parameter_vector[i]))
        sel_epv.append(error_parameter_vector[i])
     #action['error parameter vector'] = sel_epv
      docs['obs prior filters'][n]['action']['error parameter vector'] = sel_epv
      print('len(self.index) = ', len(self.index))
      print('len(sel_epv) = ', len(sel_epv))
      self.selected_error_parameter_vector = sel_epv

  def update_obs_post_filters(self, docs):
    obs_post_filters = docs['obs post filters']
   #print('obs_post_filters:', obs_post_filters)
    print('len(obs_post_filters):', len(obs_post_filters))

    n = 0
    for n in range(len(obs_post_filters)):
      opf = obs_post_filters[n]
      print('opf no %d:' %(n))
      print('opf.keys():', list(opf.keys()))
      if(opf['filter'] in ['BlackList']):
        continue

     #print('opf:', opf)

      if('test variables' in opf.keys()):
        test_variables = opf['test variables']
       #print('test_variables:', test_variables)
        print('len(test_variables):', len(test_variables))
        for itv in range(len(test_variables)):
          tv = test_variables[itv]
          print('tv.keys():', list(tv.keys()))
          options = tv['options']
          print('options.keys():', list(options.keys()))

          if('use_flag' in list(options.keys())):
            sel_use_flag = []
            use_flag = options['use_flag']
            for i in self.index:
             #print('use_flag[%d] = %s' %(i, use_flag[i]))
              sel_use_flag.append(use_flag[i])
            options['use_flag'] = sel_use_flag
            docs['obs post filters'][n]['test variables'][itv]['options']['use_flag'] = sel_use_flag
            print('len(self.index) = ', len(self.index))
            print('len(sel_use_flag) = ', len(sel_use_flag))
            self.selected_use_flag = sel_use_flag

          if('use_flag_clddet' in list(options.keys())):
            sel_use_flag_clddet = []
            use_flag_clddet = options['use_flag_clddet']
            for i in self.index:
             #print('use_flag_clddet[%d] = %s' %(i, use_flag_clddet[i]))
              sel_use_flag_clddet.append(use_flag_clddet[i])
            options['use_flag_clddet'] = sel_use_flag_clddet
            docs['obs post filters'][n]['test variables'][itv]['options']['use_flag_clddet'] = sel_use_flag_clddet
            print('len(self.index) = ', len(self.index))
            print('len(sel_use_flag_clddet) = ', len(sel_use_flag_clddet))
            self.selected_use_flag_clddet = sel_use_flag_clddet

          if('obserr_bound_max' in list(options.keys())):
            sel_obserr_bound_max = []
            obserr_bound_max = options['obserr_bound_max']
            for i in self.index:
             #print('obserr_bound_max[%d] = %s' %(i, obserr_bound_max[i]))
              sel_obserr_bound_max.append(obserr_bound_max[i])
            options['obserr_bound_max'] = sel_obserr_bound_max
            docs['obs post filters'][n]['test variables'][itv]['options']['obserr_bound_max'] = sel_obserr_bound_max
            print('len(self.index) = ', len(self.index))
            print('len(sel_obserr_bound_max) = ', len(sel_obserr_bound_max))
            self.selected_obserr_bound_max = sel_obserr_bound_max

          if('error parameter vector' in list(options.keys())):
            sel_epv = []
            epv = options['error parameter vector']
            for i in self.index:
             #print('error parameter vector[%d] = %s' %(i, epv[i]))
              sel_epv.append(epv[i])
            options['error parameter vector'] = sel_epv
            docs['obs post filters'][n]['test variables'][itv]['options']['error parameter vector'] = sel_epv
            print('len(self.index) = ', len(self.index))
            print('len(sel_epv) = ', len(sel_epv))
            self.selected_epv = sel_epv

      if('function absolute threshold' in opf.keys()):
        fat = opf['function absolute threshold']
        print('len(fat):', len(fat))
        for itv in range(len(fat)):
          tv = fat[itv]
          print('tv.keys():', list(tv.keys()))
          options = tv['options']
          print('options.keys():', list(options.keys()))

          if('obserr_bound_max' in list(options.keys())):
            sel_obserr_bound_max = []
            obserr_bound_max = options['obserr_bound_max']
            for i in self.index:
             #print('obserr_bound_max[%d] = %s' %(i, obserr_bound_max[i]))
              sel_obserr_bound_max.append(obserr_bound_max[i])
            options['obserr_bound_max'] = sel_obserr_bound_max
            docs['obs post filters'][n]['function absolute threshold'][itv]['options']['obserr_bound_max'] = sel_obserr_bound_max
            print('len(self.index) = ', len(self.index))
            print('len(sel_obserr_bound_max) = ', len(sel_obserr_bound_max))
            self.selected_obserr_bound_max = sel_obserr_bound_max

          if('error parameter vector' in list(options.keys())):
            sel_epv = []
            epv = options['error parameter vector']
            for i in self.index:
             #print('error parameter vector[%d] = %s' %(i, epv[i]))
              sel_epv.append(epv[i])
            options['error parameter vector'] = sel_epv
            docs['obs post filters'][n]['function absolute threshold'][itv]['options']['error parameter vector'] = sel_epv
            print('len(self.index) = ', len(self.index))
            print('len(sel_epv) = ', len(sel_epv))
            self.selected_epv = sel_epv

  def gen_new_yaml(self, yamlfile):
    INFILE = open(yamlfile)
    docs = self.yaml.load(INFILE)
   #print(docs)

    self.update_obs_space(docs)
    self.update_obs_prior_filters(docs)
    self.update_obs_post_filters(docs)

    OUTFILE = open('new_iasi_metop-b.yaml', 'wb')
    self.yaml.dump(docs, OUTFILE)

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 0
  outputfile = 'global_satinfo.txt'
  satdir = '/work2/noaa/da/weihuang/cycling/scripts/gdas-cycling/satinfo'
  datestr = '2020010106'
 #type = 'amsua_n19'
  type = 'iasi_metop-b'
 #yamlfile = None
  yamlfile = 'iasi_metop-b.yaml'

  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'outputfile=', 'satdir=',
                                                'datestr=', 'type=', 'yamlfile='])
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
    elif opt in ('--yamlfile'):
      yamlfile = arg
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

  if(yamlfile is not None):
    bsif.gen_new_yaml(yamlfile)

