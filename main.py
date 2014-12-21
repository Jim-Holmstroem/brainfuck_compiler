from __future__ import print_function

from itertools import imap, chain, ifilter
from functools import partial
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


ifilter_nonblanks = partial(ifilter, None)


def loop_compile(expressions):
    nonempty_rows = ifilter_nonblanks(
        chain.from_iterable(
            imap(
                methodcaller('split', '\n'),
                expressions
            )
        )
    )
    tab = partial(imap, "    {}\n".format)
    pass_if_empty = lambda s: s if s else '    pass\n'

    return "while m[p]:\n{}".format(
        pass_if_empty(
            "".join(
                tab(
                    nonempty_rows
                )
            )
        )
    )


def start_compile(M):
    def _start_compile(_):
        return "p=0\nm=bytearray({})\n".format(M)

    return _start_compile


def parser(M):
    """Brainfuck->Python
    """
    plus, minus = Literal('+'), Literal('-')
    right, left = Literal('>'), Literal('<')
    write, read = Literal('.'), Literal(',')

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
    loop = (start_bracket + expression + end_bracket).setParseAction(
        loop_compile
    )

    start = Empty().setParseAction(start_compile(M=M))

    expression << ZeroOrMore(
        memory_operation ^ pointer_operation ^ io_operation ^ loop
    )

    program = (start + expression).setParseAction(''.join)

    return program


def bf(program, M=1024):
    header_template = "def _f(i):\n{code}"
    compiled_program = parser(M=M).parseString(program)[0]

    compiled_program_with_header = header_template.format(
        code="".join(
            imap(
                "    {}\n".format,
                ifilter_nonblanks(
                    compiled_program.split('\n')
                )
            )
        )
    )
    print(compiled_program_with_header)

    def _bf(input_stream=[]):
        input_stream = iter(input_stream)
        code = compile(compiled_program_with_header, '<compiled>', 'exec')
        exec code in {}, locals()  # MAGIC: _f gets loaded into scope

        return _f(input_stream)

    return _bf

brainfuck = bf


def test(program):
    print(program)
    print(parser(1024).parseString(program)[0])
    print('-----------------------------------------')


map(
    test,
    [
        '[]'
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
