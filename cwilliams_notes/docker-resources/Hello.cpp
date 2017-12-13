//===- Hello.cpp - Example code from "Writing an LLVM Pass" ---------------===//
//
//                     The LLVM Compiler Infrastructure
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//
//
// This file implements two versions of the LLVM "Hello World" pass described
// in docs/WritingAnLLVMPass.html
//
//===----------------------------------------------------------------------===//
#include "llvm/ADT/Statistic.h"
#include "llvm/IR/Function.h"
#include "llvm/Pass.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/Value.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/Use.h"
#include <string.h>
using namespace llvm;

#define DEBUG_TYPE "hello"

STATISTIC(HelloCounter, "Counts number of functions greeted");

namespace {

  Value* is_inject_int(Value *v) {
    if (isa<CallInst>(v)) {
      Value *calledFunc = cast<CallInst>(v)->getCalledValue();
      StringRef calledFuncName = calledFunc->getName();
      if (strcmp(calledFuncName.str().c_str(), "inject_int") == 0) {
	return calledFunc;
      }
    }
    return nullptr;
  }
  
  bool operand_is_constant(CallInst *ci) {
    Value *op0 = ci->getArgOperand(0);
    return isa<ConstantInt>(op0);
  }
  
  int64_t get_constant_val(CallInst *ci) {
    Value *op0 = ci->getArgOperand(0);
    return cast<ConstantInt>(op0)->getSExtValue();
  }

  // Hello - The first implementation, without getAnalysisUsage.
  struct Hello : public FunctionPass {
    static char ID; // Pass identification, replacement for typeid
    Hello() : FunctionPass(ID) {}

    bool runOnFunction(Function &F) override {
      // Iterate over each block in the function
      for (auto &B : F) {
	// Iterate over each instruction in the block
        for (auto &I : B) {
	  // If the instruction is a CallInst type. In other words is this instruction
          // calling a fucntion
	  if (isa<CallInst>(I)) {
	    Value *calledFunc = cast<CallInst>(I).getCalledValue();
	    StringRef calledFuncName = calledFunc->getName();
            // Is this instruction making a call to the 'llvm_runtime_add' function
	    if (strcmp(calledFuncName.str().c_str(), "llvm_runtime_add") == 0) {
	      // Get each argument passed to the 'llvm_runtime_add' function
	      Value *op0 = cast<CallInst>(I).getArgOperand(0);
	      Value *op1 = cast<CallInst>(I).getArgOperand(1);
	      // Are each of the aguments a call to the 'inject_int' function
              if(is_inject_int(op0) && is_inject_int(op1)) {
                // Are each of the inject_int calls being called on a constant
		if (operand_is_constant(cast<CallInst>(op0)) && 
		    operand_is_constant(cast<CallInst>(op0))) {
                  // We can remove the llvm_runtime_add function because we can 
                  // just add the integers at compile time
		  int64_t lhs = get_constant_val(cast<CallInst>(op0));
		  int64_t rhs = get_constant_val(cast<CallInst>(op1));
		  int64_t sum = lhs + rhs;
                  // TODO: Add the new instruction
		  IRBuilder<> builder(I*);
		  errs() << "Both constant! Total is: " << sum << '\n';
		}
		
	      }
	      errs() << "llvm_runtime_add\n";
	    }
	  }
      	  ++HelloCounter;
        }
      }
      return false;
    }
  };
}

char Hello::ID = 0;
static RegisterPass<Hello> X("hello", "Hello World Pass");

namespace {
  // Hello2 - The second implementation with getAnalysisUsage implemented.
  struct Hello2 : public FunctionPass {
    static char ID; // Pass identification, replacement for typeid
    Hello2() : FunctionPass(ID) {}

    bool runOnFunction(Function &F) override {
      ++HelloCounter;
      errs() << "Hello: ";
      errs().write_escaped(F.getName()) << '\n';
      return false;
    }

    // We don't modify the program, so we preserve all analyses.
    void getAnalysisUsage(AnalysisUsage &AU) const override {
      AU.setPreservesAll();
    }
  };
}

char Hello2::ID = 0;
static RegisterPass<Hello2>
Y("hello2", "Hello World Pass (with getAnalysisUsage implemented)");
