from compiler.node import Node
from compiler.token import Token
from compiler.pylist import List
import textwrap


def compile(self: Node) -> str:
    """Generates semantically equivalent code for the target platform/compiler
    (not guaranteed to be formatted or comply with typical style conventions).
    Currently, only C is supported. This method works recursively on a "C-like"
    syntax tree and is analogous to the inverse function of that represented by
    the parser. It is assumed that by now, all higher-level constructs have
    been "lowered" to canonical forms appropriate for the target; if this is
    not the case, an error may be thrown here or when the generated code is
    passed off to gcc/g++ for translation to an object file (but preferably the
    former)."""

    match self.type:
        case 'program':
            # TODO: handle outer function generation using tree rewriting
            body = self.children.map(compile).join('\n')
            return '\n'.join(['int main () {', body, '}'])

        case 'start' | 'form':
            return self.children.map(compile).join('\n')

        case 'block':
            return '{\n' + self.children.map(compile).join('\n') + '\n}'

        case 'statement':
            return f'{self.children[0].emit_code()};'

        case 'expression' | 'declaration' | 'operation' | 'literal':
            # this is a hotfix to handle "wrapped" AST nodes; a single form
            # in the source code can sometimes produce several nested
            # statement, expression, block, etc. nodes
            return self.children.map(Node.emit_code).join('')

        case 'return':
            return f'return {self.arg.emit_code()}'

        case 'function_declaration':
            return List([self.return_type.emit_code(),
                         self.name.emit_code(),
                         '()',
                         self.body.emit_code()]).join(' ')

        case 'function':
            if self.definition == '[internal]':
                return ''
            return self.definition.emit_code()

        case 'type':
            return ''

        case 'tuple':
            assert None not in self.children, self
            return self.children.map(compile).join(', ')

        case 'list':
            return self.children.map(compile).join(', ')

        case 'call':
            return f'{self.f.emit_code()}({self.args.emit_code()})'

        case 'bin_op':
            # prior to this translation, nonstandard operators like ".."
            # must have been lowered; in the future an error will be thrown
            # if they are present in the input tree
            return List([
                self.left, self.op, self.right
            ]).map(compile).join(' ')

        case 'INT' | 'FLOAT':
            # one of the few lucky cases where the parse output is always
            # (?) equivaent to its native form (an exception may be methods
            # called on number/string literals, but this should be handled
            # during the rewriting stage)
            return self.value

        case 'let_stmt':
            assert self.right.vtype is not None
            return textwrap.dedent(f'{self.right.vtype} {self.left.emit_code()} = {self.right.emit_code()}')

        case 'assignment':
            assert self.right.vtype is not None
            return textwrap.dedent(f'{self.left.emit_code()} = {self.right.emit_code()}')

        case _:
            if isinstance(self, Token):
                return self.emit_code()
            raise NotImplementedError(self)


def comptest(node):
    print(node)
    print(compile(node))


comptest(Node([Node([Token('print', 'IDENTIFIER'),
                     Token('hello', 'STRING')], 'call')],
              'program'))
