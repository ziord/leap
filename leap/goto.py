"""
:copyright: Copyright (c) 2020 Jeremiah Ikosin (@ziord)
:license: MIT, see LICENSE for more details
"""

import dis
import types
import warnings
from collections import OrderedDict
from typing import List, Union

__all__ = (
    'goto', 'LabelLimitError',
    'LabelNotFoundError', 'GotoLimitError',
    'DuplicateLabelError')


class GotoError(Exception):
    ...


class LabelNotFoundError(GotoError):
    ...


class LabelLimitError(GotoError):
    ...


class GotoLimitError(GotoError):
    ...


class DuplicateLabelError(GotoError):
    ...


class Inst:
    """
    lightweight instruction object
    """

    def __init__(self, index, opcode, arg, offset):
        self.index = index
        self.opcode = opcode
        self.arg = arg
        self.offset = offset

    def update(self, index=None, opcode=None, arg=None, offset=None):
        if index is not None:
            self.index = index
        if opcode is not None:
            self.opcode = opcode
        if arg is not None:
            self.arg = arg
        if offset is not None:
            self.offset = offset


class ByteConstruct:
    """
    base class for label and goto statements
    """

    def __init__(self, name):
        self.instruction_set: [Inst] = []
        self._name = name

    def add(self, inst: Inst) -> None:
        self.instruction_set.append(inst)

    @property
    def iset(self) -> List:
        return self.instruction_set

    @iset.setter
    def iset(self, new_iset) -> None:
        self.instruction_set = new_iset

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, n) -> None:
        self._name = n


class Label(ByteConstruct):
    """
    label statement/instruction
    """

    def __init__(self, name, nvi, *cd):
        ByteConstruct.__init__(self, name)
        self.__next_valid_instruction = nvi
        for inst in cd:
            self.add(inst)

    @property
    def next_vi(self):
        """
        next valid instruction, after a goto/label instruction
        :return: dis.Instruction object
        """
        return self.__next_valid_instruction

    @next_vi.setter
    def next_vi(self, next_vld_cd):
        """
        set next valid instruction, after a goto/label instruction
        """
        self.__next_valid_instruction = next_vld_cd


class Goto(ByteConstruct):
    """
    Goto statement/instruction
    """

    def __init__(self, name=None, *cd):
        ByteConstruct.__init__(self, name)
        for inst in cd:
            self.add(inst)


