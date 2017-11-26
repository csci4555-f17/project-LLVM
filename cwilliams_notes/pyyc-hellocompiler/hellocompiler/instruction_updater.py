import copy
import registers as r
import values_variables as vv
import assembly_generator as ag
import x86_ir as ir

def max_ebp_offset(color_graph):
  max_offset = -1
  for k,v in color_graph.iteritems():
    if isinstance(v, r.OffsetEBP):
      if v.offset > max_offset:
	max_offset = v.offset
  return max_offset
      	
def memory_access_conflicts(instructions):
  '''Instuctions aren't valid if they two operands which are both memory locations'''
  idxs = []
  for idx, i in enumerate(instructions):
    if i.arity == 2:
      if isinstance(i.l, r.OffsetEBP) and isinstance(i.r, r.OffsetEBP):
	print "conflict line: ", i
	idxs.append(idx)
  return idxs     

def instructions_with_colors(instructions, color_mapping, num_vars):
  instructions_copy = copy.deepcopy(instructions)
  for i in instructions_copy:
    for k, v in color_mapping.iteritems():
	i.update_var(k,v)

  conflicts = memory_access_conflicts(instructions_copy)
  print "conflicts:", conflicts
  if len(conflicts) > 0:
    instructions_copy = copy.deepcopy(instructions)
    newvar = vv.Variable(len(color_mapping))    
    newvar.unspillable = True
    for i, c in enumerate(conflicts):
      # this is confusing, but since we're mutating the list the old indexes have to change
      idx = c + i 
      leftv = instructions_copy[idx].l
      newmove = ir.Mov(leftv, newvar)
      instructions_copy[idx].set_l(newvar)
      instructions_copy.insert(idx, newmove)
    instructions_copy = ir.get_optimized_instructions(instructions_copy, num_vars)
  else:
    max_offset = max_ebp_offset(color_mapping)
    if max_offset > -1:
      add_instruction = ir.Sub(vv.Value(4*(max_offset+1)), r.ESP())
      instructions_copy.insert(0,add_instruction)
  return instructions_copy
