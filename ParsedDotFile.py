class ParsedDotFile:
  def __init__(self, filename):
    self.filename = filename
    self.digraph = {}
    self.node_header = {}
    self.legend = {}
    self.nodes = {}
    self.fn_names = {}
    self.edges = {}
  
  def get_node(self, fn):
    if fn in self.nodes:
      return self.nodes[fn]
    return {
      'node_id' : None,
      'local_samples' : 0,
      'local_percentage' : 0,
      'cumulative_samples' : 0,
      'cumulative_percentage' : 0,
      'stuff_after' : '',
      'line' : None,
    }

  def get_edge(self, from_fn, to_fn):
    edge_key = ParsedDotFile.make_edge_key(from_fn, to_fn)
    if edge_key in self.edges:
      return self.edges[edge_key]
    return {
      'from_fn' : from_fn,
      'to_fn' : to_fn,
      'num_samples' : 0,
      'stuff_after' : '',
    }
  
  @staticmethod
  def make_edge_key(from_fn, to_fn):
    return from_fn + ' ' + to_fn
  
  @staticmethod
  def split_edge_key(edge_key):
    return edge_key.split(' ')


