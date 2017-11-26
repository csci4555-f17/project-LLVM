class Register():
    def __init__(self):
        pass

    def __eq__(self,other):
        return str(self) == str(other) 

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)

class AL(Register):
    def __init__(self):
        self.value = "%al"

class EAX(Register):
    def __init__(self):
        self.value = "%eax"

class ECX(Register):
    def __init__(self):
        self.value = "%ecx"

class EDX(Register):
    def __init__(self):
        self.value = "%edx"

class EBX(Register):
    def __init__(self):
        self.value = "%ebx"

class ESI(Register):
    def __init__(self):
        self.value = "%esi"

class EDI(Register):
    def __init__(self):
        self.value = "%edi"

class EBP(Register):
    def __init__(self):
        self.value = "%ebp"

class OffsetEBP(EBP):
    def __init__(self, offset):
        self.offset = offset
        self.value = "{0}(%ebp)".format(-4*(offset+1))

class ESP(Register):
    def __init__(self):
        self.value = "%esp"

class ESPDeref(Register):
    def __init__(self, offset = None):
        if offset:
            self.value = "-%s(%esp)" % (4*offset)
        else:
            self.value = "(%esp)" 

def caller_save_registers():
    return [EAX(), ECX(), EDX()]

def all_usable_registers():
    return [EAX(), EBX(), ECX(), EDX(), ESI(), EDI()]
