from typing import Any, List, Dict
import argparse


class Tokenizer:
    def __init__(self) -> None:
        pass

    def tokenize(self, s: str) -> List[str]:
        return s.split(' ')


class ParseArgs:
    def __init__(self, formatted: Dict[str, Any], remains: List[str]=None):
        self.__remains__ = remains if remains is not None else []
        for name in formatted.keys():
            setattr(self, name, formatted[name])

    def __repr__(self) -> None:
        s = 'ParseArgs('
        for k, v in self.__dict__.items():
            if k != '__remains__':
                s += f"{k}={v},"
        s = s[:-1] + ')'
        return s

    def __eq__(self, other):
        if not isinstance(other, ParseArgs):
            return NotImplemented
        return vars(self) == vars(other)

    def __contains__(self, key):
        return key in self.__dict__


class Parser:
    def __init__(self, formatters: List[str], parent: "Parser"=None) -> None:
        self.parent = parent
        self.formatters = formatters

    def next(self, formatters: List[str]) -> "Parser":
        p = Parser(formatters, self)
        return p

    def format(self, tokens: List[str]) -> ParseArgs:
        adict, tc = {}, tokens.copy()
        for f in self.formatters:
            adict[f] = tc.pop(0)
        return ParseArgs(adict, tc)

    def parse(self, s: str) -> ParseArgs:
        if self.parent:
            args = ARGS_MAP.get(self)
            if args:
                return args
            p_args = self.parent.parse(s)
            args = self.format(p_args.__remains__)
            ARGS_MAP[self] = args
            return args
        else:
            args = ARGS_MAP.get(self)
            if args:
                return args
            tokens = SPLITTER.tokenize(s)
            args = self.format(tokens)
            ARGS_MAP[self] = args
            return args


ARGS_MAP: Dict[Parser, ParseArgs] = {}
SPLITTER = Tokenizer()

p1 = Parser(['a', 'b'])

p2 = p1.next(['c'])
p3 = p1.next(['d'])

p4 = p2.next(['e'])
p5 = p2.next(['f'])

p6 = p3.next(['g'])
p7 = p3.next(['h'])

text = "word one two three four"
p4.parse(text)
p5.parse(text)
p6.parse(text)
p7.parse(text)
alist = [ARGS_MAP[p] for p in [p1, p2, p3, p4, p5, p6, p7]]
for args in alist:
    print(args)
print()