class GotoCompiler:

    def __init__(self, fn, debug=False, lmc=None, gmc=None):
        self.__func = fn
        self._code = fn.__code__
        self._labels = OrderedDict()  # Label
        self._gotos = []  # Goto
        self._instructions: [Union[dis.Instruction, Inst]] = self.get_instructions()
        self._debug = debug
        self._label_max_cap = lmc if lmc else 10
        self._goto_max_cap = gmc if gmc else 8

    @property
    def instructions(self):
        """
        function instructions list for GotoCompiler
        """
        return self._instructions

    @property
    def func(self):
        """
        gets self.__func/function to be processed
        :return: self.__func
        """
        return self.__func

    @func.setter
    def func(self, fn):
        """
        sets self.__func/function to be processed
        """
        self.__func = fn

    @property
    def keywords(self):
        """
        goto/label keywords
        """
        return ['goto', 'label']

    def show_instructions(self):
        """
        Show all bytecode instructions for self.__func
        """
        for inst in dis.get_instructions(self.func):
            print(inst)
        print()
        dis.dis(self.func)
        return

    def get_instructions(self) -> [dis.Instruction]:
        """
        get all bytecode instructions for self.__func
        """
        insts = []
        list(map(lambda x: insts.append(x), dis.get_instructions(self.func)))
        return insts

    @staticmethod
    def _create_inst(index, opcode, arg, offset):
        """
        create a lightweight instruction object
        """
        return Inst(index, opcode, arg, offset)

    def create_instruction(self, index, instruction: dis.Instruction):
        """
        create a lightweight instruction for a given Instruction object
        """
        return self._create_inst(index, instruction.opcode, instruction.arg, instruction.offset)

    def create_instructions(self, indexes, *instructions: (dis.Instruction,)):
        """
        create series of instructions for a tuple of Instruction objects
        """
        insts: [Inst] = []
        for i, inst in enumerate(instructions):
            insts.append(self.create_instruction(indexes[i], inst))
        return insts

    def find_next_valid(self, insts):
        """
        Get the next valid instruction in a list of Instruction objects
        """
        # TODO: ...
        prev_inst = None
        ind = 0
        for i, inst in enumerate(insts):
            if inst.argval not in self.keywords:
                if prev_inst and prev_inst.argval in self.keywords:
                    ind += 1
                    if ind == 2:
                        prev_inst = inst
                        ind >>= 2
                else:
                    return inst  # next valid bytecode instruction
            else:
                prev_inst = inst

    def extract_instructions(self, flag):
        """
        add all instructions in the iset of each Label or Goto object to a list and return
        """
        inst_s = []
        if flag == 'l':
            for _name, label_inst in self._labels.items():
                inst_s.extend(label_inst.iset)
        elif flag == 'g':
            for goto_inst in self._gotos:
                inst_s.extend(goto_inst.iset)
        return inst_s

    def _create_code(self):
        """
        create bytecode
        """
        # use labels and gotos in creating a list of bytecode
        label_instructions = self.extract_instructions('l')
        goto_instructions = self.extract_instructions('g')

        # replace all original label instructions with the modified
        # label instructions
        for lb_inst in label_instructions:
            index = lb_inst.index
            self.instructions[index] = lb_inst

        # replace all original goto instructions with the modified
        # goto instructions
        for gt_inst in goto_instructions:
            index = gt_inst.index
            self.instructions[index] = gt_inst

        # we obtain the bytecode by extracting the important/needed info
        # from all available instructions
        bytecode = []
        for inst in self.instructions:
            arg = 0 if inst.arg is None else inst.arg
            bytecode.extend([inst.opcode, arg])
        return bytes(bytecode)

    def validate(self):
        """
        validate the accrued label/goto instructions
        """
        if len(self._labels) > self._label_max_cap:
            raise LabelLimitError(f"Too many labels in function. Max allowed: {self._label_max_cap}")
        elif len(self._labels) == self._label_max_cap:
            warnings.warn(f"Number of labels used equals maximum allowed ({self._label_max_cap}).")
        if len(self._gotos) > self._goto_max_cap:
            raise GotoLimitError(f"Too many gotos in function. Max allowed: {self._goto_max_cap}")
        elif len(self._gotos) == self._goto_max_cap:
            warnings.warn(f"Number of gotos used equals maximum allowed. ({self._goto_max_cap})")

    def __update_goto(self, goto_obj: Goto):
        """
        update a Goto's iset (list containing goto instruction set)
        """
        label_obj: Label = self._labels.get(goto_obj.name)
        if not label_obj:
            raise LabelNotFoundError(f"Label `{goto_obj.name}` was not found.")
        #
        goto_index, goto_offset = goto_obj.iset[0].index, goto_obj.iset[0].offset
        label_offset = label_obj.iset[0].offset
        is_forward = label_offset > goto_offset
        #
        ops = [0x71, 0x6e, 0x09]  # ABS, FWD, NOP
        # modify goto instruction set and its offset
        if is_forward:
            # the jmp offset for a forward jump (FWD)  =>
            # diff of the goto instruction's offset and the next valid instruction's offset.
            # -2 is due to a python thing for FWD
            arg = label_obj.next_vi.offset - goto_offset - 2
            opcode = ops[1]
        else:
            # the jmp offset for a backward jump (JMP ABS) =>
            # exactly the next valid instruction (after the label) offset
            arg = label_obj.next_vi.offset
            opcode = ops[0]
        offset = goto_offset

        # replace the first instruction in the Goto object's iset (load global) with
        # a new (jmp) instruction
        goto_obj.iset[0] = self._create_inst(goto_index, opcode, arg, offset)

        # change the remaining insts (load attr, pop top) in the Goto object's iset to NOP
        for inst in goto_obj.iset[1:]:
            opcode = ops[-1]
            arg = 0
            inst.update(opcode=opcode, arg=arg)

    @staticmethod
    def __update_label(label_obj: Label):
        """
        update label_obj's iset
        """
        # turn the instructions to a NOP
        for inst in label_obj.iset:
            arg = 0
            opcode = 0x09  # NOP
            inst.update(arg=arg, opcode=opcode)

    def duplicate_error(self, duplicate):
        """
        raise Exception when duplicate label declarations are found
        """
        raise DuplicateLabelError(f"Duplicate labels found: `{duplicate}`")

    def update_gotos(self):
        """
        update all Goto objects in self._gotos
        """
        for goto_obj in self._gotos:
            self.__update_goto(goto_obj)

    def update_labels(self):
        """
        update all Label objects in self._labels
        """
        for _label_name, label_obj in self._labels.items():
            self.__update_label(label_obj)

    def _update_func(self, bytecode: [int]):
        """
        update self.func's bytecode (self.func.__code__.co_code)
        """
        if self._debug:
            print('Disassembly of old instructions:')
            print('--------------------------------')
            self.show_instructions()
        #
        new_code = types.CodeType(
            self._code.co_argcount,
            self._code.co_kwonlyargcount,
            self._code.co_nlocals,
            self._code.co_stacksize,
            self._code.co_flags,
            bytecode,
            self._code.co_consts,
            self._code.co_names,
            self._code.co_varnames,
            self._code.co_filename,
            self._code.co_name,
            self._code.co_firstlineno,
            self._code.co_lnotab,
            self._code.co_freevars,
            self._code.co_cellvars
        )
        self.func.__code__ = new_code
        if self._debug:
            print('Disassembly of new instructions:')
            print('--------------------------------')
            self.show_instructions()

    def compile_func(self):
        """
        recompile self.func, editing its bytecode
        """
        _L_G = 0x74
        for i, inst in enumerate(self.instructions):
            if inst.opcode == _L_G and inst.argval == self.keywords[1]:  # label
                _l_g = inst  # load global
                _l_a = self.instructions[i + 1]  # load attr
                _p_t = self.instructions[i + 2]  # pop top
                _name = _l_a.argval
                _next_index = i + 3  # + ( load global, load attr, pop top )
                _next_valid_instruction = self.find_next_valid(self.instructions[_next_index:])
                if self._labels.get(_name):
                    self.duplicate_error(_name)
                self._labels[_name] = Label(
                    _name,
                    self.create_instruction(i, _next_valid_instruction),
                    *self.create_instructions([i, i + 1, i + 2], _l_g, _l_a, _p_t)
                )
            elif inst.opcode == _L_G and inst.argval == self.keywords[0]:  # goto
                _l_g = inst  # load global
                _l_a = self.instructions[i + 1]  # load attr
                _p_t = self.instructions[i + 2]  # pop top
                _name = _l_a.argval
                _goto = Goto(
                    _name,
                    *self.create_instructions([i, i + 1, i + 2], _l_g, _l_a, _p_t)
                )
                self._gotos.append(_goto)
        # empty
        if not self._gotos and not self._labels:
            return self.func

        self.validate()
        if self._debug:
            print('Function name:')
            print('--------------')
            print(self.func.__name__)
            print('\nFully qualified name:')
            print('---------------------')
            (
                print(self.func.__qualname__)
                if hasattr(self.func, '__qualname__')
                else print(self.func.__name__)
            )

        # update all
        self.update_gotos()
        self.update_labels()

        new_bc = self._create_code()
        if self._debug:
            old_bc = list(self.func.__code__.co_code)
            print('\nOld bytecode:')
            print('--------------')
            print(old_bc)
            print()
            print('New bytecode:')
            print('--------------')
            print(list(new_bc))
        self._update_func(new_bc)
        return self.func


def goto(__f=None, *, debug=False, max_labels=None, max_gotos=None):
    """
    decorator function for processing functions with goto statements,
    handles argument calls and non-argument calls
    :param __f: function to be compiled if available
    :param debug: flag to log inner processes
    :param max_labels: maximum number of labels allowed in a function
    :param max_gotos: maximum number of gotos allowed in a function
    :return:
    """

    # for use cases such as:
    # @goto(...)
    # def func():
    #   pass
    def __apply(func):
        processor = GotoCompiler(func, debug, max_labels, max_gotos)
        function = processor.compile_func()
        return function

    # for use cases such as:
    # @goto
    # def func():
    #   pass
    if __f is not None and hasattr(__f, "__code__"):
        compiler = GotoCompiler(__f)
        fn = compiler.compile_func()
        return fn
    return __apply
