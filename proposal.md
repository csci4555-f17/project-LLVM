1. Who are the members of your team?
Megan Greening, Kathy Grimes, Aniq Shahid, and Colton Williams
Note: Three of us are distance students and one is an on campus student, so we need to discuss the final presentation with Professor Chang.


2. What basic problem will your project try to solve?
Our team would like to develop a P0 front-end for the LLVM compiler library. More specifically, we are thinking about transforming P0 language into an AST, or some other form, which can then interface with LLVM IR building APIs to generate LLVM optimized code. Permitting time and resources, we will expand the idea to P1 and P2 languages, and also look into LLVM optimizations specific to these languages.


3. Define the problem that you will solve as concretely as possible. Provide a scope of expected and potential results. Give a few example programs that exhibit the problem that you are trying to solve.
Explore novel techniques for implementing a given language fragment (from the course website).

We are interested in exploring the use of LLVM and getting a sense for its optimizations. We would like to compare optimization from LLVM with both a compiler that has no optimizations (the compiler from homework 1) and one with some optimizations (the compiler from homework 3) to see how compile speeds and register usage are improved with LLVM. As time permits, we will add in further language features and test further optimizations.

We have a fairly strong implementation plan, in that we would like to use the LLVM with the P0 (and further) language from class. In terms of the research aspect of the project, we are still exploring options. Of note is that C/C++ are well covered in LLVM, but Python is not. By developing this framework more we may be able to contribute to the LLVM project. It may be possible to take the LLVM IR, do some manipulations to that IR, and then see how the output is impacted by this. This would allow us to take our work a step further by adjusting the optimizations that LLVM already has.


4. What is the general approach that you intend to use to solve the problem?
We do not currently have timeline associated with these phases, and the details will most likely change as we continue to refine our research questions. However, this is an outline of our current plan - details will be added as we proceed.

Phase 0:
-Our compiler (no changes)
-A basic compiler using LLVM to familiarize us with the system

Phase 1:
-Use compiler.parse to get a python AST
-Pass python AST to LLVM IR and get LLVM x86
	-This should be the complete LLVM version of P0

Phase 2:
-Change to using our own x86 translation from the optimized LLVM IR instead of the LLVM x86
-Do analysis to assess quality of improvements using LLVM

Phase 3
-Extend language to include P1, then P2, and finally P3

Phase 4
-Add new optimizations and test their performance
-Example: use the linear algebra library (BLAS) to replace replace some LLVM instructions, hopefully improving compilation speed


5. Why do you think that approach will solve the problem? What resources (papers, book chapters, etc.) do you plan to base your solution on? Is there one in particular that you plan to follow? What about your solution will be similar? What will be diﬀerent?

Lattner and Adve’s original work on LLVM will be crucial to understanding how LLVM works and how we can use it. Their paper will largely serve to provide background information and knowledge.

Initially we will be exploring the use of LLVM and the small subsets of Python used in class, so we will not necessarily be following any existing approaches very closely. Since there are limited LLVM libraries related to Python, we may take inspiration from the non-Python versions, but our specific implementations may be varied.

Current citations:
-Lattner, Chris. LLVM: An Infrastructure for Multi-Stage Optimization. University of Portland. 2002.
-Chris Lattner and Vikram Adve. 2004. LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation. In Proceedings of the international symposium on Code generation and optimization: feedback-directed and runtime optimization (CGO '04). IEEE Computer Society, Washington, DC, USA, 75-. 
-Jianzhou Zhao, Santosh Nagarakatte, Milo M.K. Martin, and Steve Zdancewic. 2012. Formalizing the LLVM intermediate representation for verified program transformations. In Proceedings of the 39th annual ACM SIGPLAN-SIGACT symposium on Principles of programming languages (POPL '12). ACM, New York, NY, USA, 427-440. DOI: https://doi.org/10.1145/2103656.2103709 



6. How do you plan to demonstrate your idea? Will you use your course compiler. If so, what specific changes do you plan to make to it (e.g., what passes need to be changed or added)?
We plan to use the course compiler as a starting point and a baseline. We plan to update it using LLVM IR and other optimizations. The specific phases we hope to implement are outlined under question 4.


7.How will you evaluate your idea? What will be the measurement for success?
We will check our work by making sure that any updated and optimized version of the compiler produces the same output as the baseline compiler. Correctness will always be the first thing we need to establish. At each phase we will also analyze the time it takes for each version of the compiler to run. We would also like to consider the specific nature of the optimizations we produce. For the subset of the language we are studying, some optimizations may not improve the time very much. However, they might prove better for more complex languages subsets.

We will also alter the metrics based on any research papers we find that are in line with our project. Other was to measure success may become clearer as we delve into those papers more.
