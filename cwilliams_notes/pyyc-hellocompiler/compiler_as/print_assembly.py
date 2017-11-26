#!/usr/bin/python
def print_assembly(self):

    self.assembly_code = []

    for x in range(0, len(self.ascii_vars_label)):
        self.Print_Var(self.ascii_vars_label[x])
        
    self.assembly_code.append("""
.global main
    main:
    pushl %ebp
    movl %esp, %ebp
        
    """)
    self.assembly_code.append( "subl $" + str(self.num_vars*4) + ",%esp\n")


    self.prog_ord = self.instr_scope_dict["main"][4]
    self.instr = self.instr_scope_dict["main"][1]

    print "main's instr" + str(self.instr)

    idx_to_delete = []
    for x in range(0, len(self.free_var_env_list)):
        scoped_free_var = self.free_var_env_list[x] + "_" + str(self.cur_scope)
        if ( scoped_free_var in self.instr):
            print "found:" + str(scoped_free_var)            
            free_var_val = [self.instr[scoped_free_var][1]]
            self.instr[scoped_free_var] = ['Heapify_Var', free_var_val, self.free_var_env_list[x]]           
            idx_to_delete.append(x)
#            self.free_var_env_list.pop(x)
   #REMOVE VARIABLES FROM FREE ENVIRONMENT LIST ONCE HEAPIFIED
    
#    for y in range(0,len(idx_to_delete)):
#       self.free_var_env_list.pop(idx_to_delete[y])

    for x in range(0, len(self.prog_ord)):
        print "printing pre-instructions in the program order: " + str(self.instr[self.prog_ord[x]])

    self.Print_Instructions(self.prog_ord)
    self.assembly_code.append("    addl $" + str(self.num_vars*4) + ",%esp\n")
    self.assembly_code.append("""
    movl $0, %eax
    leave
    ret
""")        
    
    self.instr_scope_dict.pop("main",None)


    print "printing functions now" 
    for key in self.instr_scope_dict:
        print "the scope name is:" + str(key)
        self.prog_ord = self.instr_scope_dict[key][4]
        self.instr = self.instr_scope_dict[key][1]

#        for x in range(0, len(self.func_ord)):
#            print self.func_ord[x]
#            print "printing function pre-instructions in the program order: " + str(self.instr[self.func_ord[x]])

        self.Print_Instructions(self.prog_ord)
        #self.instr_scope_dict.pop("main",None)

    return "".join(self.assembly_code)
	
def Const_Oper(self,operand,store_var):
    self.assembly_code.append("    movl $"+str(operand) + ", %ecx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call inject_int\n")
    self.print_oper_instr(store_var)

def Bool_Oper(self,operand,store_var):
    self.assembly_code.append("    movl $" + str(operand) + ", %eax\n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_bool\n")
    self.print_oper_instr(store_var)
