; ModuleID = "/opt/pyyc-hellocompiler/hellocompiler/llvm_builder.pyc"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"() 
{
entry:
  %".2" = call i64 @"inject_int"(i32 5)
  call void @"print_any"(i64 %".2")
  ret i32 0
}

declare i64 @"inject_int"(i32 %".1") 

declare void @"print_any"(i64 %".1") 
