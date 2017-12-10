; ModuleID = "/opt/pyyc-hellocompiler/hellocompiler/llvm_builder.pyc"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"() 
{
entry:
  %".2" = call i64 @"inject_bool"(i32 1)
  %".3" = call i32 @"is_true"(i64 %".2")
  %".4" = icmp ne i32 %".3", 0
  br i1 %".4", label %"entry.if", label %"entry.else"
entry.if:
  %".6" = call i64 @"inject_int"(i32 1)
  br label %"entry.endif"
entry.else:
  %".8" = call i64 @"inject_int"(i32 2)
  br label %"entry.endif"
entry.endif:
  %".10" = phi i64 [%".6", %"entry.if"], [%".8", %"entry.else"]
  call void @"print_any"(i64 %".10")
  ret i32 0
}

declare i64 @"inject_bool"(i32 %".1") 

declare i32 @"is_true"(i64 %".1") 

declare i64 @"inject_int"(i32 %".1") 

declare void @"print_any"(i64 %".1") 
