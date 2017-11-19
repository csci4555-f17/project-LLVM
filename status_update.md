Status Update
Megan Greening, Kathy Grimes, Aniq Shahid, and Colton Williams

Progress Up To Now:
So far we have been looking into LLVM to get an understanding of how it works and how to write code with it. As with most projects, finding the correct installations and getting things set up takes time. We are all working on this independently with the goal of comparing notes after HW6 to get on the same page. In particular, up to this point, Aniq has the clang LLVM module and LLVMPY library installed. He is working on verifying that LLVMPY works correctly, as well as reading up on LLVM IR constructs as it will be instrumental in understanding the code optimizations. Colton has made some initial progress on generating IR from Python code. Kathy and Megan have been more focused on the literature search. Megan has downloaded the LLVMPY library but has not yet verified that it is working correctly. Both pairs of partners are also working to complete the language implementations in the homework assignments, as these will serve as baseline comparisons to our LLVM implementations.

We have also continued to work on literature searches. Some summaries of papers can be found at this end of this update. We have probably not completed the literature search and will update this as we find additional papers of note. We have not yet settled on the type of optimizations we might wish to extend the P0-3 languages with. Further literature searches will guide us in our plans.

Future Plans:
1) Get the appropriate LLVM packages installed and running on all of our computers. This is already in progress.
2) Finish reviewing any LLVM documentation we may need to get started. This is in progress and will be ongoing as we work on the implementation, but we also need to be sure we have a strong understanding before getting underway.
3) Continue literature search for relevant topics.
4) Create LLVM implementation of P0.
5) Create LLVM implementation of P1.
6) Create LLVM implementation of P2.
7) Create LLVM implementation of P3.
9)Add additional new optimizations to the implementation.
*Note that each of the above steps will be doing some testing and analysis to see what the optimizations do and how they improve the programs. 

Literature Searches:
LLVM: AN INFRASTRUCTURE FOR MULTI-STAGE OPTIMIZATION
This is the original thesis that introduced LLVM. Lattner saw a problem with the traditional approaches used in compilation and wanted to develop something that would be faster. LLVM is a multi-stage system and is meant to be good enough for use in commercial applications. The thesis outlines the features of LLVM very clearly, but is mostly useful from a theoretical point of view and for basic background.

LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation
This paper by Lattner and Adve provides further information about LLVM. The main goal of LLVM is to allow for lifetime optimizations of programs that can be run at various times during the compilation and running of a program. LLVM also allows for optimizations to be streamlined even when multiple languages contributed to a given program.

The LLVM Compiler Framework and Infrastructure Tutorial
This is an extensive document that details how to use LLVM, as well as providing background that is more practical than theoretical.

Ocelot: A Dynamic Optimization Framework for Bulk-Synchronous Applications in Heterogeneous Systems
Ocelot is a compilation framework that uses LLVM to accomplish more efficient parallel processes. While interesting, this particular paper probably will not end up being of great use to our project.