def Not_Oper(self,operand,store_var,instr_idx):

    self.assembly_code.append("    movl " + operand +", %ecx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call is_true\n")    

    # do val comparison
    self.assembly_code.append("Not_val_cmp_"+str(instr_idx)+":\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    self.assembly_code.append("    jne NotOper_is_1_"+str(instr_idx)+"\n")
    self.assembly_code.append("    movl  $1, %eax\n")
    self.assembly_code.append("jmp ret_result_as_bool_"+str(instr_idx)+"\n")
    #int/bool comparison returned false
    self.assembly_code.append("NotOper_is_1_"+str(instr_idx)+":\n")
    self.assembly_code.append("    movl  $0, %eax\n")
    self.assembly_code.append("jmp ret_result_as_bool_"+str(instr_idx)+"\n")

    #return result as bool
    self.assembly_code.append("ret_result_as_bool_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_bool\n")
    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")

    self.assembly_code.append("post_comp_"+str(instr_idx)+":\n")
    self.print_oper_instr(store_var)

def Assign_Oper(self,operand,store_var):    
    self.assembly_code.append("    movl " + operand + ", %eax\n")
    self.print_oper_instr(store_var)

def Add_Oper(self,operand0,operand1,store_var,instr_idx):
    
    #FIXME:check tags of both operands to see if they are the same
    self.assembly_code.append("    movl " + operand0 +", %ecx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call is_int\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    self.assembly_code.append("    je Add_chk_bool_"+str(instr_idx)+"\n")

    #storing first operand as int in ecx
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call project_int\n")
    self.assembly_code.append("    movl %eax, %ecx\n")

    #check for second int
    self.assembly_code.append("Add_chk_int_2nd_oper_"+str(instr_idx)+":\n")    
    self.assembly_code.append("    movl " + operand1 +", %edx\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call is_int\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    self.assembly_code.append("    je Add_chk_bool_2nd_oper_"+str(instr_idx)+"\n")
    #storing second operand as int in edx
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call project_int\n")
    self.assembly_code.append("    movl %eax, %edx\n")
    self.assembly_code.append("    jmp Add_int_bool_"+str(instr_idx)+"\n")

    #checking for 1st operand as bool
    self.assembly_code.append("Add_chk_bool_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call is_bool\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    #jmp to big obj
    self.assembly_code.append("    je add_cmp_else_"+str(instr_idx)+"\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call project_bool\n")
    self.assembly_code.append("    movl %eax, %ecx\n")    
    self.assembly_code.append("    jmp Add_chk_int_2nd_oper_"+str(instr_idx)+"\n")    

    #checking for 2nd operand as bool
    self.assembly_code.append("Add_chk_bool_2nd_oper_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call is_bool\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    #jmp to big obj
    self.assembly_code.append("    je add_cmp_else_"+str(instr_idx)+"\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call project_bool\n")
    self.assembly_code.append("    movl %eax, %edx\n")    
    self.assembly_code.append("    jmp Add_int_bool_"+str(instr_idx)+"\n")


    #do integer/bool addition
    self.assembly_code.append("Add_int_bool_"+str(instr_idx)+":\n")
    self.assembly_code.append("    add %ecx, %edx \n")                
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call inject_int\n")
    self.assembly_code.append("    jmp post_add_"+str(instr_idx)+"\n")


    #else do list concactenation
    self.assembly_code.append("add_cmp_else_"+str(instr_idx)+":\n")
    self.assembly_code.append("    movl " + operand0 +", %ecx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call project_big\n")
    self.assembly_code.append("    mov %eax, %ecx\n")
    self.assembly_code.append("    movl " + operand1 +", %edx\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call project_big\n")
    self.assembly_code.append("    mov %eax, %edx\n")

    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call add\n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_big\n")

    self.assembly_code.append("    jmp post_add_"+str(instr_idx)+"\n")

    self.assembly_code.append("post_add_"+str(instr_idx)+":\n")
    self.print_oper_instr(store_var)

def IfExp_Oper(self,condition,then,else_,store_var,instr_idx):
    
    #check tag to see if it is bool/int/big obj 
    self.assembly_code.append("    movl " + condition +", %ecx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call is_true\n")

    #compare to see if an int is 0 or other 
    self.assembly_code.append("    cmpl $0, %eax\n")
    self.assembly_code.append("    je IfExpr_condition_else_"+str(instr_idx)+"\n")
    #expression in condition is true, move then to edx so it can be saved as final value
    self.assembly_code.append("    movl " + then +", %eax\n")
    self.assembly_code.append("    jmp post_IfExpr_"+str(instr_idx)+"\n")

    self.assembly_code.append("IfExpr_condition_else_"+str(instr_idx)+":\n")
    #expression in condition is false, move else_ to edx so it can be saved as final value
    self.assembly_code.append("    movl " + else_ +", %eax\n")
    self.assembly_code.append("    jmp post_IfExpr_"+str(instr_idx)+"\n")    

    self.assembly_code.append("post_IfExpr_"+str(instr_idx)+":\n")
    self.print_oper_instr(store_var)

def Is_Oper(self,operand0,operand1,store_var,instr_idx):
    #FIXME:check tags of both operands to see if they are the same
    self.assembly_code.append("    movl " + operand0 +", %ecx\n")
    self.assembly_code.append("    movl " + operand1 +", %edx\n")
    self.assembly_code.append("    cmpl %ecx, %edx \n")

    self.assembly_code.append("    jne IS_Oper_false_"+str(instr_idx)+"\n")
    self.assembly_code.append("    movl  $1, %eax\n")
    #return result as bool
    self.assembly_code.append("    call inject_bool\n")
    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")

    self.assembly_code.append("IS_Oper_false_"+str(instr_idx)+":\n")
    self.assembly_code.append("    movl  $0, %edx\n")
    #return result as bool
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call inject_bool\n")
    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")

    self.assembly_code.append("post_comp_"+str(instr_idx)+":\n")
    self.print_oper_instr(store_var)

def CmpEq_Oper(self,operand0,operand1,store_var,instr_idx):


    self.assembly_code.append("    movl " + operand0 +", %ecx\n")
    #checking for 1st operand as int
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call is_int\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    self.assembly_code.append("    je CmpEq_chk_bool_"+str(instr_idx)+"\n")
    #storing first operand as int in ecx
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call project_int\n")
    self.assembly_code.append("    movl %eax, %ecx\n")
            
    #check for second int
    self.assembly_code.append("CmpEq_chk_int_2nd_oper_"+str(instr_idx)+":\n")    
    self.assembly_code.append("    movl " + operand1 +", %edx\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call is_int\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    self.assembly_code.append("    je CmpEq_chk_bool_2nd_oper_"+str(instr_idx)+"\n")
    #storing second operand as int in edx
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call project_int\n")
    self.assembly_code.append("    movl %eax, %edx\n")
    self.assembly_code.append("    jmp CmpEq_int_bool_"+str(instr_idx)+"\n")


    #checking for 1st operand as bool
    self.assembly_code.append("CmpEq_chk_bool_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call is_bool\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    #jmp to big obj
    self.assembly_code.append("    je CmpEq_cmp_else_"+str(instr_idx)+"\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call project_bool\n")
    self.assembly_code.append("    movl %eax, %ecx\n")    
    self.assembly_code.append("    jmp CmpEq_chk_int_2nd_oper_"+str(instr_idx)+"\n")    

    #checking for 2nd operand as bool
    self.assembly_code.append("CmpEq_chk_bool_2nd_oper_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call is_bool\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    #jmp to big obj
    self.assembly_code.append("    je CmpEq_cmp_else_"+str(instr_idx)+"\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call project_bool\n")
    self.assembly_code.append("    movl %eax, %edx\n")    
    self.assembly_code.append("    jmp CmpEq_int_bool_"+str(instr_idx)+"\n")


    #do integer/bool comparison
    self.assembly_code.append("CmpEq_int_bool_"+str(instr_idx)+":\n")
    self.assembly_code.append("    cmpl %ecx, %edx \n")
    #int comparison returned true
    self.assembly_code.append("    jne CmpEq_int_bool_false_"+str(instr_idx)+"\n")
    self.assembly_code.append("    movl  $1, %edx\n")
    self.assembly_code.append("    jmp ret_bool_int_cmp_result_"+str(instr_idx)+"\n")

    #int/bool comparison returned false
    self.assembly_code.append("CmpEq_int_bool_false_"+str(instr_idx)+":\n")
    self.assembly_code.append("    movl  $0, %edx\n")
    self.assembly_code.append("    jmp ret_bool_int_cmp_result_"+str(instr_idx)+"\n")

    #return result as bool
    self.assembly_code.append("ret_bool_int_cmp_result_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call inject_bool\n")
    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")


    #big obj comparison
    self.assembly_code.append("CmpEq_cmp_else_"+str(instr_idx)+":\n")
    self.assembly_code.append("    movl " + operand0 +", %ecx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call project_big\n")
    self.assembly_code.append("    mov %eax, %ecx\n")
    self.assembly_code.append("    movl " + operand1 +", %edx\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call project_big\n")
    self.assembly_code.append("    mov %eax, %edx\n")

    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call equal\n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_bool\n")
    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")


    self.assembly_code.append("post_comp_"+str(instr_idx)+":\n")
    self.print_oper_instr(store_var)

def CmpNeq_Oper(self,operand0,operand1,store_var,instr_idx):


    self.assembly_code.append("    movl " + operand0 +", %ecx\n")
    #checking for 1st operand as int
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call is_int\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    self.assembly_code.append("    je CmpEq_chk_bool_"+str(instr_idx)+"\n")
    #storing first operand as int in ecx
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call project_int\n")
    self.assembly_code.append("    movl %eax, %ecx\n")
            
    #check for second int
    self.assembly_code.append("CmpEq_chk_int_2nd_oper_"+str(instr_idx)+":\n")    
    self.assembly_code.append("    movl " + operand1 +", %edx\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call is_int\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    self.assembly_code.append("    je CmpEq_chk_bool_2nd_oper_"+str(instr_idx)+"\n")
    #storing second operand as int in edx
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call project_int\n")
    self.assembly_code.append("    movl %eax, %edx\n")
    self.assembly_code.append("    jmp CmpEq_int_bool_"+str(instr_idx)+"\n")

    #checking for 1st operand as bool
    self.assembly_code.append("CmpEq_chk_bool_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call is_bool\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    #jmp to big obj
    self.assembly_code.append("    je CmpEq_cmp_else_"+str(instr_idx)+"\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call project_bool\n")
    self.assembly_code.append("    movl %eax, %ecx\n")    
    self.assembly_code.append("    jmp CmpEq_chk_int_2nd_oper_"+str(instr_idx)+"\n")    

    #checking for 2nd operand as bool
    self.assembly_code.append("CmpEq_chk_bool_2nd_oper_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call is_bool\n")
    self.assembly_code.append("    cmpl $0, %eax  \n")
    #jmp to big obj
    self.assembly_code.append("    je CmpEq_cmp_else_"+str(instr_idx)+"\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call project_bool\n")
    self.assembly_code.append("    movl %eax, %edx\n")    
    self.assembly_code.append("    jmp CmpEq_int_bool_"+str(instr_idx)+"\n")

    #do integer/bool comparison
    self.assembly_code.append("CmpEq_int_bool_"+str(instr_idx)+":\n")
    self.assembly_code.append("    cmpl %ecx, %edx \n")
    #int comparison returned true
    self.assembly_code.append("    jne CmpEq_int_bool_false_"+str(instr_idx)+"\n")
    self.assembly_code.append("    movl  $0, %edx\n")
    self.assembly_code.append("    jmp ret_bool_int_cmp_result_"+str(instr_idx)+"\n")

    #int/bool comparison returned false
    self.assembly_code.append("CmpEq_int_bool_false_"+str(instr_idx)+":\n")
    self.assembly_code.append("    movl  $1, %edx\n")
    self.assembly_code.append("    jmp ret_bool_int_cmp_result_"+str(instr_idx)+"\n")

    #return result as bool
    self.assembly_code.append("ret_bool_int_cmp_result_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call inject_bool\n")
    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")

    #big obj comparison
    self.assembly_code.append("CmpEq_cmp_else_"+str(instr_idx)+":\n")
    self.assembly_code.append("    movl " + operand0 +", %ecx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call project_big\n")
    self.assembly_code.append("    mov %eax, %ecx\n")
    self.assembly_code.append("    movl " + operand1 +", %edx\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    call project_big\n")
    self.assembly_code.append("    mov %eax, %edx\n")

    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call not_equal\n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_bool\n")
    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")

    self.assembly_code.append("post_comp_"+str(instr_idx)+":\n")
    self.print_oper_instr(store_var)
            	
def UNeg_Oper(self,operand0,store_var):
    # print operand0
    self.assembly_code.append("    movl " + str(operand0) + ", %ecx\n")
    self.assembly_code.append("    negl %ecx\n")
    self.assembly_code.append("    movl %ecx, %eax\n")
    self.print_oper_instr(store_var)
	
def Print_Oper(self,operand0,store_var):
    if (store_var in self.red_vars):
        self.assembly_code.append("    movl %ebx, %ecx\n")
    elif (store_var in self.blue_vars):
        self.assembly_code.append("    movl %edi, %ecx\n")
    elif (store_var in self.green_vars):
        self.assembly_code.append("    movl %esi, %ecx\n")
    elif (store_var in self.orange_vars):
        self.assembly_code.append("    movl %eax, %ecx\n")
    elif (store_var in self.black_vars):
        self.assembly_code.append("    movl %ecx, %ecx\n")
    elif (store_var in self.white_vars):
        self.assembly_code.append("    movl %edx, %ecx\n")
    else:
        self.assembly_code.append("    movl "+str(operand0) + ", %ebx\n")

    self.assembly_code.append("    push %ebx\n")
    self.assembly_code.append("    call print_any\n")

def Ret_Oper(self,operand0,store_var):
    if (store_var in self.red_vars):
        self.assembly_code.append("    movl %ebx, %eax\n")
    elif (store_var in self.blue_vars):
        self.assembly_code.append("    movl %edi, %eax\n")
    elif (store_var in self.green_vars):
        self.assembly_code.append("    movl %esi, %eax\n")
    elif (store_var in self.orange_vars):
        self.assembly_code.append("    movl %eax, %eax\n")
    elif (store_var in self.black_vars):
        self.assembly_code.append("    movl %ecx, %eax\n")
    elif (store_var in self.white_vars):
        self.assembly_code.append("    movl %edx, %eax\n")
    else:
        self.assembly_code.append("    movl "+str(operand0) + ", %eax\n")

    self.assembly_code.append("    leave\n")     
    self.assembly_code.append("    ret\n")

def Make_List(self,listLength,store_var):
    self.assembly_code.append("    movl $" + str(listLength) + ", %eax\n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_int \n")    
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call create_list\n") 
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_big\n") 
    self.print_oper_instr(store_var)

def Create_Class(self,py_obj_list_ptr,intmd_var):
    self.assembly_code.append("    movl " + str(py_obj_list_ptr) + ", %eax\n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call create_class\n") 
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_big\n") 

    self.print_oper_instr(intmd_var)

def Make_Dict(self,store_var):
    self.assembly_code.append("    call create_dict\n") 
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_big\n") 
    self.print_oper_instr(store_var)

def List_Assign(self,key,val,py_obj_list):
    self.assembly_code.append("    movl $" + str(key) + ", %ecx\n")
    # need to convert index into pyobj
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call inject_int\n")
    self.assembly_code.append("    movl %eax, %ecx\n")                                           
    self.assembly_code.append("    movl " + str(val) + ", %edx\n")
    self.assembly_code.append("    movl  " + str(py_obj_list) + ", %eax\n")
    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    push %eax\n")    
    self.assembly_code.append("    call set_subscript\n")


def Dict_Assign(self,key,val,py_obj_list):
    self.assembly_code.append("    movl " + str(key) + ", %ecx\n")    
    self.assembly_code.append("    movl " + str(val) + ", %edx\n")
    self.assembly_code.append("    movl  " + str(py_obj_list) + ", %eax\n")

    self.assembly_code.append("    push %edx\n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    push %eax\n")    
    self.assembly_code.append("    call set_subscript\n")

def GetBigVal_Oper(self,key,py_obj,store_var):
    self.assembly_code.append("    movl " + str(key) + ", %ecx\n")    
    self.assembly_code.append("    movl  " + str(py_obj) + ", %eax\n")

    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    push %eax\n")    
    self.assembly_code.append("    call get_subscript\n")
    self.print_oper_instr(store_var)

def Call_Func(self,func_name,arg_list,store_var,func_ptr, instr_idx):

    #check to see if it is a function call or object initialization
    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call is_class\n") 
#    self.assembly_code.append("    push %eax\n")
#    self.assembly_code.append("    call inject_int\n")
#    self.assembly_code.append("    push %eax\n")
#    self.assembly_code.append("    call print_any\n") 
    self.assembly_code.append("    cmpl $1, %eax  \n")
    self.assembly_code.append("    je create_object_"+str(instr_idx)+"\n")

    #check to see if it is an unbound menthod
    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call is_unbound_method\n")
    self.assembly_code.append("    cmpl $1, %eax  \n")
    self.assembly_code.append("    je get_unbound_func_"+str(instr_idx)+"\n")

    #check to see if it is an bound menthod
    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call is_bound_method\n")
    self.assembly_code.append("    cmpl $1, %eax  \n")
    self.assembly_code.append("    je get_bound_func_"+str(instr_idx)+"\n")

   #check to see if it is a non-class function

    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call is_function\n") 
#    self.assembly_code.append("    push %eax\n")
#    self.assembly_code.append("    call inject_int\n")
#    self.assembly_code.append("    push %eax\n")
#    self.assembly_code.append("    call print_any\n") 
    self.assembly_code.append("    cmpl $1, %eax  \n")
    self.assembly_code.append("    je non_class_func_"+str(instr_idx)+"\n")

    #return unbound function
    self.assembly_code.append("get_unbound_func_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call get_function\n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_big\n")
    self.assembly_code.append("    mov  %eax, %ecx  \n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call get_fun_ptr \n")
    self.assembly_code.append("    mov  %eax, %ebx  \n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call get_free_vars \n")
    for x in range(0,len(arg_list)):
        self.assembly_code.append("    push " + str(arg_list[x]) + "\n")
    #push dummy val  as first arg for unbound methods
    self.assembly_code.append("    push $0\n")
    #push free vars
    self.assembly_code.append("    push %eax \n")
    self.assembly_code.append("    call *%ebx \n")

    #need to pop back all the pushes. need to add 2 extra pushes for the dummy self call($0)
    #and call for function free vars
    for x in range(0,len(arg_list)+2):
        self.assembly_code.append("    pop %ebx \n")

    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")

    #return unbound function
    self.assembly_code.append("get_bound_func_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call get_receiver\n")
    self.assembly_code.append("    mov  %eax, %edi  \n")
    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call get_function\n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call inject_big\n")
    self.assembly_code.append("    mov  %eax, %ecx  \n")
    self.assembly_code.append("    push %eax\n")
    self.assembly_code.append("    call get_fun_ptr \n")
    self.assembly_code.append("    mov  %eax, %ebx  \n")
    self.assembly_code.append("    push %ecx\n")
    self.assembly_code.append("    call get_free_vars \n")
    for x in range(0,len(arg_list)):
        self.assembly_code.append("    push " + str(arg_list[x]) + "\n")
    #push dummy val  as first arg for bound methods
    self.assembly_code.append("    push %edi\n")
    #push free vars
    self.assembly_code.append("    push %eax \n")
    self.assembly_code.append("    call *%ebx \n")

    #need to pop back all the pushes. need to add 2 extra pushes for the dummy self call($0)
    #and call for function free vars
    for x in range(0,len(arg_list)+2):
        self.assembly_code.append("    pop %ebx \n")

    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")


    #create object        
    self.assembly_code.append("create_object_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call create_object \n")
    self.assembly_code.append("    push %eax \n")
    self.assembly_code.append("    call inject_big \n") 
    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")

    #non-class function
    self.assembly_code.append("non_class_func_"+str(instr_idx)+":\n")
    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call get_fun_ptr \n")
    self.assembly_code.append("    mov  %eax, %ebx  \n")
    self.assembly_code.append("    push " + str(func_ptr) + "\n")
    self.assembly_code.append("    call get_free_vars \n")
    for x in range(0,len(arg_list)):
        self.assembly_code.append("    push " + str(arg_list[x]) + "\n")
    self.assembly_code.append("    push %eax \n")
    self.assembly_code.append("    call *%ebx \n")
    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")


    self.assembly_code.append("post_comp_"+str(instr_idx)+":\n")
    self.print_oper_instr(store_var)

def Create_Closure(self,func_name,fvl_ptr):
    #create closure
    self.assembly_code.append("    push " + str(fvl_ptr) + " \n")
    self.assembly_code.append("    push $" + str(func_name)+ " \n")
    self.assembly_code.append("    call create_closure \n")    
    self.assembly_code.append("    push %eax  \n")
    self.assembly_code.append("    call inject_big \n")
    self.print_oper_instr(func_name)
 
def Get_First_Idx(self,idx,obj_ptr,store_var):
    
    self.assembly_code.append("    push  $" + str(idx) + " \n")
    self.assembly_code.append("    call inject_int \n")
    self.assembly_code.append("    push  %eax \n")
    self.assembly_code.append("    push  " + str(obj_ptr) + "\n")
    self.assembly_code.append("    call get_subscript\n")
    self.print_oper_instr(store_var)

def Set_First_Idx(self,idx,obj_ptr,val,store_var):

    self.assembly_code.append("    push  $" + str(val) + " \n")
    self.assembly_code.append("    call inject_int \n")
    self.assembly_code.append("    push  %eax \n")    
    self.assembly_code.append("    push  $" + str(idx) + " \n")
    self.assembly_code.append("    call inject_int \n")
    self.assembly_code.append("    push  %eax \n")
    self.assembly_code.append("    push  " + str(obj_ptr) + "\n")
    self.assembly_code.append("    call set_subscript\n")
    self.print_oper_instr(store_var)

def Print_Func(self,func_name,store_var):
    self.assembly_code.append(str(func_name)+":\n")
    self.assembly_code.append("    pushl %ebp\n")
    self.assembly_code.append("    movl %esp, %ebp\n")

def Print_Var(self,var_name):
    self.assembly_code.append(str(var_name)+":\n")
    self.assembly_code.append("    .asciz \"" + str(var_name) + "\"\n")

def SetClassAttribute(self,class_name_pyobj,attr_name,expr_pyobj):

    self.assembly_code.append("    pushl " + str(expr_pyobj) + "\n")
    self.assembly_code.append("    pushl $" + str(attr_name) + "\n")
    self.assembly_code.append("    pushl " + str(class_name_pyobj) + "\n")
    self.assembly_code.append("    call set_attr\n")

def GetClassAttribute(self,class_name_pyobj,attr_name,store_var,instr_idx):
    self.assembly_code.append("    push $" + str(attr_name) + "\n")
    self.assembly_code.append("    push " + str(class_name_pyobj) + "\n")
    self.assembly_code.append("    call get_attr\n")
#    self.assembly_code.append("    movl %eax, %ebx\n")
#
#    self.assembly_code.append("    push %eax \n")
#    self.assembly_code.append("    call is_unbound_method\n")
#    self.assembly_code.append("    push %eax  \n")
#    self.assembly_code.append("    call inject_bool  \n")
#    self.assembly_code.append("    push %eax  \n")
#    self.assembly_code.append("    call print_any  \n")

#    self.assembly_code.append("    cmpl $1, %eax  \n")
#    self.assembly_code.append("    je chk_unbound_func_"+str(instr_idx)+"\n")
#
#    #the attribute is not a function
#    self.assembly_code.append("    movl %ebx, %eax\n")
#    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")
#
#     #return unbound function
#    self.assembly_code.append("chk_unbound_func_"+str(instr_idx)+":\n")
#    self.assembly_code.append("    push %ebx\n")
#    self.assembly_code.append("    call get_function\n")
#    self.assembly_code.append("    push %eax\n")
#    self.assembly_code.append("    call inject_big\n")
#    self.assembly_code.append("    jmp post_comp_"+str(instr_idx)+"\n")
#
#    self.assembly_code.append("post_comp_"+str(instr_idx)+":\n")
#    self.assembly_code.append("    movl %ebx, %eax\n")
    self.print_oper_instr(store_var)    

def Print_Input(self,store_var):
    self.assembly_code.append("    call input_int\n")
    self.print_oper_instr(store_var)

def Print_Instructions(self,instr_list):
    print self.instr
    for x in range(0, len(instr_list)):
        print instr_list[x]
        print "printing instructions in the program order: " + str(self.instr[instr_list[x]])
        if (self.instr[instr_list[x]][0] == 'Add') :
            print self.instr[instr_list[x]]
            if (self.instr[self.instr[instr_list[x]][1]][0] == 'reg'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]
            elif ( self.instr[self.instr[instr_list[x]][1]][0] == 'stack'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]*-4
                op0 = str(op0) + "(%ebp)"
            if (self.instr[self.instr[instr_list[x]][2]][0] == 'reg'):
                op1 = self.instr[self.instr[instr_list[x]][2]][1]
            elif ( self.instr[self.instr[instr_list[x]][2]][0] == 'stack'):
                op1 = self.instr[self.instr[instr_list[x]][2]][1]*-4
                op1 = str(op1) + "(%ebp)"
            #print "add result:" + str(instr_list[x])
            self.Add_Oper(op0,op1,instr_list[x],x)
    
    
        if ( self.instr[instr_list[x]][0] == 'Subscript'):
            py_obj_attr = self.instr[self.instr[instr_list[x]][1]]
            big_idx_attr = self.instr[self.instr[instr_list[x]][2]]
            big_val_attr = self.instr[self.instr[instr_list[x]][3]]
                
               #get py_obj_ptr
            if (py_obj_attr[0] == 'reg'):
                py_obj_ptr = py_obj_attr[1]
            elif ( py_obj_attr[0] == 'stack'):
                py_obj_ptr = py_obj_attr[1]*-4
                py_obj_ptr = str(py_obj_ptr) + "(%ebp)"
    
               #get idx 
            if (big_idx_attr[0] == 'reg'):
                big_idx = big_idx_attr[1]
            elif ( big_idx_attr[0] == 'stack'):
                big_idx = big_idx_attr[1]*-4
                big_idx = str(big_idx) + "(%ebp)"
    
               #get val 
            if (big_val_attr[0] == 'reg'):
                big_val = big_val_attr[1]
            elif ( big_val_attr[0] == 'stack'):
                big_val = big_val_attr[1]*-4
                big_val = str(big_val) + "(%ebp)"
    
            # Subscript takes same argument as Dict assign does
            self.Dict_Assign(big_idx,big_val,py_obj_ptr)
    
        if ( self.instr[instr_list[x]][0] == 'Read_Big'):
            intmd_var = instr_list[x]
            py_obj_attr = self.instr[self.instr[instr_list[x]][1]]
            big_idx_attr = self.instr[self.instr[instr_list[x]][2]]
                
            #get py_obj_ptr
            if (py_obj_attr[0] == 'reg'):
                py_obj_ptr = py_obj_attr[1]
            elif ( py_obj_attr[0] == 'stack'):
                py_obj_ptr = py_obj_attr[1]*-4
                py_obj_ptr = str(py_obj_ptr) + "(%ebp)"
    
            #get idx 
            if (big_idx_attr[0] == 'reg'):
                big_idx = big_idx_attr[1]
            elif ( big_idx_attr[0] == 'stack'):
                big_idx = big_idx_attr[1]*-4
                big_idx = str(big_idx) + "(%ebp)"
    
            # Subscript takes same argument as Dict assign does
            self.GetBigVal_Oper(big_idx,py_obj_ptr,intmd_var)
    
    
        if ( self.instr[instr_list[x]][0] == 'IfExp'):
            #get condition
            condition_attr = self.instr[self.instr[instr_list[x]][1]]
            then_attr =      self.instr[self.instr[instr_list[x]][2]]
            else_attr =      self.instr[self.instr[instr_list[x]][3]]
    
            #get condition_attr
            if (condition_attr[0] == 'reg'):
                condition = condition_attr[1]
            elif ( condition_attr[0] == 'stack'):
                condition = condition_attr[1]*-4
                condition = str(condition) + "(%ebp)"
    
            #get then
            #print then_attr
            if (then_attr[0] == 'reg'):
                then = then_attr[1]
            elif ( then_attr[0] == 'stack'):
                then = then_attr[1]*-4
                then = str(then) + "(%ebp)"
    
            #get else 
            if (else_attr[0] == 'reg'):
                else_ = else_attr[1]
            elif ( else_attr[0] == 'stack'):
                else_ = else_attr[1]*-4
                else_ = str(else_) + "(%ebp)"
                    
            self.IfExp_Oper(condition,then,else_,self.get_dict_key_from_instr_idx(x),x)

        if ( self.instr[instr_list[x]][0] == 'Create_Class'):
           
            op0 = self.instr[instr_list[x]][1]
            intmd_var = instr_list[x]
            #convert bases list to pyobj
            #create list_pyobj 
            self.var = self.var + 1 
            list_pyobj = 't' + str(self.var)
            self.Make_List(len(op0),list_pyobj)
            print "the list obj is:" + str(self.instr[list_pyobj])
            if (self.instr[list_pyobj][0] == 'reg'):
                py_obj_list_ptr = intmd_var[1]
            elif (self.instr[list_pyobj][0] == 'stack'):
                py_obj_list_ptr = self.instr[list_pyobj][1]*-4
                py_obj_list_ptr = str(py_obj_list_ptr) + "(%ebp)"            
            self.Create_Class(py_obj_list_ptr,intmd_var)

        if ( self.instr[instr_list[x]][0] == 'Set_Attribute'):
            class_name = self.instr[instr_list[x]][1] 
            if (self.instr[class_name][0] == 'reg'):
                class_name_pyobj = self.instr[class_name][1]
            elif (self.instr[class_name][0] == 'stack'):
                class_name_pyobj= self.instr[class_name][1]*-4
                class_name_pyobj = str(class_name_pyobj) + "(%ebp)"                        
            attr_name = self.instr[instr_list[x]][2]
            #convert the expression to char array
            expr = self.instr[instr_list[x]][3]
            if (self.instr[expr][0] == 'reg'):
                expr_pyobj = self.instr[expr][1]
            elif (self.instr[expr][0] == 'stack'):
                expr_pyobj= self.instr[expr][1]*-4
                expr_pyobj = str(expr_pyobj) + "(%ebp)"
            self.SetClassAttribute(class_name_pyobj,attr_name,expr_pyobj)

        if ( self.instr[instr_list[x]][0] == 'Get_Attribute'):
            intmd_var = instr_list[x]
            class_name = self.instr[instr_list[x]][1] 
            if (self.instr[class_name][0] == 'reg'):
                class_name_pyobj = self.instr[class_name][1]
            elif (self.instr[class_name][0] == 'stack'):
                class_name_pyobj= self.instr[class_name][1]*-4
                class_name_pyobj = str(class_name_pyobj) + "(%ebp)"                        
            attr_name = self.instr[instr_list[x]][2]
            self.GetClassAttribute(class_name_pyobj,attr_name,intmd_var,x)
            
           
        if ( self.instr[instr_list[x]][0] == 'Create_List_Only'):        
            op0 = self.instr[instr_list[x]][1]
            intmd_var = instr_list[x]
            self.Make_List(op0,intmd_var)

        if ( self.instr[instr_list[x]][0] == 'Free_Var_List'):        
            free_var_list = self.instr[instr_list[x]][1]
            list_len = len(free_var_list)
            intmd_var = instr_list[x]
            self.Make_List(list_len,intmd_var)

            #get py_obj_ptr
            if (self.instr[intmd_var][0] == 'reg'):
                py_obj_list = intmd_var[1]
            elif (self.instr[intmd_var][0] == 'stack'):
                py_obj_list = self.instr[intmd_var][1]*-4
                py_obj_list = str(py_obj_list) + "(%ebp)"

            #assign list nodes
            print free_var_list
            for y in range (0, len(free_var_list)):
                heap_var = self.free_var_maps[free_var_list[y]]
                if ( heap_var[0] == 'reg'):
                    val = heap_var[1]
    
                elif ( heap_var[0] == 'stack'):
                    val = heap_var[1]*-4
                    val = str(val) + "(%ebp)"
                print "printing valueeeeee:" + str(val)                    
                self.List_Assign(y,val, py_obj_list)    


        if ( self.instr[instr_list[x]][0] == 'Heapify_Var'):
            print self.instr[instr_list[x]]
            op0 = self.instr[instr_list[x]][1]
            intmd_var = instr_list[x]
            print intmd_var
            free_var = self.instr[instr_list[x]][2]
            self.Make_List(len(op0),intmd_var)

            self.free_var_maps[free_var] = self.instr[intmd_var]
            print "dict:" + str(self.free_var_maps)

            #get py_obj_ptr
            if (self.instr[intmd_var][0] == 'reg'):
                py_obj_list = intmd_var[1]
            elif (self.instr[intmd_var][0] == 'stack'):
                py_obj_list = self.instr[intmd_var][1]*-4
                py_obj_list = str(py_obj_list) + "(%ebp)"
            #assign list nodes
            for y in range (0, len(op0)):
                print "val of nodes:" + str(self.instr[op0[y]])
                if ( self.instr[op0[y]][0] == 'reg'):
                    val = self.instr[op0[y]][1]
    
                elif ( self.instr[op0[y]][0] == 'stack'):
                    val = self.instr[op0[y]][1]*-4
                    val = str(val) + "(%ebp)"
                #print "printing value:" + str(val)                    
                self.List_Assign(y, val, py_obj_list)    


    
        if ( self.instr[instr_list[x]][0] == 'List'):
            print self.instr[instr_list[x]]
            op0 = self.instr[instr_list[x]][1]
            intmd_var = instr_list[x]
            self.Make_List(len(op0),intm_var)
    
            #get py_obj_ptr
            if (self.instr[intmd_var][0] == 'reg'):
                py_obj_list = intmd_var[1]
            elif (self.instr[intmd_var][0] == 'stack'):
                py_obj_list = self.instr[intmd_var][1]*-4
                py_obj_list = str(py_obj_list) + "(%ebp)"
            #assign list nodes
            for y in range (0, len(op0)):
                print "val of nodes:" + str(self.instr[op0[y]])
                if ( self.instr[op0[y]][0] == 'reg'):
                    val = self.instr[op0[y]][1]
    
                elif ( self.instr[op0[y]][0] == 'stack'):
                    val = self.instr[op0[y]][1]*-4
                    val = str(val) + "(%ebp)"
                #print "printing value:" + str(val)                    
                self.List_Assign(y, val, py_obj_list)    
            
    
        if ( self.instr[instr_list[x]][0] == 'Dict'):
            temp_dict = self.instr[instr_list[x]][1]
            intmd_var = instr_list[x]
            self.Make_Dict(intmd_var)
            #get py_obj_ptr
            if (self.instr[intmd_var][0] == 'reg'):
                py_obj_list = self.instr[intmd_var][1]
            elif (self.instr[intmd_var][0] == 'stack'):
                py_obj_list = self.instr[intmd_var][1]*-4
                py_obj_list = str(py_obj_list) + "(%ebp)"
    
            #assign dict keys
            #print temp_dict
            for temp_key in temp_dict:
                #look for key
                if ( self.instr[temp_key][0] == 'reg'):
                    key = self.instr[temp_key][1]
                elif ( self.instr[temp_key][0] == 'stack'):
                    key = self.instr[temp_key][1]*-4
                    key = str(key) + "(%ebp)"
    
                #look for map_value
                if ( self.instr[temp_dict[temp_key]][0] == 'reg'):
                    map_value = self.instr[temp_dict[temp_key]][1]
                elif ( self.instr[temp_dict[temp_key]][0] == 'stack'):
                    map_value = self.instr[temp_dict[temp_key]][1]*-4
                    map_value = str(map_value) + "(%ebp)"
    
                #print "key:" +str(key) + " map_value:" + str(map_value)
                self.Dict_Assign(key, map_value, py_obj_list)
            
    
        #FIXME: code cleanup - consolidate all these three condition
        if (   (self.instr[instr_list[x]][0] == 'Cmp_Eq')
               or (self.instr[instr_list[x]][0] == 'Cmp_Neq')
               or (self.instr[instr_list[x]][0] == 'IS')
               or (self.instr[instr_list[x]][0] == 'Or')
               or (self.instr[instr_list[x]][0] == 'And')
           ) :
            if (self.instr[self.instr[instr_list[x]][1]][0] == 'reg'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]
            elif ( self.instr[self.instr[instr_list[x]][1]][0] == 'stack'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]*-4
                op0 = str(op0) + "(%ebp)"
            if (self.instr[self.instr[instr_list[x]][2]][0] == 'reg'):
                op1 = self.instr[self.instr[instr_list[x]][2]][1]
            elif ( self.instr[self.instr[instr_list[x]][2]][0] == 'stack'):
                op1 = self.instr[self.instr[instr_list[x]][2]][1]*-4
                op1 = str(op1) + "(%ebp)"
                intmd_var = instr_list[x]
    
            if (self.instr[instr_list[x]][0] == 'Cmp_Eq'):
                self.CmpEq_Oper(op0,op1,instr_list[x],x)
            elif (self.instr[instr_list[x]][0] == 'Cmp_Neq'):
                self.CmpNeq_Oper(op0,op1,instr_list[x],x)
            elif (self.instr[instr_list[x]][0] == 'IS'):
                self.Is_Oper(op0,op1,instr_list[x],x)
            elif (self.instr[instr_list[x]][0] == 'Or'):
                self.IfExp_Oper(op0,op0,op1,intmd_var,x)
            elif (self.instr[instr_list[x]][0] == 'And'):
                self.IfExp_Oper(op0,op1,op0,intmd_var,x)
    
    
        elif (self.instr[instr_list[x]][0] == 'Not') :
            intmd_var = instr_list[x]
            if (self.instr[self.instr[instr_list[x]][1]][0] == 'reg'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]
            elif ( self.instr[self.instr[instr_list[x]][1]][0] == 'stack'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]*-4
                op0 = str(op0) + "(%ebp)"
            self.Not_Oper(op0,intmd_var,x)
    
        elif (   (self.instr[instr_list[x]][0] == 'Const')
              or (self.instr[instr_list[x]][0] == 'Bool')
             ):
            op0 = self.instr[instr_list[x]][1]
            intmd_var = instr_list[x]
            if (self.instr[instr_list[x]][0] == 'Const'):
                self.Const_Oper(op0,intmd_var)
            elif (self.instr[instr_list[x]][0] == 'Bool'):
                self.Bool_Oper(op0,intmd_var)
    
        elif (self.instr[instr_list[x]][0] == 'Assign') :

           # print self.instr[instr_list[x]]

            if (self.instr[self.instr[instr_list[x]][1]][0] == 'reg'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]
            elif ( self.instr[self.instr[instr_list[x]][1]][0] == 'stack'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]*-4
                op0 = str(op0) + "(%ebp)"
            self.Assign_Oper(op0,"temp_key")
            self.instr[instr_list[x]][0] = self.instr["temp_key"][0]
            self.instr[instr_list[x]][1] = self.instr["temp_key"][1]
          #  print self.instr[instr_list[x]]

#variable reassignment
        elif (    ((self.instr[instr_list[x]][0] == 'stack') or (self.instr[instr_list[x]][0] == 'reg'))
                  and (len(self.instr[instr_list[x]]) > 2)
             ) :
           # print "got here"
          #  print self.instr[instr_list[x]]
            del self.instr[instr_list[x]][0]
            del self.instr[instr_list[x]][0]

           # print self.instr[instr_list[x]]
            if (self.instr[self.instr[instr_list[x]][1]][0] == 'reg'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]
            elif ( self.instr[self.instr[instr_list[x]][1]][0] == 'stack'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]*-4
                op0 = str(op0) + "(%ebp)"
            self.Assign_Oper(op0,"temp_key")
            self.instr[instr_list[x]][0] = self.instr["temp_key"][0]
            self.instr[instr_list[x]][1] = self.instr["temp_key"][1]
           # print self.instr[instr_list[x]]
                    
        elif (self.instr[instr_list[x]][0] == 'UNeg') :
         #   print self.instr[instr_list[x]]
            if (self.instr[self.instr[instr_list[x]][1]][0] == 'reg'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]
            elif ( self.instr[self.instr[instr_list[x]][1]][0] == 'stack'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]*-4
                op0 = str(op0) + "(%ebp)"
            self.UNeg_Oper(op0,instr_list[x])
                                    
        elif (self.instr[instr_list[x]][0] == 'Print') :
            print self.instr[self.instr[instr_list[x]][1]]
            if ( self.instr[self.instr[instr_list[x]][1]][0] == 'reg'):
                op5 = self.instr[self.instr[instr_list[x]][1]][1]
            elif ( self.instr[self.instr[instr_list[x]][1]][0] == 'stack'):
                op5 = self.instr[self.instr[instr_list[x]][1]][1]*-4
                op5 = str(op5) + "(%ebp)"
            self.Print_Oper(op5, self.instr[instr_list[x]][1])
    	
        elif (self.instr[instr_list[x]][0] == 'CallFunc') :
            #print self.instr
            func_name = self.instr[instr_list[x]][1]
            arg_list = self.instr[self.instr[instr_list[x]][2]]                
            arg_list_updated = []
            for z in range(len(arg_list), 0,-1 ):
                if ( self.instr[arg_list[z-1]][0] == 'reg'):
                    op0 = self.instr[arg_list[z-1]][1]
                elif ( self.instr[arg_list[z-1]][0] == 'stack'):
                    op0 = self.instr[arg_list[z-1]][1] * -4
                    op0 = str(op0) + "(%ebp)"
                arg_list_updated.append(op0)

            #check to see where is func_name stored
            if (func_name == ('input' + "_" + str(self.cur_scope))):
                self.Print_Input(instr_list[x])
            else:
                if (self.instr[func_name][0] == 'reg'):
                    func_ptr = self.instr[func_name][1]
                elif (self.instr[func_name][0] == 'stack'):
                    func_ptr = self.instr[func_name][1]*-4
                    func_ptr = str(func_ptr) + "(%ebp)"
                self.Call_Func(func_name,arg_list_updated,instr_list[x],func_ptr,x)

        elif (self.instr[instr_list[x]][0] == 'Create_Closure') :
            func_name = instr_list[x]
           # print self.instr[self.instr[instr_list[x]][2]][0]
            if ( self.instr[self.instr[instr_list[x]][2]][0] == 'reg'):
                fvl_ptr = self.instr[self.instr[instr_list[x]][2]][1]
            elif ( self.instr[self.instr[instr_list[x]][2]][0] == 'stack'):
                fvl_ptr = self.instr[self.instr[instr_list[x]][2]][1]*-4
                fvl_ptr = str(fvl_ptr) + "(%ebp)"
            self.Create_Closure(func_name, fvl_ptr)


        elif (self.instr[instr_list[x]][0] == 'List_Assign') :                                           
             key = self.instr[instr_list[x]][1]
             val = self.instr[instr_list[x]][2]
             list_ptr = self.instr[instr_list[x]][3]
             self.List_Assign(key, val, list_ptr)
             instr_list[x] = ['stack',list_ptr]
                                 
        elif (self.instr[instr_list[x]][0] == 'Function') :
            func_name = self.instr[instr_list[x]][1]
            self.Print_Func(func_name,instr_list[x])

        elif (self.instr[instr_list[x]][0] == 'Func_Args_FV') :
            func_argList = self.instr[instr_list[x]][1]
            free_vars_list = self.instr[instr_list[x]][2]
            #assign stack space for free vars used in the function
            for z in range (0, len(free_vars_list)): 
                #first get the address of the free var
                py_obj = "8(%ebp)"
                self.Get_First_Idx(z,py_obj,free_vars_list[z])
                #use the address of the free to access index 0 and assign it to the local version of free var
                if ( self.instr[free_vars_list[z]][0] == 'reg'):
                    py_obj1 = self.instr[free_vars_list[z]][1]
                elif ( self.instr[free_vars_list[z]][0] == 'stack'):
                    py_obj1 = self.instr[free_vars_list[z]][1]*-4
                    py_obj1 = str(py_obj1) + "(%ebp)"
                self.Get_First_Idx(0,py_obj1,free_vars_list[z])

            stk_idx_post_free_vars = len(free_vars_list)
            #assign stack space for each parameter in the function call
            for y in range (0, len(func_argList)): 
                offset = -3 - y 
                self.instr[func_argList[y]] = ['stack', offset]                
            
        elif (self.instr[instr_list[x]][0] == 'Return') :
#            print self.instr
            if (self.instr[self.instr[instr_list[x]][1]][0] == 'reg'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]
            elif ( self.instr[self.instr[instr_list[x]][1]][0] == 'stack'):
                op0 = self.instr[self.instr[instr_list[x]][1]][1]*-4
                op0 = str(op0) + "(%ebp)"
            self.Ret_Oper(op0, self.instr[instr_list[x]][1])

