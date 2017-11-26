#!/usr/bin/python
import re
import compiler
from compiler.ast import *
import copy
import sys
from node import node
from color_graph import color_graph
from print_oper_instr import print_oper_instr 
from print_assembly import * 
import p0_parser as ply_lex_parse

class py_to_x86():

    def __init__(self):
        self.var = 0
        self.ebp_offset = 0
        self.instr = dict()
        self.instr_scope_dict = dict()
        
        self.scope_val = "main"
        self.free_var_envs = dict()
        self.free_var_env_list = []
        self.free_var_maps = dict()
        self.free_var_list = []
        self.fve_per_label = dict()
        self.prog_ord = []
        self.class_ord = []
        
        self.ascii_vars_label = []

        self.num_vars = 0
        self.assemb_prog = ''
        self.nodes = []
        self.red_vars = []
        self.blue_vars = []
        self.green_vars= []
        self.orange_vars = []
        self.black_vars = []
        self.white_vars = []
        self.vars_live_at_call_instr = []
        self.vars_live_at_uni_oper_instr = []
        self.vars_live_at_add_instr = []
        self.all_vars_set = set([])
        self.local_vars_set = set([])
        self.cur_scope = "main"
        self.prev_scope = "main"
        self.instr_scope_dict[self.cur_scope] = [self.prev_scope,self.instr,self.all_vars_set,self.local_vars_set,self.prog_ord]

    def flatten(self,ast,is_func):
        if isinstance(ast,Module):
            self.flatten(ast.node,is_func)
        elif isinstance(ast,Stmt):
            [self.flatten(x,0) for x in ast.nodes]
        elif isinstance(ast,Discard):
            return self.flatten(ast.expr,is_func)
        elif isinstance(ast,Add):
            lvalue = self.flatten(ast.left,is_func)
            rvalue = self.flatten(ast.right,is_func)
            if ['Add',lvalue,rvalue] in self.instr.values():
                temp_var = self.get_dict_key_from_value(['Add',lvalue,rvalue])
                return temp_var
            else : 
                self.var = self.var + 1
                temp_var = 't' + str(self.var) 
                self.instr[temp_var] = ['Add',lvalue,rvalue]
                if (is_func):
                    self.class_ord.append(temp_var)
                else:
                    self.prog_ord.append(temp_var)
                return temp_var
        elif isinstance(ast,And):
            lvalue = self.flatten(ast.nodes[0],is_func)
            rvalue = self.flatten(ast.nodes[1],is_func)
            if ['And',lvalue,rvalue] in self.instr.values():
                temp_var = self.get_dict_key_from_value(['And',lvalue,rvalue])
                return temp_var
            else : 
                self.var = self.var + 1
                temp_var = 't' + str(self.var) 
                self.instr[temp_var] = ['And',lvalue,rvalue]
                if (is_func):
                    self.class_ord.append(temp_var)
                else:
                    self.prog_ord.append(temp_var)                
                return temp_var
        elif isinstance(ast,Or):
            lvalue = self.flatten(ast.nodes[0],is_func)
            rvalue = self.flatten(ast.nodes[1],is_func)
            if ['Or',lvalue,rvalue] in self.instr.values():
                temp_var = self.get_dict_key_from_value(['Or',lvalue,rvalue])
                return temp_var
            else : 
                self.var = self.var + 1
                temp_var = 't' + str(self.var) 
                self.instr[temp_var] = ['Or',lvalue,rvalue]
                if (is_func):
                    self.class_ord.append(temp_var)
                else:
                    self.prog_ord.append(temp_var)
                return temp_var
        elif isinstance(ast,IfExp):
            cond = self.flatten(ast.test,is_func)
            then = self.flatten(ast.then,is_func)
            else_ = self.flatten(ast.else_,is_func)
            self.var = self.var + 1
            temp_var = 't' + str(self.var) 
            self.instr[temp_var] = ['IfExp',cond,then,else_]
            if (is_func):
                self.class_ord.append(temp_var)
            else:
                self.prog_ord.append(temp_var)
            return temp_var        
        elif isinstance(ast,List):            
            self.var = self.var + 1
            temp_var = 't' + str(self.var)     
            list_nodes = []
            len_nodes = len(ast.nodes)
            for x in range ( 0, len_nodes):                
                list_nodes.append(self.flatten(ast.nodes[x],is_func))
            self.instr[temp_var] = ['List',list_nodes,len_nodes]
            if (is_func):
                self.class_ord.append(temp_var)
            else:
                self.prog_ord.append(temp_var)                
            return temp_var
        elif isinstance(ast,Dict):  
            self.var = self.var + 1
            temp_var = 't' + str(self.var)
            dict_len = len(ast.items)     
            dict_nodes = {}
            for x in range ( 0, dict_len):
                key = self.flatten(ast.items[x][0],is_func)
                print key
                map_val = self.flatten(ast.items[x][1],is_func)
                print map_val
                dict_nodes[key] = map_val 
            self.instr[temp_var] = ['Dict',dict_nodes,dict_len]
            if (is_func):
                self.class_ord.append(temp_var)
            else:
                self.prog_ord.append(temp_var)
            return temp_var
        elif isinstance(ast,Compare):
            lvalue = self.flatten(ast.expr,is_func)
            rvalue = self.flatten(ast.ops[0][1],is_func)
            cmp_type = ast.ops[0][0]
            if ( cmp_type == '==' ) :
                self.var = self.var + 1
                temp_var = 't' + str(self.var) 
                self.instr[temp_var] = ['Cmp_Eq',lvalue,rvalue]
                if (is_func):
                    self.class_ord.append(temp_var)
                else:
                   self.prog_ord.append(temp_var)

                return temp_var
            elif ( cmp_type == '!='):                
                self.var = self.var + 1
                temp_var = 't' + str(self.var) 
                self.instr[temp_var] = ['Cmp_Neq',lvalue,rvalue]
                if (is_func):
                    self.class_ord.append(temp_var)
                else:
                    self.prog_ord.append(temp_var)                
                return temp_var
            elif ( cmp_type == 'is'):
                self.var = self.var + 1
                temp_var = 't' + str(self.var) 
                self.instr[temp_var] = ['IS',lvalue,rvalue]
                if (is_func):
                    self.class_ord.append(temp_var)
                else:
                    self.prog_ord.append(temp_var)
                return temp_var
        elif isinstance(ast,AssName):
            temp_var = ast.name + "_" + str(self.cur_scope) 
            self.local_vars_set |= set([temp_var])
            return temp_var
        elif isinstance(ast,Assign):
           print "is_func: " + str(is_func)
           temp_var = self.flatten(ast.nodes[0],is_func)
           expr = self.flatten(ast.expr,is_func)
           #Review if subscript needs to be added as write var
           if ( isinstance (temp_var, list)):
               self.var = self.var + 1
               temp_var2 = 't' + str(self.var) 
               if (temp_var[2] == 'Subscript'):
                   self.instr[temp_var2] = ['Subscript',temp_var[0],temp_var[1],expr]
               elif (temp_var[2] == 'AssAttr'):
                   if temp_var[1] not in self.ascii_vars_label:
                       self.ascii_vars_label.append(temp_var[1])                    
                   self.instr[temp_var2] = ['Set_Attribute',temp_var[0],temp_var[1],expr]                   
               if (is_func):
                   print "got here too"
                   self.class_ord.append(temp_var2)
               else:
                   self.prog_ord.append(temp_var2)
           else:
               if temp_var in self.instr:
                   self.instr[temp_var].append('Assign')
                   self.instr[temp_var].append(expr)
                   print "reinit var:" + str(self.instr[temp_var])
               else:
                   self.instr[temp_var] =['Assign', expr]
               if (is_func):
                   print "got here too 2"
                   self.class_ord.append(temp_var)
               else:
                   self.prog_ord.append(temp_var)

        elif isinstance(ast,Subscript):            
            key_or_idx = self.flatten(ast.subs[0],is_func)
            name = self.flatten(ast.expr,is_func)
            flags = ast.flags
            if (flags == 'OP_APPLY'):
               self.var = self.var + 1
               temp_var = 't' + str(self.var)
               self.instr[temp_var] = ['Read_Big',name,key_or_idx]
               if (is_func):
                   self.class_ord.append(temp_var)
               else:
                   self.prog_ord.append(temp_var)
               return temp_var
            else:
                return [name,key_or_idx,'Subscript']

        elif isinstance(ast,Not):            
            self.var = self.var + 1
            temp_var = 't' + str(self.var)
            self.instr[temp_var] =['Not', self.flatten(ast.expr,is_func)]
            if (is_func):
                self.class_ord.append(temp_var)
            else:
                self.prog_ord.append(temp_var)
            return temp_var

        elif isinstance(ast,Const):
            # for discarded statements, especially the character ; is treated as const NONE. ignore it
            if ( str(ast.value) == 'None'):
                return
            # if a given const mapping already exists, then no nead to create a new dictionary
            # mapping for it
            elif ['Const',ast.value] in self.instr.values():                
                temp_var = self.get_dict_key_from_value(['Const',ast.value])
                return temp_var
            else : 
                self.var = self.var + 1
                temp_var = 't' + str(self.var) 
                self.instr[temp_var] = ['Const',ast.value]
                if (is_func):
                    self.class_ord.append(temp_var)
                else:
                    self.prog_ord.append(temp_var)
                return temp_var

        elif isinstance(ast,Name):
            print "hi my name is :" + str(ast.name)
            self.all_vars_set |= set([str(ast.name) + "_" + str(self.cur_scope)])
            if (     (ast.name in self.instr)
                 and (self.instr[ast.name][0] != 'Function')
                 and (self.instr[ast.name][0] != 'Create_Class')
               ):
                #if key with ast.name preexists in the list,
                #update the key to return its value instead of the name
                #also remove previous key from program order because it has been               
                #overriden by assignment of same variable
                print self.instr
                if ast.name in self.prog_ord:
                    #FIXME: not removing dict or list from the prog ord so that original 
                    #list assignment can be made
                    if (    (self.instr[self.instr[ast.name][1]][0] != 'List')
                        and (self.instr[self.instr[ast.name][1]][0] != 'Dict')
                        and (self.instr[self.instr[ast.name][1]][0] != 'Create_Closure')
                        and (self.instr[self.instr[ast.name][1]][0] != 'Create_Class')                            
                        and (self.instr[self.instr[ast.name][1]][0] != 'Function')
                       ):
                        print self.instr[self.instr[ast.name][1]][0]
                        print "removing the name:" + str(ast.name)
                        self.prog_ord.remove(ast.name)
                print "returning the name :" + str(self.instr[ast.name][1])
                return self.instr[ast.name][1];
            else:
                if ( (ast.name == 'True') or (ast.name =='False')):
                    if (ast.name == 'True'):
                        expr = 1
                    else:
                        expr = 0
                    self.var = self.var + 1
                    temp_var = 't' + str(self.var)
                    self.instr[temp_var] =['Bool', expr]
                    if (is_func):
                        self.class_ord.append(temp_var)
                    else:
                        self.prog_ord.append(temp_var)
                    return temp_var
                else:    

                    return str(ast.name)  + "_" + str(self.cur_scope)

        elif isinstance(ast, UnarySub):
            value = self.flatten(ast.expr,is_func)
            if ['UNeg',value] in self.instr.values():
                temp_var = self.get_dict_key_from_value(['UNeg',value])
                return temp_var
            else :
                self.var = self.var + 1
                temp_var = 't' + str(self.var)
                self.instr[temp_var] = ['UNeg',value]
                if (is_func):
                    self.class_ord.append(temp_var)
                else:
                    self.prog_ord.append(temp_var)                
                return temp_var

        elif isinstance(ast, Printnl):
            value = self.flatten(ast.nodes[0],is_func)
            self.var = self.var+1
            temp_var = 't'+ str(self.var) 
            self.instr[temp_var] = ['Print', value];
            if (is_func):
                self.class_ord.append(temp_var)
            else:
                self.prog_ord.append(temp_var)
            return temp_var

        elif isinstance(ast, Function):
            func_name = ast.name
            func_name_scoped = func_name + "_" + str(self.cur_scope)
            func_argsList = ast.argnames
            print " The args list is:::::::::::::::::::" + str(func_argsList)
            self.local_vars_set |= set([func_name + "_" + str(self.cur_scope)])

            #Increment Scope
            print "Incr Current Scope:" + str(self.cur_scope) + " Instr:" + str(self.instr) + "Scope:" + str(self.local_vars_set)
            #store current scope dictionary before incrementing scope
            self.instr_scope_dict[self.cur_scope][1].update(copy.deepcopy(self.instr))
            #store current scope all/local vars before incremeneting scope
            self.instr_scope_dict[self.cur_scope][2].update(copy.deepcopy(self.all_vars_set))
            self.instr_scope_dict[self.cur_scope][3].update(copy.deepcopy(self.local_vars_set))
            self.instr_scope_dict[self.cur_scope][4] += copy.deepcopy(self.prog_ord)
            self.prev_scope  = self.cur_scope
            self.cur_scope = func_name
            if self.cur_scope not in self.instr_scope_dict:
                self.instr_scope_dict[self.cur_scope] = [self.prev_scope,dict(),set([]),set([]),[]]
            #reset dicts and vars
            self.instr = dict()
            self.prog_ord = []
            self.all_vars_set = set([])
            self.local_vars_set = set([])

            func_args_scoped = []

            for a in range (0,len(func_argsList)):
                func_args_scoped.append(func_argsList[a] + "_" + str(self.cur_scope))
            self.local_vars_set = set(func_args_scoped)
            self.var = self.var+1
            func_def = 'fdef_'+ str(self.var)
            self.instr[func_def] = ['Function',func_name]
            self.prog_ord.append(func_def)

            [self.flatten(x,0) for x in ast.code.nodes]

            print "local vars:" + str(self.local_vars_set)
            print "all vars:" + str(self.all_vars_set)
            free_vars_list = list(self.all_vars_set - self.local_vars_set)
            print "free vars list: " + str(free_vars_list)

            #create list of free_vars
            free_vars_val_list = []
            free_vars_caller_list = []
            print self.prog_ord
            for y in range(0,len(free_vars_list)):
                fvl_unscoped = re.sub("_[a-zA-Z0-9]+","",free_vars_list[y]);
              #  fvl_re = fvl_re+ "_" + str(self.cur_scope)
                #check to see if it is already in the free var env
                if fvl_unscoped not in self.free_var_env_list:
                    #dont heapify if it exists
                    print "heapify var:" + str(fvl_unscoped)
                    self.free_var_env_list.append(fvl_unscoped)
                free_vars_val_list.append(fvl_unscoped)
                print self.prog_ord


            self.var = self.var+1
            func_args_fv = 'f_args_fv_'+ str(self.var)
            #move the instruction declaration above in the beginning of the function because it need to 
            #happen before the body of function is printed
            self.instr[func_args_fv] = ['Func_Args_FV',func_args_scoped,free_vars_list]  
            self.prog_ord.insert(1,func_args_fv)
                
            #Decrement Scope
            print "Decr Current Scope:" + str(self.cur_scope) + " Instr:" + str(self.instr)
            #store current scope dictionary before decrementing scope
            self.instr_scope_dict[self.cur_scope][1].update(copy.deepcopy(self.instr))
            #store current scope all/local vars before decremeneting scope
            self.instr_scope_dict[self.cur_scope][2].update(copy.deepcopy(self.all_vars_set))
            self.instr_scope_dict[self.cur_scope][3].update(copy.deepcopy(self.local_vars_set))
            self.instr_scope_dict[self.cur_scope][4] = copy.deepcopy(self.prog_ord)

            self.cur_scope = self.instr_scope_dict[self.cur_scope][0]
            #need to store
            self.instr = dict()
            self.prog_ord = []
            self.instr = self.instr_scope_dict[self.cur_scope][1]
            self.prog_ord = self.instr_scope_dict[self.cur_scope][4]
            print "Current Scope:" + str(self.cur_scope)

            #pick back current scope variables only after processing(calculating free vars)  the inner scope variables
            self.all_vars_set = self.instr_scope_dict[self.cur_scope][2]
            self.local_vars_set = self.instr_scope_dict[self.cur_scope][3]

            fvl_var = 'fvl_'+ str(self.var)
            self.instr[fvl_var] = ['Free_Var_List',free_vars_val_list]
            self.prog_ord.append(fvl_var) 
            self.instr[func_name] = ['Create_Closure',func_name,fvl_var]
            self.prog_ord.append(func_name)
            
            self.instr[func_name_scoped] = ['Assign',func_name]
            return func_name

        elif isinstance(ast, Lambda):
            self.var = self.var+1
            func_name = 'Lambda' + str(self.var)
            func_argsList = ast.argnames
          #  self.all_vars_set = set([])

             #Increment Scope
            print "Incr Current Scope:" + str(self.cur_scope) + " Instr:" + str(self.instr) + "Scope:" + str(self.local_vars_set)
            #store current scope dictionary before incrementing scope
            self.instr_scope_dict[self.cur_scope][1].update(copy.deepcopy(self.instr))
            #store current scope all/local vars before incremeneting scope
            self.instr_scope_dict[self.cur_scope][2].update(copy.deepcopy(self.all_vars_set))
            self.instr_scope_dict[self.cur_scope][3].update(copy.deepcopy(self.local_vars_set))
            self.instr_scope_dict[self.cur_scope][4] += copy.deepcopy(self.prog_ord)
            self.prev_scope  = self.cur_scope
            self.cur_scope = func_name
            if self.cur_scope not in self.instr_scope_dict:
                self.instr_scope_dict[self.cur_scope] = [self.prev_scope,dict(),set([]),set([]),[]]
            #reset dicts and vars
            self.instr = dict()
            self.prog_ord = []
            self.all_vars_set = set([])
            self.local_vars_set = set([])


            func_args_scoped = []
            for a in range (0,len(func_argsList)):
                func_args_scoped.append(func_argsList[a] + "_" + str(self.cur_scope))
            self.local_vars_set = set(func_args_scoped)
            self.var = self.var+1
            func_def = 'ldef_'+ str(self.var)
            self.instr[func_def] = ['Function',func_name]
            self.prog_ord.append(func_def)

            self.var = self.var+1
            temp_var = 't'+ str(self.var)
            ret_val = self.flatten(ast.code,0)
            self.instr[temp_var] = ['Return', ret_val]
            self.prog_ord.append(temp_var)

            print "local vars:" + str(self.local_vars_set)
            print "all vars:" + str(self.all_vars_set)
            free_vars_list = list(self.all_vars_set - self.local_vars_set)
            print "free vars list: " + str(free_vars_list)

            #create list of free_vars
            free_vars_val_list = []
            free_vars_caller_list = []
            print self.prog_ord
            for y in range(0,len(free_vars_list)):
                fvl_unscoped = re.sub("_[a-zA-Z0-9]+","",free_vars_list[y]);
              #  fvl_re = fvl_re+ "_" + str(self.cur_scope)
                #check to see if it is already in the free var env
                if fvl_unscoped not in self.free_var_env_list:
                    #dont heapify if it exists
                    print "heapify var:" + str(fvl_unscoped)
                    self.free_var_env_list.append(fvl_unscoped)
                free_vars_val_list.append(fvl_unscoped)
                print self.prog_ord


            self.var = self.var+1
            func_args_fv = 'f_args_fv_'+ str(self.var)
            #move the instruction declaration above in the beginning of the function because it need to 
            #happen before the body of function is printed
            self.instr[func_args_fv] = ['Func_Args_FV',func_args_scoped,free_vars_list]  
            self.prog_ord.insert(1,func_args_fv)
                
            #Decrement Scope
            print "Decr Current Scope:" + str(self.cur_scope) + " Instr:" + str(self.instr)
            #store current scope dictionary before decrementing scope
            self.instr_scope_dict[self.cur_scope][1].update(copy.deepcopy(self.instr))
            #store current scope all/local vars before decremeneting scope
            self.instr_scope_dict[self.cur_scope][2].update(copy.deepcopy(self.all_vars_set))
            self.instr_scope_dict[self.cur_scope][3].update(copy.deepcopy(self.local_vars_set))
            self.instr_scope_dict[self.cur_scope][4] = copy.deepcopy(self.prog_ord)

            self.cur_scope = self.instr_scope_dict[self.cur_scope][0]
            #need to store
            self.instr = dict()
            self.prog_ord = []
            self.instr = self.instr_scope_dict[self.cur_scope][1]
            self.prog_ord = self.instr_scope_dict[self.cur_scope][4]
            print "Current Scope:" + str(self.cur_scope)

            #pick back current scope variables only after processing(calculating free vars)  the inner scope variables
            self.all_vars_set = self.instr_scope_dict[self.cur_scope][2]
            self.local_vars_set = self.instr_scope_dict[self.cur_scope][3]

            fvl_var = 'fvl_'+ str(self.var)
            self.instr[fvl_var] = ['Free_Var_List',free_vars_val_list]
            self.prog_ord.append(fvl_var)                

            self.instr[func_name] = ['Create_Closure',func_name,fvl_var]
            self.prog_ord.append(func_name)

            return func_name

        elif isinstance(ast, Return):
            self.var = self.var+1
            temp_var = 't'+ str(self.var)
            ret_val = self.flatten(ast.value,is_func)
            self.instr[temp_var] = ['Return', ret_val];

            if (is_func):
                self.class_ord.append(temp_var)
            else:
                self.prog_ord.append(temp_var)            

            return temp_var 

        elif isinstance(ast, Class):   
            self.var = self.var+1
            temp_var = 'temp_class_'+ str(self.var)
            bases = ast.bases
            class_name = ast.name + "_" + str(self.cur_scope)
            self.local_vars_set = set([])
            self.all_vars_set = set([])
            self.instr[class_name] = ['Create_Class',bases]
            self.prog_ord.append(class_name)
            [self.flatten(x,0) for x in ast.code]
            print "local vars set:" + str(self.local_vars_set)  
            local_vars_list = list(self.local_vars_set)
            print "local vars list:" + str(local_vars_list)  
            for x in range (0,len(local_vars_list)):
                self.var = self.var+1
                temp_var2 = 'temp_set_attr_'+ str(self.var)
                if (local_vars_list[x] not in self.ascii_vars_label):
                    self.ascii_vars_label.append(local_vars_list[x])                    
                self.instr[temp_var2] = ['Set_Attribute',class_name,local_vars_list[x],self.instr[local_vars_list[x]][1]]   
                self.prog_ord.append(temp_var2)
