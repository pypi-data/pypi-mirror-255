#
# The MIT License (MIT)
#
# Copyright (c) 2016, 2024 eGauge Systems LLC
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
from __future__ import print_function

import os
import re
import sys
import textwrap

from dataclasses import dataclass, field
from typing import Any, Callable


class Error(Exception):
    pass


class Command_Done(Exception):
    pass


functions = {
    "mac_addr": True,
    "int": True,
}

quoted_string_pat = r'"((\\.|[^\\"])*)"'
varname_pat = r"[a-z_][a-z_0-9]*"
non_blank_pat = r"[^ \t]+"


@dataclass
class CmdSpec:
    # set this to True if the command needs to communicate with SAM-BA
    samba: bool = False
    args: list[Callable[[Any], Any]] = field(default_factory=list)
    min_args: int = None


def get_var(scope, varname):
    if varname not in scope:
        raise Error(f"Unknown variable name `{varname}'")
    return scope[varname]


def get_int(arg):
    try:
        return int(arg, 0)
    except ValueError as e:
        raise Error(f"Value `{arg}' is not a valid integer literal") from e


def get_string(arg):
    return re.sub(r"\\(.)", r"\1", arg)


def func_int(scope, args_string):
    """Expects a single string argument.  The function converts the string
    argument to a number and returns that number as its value.  A prefix
    of 0x can be used to specify a hex number; a prefix of 0o can be
    used to specify an octal number.

    """
    m = re.match(varname_pat, args_string, flags=re.IGNORECASE)
    if m:
        val = get_var(scope, args_string)
    else:
        m = re.match(quoted_string_pat + "$", args_string, flags=re.IGNORECASE)
        if not m:
            raise Error(f"Argument `{val}' is not a variable name or string")
        val = get_string(m.group(1))
    return get_int(val)


def func_mac_addr(scope, args_string):
    """Expects a single string argument specifying a MAC address in the
    form aa:bb:cc:dd:ee:ff, that is, six hex numbers separated by
    colons.  The function converts each hex string to a byte and
    returns them as a list of six bytes.

    """
    m = re.match(varname_pat, args_string, flags=re.IGNORECASE)
    if m:
        val = get_var(scope, args_string)
    else:
        m = re.match(quoted_string_pat + "$", args_string, flags=re.IGNORECASE)
        if not m:
            raise Error(f"Argument `{val}' is not a variable name or string")
        val = get_string(m.group(1))
    m = re.match(
        r"([0-9a-f]{1,2}):([0-9a-f]{1,2}):([0-9a-f]{1,2})"
        ":([0-9a-f]{1,2}):([0-9a-f]{1,2}):([0-9a-f]{1,2})",
        val,
        re.IGNORECASE,
    )
    if not m:
        raise Error(
            f"Argument `{val}' is not a MAC address of "
            "the form aa:bb:cc:dd:ee:ff"
        )
    return [
        int(m.group(1), 16),
        int(m.group(2), 16),
        int(m.group(3), 16),
        int(m.group(4), 16),
        int(m.group(5), 16),
        int(m.group(6), 16),
    ]


def fun_call(scope, name, args_string):
    if name not in functions:
        raise Error(f"Unknown function name `{name}'")
    func = globals()["func_" + name]
    return func(scope, args_string)


def parse_value(scope, arg):
    m = re.match(r"([a-z_][a-z_0-9]*)[(]([^)]*)[)]", arg, flags=re.IGNORECASE)
    if m:
        # function call
        return fun_call(scope, name=m.group(1), args_string=m.group(2))

    m = re.match(varname_pat, arg, flags=re.IGNORECASE)
    if m:
        return get_var(scope, arg)
    m = re.match(quoted_string_pat + r"$", arg, flags=re.IGNORECASE)
    if m:
        # string literal
        return get_string(m.group(1))
    return get_int(arg)


def parse_value_list(scope, arg):
    str_list = arg.split(",")
    ret = []
    for vstr in str_list:
        val = parse_value(scope, vstr.strip())
        if isinstance(val, list):
            ret += val
        else:
            ret.append(val)
    return ret


