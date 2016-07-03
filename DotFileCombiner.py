from ParsedDotFile import ParsedDotFile

class DotFileCombiner:
  def __init__(self, output_filename):
    self.dot = ParsedDotFile(output_filename)
  
  def get_combined_dot(self, dot1, dot2):
    self.combine_filenames(dot1, dot2)
    self.combine_digraph(dot1, dot2)
    self.combine_node_header(dot1, dot2)
    self.combine_legend(dot1, dot2)
    self.combine_nodes(dot1, dot2)
    self.combine_edges(dot1, dot2)
    return self.dot

  def combine_filenames(self, dot1, dot2):
    self.dot.filenames = (dot1.filename, dot2.filename)

  def combine_digraph(self, dot1, dot2):
    self.dot.digraph = dot1.digraph
  
  def combine_node_header(self, dot1, dot2):
    self.dot.node_header = dot1.node_header

  def combine_legend(self, dot1, dot2):
    self.copy_vals_for_keys(
        dot1.legend, self.dot.legend, 
        ('stuff_before', 'stuff_after', 'line'))
    self.zip_vals_for_keys(
        dot1.legend, dot2.legend, self.dot.legend, 
        ('executable', 'total_samples'))
 
  def combine_nodes(self, dot1, dot2):
    fns = set(dot1.nodes.keys()) | set(dot2.nodes.keys())
    fn_num = 0
    for fn in fns:
      fn_num += 1
      node_id = 'M' + str(fn_num)
      self.dot.nodes[fn] = {
        'fn_name' : fn,
        'node_id' : node_id,   
      }
      self.zip_vals_for_keys(
        dot1.get_node(fn), dot2.get_node(fn), self.dot.nodes[fn],
        ('local_samples', 'local_percentage', 
         'cumulative_samples','cumulative_percentage'))
      which_dot = dot1 if fn in dot1.nodes else dot2
      self.copy_vals_for_keys(
        which_dot.get_node(fn), self.dot.nodes[fn], ('stuff_after',))
      self.dot.fn_names[node_id] = fn

  def combine_edges(self, dot1, dot2):
    edge_keys = set(dot1.edges.keys()) | set(dot2.edges.keys())
    for edge_key in edge_keys:
      self.dot.edges[edge_key] = {}
      from_fn, to_fn = ParsedDotFile.split_edge_key(edge_key)
      edge1 = dot1.get_edge(from_fn, to_fn)
      edge2 = dot2.get_edge(from_fn, to_fn)
      self.dot.edges[edge_key] = {
        'from_fn' : from_fn,
        'to_fn' : to_fn,
        'num_samples' : (edge1['num_samples'], edge2['num_samples'])
      }
      which_edge = edge1 if edge_key in dot1.edges else edge2
      self.copy_vals_for_keys(
        which_edge, self.dot.edges[edge_key], ('stuff_after',))

  def copy_vals_for_keys(self, map1, map_out, keys):
    for key in keys:
      map_out[key] = map1[key]
  
  def zip_vals_for_keys(self, map1, map2, map_out, keys):
    for key in keys: 
      map_out[key] = (map1[key], map2[key])


