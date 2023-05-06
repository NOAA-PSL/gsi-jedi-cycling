import getopt
import logging
import os, sys
import re
import yaml
import datetime as dt

from pygw.template import Template, TemplateConstants
from pygw.yaml_file import YAMLFile

#=========================================================================
class GenerateYAML():
  def __init__(self, debug=0, config_file='config.yaml', solver='getkf.yaml.template.solver',
               observer='getkf.yaml.template.rr.observer', numensmem=80, obsdir='observer'):
    self.debug = debug
    self.solver = solver
    self.observer = observer
    self.numensmem = numensmem
    self.obsdir = obsdir

    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
   #open YAML file to get config
    try:
      with open(config_file, 'r') as yamlconfig_opened:
        all_config = yaml.safe_load(yamlconfig_opened)
      logging.info(f'Loading configuration from {config_file}')
    except Exception as e:
      logging.error(f'Error occurred when attempting to load: {config_file}, error: {e}')
  
   #print('all_config: ', all_config)

    self.config = all_config['executable options']

   #for key in self.config.keys():
   #  print('key: ', key)
   #  print('\tconfig[key]:', self.config[key])

  def genYAML(self, config, yaml_in, yaml_out):
    yaml_file = YAMLFile(path=yaml_in)
    yaml_file = Template.substitute_structure(yaml_file, TemplateConstants.DOUBLE_CURLY_BRACES,
                                              self.config.get)
    yaml_file = Template.substitute_structure(yaml_file, TemplateConstants.DOLLAR_PARENTHESES,
                                              self.config.get)
    yaml_file.save(yaml_out)

  def add_obs2observer(self, n=1, obstype='sondes'):
    ctype = obstype.upper()
    ctype = ctype.replace('-', '_')
    infile = '%s_OBSINFILE' %(ctype)
    outfile = '%s_OBSOUTFILE' %(ctype)
    self.config[infile] = 'ioda_v2_data/%s_obs_%s.nc4' %(obstype, self.config['YYYYMMDDHH'])
    self.config[outfile] = '%s/mem%3.3d/%s_obs_%s.nc4' %(self.obsdir, n, obstype, self.config['YYYYMMDDHH'])

  def genObserverYAML(self, obstypelist):
    os.system('cp rr.distribution distribution.yaml')

    if not os.path.exists(self.obsdir):
      os.makedirs(self.obsdir)

    n = 0
    while (n <= self.numensmem):
      yaml_out = '%s/getkf.yaml.observer.mem%3.3d' %(self.obsdir, n)
      if(self.debug):
        print('YAML %d: %s' %(n, yaml_out))

     #for obstype in obstypelist:
     #  self.add_obs2observer(n=n, obstype=obstype)

     #self.config['PS_OBSINFILE'] = 'ioda_v2_data/ps_obs_%s.nc4' %(self.config['YYYYMMDDHH'])
     #self.config['PS_OBSOUTFILE'] = '%s/mem%3.3d/ps_obs_%s.nc4' %(self.obsdir, n, self.config['YYYYMMDDHH'])
      self.config['SONDES_OBSINFILE'] = 'ioda_v2_data/sondes_obs_%s.nc4' %(self.config['YYYYMMDDHH'])
      self.config['SONDES_OBSOUTFILE'] = '%s/mem%3.3d/sondes_obs_%s.nc4' %(self.obsdir, n, self.config['YYYYMMDDHH'])

     #self.config['AMSUA_N15_OBSINFILE'] = 'ioda_v2_data/amsua_n15_obs_%s.nc4' %(self.config['YYYYMMDDHH'])
     #self.config['AMSUA_N18_OBSINFILE'] = 'ioda_v2_data/amsua_n18_obs_%s.nc4' %(self.config['YYYYMMDDHH'])
      self.config['AMSUA_N19_OBSINFILE'] = 'ioda_v2_data/amsua_n19_obs_%s.nc4' %(self.config['YYYYMMDDHH'])
     #self.config['AMSUA_N15_OBSOUTFILE'] = '%s/mem%3.3d/amsua_n15_obs_%s.nc4' %(self.obsdir, n, self.config['YYYYMMDDHH'])
     #self.config['AMSUA_N18_OBSOUTFILE'] = '%s/mem%3.3d/amsua_n18_obs_%s.nc4' %(self.obsdir, n, self.config['YYYYMMDDHH'])
      self.config['AMSUA_N19_OBSOUTFILE'] = '%s/mem%3.3d/amsua_n19_obs_%s.nc4' %(self.obsdir, n, self.config['YYYYMMDDHH'])

     #self.config['IASI_METOP_B_OBSINFILE'] = 'ioda_v2_data/iasi_metop-b_obs_%s.nc4' %(self.config['YYYYMMDDHH'])
     #self.config['IASI_METOP_B_OBSOUTFILE'] = '%s/mem%3.3d/iasi_metop-b_obs_%s.nc4' %(self.obsdir, n, self.config['YYYYMMDDHH'])

      self.config['MEMBERDATAPATH'] = 'mem%3.3d/INPUT' %(n)
      self.config['MEMSTR'] = 'mem%3.3d' %(n)

      self.genYAML(self.config, self.observer, yaml_out)

      n += 1

  def add_obs2solver(self, obstype='sondes'):
    ctype = obstype.upper()
    ctype = ctype.replace('-', '_')
    infile = '%s_OBSINFILE' %(ctype)
    outfile = '%s_OBSOUTFILE' %(ctype)
    self.config[infile] = '%s/%s_obs_%s.nc4' %(self.obsdir, obstype, self.config['YYYYMMDDHH'])
    self.config[outfile] = 'solver/%s_obs_%s.nc4' %(obstype, self.config['YYYYMMDDHH'])

  def genSolverYAML(self, obstypelist):
    os.system('cp halo.distribution distribution.yaml')
    yaml_out = 'getkf.solver.yaml'
    if(self.debug):
      print('YAML: %s' %(yaml_out))

   #for obstype in obstypelist:
   #  self.add_obs2solver(obstype=obstype)

   #self.config['PS_OBSINFILE'] = '%s/ps_obs_%s.nc4' %(self.obsdir, self.config['YYYYMMDDHH'])
   #self.config['PS_OBSOUTFILE'] = 'solver/ps_obs_%s.nc4' %(self.config['YYYYMMDDHH'])
    self.config['SONDES_OBSINFILE'] = '%s/sondes_obs_%s.nc4' %(self.obsdir, self.config['YYYYMMDDHH'])
    self.config['SONDES_OBSOUTFILE'] = 'solver/sondes_obs_%s.nc4' %(self.config['YYYYMMDDHH'])

   #self.config['AMSUA_N15_OBSINFILE'] = '%s/amsua_n15_obs_%s.nc4' %(self.obsdir, self.config['YYYYMMDDHH'])
   #self.config['AMSUA_N18_OBSINFILE'] = '%s/amsua_n18_obs_%s.nc4' %(self.obsdir, self.config['YYYYMMDDHH'])
    self.config['AMSUA_N19_OBSINFILE'] = '%s/amsua_n19_obs_%s.nc4' %(self.obsdir, self.config['YYYYMMDDHH'])
   #self.config['AMSUA_N15_OBSOUTFILE'] = 'solver/amsua_n15_obs_%s.nc4' %(self.config['YYYYMMDDHH'])
   #self.config['AMSUA_N18_OBSOUTFILE'] = 'solver/amsua_n18_obs_%s.nc4' %(self.config['YYYYMMDDHH'])
    self.config['AMSUA_N19_OBSOUTFILE'] = 'solver/amsua_n19_obs_%s.nc4' %(self.config['YYYYMMDDHH'])

   #self.config['IASI_METOP_B_OBSINFILE'] = '%s/iasi_metop-b_obs_%s.nc4' %(self.obsdir, self.config['YYYYMMDDHH'])
   #self.config['IASI_METOP_B_OBSOUTFILE'] = 'solver/iasi_metop-b_obs_%s.nc4' %(self.config['YYYYMMDDHH'])

    self.genYAML(self.config, self.solver, yaml_out)