def parse_string(scope, arg):
    val = parse_value(scope, arg)
    if not isinstance(val, str):
        raise Error(f"Invalid string `{arg}'")
    return val


def parse_number(scope, arg):
    val = parse_value(scope, arg)
    if not isinstance(val, int):
        raise Error(f"Invalid number `{arg}'")
    return val


def parse_address(scope, arg):
    return parse_number(scope, arg)


def parse_number_list(scope, arg):
    l = parse_value_list(scope, arg)
    for val in l:
        if not isinstance(val, int):
            raise Error(f"Invalid number list `{arg}'")
    return l


def parse_variable(_scope, arg):
    if not re.match(r"[a-z_][a-z_0-9]*", arg, flags=re.IGNORECASE):
        raise Error(f"Illegal variable name `{arg}'")
    return arg


CMDS = {
    "baud": CmdSpec(args=[parse_number]),
    "go": CmdSpec(samba=True, args=[parse_address, parse_number], min_args=1),
    "help": CmdSpec(),
    "print": CmdSpec(args=[parse_string, parse_value_list]),
    "quit": CmdSpec(),
    "readb": CmdSpec(
        samba=True, args=[parse_variable, parse_address, parse_number]
    ),
    "readh": CmdSpec(
        samba=True, args=[parse_variable, parse_address, parse_number]
    ),
    "readw": CmdSpec(
        samba=True, args=[parse_variable, parse_address, parse_number]
    ),
    "reads": CmdSpec(
        samba=True, args=[parse_variable, parse_address, parse_number]
    ),
    "readimg": CmdSpec(
        samba=True, args=[parse_address, parse_number, parse_string]
    ),
    "sendimg": CmdSpec(samba=True, args=[parse_address, parse_string]),
    "set": CmdSpec(args=[parse_variable, parse_value]),
    "default": CmdSpec(args=[parse_variable, parse_value]),
    "writeb": CmdSpec(samba=True, args=[parse_address, parse_number_list]),
    "writeh": CmdSpec(samba=True, args=[parse_address, parse_number_list]),
    "writew": CmdSpec(samba=True, args=[parse_address, parse_number_list]),
    "writes": CmdSpec(samba=True, args=[parse_address, parse_string]),
}


# pylint: disable=unused-argument

def cmd_baud(scope, samba, args, serial):
    """Change the baudrate to NUMBER."""
    serial.flush()
    serial.baudrate = args[0]


def cmd_go(scope, samba, args, serial):
    """Jump to specified ADDRESS and switch to terminal-emulation mode.
    If NUMBER is given, switch to baudrate NUMBER before entering
    terminal-emulation mode.

    """
    samba.go(addr=args[0])
    if len(args) > 1:
        serial.flush()
        serial.baudrate = int(args[1])
    raise Command_Done("go")


def cmd_writes(scope, samba, args, serial):
    # pylint: disable=unused-argument
    """Write STRING to ADDRESS.  A trailing 0 byte will stored after the
    end of the string.

    """
    addr = args[0]
    blist = bytearray(args[1].encode("utf-8"))
    for byte in blist:
        samba.write_byte(addr, int(byte))
        addr += 1
    samba.write_byte(addr, 0)


def cmd_writeb(scope, samba, args, serial):
    # pylint: disable=unused-argument
    """Write the bytes in the NUMBER_LIST to memory starting at ADDRESS."""
    addr = args[0]
    for val in args[1]:
        samba.write_byte(addr, val)
        addr += 1


def cmd_writeh(scope, samba, args, serial):
    # pylint: disable=unused-argument
    addr = args[0]
    for val in args[1]:
        samba.write_halfword(addr, val)
        addr += 2


def cmd_writew(scope, samba, args, serial):
    # pylint: disable=unused-argument
    addr = args[0]
    for val in args[1]:
        samba.write_word(addr, val)
        addr += 4


def cmd_reads(scope, samba, args, serial):
    varname = args[0]
    addr = args[1]
    count = args[2]
    ret = ""
    for _ in range(count):
        val = samba.read_byte(addr)
        if val == 0:
            break
        ret += chr(val)
        addr += 1
    scope[varname] = ret


