# Copyright (C) Juergen Nickelsen <ni@w21.org>, see LICENSE.

"""POSIX-conformant command-line option parser (plus long options)
See the parse() function for details. Build 2024.206.1405
"""

import os
import sys
import copy

# Exception argument string and additional value (used to generate README)
ErrorNotopt = "unknown option"                     # option
ErrorArg = "option does not take an argument"      # option
ErrorNoarg = "option needs argument"               # option
ErrorIntarg = "option argument must be integer"    # option
ErrorMinarg = "too few arguments, needs at least"  # minimum
ErrorMaxarg = "too many arguments, at most"        # maximum

class OptionError(Exception):
    pass

class OptionValueContainer:
    def __init__(self, descriptors, args):
        """Arguments: dict optchar => descriptor; command-line args.

        See the parse() function below for details.

        """
        self._opts = copy.deepcopy(descriptors)
        _keywords = ("_arguments", "_help_header", "_help_footer",
                 "_usage", "_program")
        for opt, desc in self._opts.items():
            if opt.startswith("_"):
                assert opt in _keywords, "keyword unknown: " + repr(opt)
                continue
            assert type(opt) == str and len(opt) == 1, \
              "option key must be string of length 1: " + repr(opt)
            assert type(desc) == tuple and len(desc) in (4, 5), \
              "descriptor not sequence len 4 or 5: -" + opt

            name, typ, default, *_ = desc
            assert isinstance(name, str), "option name is not a string: -" + opt
            if type(typ) == type:
                assert typ in (bool, int, str), "invalid option type: -" + opt
            else:
                assert callable(typ), "invalid option type: -"+opt
            self.__dict__[name] = default

        if "h" not in self._opts:
            self._opts["h"] = \
                ("help", self.ovc_help, None, "show help on options")
        if "?" not in self._opts:
            self._opts["?"] = \
                ("usage", self.ovc_usage, None, "show usage briefly")
        for field in _keywords:
            self.__dict__[field] = self._opts.get(field)
        if not self._program:
            self._program = os.path.basename(sys.argv[0])
        self._long = { v[0].replace("_", "-"): v
                       for k, v in self._opts.items() if len(k) == 1 }
        self._args = args[:]
        self._min = self._max = None
        if type(self._arguments) == list:
            min = max = 0
            inf = False
            for arg in self._arguments:
                if "..." in arg:
                    inf = True
                if arg.startswith("["):
                    max += len(arg.split(" "))
                elif not arg == "...":
                    min += 1
                    max += 1
            self._min = min
            self._max = None if inf else max
            self._arguments = " ".join(self._arguments)


    def _parse(self):
        while self._args and self._args[0].startswith("-"):
            arg = self._args.pop(0)
            if arg == "--": break
            if arg.startswith("--"):
                self._have_opt(arg[2:])
            else:
                arg = arg[1:]
                while arg:
                    arg = self._have_opt(arg[0], arg[1:])
        if self._min is not None and len(self._args) < self._min:
            raise OptionError(ErrorMinarg, self._min)
        if self._max is not None and len(self._args) > self._max:
                raise OptionError(ErrorMaxarg, self._max)


    def _have_opt(self, opt, arg=None):
        value = None
        if len(opt) > 1:
            parts = opt.split("=", 1)
            if len(parts) > 1:
                opt, value = parts
            desc = self._long.get(opt)
        else:
            desc = self._opts.get(opt)
        if not desc:
            raise OptionError(ErrorNotopt, opt)
        name, typ, defval, *_ = desc
        if typ == bool:
            if value:
                raise OptionError(ErrorArg, opt)
            self.__dict__[name] += 1
        else:
            if typ not in (str, int):
                value = typ()
            elif arg:
                value = arg
                arg = ""
            self._set_optarg(opt, desc, value)
        return arg


    def _set_optarg(self, opt, desc, value):
        if value is None:
            if not self._args:
                raise OptionError(ErrorNoarg, opt)
            value = self._args.pop(0)
        if desc[1] == int:
            try:
                value = int(value)
            except:
                raise OptionError(ErrorIntarg, opt)
        if isinstance(getattr(self, desc[0], None), list):
            getattr(self, desc[0]).append(value)
        else:
            setattr(self, desc[0], value)


    def ovc_help(self):
        """Print the help message and exit."""
        print(self.ovc_help_msg())
        sys.exit()

        
    def ovc_help_msg(self):
        """Return a detailed help message."""
        msg = self.ovc_usage_msg() + "\n"
        if self._help_header:
            msg += self._help_header + "\n\n"
        for opt in sorted(self._opts.keys()):
            if opt.startswith("_"):
                continue
            desc = self._opts[opt]
            arg = ""
            if desc[1] in (str, int):
                arg = (desc[4] if len(desc) == 5 else "ARG")
            msg += " -%s, --%s %s\n    %s" % (
                opt, desc[0].replace('_', '-'), arg, desc[3])
            if desc[1] in (int, str):
                msg += " (%s arg, default %s)" % (
                    desc[1].__name__, repr(desc[2]))
            msg += "\n"
        if self._help_footer:
            msg += "\n" + self._help_footer
        return msg


    def ovc_usage(self, error="", exit_status=64):
        """Print usage message (with optional error message) and exit."""
        out = sys.stdout if not exit_status else sys.stderr
        if error:
            print(self._program + ":", error, file=out, end="\n\n")
        print(self.ovc_usage_msg(), file=out)
        print("use '-h' option to get help on options", file=out)
        sys.exit(exit_status)


    def ovc_usage_msg(self):
        """Return a brief usage message."""
        args = ""
        if self._arguments is None:
            args = " <arguments>"
        elif self._arguments:
            args = " " + self._arguments
        return self._usage or "usage: " + self._program + " [options]" + args


    def ovc_values(self):
        """Return a dict of options and their values (for testing)."""
        return { key: val for key, val in self.__dict__.items()
                 if not key.startswith("_") }


