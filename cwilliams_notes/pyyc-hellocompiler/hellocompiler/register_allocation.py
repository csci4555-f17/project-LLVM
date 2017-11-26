import x86_ir as ir
import registers 
import values_variables as vv

def except_key_error(f):
    try:
        f()
    except KeyError:
        pass

def handle_two_memory_locations(a,b):
    before_instructions = []
    after_instructions = []
    replace_var = a
    if isinstance(a, registers.EBP) and isinstance(b, registers.EBP):
        before_instructions += [ir.Push(registers.EAX()),
                               ir.Mov(a, registers.EAX())]
        after_instructions = [ir.Pop(registers.EAX())]
        replace_var = registers.EAX()
    return (replace_var, before_instructions, after_instructions)

def colorize_instructions(instructions, color_mapping, spill_var_count=0):
    new_instructions = []
    if spill_var_count > 0:
        new_instructions.append(ir.SubHeader(vv.Value(4*spill_var_count), registers.ESP()))

    for i in instructions:
        if isinstance(i, ir.Mov):
            if color_mapping.get(i.l, None):
                l = color_mapping[i.l]
            else:
                l = i.l
            if color_mapping.get(i.r, None):
                r = color_mapping[i.r]
            else:
                r = i.r
            # Don't write an instruction that does a nonsense move
            if not l == r:
                (n, b, a) = handle_two_memory_locations(l, r)
                new_instructions += b
                new_instructions.append(ir.Mov(n,r))
                new_instructions += a

        elif isinstance(i, ir.MovZB):
            if color_mapping.get(i.l, None):
                l = color_mapping[i.l]
            else:
                l = i.l
            if color_mapping.get(i.r, None):
                r = color_mapping[i.r]
            else:
                r = i.r
            # Don't write an instruction that does a nonsense move
            if not l == r:
                (n, b, a) = handle_two_memory_locations(l, r)
                new_instructions += b
                new_instructions.append(ir.MovZB(n,r))
                new_instructions += a

        elif isinstance(i, ir.ShiftLeft):
            if color_mapping.get(i.shift_by, None):
                shift_by = color_mapping[i.shift_by]
            else:
                shift_by = i.shift_by
            if color_mapping.get(i.reg, None):
                reg = color_mapping[i.reg]
            else:
                reg = i.reg
            (n, b, a) = handle_two_memory_locations(shift_by, reg)
            new_instructions += b
            new_instructions.append(ir.ShiftLeft(n, reg))
            new_instructions += a

        elif isinstance(i, ir.ShiftRight):
            if color_mapping.get(i.shift_by, None):
                shift_by = color_mapping[i.shift_by]
            else:
                shift_by = i.shift_by
            if color_mapping.get(i.reg, None):
                reg = color_mapping[i.reg]
            else:
                reg = i.reg
            (n, b, a) = handle_two_memory_locations(shift_by, reg)
            new_instructions += b
            new_instructions.append(ir.ShiftRight(n, reg))
            new_instructions += a

        elif isinstance(i, ir.Push):
            if color_mapping.get(i.register, None):
                register = color_mapping[i.register]
            else:
                register = i.register
            new_instructions.append(ir.Push(register))

        elif isinstance(i, ir.Add):
            if color_mapping.get(i.l, None):
                l = color_mapping[i.l]
            else:
                l = i.l
            if color_mapping.get(i.r, None):
                r = color_mapping[i.r]
            else:
                r = i.r
            (n, b, a) = handle_two_memory_locations(l, r)
            new_instructions += b
            new_instructions.append(ir.Add(n,r))
            new_instructions += a

        elif isinstance(i, ir.Cmp):
            if color_mapping.get(i.l, None):
                l = color_mapping[i.l]
            else:
                l = i.l
            if color_mapping.get(i.r, None):
                r = color_mapping[i.r]
            else:
                r = i.r
            (n, b, a) = handle_two_memory_locations(l, r)
            new_instructions += b
            new_instructions.append(ir.Cmp(n, r))
            new_instructions += a

        elif isinstance(i, ir.Neg):
            if color_mapping.get(i.v, None):
                v = color_mapping[i.v]
            else:
                v = i.v
            new_instructions.append(ir.Neg(v))

        elif isinstance(i, ir.JmpEq):
            new_instructions.append(i)

        elif isinstance(i, ir.Jmp):
            new_instructions.append(i)

        elif isinstance(i, ir.Label):
            new_instructions.append(i)

        elif isinstance(i, ir.CallFunc):
            new_instructions.append(i)

        elif isinstance(i, ir.CallStar):
            if color_mapping.get(i.fname, None):
                fname = color_mapping[i.fname]
            else:
                fname = i.fname
            new_instructions.append(ir.CallStar(fname))

        elif isinstance(i, ir.Print):
            new_instructions.append(ir.Print())

        elif isinstance(i, ir.Input):
            new_instructions.append(ir.Input())

        elif isinstance(i, ir.SetE):
            new_instructions.append(i)

        elif isinstance(i, ir.SetNE):
            new_instructions.append(i)

        elif isinstance(i, ir.IfExp):
            if color_mapping.get(i.test_var, None):
                i.test_var = color_mapping[i.test_var]

            i.test_instructions = colorize_instructions(i.test_instructions, color_mapping)
            i.then = colorize_instructions(i.then, color_mapping)
            i.else_ = colorize_instructions(i.else_, color_mapping)
            new_instructions.append(i)

        else:
            raise Exception("instruction type %s not supported" % i.__class__.__name__)

    return new_instructions