def cmd_readb(scope, samba, args, serial):
    """Read NUMBER bytes starting at ADDRESS and store the result in
    VARIABLE.  If NUMBER is equal to 1, the read value is stored
    directly in VARIABLE.  If NUMBER is greater than 1, the read
    values are stored as a list of values of length NUMBER.

    """
    varname = args[0]
    addr = args[1]
    count = args[2]
    if count < 1:
        return
    l = []
    for _ in range(count):
        val = samba.read_byte(addr)
        l.append(val)
        addr += 1
    scope[varname] = l if len(l) > 1 else l[0]


def cmd_readh(scope, samba, args, serial):
    """Read NUMBER halfwords starting at ADDRESS and store the result in
    VARIABLE.  If NUMBER is equal to 1, the read value is stored
    directly in VARIABLE.  If NUMBER is greater than 1, the read
    values are stored as a list of values of length NUMBER.

    """
    varname = args[0]
    addr = args[1]
    count = args[2]
    if count < 1:
        return
    l = []
    for _ in range(count):
        val = samba.read_halfword(addr)
        l.append(val)
        addr += 2
    scope[varname] = l if len(l) > 1 else l[0]


def cmd_readw(scope, samba, args, serial):
    """Read NUMBER words starting at ADDRESS and store the result in
    VARIABLE.  If NUMBER is equal to 1, the read value is stored
    directly in VARIABLE.  If NUMBER is greater than 1, the read
    values are stored as a list of values of length NUMBER.

    """
    varname = args[0]
    addr = args[1]
    count = args[2]
    if count < 1:
        return
    l = []
    for _ in range(count):
        val = samba.read_word(addr)
        l.append(val)
        addr += 4
    scope[varname] = l if len(l) > 1 else l[0]


def cmd_sendimg(scope, samba, args, serial):
    """Send the binary image with filename STRING to memory starting at
    ADDRESS.

    """
    script_dir = get_var(scope, "SCRIPTDIR")
    addr = args[0]
    filename = os.path.join(script_dir, args[1])
    try:
        with open(filename, "rb") as stream:
            samba.send_file(addr, stream)
    except IOError as e:
        raise Error(
            f"Failed to open file `{filename}' for reading: {sys.exc_info()[1]}"
        ) from e


def cmd_readimg(scope, samba, args, serial):
    # pylint: disable=unused-argument
    """Read NUMBER of bytes from memory starting at ADDRESS and store them
    as a binary image in a file with name STRING.

    """
    addr = args[0]
    count = args[1]
    filename = args[2]
    try:
        with open(filename, "wb") as stream:
            samba.receive_file(addr, count, stream)
    except IOError as e:
        raise Error(
            f"Failed to open file `{filename}' for writing:{sys.exc_info()[1]}"
        ) from e


def cmd_print(scope, samba, args, serial):
    # pylint: disable=unused-argument
    """Output the values in VALUE_LIST according to the format given by
    STRING.  The values are formatted using the Python format()
    function so any of its supported format specifiers can be used.
    Most simply, the values can be referred by position.  For example:
    ``print "the answer is {0} not {1}" 42, 43'' would print "the
    answer is 42 not 43" since 42 and 43 are the first and second
    positional argument, respectively.  If the arguments values are
    printed in order, you can omit the argument number.  For example
    ``print "{} {}" 42, 43'' would also print "42 43".  Formatting
    characters can be specified after a colon.  For example, ``print
    "0x{:04x}" 42'' would print "0x002a".

    """
    fmt = args[0]
    print(fmt.format(*args[1]))


def cmd_set(scope, samba, args, serial):
    # pylint: disable=unused-argument
    """Set VARIABLE to VALUE."""
    varname = args[0]
    val = args[1]
    scope[varname] = val


def cmd_default(scope, samba, args, serial):
    # pylint: disable=unused-argument
    """Sets VARIABLE to VALUE but only if VARIABLE isn't defined already."""
    varname = args[0]
    val = args[1]
    if varname in scope:
        return
    scope[varname] = val


