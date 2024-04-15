import argumentsparser
from funcs import die

a = argumentsparser.WRArgumentParser()
a.compilePosArgumentsParser()
c = a.parse_args(["bleh", "--run"])
a.positionalArgumentsCheck(c)
d = a.getNextOptArg(c)

die(str(a._option_string_actions["--run"]), 0)
