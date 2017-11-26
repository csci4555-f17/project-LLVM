#!/usr/bin/python
def color_graph(self):
    skip = 0
    min_value = len(self.nodes)
    
    for x in range(0, min_value):
        self.update_nodes_degrees()
        skip = 0
        
        # find suitable color for the variable.
        if ( x % 6 == 0):
            if (len(self.red_vars) == 0):
                temp_node = self.nodes.pop(0)
                self.red_vars.append(temp_node.var_name)
            else:
                skip = 1
                for a in range ( 0, len (self.nodes)):
                    if ( len([val for val in self.red_vars if val in self.nodes[a].intf_nodes]) == 0):
                        temp_node = self.nodes.pop(a)
                        self.red_vars.append(temp_node.var_name)
                        skip = 0
                        break                        
        elif ( x % 6 == 1):
            if (len(self.blue_vars) == 0):
                temp_node = self.nodes.pop(0)
                self.blue_vars.append(temp_node.var_name)
            else:
                skip = 1
                for a in range ( 0, len (self.nodes)):
                    if ( len([val for val in self.blue_vars if val in self.nodes[a].intf_nodes]) == 0):
                        temp_node = self.nodes.pop(a)
                        self.blue_vars.append(temp_node.var_name)
                        skip = 0
                        break                        
        elif ( x % 6 == 2):
            if (len(self.green_vars) == 0):
                temp_node = self.nodes.pop(0)
                self.green_vars.append(temp_node.var_name)
            else:
                skip = 1
                for a in range ( 0, len (self.nodes)):
                    if ( len([val for val in self.green_vars if val in self.nodes[a].intf_nodes]) == 0):
                        temp_node = self.nodes.pop(a)
                        self.green_vars.append(temp_node.var_name)
                        skip = 0
                        break                        
        elif ( x % 6 == 3):
            if ((self.nodes[0].is_live_at_call_instr == 0) and (len(self.orange_vars) == 0)):
                temp_node = self.nodes.pop(0)
                self.orange_vars.append(temp_node.var_name)
            else:
                #just go through the list and find the variable that we might be able to store 
                #in eax. if we dont find anything then just move on without storing anything inside eax
                #and set skip to 1
                skip  = 1
                for a in range(0,len(self.nodes)):
                    if (      (self.nodes[a].is_live_at_call_instr == 0)
                         and  (len([val for val in self.orange_vars if val in self.nodes[a].intf_nodes]) == 0)
                       ):
                        temp_node = self.nodes.pop(a)
                        self.orange_vars.append(temp_node.var_name)
                        skip = 0
                        break
        elif ( x % 6 == 4):
            if ((self.nodes[0].is_live_at_call_instr == 0) and (len(self.black_vars) == 0) and (self.nodes[0].is_live_at_uni_oper_instr == 0) and (self.nodes[0].is_live_at_add_instr == 0)):
                temp_node = self.nodes.pop(0)
                self.black_vars.append(temp_node.var_name)
            else:
                #just go through the list and find the variable that we might be able to store 
                #in eax. if we dont find anything then just move on without storing anything inside eax
                #and set skip to 1
                skip  = 1
                for a in range(0,len(self.nodes)):
                #    print "displaying nodes right now:" + str(self.nodes[a].is_live_at_call_instr)
                    if (      (self.nodes[a].is_live_at_call_instr == 0)
                            and   (self.nodes[a].is_live_at_uni_oper_instr == 0) 
                            and   (self.nodes[a].is_live_at_add_instr == 0)
                            and  (len([val for val in self.black_vars if val in self.nodes[a].intf_nodes]) == 0)
                       ):
                        print "adding node:" + str(self.nodes[a].var_name)
                        temp_node = self.nodes.pop(a)
                        self.black_vars.append(temp_node.var_name)
                        skip = 0
                        break
        elif ( x % 6 == 5):
            if ((self.nodes[0].is_live_at_call_instr == 0) and (len(self.white_vars) == 0) and (self.nodes[0].is_live_at_add_instr == 0)):
                temp_node = self.nodes.pop(0)
                self.white_vars.append(temp_node.var_name)
            else:
                #just go through the list and find the variable that we might be able to store 
                #in eax. if we dont find anything then just move on without storing anything inside eax
                #and set skip to 1
                skip  = 1
                for a in range(0,len(self.nodes)):
                    #    print "displaying nodes right now:" + str(self.nodes[a].is_live_at_call_instr)
                    if (     (self.nodes[a].is_live_at_call_instr == 0)
                        and (self.nodes[a].is_live_at_add_instr == 0)
                        and (len([val for val in self.white_vars if val in self.nodes[a].intf_nodes]) == 0)
                       ):
                        #print "adding node:" + str(self.nodes[a].var_name)
                        temp_node = self.nodes.pop(a)
                        self.white_vars.append(temp_node.var_name)
                        skip = 0
                        break

        if ( skip == 0):
            # update saturation degree for neighbouring nodes 
            for y in range (0, len(self.nodes)):            
                if ( temp_node.var_name in self.nodes[y].intf_nodes):
                    self.nodes[y].sat_deg += 1
                    
    print ' Red Vars: ' + str(self.red_vars)
    print ' Blue Vars ' + str(self.blue_vars)
    print ' Green Vars ' + str(self.green_vars)
    print ' Orange Vars ' + str(self.orange_vars)
    print ' Black Vars ' + str(self.black_vars)
    print ' White Vars ' + str(self.white_vars)        
