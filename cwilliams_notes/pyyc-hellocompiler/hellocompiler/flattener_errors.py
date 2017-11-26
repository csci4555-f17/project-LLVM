DocError = SyntaxError("Module documentation not supported in P_0")
MultipleAssignmentError = SyntaxError("Multiple variable assignment not supported in P_0")
OPAssignError = SyntaxError("Variable assignment only supports 'OP_ASSIGN' in P_0")
IntegersOnlyError = SyntaxError("only integer literals are supported")
UndefinedVariableError = SyntaxError("Usage of undefined variable")
MultiplePrintError = SyntaxError("Printing of multiple values not supported in P_0")
PrintingOutputError = SyntaxError("Only printing to stdout is supported in P_0")
UnsupportedFuncError = SyntaxError("Only 'input' function suported in P_0")
ArgsError = SyntaxError("Arguments to 'input' not supported in P_0")
def UnsupportedError(node):
    return SyntaxError("instance of %s not supported in P_0" % node)