#            self.instr[class_name] = temp_var 

        elif isinstance(ast, CallFunc):
            self.var = self.var+1
            temp_var = 't'+ str(self.var)
            func_name = self.flatten(ast.node,0)
            temp_list = 't'+ str(self.var) + '_list'
            self.instr[temp_list] = []

            for x in range ( 0,len(ast.args)):
                self.instr[temp_list].append(self.flatten(ast.args[x],is_func))

            print " The caller list length is:::::::::::::::::::" + str(len(ast.args))
            self.instr[temp_var] = ['CallFunc', func_name, temp_list];
            if (is_func):
                self.class_ord.append(temp_var)
            else:
                self.prog_ord.append(temp_var)
            return temp_var


        elif isinstance(ast,AssAttr):
            attr_name = ast.attrname + "_" + str(self.cur_scope)
            class_name = ast.expr.name + "_" + str(self.cur_scope)
            return[class_name,attr_name,'AssAttr']

        elif isinstance(ast,Getattr):
            self.var = self.var + 1
            temp_var = 't' + str(self.var)
            class_name = self.flatten(ast.expr, 0)
            attr_name = ast.attrname  + "_" + str(self.cur_scope)
            self.instr[temp_var] = ['Get_Attribute', class_name, attr_name] 
            self.prog_ord.append(temp_var)
            return temp_var

        elif isinstance(ast,If):
            self.var = self.var + 1
            temp_var = 't' + str(self.var)            
            cond = self.flatten(ast.tests[0][0])
            self.instr[temp_var] = ['IF_COND',cond]
            self.prog_ord.append(temp_var)
            [self.flatten(x,0) for x in ast.tests[0][1]]
            self.var = self.var + 1
            temp_var = 't' + str(self.var)         
            self.instr[temp_var] = ['ELSE_COND',cond]   
            self.prog_ord.append(temp_var)
            [self.flatten(x,0) for x in ast.else_]            
            
        
    def get_dict_key_from_instr_idx(self, idx):
        for k, v in self.instr.items():
            if self.instr[self.prog_ord[idx]] == v or isinstance(v, list) and self.instr[self.prog_ord[idx]] in v:
                #print k
                return k

    def get_dict_key_from_value(self, value):
        #print value
        for k,v in self.instr.items():
            if value == v or isinstance(v, list) and value in v:
                return k
        assert False


    def update_interference_graph(self,idx,live_vars_after_instr_set):
        old_node = 0
        var_name = self.get_dict_key_from_instr_idx(idx)
        for a in range ( 0, len(self.nodes)):
            if ( var_name == self.nodes[a].var_name):
                node_inst = self.nodes.pop(a)
                print "old node found:" + str(node_inst.var_name)
                old_node = 1
                break;

        if ( old_node == 0 ):
            node_inst = node()
            node_inst.var_name = self.get_dict_key_from_instr_idx(idx)

        instr = self.instr[self.prog_ord[idx]]

        #check for all the live variables, and update live call/add/uni oper var list
        #based on the instruction type so these variables don't get added to certain
        #registers.
        #special case for uni oper registers
        if (instr[0] == 'Assign' or instr[0] == 'UNeg' or instr[0] == 'Const'):
            print "adding uni oper to the node with name:" + node_inst.var_name
            for x in range(0, len(live_vars_after_instr_set)):
                self.vars_live_at_uni_oper_instr.append(list(live_vars_after_instr_set)[x])

        #special case for uni oper registers
        if (instr[0] == 'Add'):
            print "adding add to  the node with name:" + node_inst.var_name
            for x in range(0, len(live_vars_after_instr_set)):
                self.vars_live_at_add_instr.append(list(live_vars_after_instr_set)[x])

        #special case for caller-save registers
        if (instr[0] == 'Call' or instr[0] == 'Print'):
            print "adding caller to the node with name:" + node_inst.var_name
            for x in range(0, len(live_vars_after_instr_set)):
                self.vars_live_at_call_instr.append(list(live_vars_after_instr_set)[x])

        if (instr[0] == 'Const' or instr[0] == 'Add' or instr[0] == 'Assign' or instr[0] == 'UNeg' or instr[0] == 'Call' or instr[0] == 'Print'):
            for x in range(0, len(live_vars_after_instr_set)):
                if (list(live_vars_after_instr_set)[x] != node_inst.var_name):
                    node_inst.intf_nodes.append(list(live_vars_after_instr_set)[x])
            #search in the previous nodes if the current node has been added as neighbor,
            #if so, add that previous node as the current node's intf_node
            for y in range(0, len(self.nodes)):
                for z in range(0, len(self.nodes[y].intf_nodes)):
                    if ( self.nodes[y].intf_nodes[z] == node_inst.var_name):
                        node_inst.intf_nodes.append(self.nodes[y].var_name)

            #if a given variable is found in one of the live vars list, update the flag for the list appropriatly 
            for x in range(0, len(self.vars_live_at_call_instr)):
                if (self.vars_live_at_call_instr[x] == node_inst.var_name):
                    node_inst.is_live_at_call_instr = 1
                    self.vars_live_at_call_instr.pop(x)
                    break

            for x in range(0, len(self.vars_live_at_uni_oper_instr)):
                if (self.vars_live_at_uni_oper_instr[x] == node_inst.var_name):
                    node_inst.is_live_at_uni_oper_instr = 1
                    self.vars_live_at_uni_oper_instr.pop(x)
                    break

            for x in range(0, len(self.vars_live_at_add_instr)):
                if (self.vars_live_at_add_instr[x] == node_inst.var_name):
                    node_inst.is_live_at_add_instr = 1
                    self.vars_live_at_add_instr.pop(x)
                    break

            node_inst.neighbor_nodes_cnt = len(node_inst.intf_nodes)
            print 'printing node:' + node_inst.var_name
            print node_inst.display_node()
            self.nodes.append(node_inst)  
        
            
    def print_intf_graph(self):
        print "printing interference graph" 
        for x in range(0, len(self.nodes)):        
            print self.nodes[x].display_node()


    def update_nodes_degrees(self):
        temp_nodes_list = []
        temp_nodes_list = sorted(self.nodes, key=lambda x: (x.sat_deg,x.neighbor_nodes_cnt), reverse=True)
        self.nodes = temp_nodes_list
    #    self.print_intf_graph()

    def gen_live_var_analysis(self):
        live_vars_after_instr = []
        live_vars_before_instr = []
        live_vars_before_instr_set = set(live_vars_before_instr)
        live_vars_after_instr_set = set(live_vars_after_instr)
        vars_written = []
        vars_read = []

        for x in range(len(self.prog_ord), 0, -1):
            instr = self.instr[self.prog_ord[x-1]]
            if (instr[0] == 'Add'):
                vars_written.append(self.get_dict_key_from_instr_idx(x-1))
                vars_read.append(instr[1])
                vars_read.append(instr[2])                
            if (instr[0] == 'UNeg'):
                vars_read.append(instr[1]) 
                vars_written.append(self.get_dict_key_from_instr_idx(x-1))
            if (instr[0] == 'Assign'):
                vars_read.append(instr[1])
                vars_written.append(self.get_dict_key_from_instr_idx(x-1))
            if (instr[0] == 'Const'):
                vars_written.append(self.get_dict_key_from_instr_idx(x-1))
            if (instr[0] == 'Call'):
                vars_written.append(instr[1])
            if (instr[0] == 'Print'):
                vars_read.append(instr[1])                
            vars_read_set = set(vars_read)
            vars_written_set = set(vars_written)
            live_vars_before_instr_set = (live_vars_after_instr_set-vars_written_set) | vars_read_set
            print instr
            print live_vars_before_instr_set
            self.update_interference_graph(x-1,live_vars_after_instr_set)
            vars_read = []
            vars_written = []
            live_vars_after_instr_set = live_vars_before_instr_set


    def Const_Oper(self,operand,store_var):
        Const_Oper(self,operand,store_var)

    def Bool_Oper(self,operand,store_var):
        Bool_Oper(self,operand,store_var)    

    def Not_Oper(self,operand,store_var,x):
        Not_Oper(self,operand,store_var,x)    

    def Assign_Oper(self,operand,store_var):
        Assign_Oper(self,operand,store_var) 

    def Add_Oper(self,operand0,operand1,store_var,instr_idx):
        Add_Oper(self,operand0,operand1,store_var,instr_idx)

    def IfExp_Oper(self,condition,then,else_,store_var,instr_idx):
        IfExp_Oper(self,condition,then,else_,store_var,instr_idx)

    def Make_List(self,listLength,store_var):
        Make_List(self,listLength,store_var)

    def Make_Dict(self,store_var):
        Make_Dict(self,store_var)

    def List_Assign(self,key,val,py_obj_list):
        List_Assign(self,key,val,py_obj_list)

    def Dict_Assign(self,key,val,py_obj_list):
        Dict_Assign(self,key,val,py_obj_list)

    def GetBigVal_Oper(self,key,py_obj,store_var):
        GetBigVal_Oper(self,key,py_obj,store_var)

    def CmpEq_Oper(self,operand0,operand1,store_var,instr_idx):
        CmpEq_Oper(self,operand0,operand1,store_var,instr_idx)

    def CmpNeq_Oper(self,operand0,operand1,store_var,instr_idx):
        CmpNeq_Oper(self,operand0,operand1,store_var,instr_idx)

    def Is_Oper(self,operand0,operand1,store_var,instr_idx):
        Is_Oper(self,operand0,operand1,store_var,instr_idx)

    def UNeg_Oper(self,operand0,store_var):
        UNeg_Oper(self,operand0,store_var)

    def Print_Oper(self,operand0,store_var):
        Print_Oper(self,operand0,store_var)

    def Ret_Oper(self,operand0,store_var):
        Ret_Oper(self,operand0,store_var)

    def print_oper_instr(self,store_var):
        print_oper_instr(self,store_var)

    def Call_Func(self,func_name,arg_list,store_var,func_ptr,instr_idx):
        Call_Func(self,func_name,arg_list,store_var,func_ptr,instr_idx)

    def Print_Func(self,func_name,store_var):
        Print_Func(self,func_name,store_var)
    
    def Print_Input(self,store_var):
        Print_Input(self,store_var)
 
    def Create_Closure(self,func_name,fvl_ptr):
        Create_Closure(self,func_name,fvl_ptr)

    def Print_Var(self,var_name):
        Print_Var(self,var_name)

    def SetClassAttribute(self,class_name_pyobj,attr_name,expr_pyobj):
        SetClassAttribute(self,class_name_pyobj,attr_name,expr_pyobj)

    def GetClassAttribute(self,class_name_pyobj,attr_name,store_var,instr_idx):
        GetClassAttribute(self,class_name_pyobj,attr_name,store_var,instr_idx)    

    def Create_Class(self,py_obj_list_ptr,intmd_var):
        Create_Class(self,py_obj_list_ptr,intmd_var)

    def Get_First_Idx(self,idx,obj_ptr,store_var):
        Get_First_Idx(self,idx,obj_ptr,store_var)

    def Set_First_Idx(self,idx,obj_ptr,val,store_var):
        Set_First_Idx(self,idx,obj_ptr,val,store_var)

    def Print_Instructions(self,instr_list):
        Print_Instructions(self,instr_list)


    def generate_assembly(self):
        return  print_assembly(self)

    def my_color_graph(self):
        color_graph(self)
        

def py_compile(fn):
    assembly_fn = fn.split(".")[0] + ".s"

    with open(fn, 'r') as fh:
        ast = compiler.parseFile(fn)
        print ast
        #ast = ply_lex_parse.parse_file(fn)
        #print ast

    try:
        py_to_x86_inst = py_to_x86()
        py_to_x86_inst.flatten(ast,0)

        py_to_x86_inst.num_vars = len(py_to_x86_inst.prog_ord)
        #print py_to_x86_inst.prog_ord
        #print py_to_x86_inst.instr
#        py_to_x86_inst.gen_live_var_analysis()
#        py_to_x86_inst.my_color_graph()

        with open(assembly_fn, 'w') as fh:
            fh.write(py_to_x86_inst.generate_assembly())
    except SyntaxError as se:
        print "SyntaxError:", se


if __name__ == "__main__":
    for fn in sys.argv[1:]:
        py_compile(fn)
