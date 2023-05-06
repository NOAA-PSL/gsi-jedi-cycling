#import yaml
import sys
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

yaml = YAML(typ='rt')

yaml.register_class(INC)

yamlfile = 'iasi_metop-b.yaml'

yaml.preserve_quotes = True

with open(yamlfile) as f:
  docs = yaml.load(f)
 #print(docs)

  obsspace = docs['obs space']
 #print('obsspace:', obsspace)

  channels = obsspace['channels']
  print('channels:', channels)

