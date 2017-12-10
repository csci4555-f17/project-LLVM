; ModuleID = "/opt/pyyc-hellocompiler/hellocompiler/llvm_builder.pyc"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"() 
{
entry:
  %".2" = call i64 @"inject_int"(i32 1)
  %".3" = call i64 @"inject_int"(i32 2)
  %".4" = call i64 @"llvm_runtime_add"(i64 %".2", i64 %".3")
  %".5" = call i64 @"inject_int"(i32 3)
  %".6" = call i64 @"llvm_runtime_add"(i64 %".4", i64 %".5")
  call void @"print_any"(i64 %".6")
  ret i32 0
}

declare i64 @"inject_int"(i32 %".1") 

declare i32 @"is_int"(i64 %".1") 

declare i32 @"is_bool"(i64 %".1") 

declare i32 @"is_true"(i64 %".1") 

declare i64 @"inject_bool"(i32 %".1") 

declare i32 @"project_bool"(i64 %".1") 

declare i32 @"project_int"(i64 %".1") 

declare i64 @"inject_big"(i64 %".1") 

declare i64 @"project_big"(i64 %".1") 

declare i64 @"add"(i64 %".1", i64 %".2") 

declare i64 @"negate"(i64 %".1") 

define i64 @"llvm_runtime_add"(i64 %".1", i64 %".2") 
{
entry:
  %".4" = call i32 @"is_int"(i64 %".1")
  %".5" = call i64 @"inject_bool"(i32 %".4")
  %".6" = call i32 @"is_true"(i64 %".5")
  %".7" = icmp ne i32 %".6", 0
  br i1 %".7", label %"entry.if", label %"entry.else"
entry.if:
  %".9" = call i32 @"project_int"(i64 %".1")
  %".10" = call i32 @"project_int"(i64 %".2")
  %".11" = add i32 %".9", %".10"
  %".12" = call i64 @"inject_int"(i32 %".11")
  ret i64 %".12"
entry.else:
  %".14" = call i32 @"is_bool"(i64 %".1")
  %".15" = call i64 @"inject_bool"(i32 %".14")
  %".16" = call i32 @"is_true"(i64 %".15")
  %".17" = icmp ne i32 %".16", 0
  br i1 %".17", label %"entry.else.if", label %"entry.else.else"
entry.endif:
  ret i64 0
entry.else.if:
  %".19" = call i32 @"project_bool"(i64 %".1")
  %".20" = call i32 @"project_bool"(i64 %".2")
  %".21" = add i32 %".19", %".20"
  %".22" = call i64 @"inject_int"(i32 %".21")
  ret i64 %".22"
entry.else.else:
  %".24" = call i64 @"project_big"(i64 %".1")
  %".25" = call i64 @"project_big"(i64 %".2")
  %".26" = call i64 @"add"(i64 %".24", i64 %".25")
  %".27" = call i64 @"inject_big"(i64 %".26")
  ret i64 %".27"
entry.else.endif:
  br label %"entry.endif"
}

declare void @"print_any"(i64 %".1") 