def help_text():
    wrapper = textwrap.TextWrapper(initial_indent="\t", subsequent_indent="\t")
    txt = ""
    intro = (
        "Line-comments start with the hash characer (#).\n"
        "Lines ending with a backslash (\\) are merged with the "
        "next line, replacing any white space at the start of the "
        "next line with a single blank.\n"
        "NUMBER is an integer number.  A prefix of 0x can be used to "
        "to indicate a hexadecimal number or a prefix of 0o can be used "
        "to indicate an octal number.\n"
        "ADDRESS is a number that is interpreted as a memory address.\n"
        "STRING is a string of characters that must be enclosed "
        "in double quotes. "
        "Special characters such as double quote or backslash can "
        "be included in a string by escaping them with a backslash (\\) "
        "character.\n"
        "VALUE may be a STRING or NUMBER.\n"
        "NUMBER_LIST represents a list of comma-separated NUMBERs.\n"
        "VALUE_LIST represents a list of comma-separated numbers or "
        "strings.\n"
        "A variable name can be specified where a literal value "
        "is expected, provided the variable contains a value "
        "of the required type.\n"
        "A function call may also be used in place of a literal value. "
        "The following functions are available:"
    )
    for paragraph in intro.split("\n"):
        for line in textwrap.wrap(paragraph, initial_indent="\n"):
            txt += line + "\n"

    for name in sorted(functions.keys()):
        func = globals()["func_" + name]
        txt += f"\n {name}()\n"
        if func.__doc__ is not None:
            for line in wrapper.wrap(func.__doc__):
                txt += line + "\n"

    txt += "\nAvailable commands:\n"

    for cmd in sorted(CMDS.keys()):
        func = globals()["cmd_" + cmd]
        args = []
        cmd_spec = CMDS[cmd]
        if cmd_spec.min_args is not None:
            first_optional = cmd_spec.min_args
        else:
            first_optional = len(cmd_spec.args)
        for i, parser in enumerate(cmd_spec.args):
            arg_type = parser.__name__.upper()
            m = re.match(r"parse_(.*)", arg_type, flags=re.IGNORECASE)
            if m:
                arg_type = m.group(1)

            if i == first_optional:
                args.append("[")

            args.append(arg_type)

            if i == len(cmd_spec.args) - 1 and first_optional <= i:
                args.append("]")

        arg_str = " ".join(args)
        txt += f"\n  {cmd} {arg_str}\n"
        if func.__doc__ is not None:
            for line in wrapper.wrap(func.__doc__):
                txt += line + "\n"
    return txt


def cmd_help(scope, samba, args):
    # pylint: disable=unused-argument
    """Print this help message."""
    print(help_text())


def cmd_quit(scope, samba, args):
    # pylint: disable=unused-argument
    """Exit carioca."""
    raise Command_Done("quit")


def fmt_arg(arg):
    if isinstance(arg, int):
        return f"0x{arg:x}"
    if isinstance(arg, list):
        return ",".join(map(fmt_arg, arg))
    return str(arg)


def execute(scope, get_samba, line, print_commands, serial):
    res = line.split(None, 1)
    cmd = res[0]
    rest = res[1] if len(res) > 1 else ""
    if cmd not in CMDS:
        raise Error(f"Unknown command `{cmd}'")
    cmd_spec = CMDS[cmd]
    samba = get_samba() if cmd_spec.samba else None
    pat = r"(" + quoted_string_pat + r")|" + non_blank_pat
    arg_strings = []
    for m in re.finditer(pat, rest, flags=re.IGNORECASE):
        if len(arg_strings) >= len(cmd_spec.args):
            arg_strings[len(arg_strings) - 1] += " " + m.group(0)
        else:
            arg_strings.append(m.group(0))
    min_args = cmd_spec.min_args or len(cmd_spec.args)
    if len(arg_strings) < min_args:
        raise Error(
            f"Command `{cmd}' requires {min_args} argument(s) "
            f"but only {len(arg_strings)} given"
        )
    args = []
    for i, arg_str in enumerate(arg_strings):
        args.append(cmd_spec.args[i](scope, arg_str))
    func = globals()["cmd_" + cmd]
    if print_commands:
        args_str = " ".join(map(fmt_arg, args))
        print(f"+ {cmd} {args_str}", file=sys.stderr)
    func(scope, samba, args, serial)
