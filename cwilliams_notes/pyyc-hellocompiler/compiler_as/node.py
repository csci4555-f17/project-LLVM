#!/usr/bin/python
class node():

    def __init__(self):
       self.var_name = ''
       self.intf_nodes = []
       self.location = 'stack'
       self.sat_deg = 0
       self.neighbor_nodes_cnt = 0
       self.is_live_at_call_instr = 0
       self.is_live_at_add_instr = 0
       self.is_live_at_uni_oper_instr = 0

    def display_node(self):
        print 'node name:' + str(self.var_name)
        print 'neighbor nodes:' + str(self.intf_nodes)
        print 'neighbor nodes cnt:' + str(self.neighbor_nodes_cnt)
        print 'saturation degree:' + str(self.sat_deg)
        print 'is live at call instr:' + str(self.is_live_at_call_instr)
        print 'is live at uni oper instr:' + str(self.is_live_at_uni_oper_instr)
        print 'is live at add instr:' + str(self.is_live_at_add_instr)
