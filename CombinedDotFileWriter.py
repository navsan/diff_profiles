from ParsedDotFile import ParsedDotFile
import re

def get_RGB_color(threshold, value):
  T = float(threshold)
  if value > T: 
    value = T
  elif value < -T:
    value = -T
  x = value / T  # Normalized value
  # These RGB functions were obtained by fitting a quadratic function like so:
  # At x = 1, (r, g, b) = (1, 0, 0)
  # At x = 0, (r, g, b) = (1, 1, 1)
  # At x = 1, (r, g, b) = (0, 1, 0)
  r = int(255 * min(1, (-x*x/2) + (x/2) + 1))
  g = int(255 * min(1, (-x*x/2) - (x/2) + 1))
  b = int(255 *        ((-x*x)          + 1))
  return '#' + ('%0.2x' % r) + ('%0.2x' % g) + ('%0.2x' % b)

class CombinedDotFileWriter:
  def __init__(self, dot, diff_attr, diff_threshold):
    self.dot = dot
    self.diff_attr = diff_attr
    self.diff_threshold = diff_threshold
    self.outfile = open(dot.filename, 'w')
    assert self.outfile, 'Could not open file ' + dot.filename

  def print_dot_file(self):
    self.print_digraph_line()
    self.print_node_header_line()
    self.print_legend_line()
    self.print_node_lines()
    self.print_edge_lines()
    self.print_end_line()

  def print_digraph_line(self):
    self.write('digraph "Diff between profiles', 
        self.dot.filenames[0], 'and', self.dot.filenames[1], '" {\n')

  def print_node_header_line(self):
    self.write(self.dot.node_header['line'])

  def print_legend_line(self):
    legend = self.dot.legend
    self.merge_each_key(legend,('executable','total_samples'))
    filename1 = self.dot.filenames[0] 
    filename2 = self.dot.filenames[1]
    self.write_dict(legend, 
        r'Legend [{stuff_before},label="'
        'Comparing profiles', filename1, ' / ', filename2,
        r'using heatmap colors',
        r'\nRed   =>', self.diff_attr, 
        r'in ', filename1, ' > ', filename2, 
        r'\nGreen =>', self.diff_attr, 
        r'in ', filename1, ' < ', filename2, 
        r'\n{executable}'
        r'\lTotal samples: {total_samples}'
        r'\l"];', '\n')

  def print_node_lines(self):
    node_ids = sorted(self.dot.fn_names.keys(), key=lambda i: int(i[1:]))
    for node_id in node_ids:
      fn = self.dot.fn_names[node_id]
      node = self.dot.nodes[fn]
      node['color'] = get_RGB_color(self.diff_threshold,
          node[self.diff_attr][0] - node[self.diff_attr][1])
      self.merge_each_key(node, 
          ('local_samples', 'local_percentage', 
           'cumulative_samples', 'cumulative_percentage'))
      self.make_fn_name_readable(node)
      self.write_dict(node,
        r'{node_id} [label="{fn_name}\n'
        r'{local_samples} ({local_percentage}%)\r'
        r'of {cumulative_samples} ({cumulative_percentage}%)\r",'
        r'{stuff_after},style=filled,fillcolor="{color}"];', '\n')

  def print_edge_lines(self):
    for edge_key in self.dot.edges:
      edge = self.dot.edges[edge_key]
      edge['from_node_id'] = self.dot.nodes[edge['from_fn']]['node_id']
      edge['to_node_id'] = self.dot.nodes[edge['to_fn']]['node_id']
      self.merge_each_key(edge, ('num_samples',))
      self.write_dict(edge, 
          r'{from_node_id} -> {to_node_id} [label="{num_samples}", '
          r'{stuff_after}];', '\n')

  def print_end_line(self):
    self.write('}')

  def write_dict(self, d, *args):
    out_args = []
    for arg in args:
      out_args.append(arg.format(**d))
    self.write(*out_args)
  
  def write(self, *args):
    for arg in args: 
      #print arg,
      print >> self.outfile,  arg,

  def merge_each_key(self, d, keys):
    for key in keys:
      d[key] = self.merge_pair(d[key])

  def merge_pair(self, pair):
    assert len(pair) == 2
    if (pair[0] == pair[1]):
      return pair[0]
    return ' / '.join((str(pair[0]), str(pair[1]))) 

  # For some unknown reason, some really long symbols don't get demangled 
  # properly. Consequenctly, by default such fn_names don't contain enough 
  # newlines, making the profile output harder to read. 
  # This function uses some heuristics to break up such functions so that 
  # both the function names as well as the profile output become more readable.
  def make_fn_name_readable(self, node):
    fn_name = node['fn_name']
    if len(fn_name) < 32:
      return
    num_terms = 1 + fn_name.count('\\')
    if len(fn_name) / num_terms < 32:
      return
    identifier_length = re.compile('[0-9][0-9][a-zA-Z]')
    fn_list = list(fn_name)
    pos = 0
    match = identifier_length.search(fn_name)
    while match:
      pos = match.start()
      length = int(fn_name[pos:pos+2])
      fn_list[pos:pos+2] = ' \n'
      pos += length
      match = identifier_length.search(fn_name, pos)
    node['fn_name'] = ''.join(fn_list)