#--------------------------------------------------------------------------------
if __name__== '__main__':
  debug = 1
  config_file = 'config.yaml'
  observer = 'getkf.yaml.template.rr.observer'
  solver = 'getkf.yaml.template.solver'
  numensmem = 80
  obsdir = 'observer'
  obstypelist = ['sfc_ps', 'sfcship_ps', 'sondes_ps',
                 'sondes', 'amsua_n15', 'amsua_n18', 'amsua_n19']

 #--------------------------------------------------------------------------------
  opts, args = getopt.getopt(sys.argv[1:], '', ['debug=', 'config=', 'observer=',
                                                'solver=', 'numensmem=', 'obsdir='])
  print('opts = ', opts)
  print('args = ', args)

  for o, a in opts:
    print('o: <%s>' %(o))
    print('a: <%s>' %(a))
    if o in ('--debug'):
      debug = int(a)
    elif o in ('--config'):
      config_file = a
    elif o in ('--observer'):
      observer = a
    elif o in ('--solver'):
      solver = a
    elif o in ('--numensmem'):
      numensmem = int(a)
    elif o in ('--obsdir'):
      obsdir = a
    else:
      print('o: <%s>' %(o))
      print('a: <%s>' %(a))
      assert False, 'unhandled option'

 #--------------------------------------------------------------------------------
  gy = GenerateYAML(debug=debug, config_file=config_file, solver=solver,
                    observer=observer, numensmem=numensmem, obsdir=obsdir)

  gy.genSolverYAML(obstypelist)
  gy.genObserverYAML(obstypelist)

