from __future__ import print_function

from itertools import imap, chain
from operator import methodcaller
from collections import Counter

from pyparsing import (
    Literal,
    ZeroOrMore,
    OneOrMore,
    Forward,
    Group,
    Empty
)


class Operation(object):
    pass


class MemoryOperation(Operation):
    def __init__(self, operations):
        count = Counter(operations)
        self.diff = count['+'] - count['-']


class PointerOperation(Operation):
    def __init__(self, operations):
        pass


class IOOperation(Operation):
    pass


def memory_operation_compile(memory_operations):
    count = Counter(list(memory_operations))
    return "m[p]=(m[p]+({}))%256\n".format(count['+']-count['-'])


def pointer_operation_compile(M):
    def _pointer_operation_compile(pointer_operations):
        count = Counter(list(pointer_operations))
        return "p=(p+({}))%{}\n".format(count['>']-count['<'], M)

    return _pointer_operation_compile


def io_operation_compile(io_operations):
    def translate(token):
        if token == '.':
            return "yield m[p]\n"
        else:
            return "m[p]=i.next()%256\n"

    return "".join(
        map(
            translate,
            io_operations
        )
    )


def loop_compile(expressions):
    return "while m[p]:\n{}".format(
        "".join(
            imap(
                "    {}\n".format,
                chain.from_iterable(
                    imap(
                        methodcaller('split', '\n'),
                        expressions[0]
                    )
                )
            )
        )
    )


def start_compile(M):
    def _start_compile(_):
        return "p=0\nm=bytearray({})\n".format(M)

    return _start_compile


def parser(M=1024):
    plus = Literal('+')
    minus = Literal('-')
    right = Literal('>')
    left = Literal('<')
    write = Literal('.')
    read = Literal(',')

    memory_operation = OneOrMore(plus ^ minus).setParseAction(
        memory_operation_compile
    )
    pointer_operation = OneOrMore(right ^ left).setParseAction(
        pointer_operation_compile(M=M)
    )
    io_operation = OneOrMore(write ^ read).setParseAction(
        io_operation_compile
    )

    start_bracket = Literal('[').suppress()
    end_bracket = Literal(']').suppress()
    expression = Forward()
    loop = Group(start_bracket + expression + end_bracket).setParseAction(
        loop_compile
    )

    start = Empty().setParseAction(start_compile(M=M))

    expression << ZeroOrMore(
        memory_operation ^ pointer_operation ^ io_operation ^ loop
    )

    program = (start + expression).setParseAction(''.join)

    return program


def bf(program):
    precompiled = None

    def _bf(input_stream=[]):
        input_stream = iter(input_stream)
        code = compile(precompiled, '<compiled>', 'eval')
        evaluated_code = eval(code)

        return evaluated_code


brainfuck = bf


def test(program):
    print(program)
    print(parser().parseString(program).asList()[0])
    print('-----------------------------------------')


map(
    test,
    [
        '++++----',
        '><<>><<>',
        '>>[++---]',
        '[-[++]+]',
        '++[>>[-]..,]',
        '++[-->>+++][+[+]+][+>-]',
    ]
)


def main():
    pass


if __name__ == '__main__':
    main()
