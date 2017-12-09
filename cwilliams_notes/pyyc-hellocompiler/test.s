	.text
	.file	"llvm-link"
	.globl	main                    # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# BB#0:                                 # %entry
	pushq	%rbx
.Lcfi0:
	.cfi_def_cfa_offset 16
.Lcfi1:
	.cfi_offset %rbx, -16
	movl	$1, %edi
	callq	inject_int
	movq	%rax, %rbx
	movl	$1, %edi
	callq	inject_int
	movq	%rbx, %rdi
	movq	%rax, %rsi
	callq	llvm_runtime_add
	movq	%rax, %rdi
	callq	print_any
	xorl	%eax, %eax
	popq	%rbx
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.globl	llvm_runtime_add        # -- Begin function llvm_runtime_add
	.p2align	4, 0x90
	.type	llvm_runtime_add,@function
llvm_runtime_add:                       # @llvm_runtime_add
	.cfi_startproc
# BB#0:                                 # %entry
	pushq	%r14
.Lcfi2:
	.cfi_def_cfa_offset 16
	pushq	%rbx
.Lcfi3:
	.cfi_def_cfa_offset 24
	pushq	%rax
.Lcfi4:
	.cfi_def_cfa_offset 32
.Lcfi5:
	.cfi_offset %rbx, -24
.Lcfi6:
	.cfi_offset %r14, -16
	movq	%rsi, %r14
	movq	%rdi, %rbx
	callq	is_int
	movl	%eax, %edi
	callq	inject_bool
	movq	%rax, %rdi
	callq	is_true
	testl	%eax, %eax
	je	.LBB1_4
# BB#1:                                 # %entry.if
	movq	%rbx, %rdi
	callq	project_int
	movl	%eax, %ebx
	movq	%r14, %rdi
	callq	project_int
	jmp	.LBB1_2
.LBB1_4:                                # %entry.else
	movq	%rbx, %rdi
	callq	is_bool
	movl	%eax, %edi
	callq	inject_bool
	movq	%rax, %rdi
	callq	is_true
	movq	%rbx, %rdi
	testl	%eax, %eax
	je	.LBB1_6
# BB#5:                                 # %entry.else.if
	callq	project_bool
	movl	%eax, %ebx
	movq	%r14, %rdi
	callq	project_bool
.LBB1_2:                                # %entry.if
                                        # kill: %EAX<def> %EAX<kill> %RAX<def>
	leal	(%rax,%rbx), %edi
	callq	inject_int
.LBB1_3:                                # %entry.if
	addq	$8, %rsp
	popq	%rbx
	popq	%r14
	retq
.LBB1_6:                                # %entry.else.else
	callq	project_big
	movq	%rax, %rbx
	movq	%r14, %rdi
	callq	project_big
	movq	%rbx, %rdi
	movq	%rax, %rsi
	callq	add
	movq	%rax, %rdi
	callq	inject_big
	jmp	.LBB1_3
.Lfunc_end1:
	.size	llvm_runtime_add, .Lfunc_end1-llvm_runtime_add
	.cfi_endproc
                                        # -- End function

	.section	".note.GNU-stack","",@progbits
