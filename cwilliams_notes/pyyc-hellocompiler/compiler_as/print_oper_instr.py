#!/usr/bin/python

def print_oper_instr(self,store_var):
    if (store_var in self.red_vars):
        self.assembly_code.append("    movl %eax, %ebx\n")
        self.instr[store_var] = ['reg','%ebx']
    elif (store_var in self.blue_vars):
        self.assembly_code.append("    movl %eax, %edi\n")
        self.instr[store_var] = ['reg','%edi']
    elif (store_var in self.green_vars):
        self.assembly_code.append("    movl %eax, %esi\n")
        self.instr[store_var] = ['reg','%esi']
    elif (store_var in self.orange_vars):
        #   self.assembly_code.append("    movl %eax, %esi\n")
        self.instr[store_var] = ['reg','%eax']
    elif (store_var in self.black_vars):
        self.assembly_code.append("    movl %eax, %ecx\n")
        self.instr[store_var] = ['reg','%ecx']
    elif (store_var in self.white_vars):
        self.assembly_code.append("    movl %eax, %edx\n")
        self.instr[store_var] = ['reg','%edx']
    else:
            #update variable mapping as we go along                                     
        self.ebp_offset = self.ebp_offset + 1
        self.assembly_code.append("    movl %eax," + str(self.ebp_offset*-4) +"(%ebp)\n")
        self.instr[store_var] = ['stack',self.ebp_offset]