def parse(descriptors, args=sys.argv[1:], exit_on_error=True):
    """Parse the command line options according to the specified descriptors.

    Keys of the descriptors dictionary are options or keywords. In case
    of an option, the key is the single option character, and the value
    is a tuple of four or five fields:

      (1) name of the option, used in the returned namespace and as the
      name of the corresponding long option name (after replacing
      underscores with dashes)

      (2) type of the option, which may be bool for options without
      arguments (actually counters), or str or int for options with an
      argument of the respective type

      (3) default value, which can be a starting counter (or False) for
      bool options, or an integer or string value for int or str
      options, respectively, or a list, to which each option argument
      will be appended (for multi-value options)

      (4) description of the option for the help text

      (5) (optional) name of the option's argument for the help text
      (defaults to 'ARG')

    A key may also be one of these keywords:

      "_arguments": string to print in the usage to describe the
      non-option arguments, or, for argument count checking, a sequence
      with the argument names:
    
         - a normal string counts as one argument towards minimum and
           maximum

         - if it contains '...', there is no maximum the number of
           arguments

         - if it begins with '[', it is optional; if it can be split by
           blanks into multiple words, each one counts toward the
           maximum; e.g. "[param1 param2 param3]" increases the maximum
           by 3, but not the minimum

      "_help_footer": string to print with 'help' after the option
      explanations

      "_help_header": string to print with 'help' before the option
      explanations

      "_program": string to use as program name for help and usage
      message instead of sys.argv[0]

      "_usage": string to use as usage message instead of the default
      constructed one

    If no '?' or 'h' option is specified, they will default to a 'help'
    or a 'usage' function, respectively, which will be called
    immediately when the option is seen. 'help' prints a description of
    the options, framed by the _help_header and the _help_footer;
    'usage' prints a brief summary of the program's parameters. Both
    terminate the program after printing the message.

    In case of a normal return of parse() (i.e. options and number of
    arguments okay), it returns an OptionValueContainer and a list of
    the remaining command line arguments. Example:

      ovc, args = pgetopt.parse({
      # opt: (name,          type, default value, helptext[, arg name])
        "s": ("schmooze",    bool, 0,    "more schmooziness"),
        "o": ("output_file", str,  None, "output file (or stdout)", "NAME"),
        "n": ("repetitions", int,  3,    "number of repetitions"),
        "d": ("debug",       str, [],    "debug topics", "DEBUG_TOPIC"),
      # keyword:        value
        "_arguments":   ["string_to_print", "..."],
        "_help_header": "print a string a number of times",
        "_help_footer": "This is just an example program.",
      }

      On return, ovc has the following fields:
        ovc.schmooze:    number of -s options counted,
        ovc.output_file: parameter of -o or --output-file, or None
        ovc.repetitions: parameter of -n or --repetitions, or 3
        ovc.debug:       list with all parameters given to -d or --debug

    Parameters to int or str options are taken from the next argument;
    with long options, "--option=parameter" is also possible.

    Other potentially useful fields of ovc:
      ovc.ovc_help():  help function
      ovc.ovc_usage(): usage function
    
      ovc.ovc_help_msg(),
      ovc.ovc_usage_msg(): get corresponding messages as strings

    """
    ovc = OptionValueContainer(descriptors, args)
    try:
        ovc._parse()
        return ovc, ovc._args
    except OptionError as e:
        if exit_on_error:
            ovc.ovc_usage(e.args[0] + ": " + repr(e.args[1]))
        raise(e)

# EOF
