from lark import Lark, Transformer
import sys

with open("grammar.ebnf") as fd:
    grammar = fd.read()
    parser = Lark(grammar, start='program')

class TransTree(Transformer):

