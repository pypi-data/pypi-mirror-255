'''
Wrapper for argparse and argcomplete.

Compatible with Python versions 3.6 - 3.11.
'''

import sys

from typing import overload


__all__ = [
    'Arg',
    'App',
    'ArgHelper',
    'AppHelper',
    'Completer',
    'CompleterNone',
    'CompleterList',
    'CompleterPath',
    'CallError',
    'main',
]


try:
    from argcomplete.completers import BaseCompleter as Completer
    from argcomplete.completers import SuppressCompleter as CompleterNone
    from argcomplete.completers import ChoicesCompleter as CompleterList
    from argcomplete.completers import FilesCompleter as CompleterPath
except:
    class Completer:
        '''
        A dummy when argcomplete is not installed.
        '''

        def __init__(self) -> 'None':
            ...

        def __call__(self, *args, **kwds) -> 'list[str]':
            ...

    class CompleterNone(Completer):
        '''
        A dummy when argcomplete is not installed.
        '''

        def __init__(self) -> 'None':
            ...

        def __call__(self, *args, **kwds) -> 'list[str]':
            ...

    class CompleterList(Completer):
        '''
        A dummy when argcomplete is not installed.
        '''

        def __init__(self, v: 'list[str]') -> 'None':
            ...

        def __call__(self, *args, **kwds) -> 'list[str]':
            ...

    class CompleterPath(Completer):
        '''
        A dummy when argcomplete is not installed.
        '''

        def __init__(self) -> 'None':
            ...

        def __call__(self, *args, **kwds) -> 'list[str]':
            ...


class Arg:
    '''
    Represents a command line argument.
    '''

    @property
    def name(self) -> 'str':
        '''
        The name of the argument's value.

        Defaults:
        * Uppercase `self.lopt`, if set.
        * Uppercase `self.sopt`, if set.
        * `''`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @name.setter
    def name(self, v: 'str | None') -> 'None':
        ...

    @property
    def lopt(self) -> 'str':
        '''
        The long option name.

        Defaults:
        * `""`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @lopt.setter
    def lopt(self, v: 'str | None') -> 'None':
        ...

    @property
    def sopt(self) -> 'str':
        '''
        The short option name.

        Defaults:
        * `''`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        * `ValueError`, if the value exceeds one character.
        '''

    @sopt.setter
    def sopt(self, v: 'str | None') -> 'None':
        ...

    @property
    def help(self) -> 'str':
        '''
        The argument's description.

        Defaults:
        * `''`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @help.setter
    def help(self, v: 'str | None') -> 'None':
        ...

    @property
    def helper(self) -> 'ArgHelper':
        '''
        The argument's help text generator.

        Defaults:
        * `ArgHelper()`.

        Exceptions:
        * `TypeError`, if the type is not `ArgHelper` or `None`.
        '''

    @helper.setter
    def helper(self, v: 'ArgHelper | None') -> 'None':
        ...

    @property
    def type(self) -> 'type':
        '''
        The type of an individual value.

        Defaults:
        * Always `bool`, if `self.flag` is `True`.
        * The type of the first item of `self.default`, if its type is `list` and it is not empty.
        * The type of `self.default`, if its type is not `list` and it is not `None`.
        * `str`.

        Exceptions:
        * `TypeError`, if the type is not `type` or `None`.
        * `ValueError`, if the value does not match `self.default`.
        '''

    @type.setter
    def type(self, v: 'type | None') -> 'None':
        ...

    @property
    def count(self) -> 'int | str':
        '''
        The number of values consumed by the argument:
        * `0`: indicates a flag. Can be set if `self.optional` is `True`.
        * `1`: a single value.
        * `2` or greater: multiple values, an exact number.
        * `'?'`: a single value, zero or one.
        * `'*'`: multiple values, zero or more.
        * `'+'`: multiple values, one or more.
        * `'~'`: multiple values, zero or more. Consume the rest of the command line without parsing. Can be set if `self.positional` is `True`.

        Defaults:
        * `'*'`, if the type of `self.default` is `list`.
        * `1`.

        Exceptions:
        * `TypeError`, if the type is not `int`, `str` or `None`.
        * `ValueError`, if the type is `int` and the value is negative.
        * `ValueError`, if the type is `str` and the value is not one of: `'?'`, `'*'`, `'+'`, `'~'`.
        * `ValueError`, if the value is `0` and `self.optional` is `False`.
        * `ValueError`, if the value is `'~'` and `self.positional` is `False`.
        * `ValueError`, if the value is `'+'` and `self.default` is an empty `list`.
        * `ValueError`, if the type is `int` and the value does not match the number of items in `self.default`.
        '''

    @count.setter
    def count(self, v: 'int | str | None') -> 'None':
        ...

    @property
    def default(self) -> 'object | list | None':
        '''
        The default value. It is used by the base implementations of `Arg.__call__(...)` in the following cases:
        * `self.count` is `'?'`, `'*'` or `'~'` and no values provided.
        * `self.optional` is `True`, `self.suppress` is `False`, and the argument is not mentioned.

        Defaults:
        * `False`, if `self.flag` is `True`.
        * `[]`, if `self.count` is `'*'` or `'~'`.
        * `None`.

        Exceptions:
        * `TypeError`, if the type is not `list` or `None` and `self.multiple` is `True`.
        * `TypeError`, if the type is `list`, and `self.single` is `True`.
        * `TypeError`, if the type is not `list` and it is not `self.type` or `None`.
        * `TypeError`, if the type is `list` and one of the items is not `self.type`.
        *  `ValueError`, if the type is `list`, and the number of items does not match `self.count`.
        *  `ValueError`, if the value is an empty `list`, and `self.count` is `'+'`.
        '''

    @default.setter
    def default(self, v: 'object | list | None') -> 'None':
        ...

    @property
    def choices(self) -> 'dict[str, str]':
        '''
        A `dict` of the possible values.
        * Converted to a `dict[str, str]` from any `Iterable`.
        * The dictionary values are used as the descriptions, if not empty.
        * `self.default` is never checked against `self.choices`.

        Defaults:
        * `{}`.

        Exceptions:
        * `TypeError`, if the type is not `Iterable` or `None`.
        '''

    @choices.setter
    def choices(self, v: 'list | dict | None') -> 'None':
        ...

    @property
    def restrict(self) -> 'bool':
        '''
        Whether `self.choices` are restrictive.

        Defaults:
        * `True`.

        Exceptions:
        * `TypeError`, if the type is not `bool` or `None`.
        '''

    @restrict.setter
    def restrict(self, v: 'bool | None') -> 'None':
        ...

    @property
    def suppress(self) -> 'bool':
        '''
        Whether to not set the optional argument to `self.default` if it is not mentioned.

        Defaults:
        * Always `False`, if `self.optional` is `False`.
        * `False`.

        Exceptions:
        * `TypeError`, if the type is not `bool` or `None`.
        '''

    @suppress.setter
    def suppress(self, v: 'bool | None') -> 'None':
        ...

    @property
    def required(self) -> 'bool':
        '''
        Whether the optional argument must be mentioned.

        Defaults:
        * Always `True`, if `self.optional` is `False`.
        * `False`.

        Exceptions:
        * `TypeError`, if the type is not `bool` or `None`.
        '''

    @required.setter
    def required(self, v: 'bool | None') -> 'None':
        ...

    @property
    def append(self) -> 'bool':
        '''
        Whether the optional argument is appended on repeat.

        Defaults:
        * Always `False`, if `self.optional` is `False`.
        * `False`.

        Exceptions:
        * `TypeError`, if the type is not `bool` or `None`.
        '''

    @append.setter
    def append(self, v: 'bool | None') -> 'None':
        ...

    @property
    def completer(self) -> 'Completer':
        '''
        The command line completer for the argument.

        Defaults:
        * `CompleterList(self.choices)`, if `self.choices` is not empty.
        * `CompleterPath()`, if `self.type` is `str`.
        * `CompleterNone()`.

        Exceptions:
        * `TypeError`, if the type is not `Completer` or `None`.
        '''

    @completer.setter
    def completer(self, v: 'Completer | None') -> 'None':
        ...

    @property
    def optional(self) -> 'bool':
        '''
        Whether the argument is optional.

        Defaults:
        * `True`, if either `self.sopt` or `self.lopt` is set.
        * `False`.
        '''

    @property
    def positional(self) -> 'bool':
        '''
        Whether the argument is positional.

        Defaults:
        * `True`, if both `self.sopt` and `self.lopt` are not set.
        * `False`.
        '''

    @property
    def flag(self) -> 'bool':
        '''
        Whether the argument does not consume a value.

        Defaults:
        * `True`, if `self.count` is `0`.
        * `False`.
        '''

    @property
    def single(self) -> 'bool':
        '''
        Whether the argument can consume at most one value.

        Defaults:
        * `True`, if `self.count` is `'?'` or `1`.
        * `False`.
        '''

    @property
    def multiple(self) -> 'bool':
        '''
        Whether the argument can consume more than one value.

        Defaults:
        * `True`, if `self.count` is `'*'`, `'+'`, `'~'` or greater than one.
        * `False`.
        '''

    def __init__(
        self,
        name: 'str | None' = None,
        lopt: 'str | None' = None,
        sopt: 'str | None' = None,
        help: 'str | None' = None,
        helper: 'ArgHelper | None' = None,
        type: 'type | None' = None,
        count: 'int | str | None' = None,
        default: 'object | list | None' = None,
        choices: 'dict | None' = None,
        restrict: 'bool | None' = None,
        suppress: 'bool | None' = None,
        required: 'bool | None' = None,
        append: 'bool | None' = None,
        completer: 'Completer | None' = None,
    ) -> 'None':
        '''
        The constructor. Sets each field in the declaration order.

        Parameters:
        * `name` - corresponds to `self.name`.
        * `lopt` - corresponds to `self.lopt`.
        * `sopt` - corresponds to `self.sopt`.
        * `help` - corresponds to `self.help`.
        * `helper` - corresponds to `self.helper`.
        * `type` - corresponds to `self.type`.
        * `count` - corresponds to `self.count`.
        * `default` - corresponds to `self.default`.
        * `choices` - corresponds to `self.choices`.
        * `restrict` - corresponds to `self.restrict`.
        * `suppress` - corresponds to `self.suppress`.
        * `required` - corresponds to `self.required`.
        * `append` - corresponds to `self.append`.
        * `completer` - corresponds to `self.completer`.
        '''

    @overload
    def __call__(
        self,
        v: 'bool',
    ) -> 'bool':
        '''
        Parse the command line value. This overload is called if:
        * `self.flag` is `True`.
        * `self.append` is `False`.

        Parameters:
        * `v` - `True` if the argument is mentioned in the command line. `False` otherwise.

        Returns:
        * `self.default`, if v is `True`.
        * `not self.default`, if v is `False`.
        '''

    @overload
    def __call__(
        self,
        v: 'int',
    ) -> 'int':
        '''
        Parse the command line value. This overload is called if:
        * `self.flag` is `True`.
        * `self.append` is `True`.

        Parameters:
        * `v` - a number of times the argument is mentioned in the command line.

        Returns:
        * `v`.
        '''

    @overload
    def __call__(
        self,
        v: 'str | None',
    ) -> 'object | None':
        '''
        Parse the command line value. This overload is called if:
        * `self.single` is `True`.
        * `self.append` is `False`.

        Parameters:
        * `v` - a value from the command line. `None` if not provided.

        Returns:
        * `self.default`, if `v` is `None`.
        * `self.type(v)`.

        Exceptions:
        * `CallError`, if `self.restrict` is `True` and the value is not in `self.choices`.
        '''

    @overload
    def __call__(
        self,
        v: 'list[str | None]',
    ) -> 'list[object | None]':
        '''
        Parse the command line value. This overload is called if:
        * `self.single` is `True`.
        * `self.append` is `True`.

        Parameters:
        * `v` - a list of values from the command line associated with the argument.

        Returns:
        * A `list` where each item `x` from `v` is set to:
           * `self.default`, if `x` is `None`.
           * `self.type(x)`.

        Exceptions:
        * `CallError`, if `self.restrict` is `True` and any item is not in `self.choices`.
        '''

    @overload
    def __call__(
        self,
        v: 'list[str] | None',
    ) -> 'list[object] | None':
        '''
        Parse the command line value. This overload is called if:
        * `self.multiple` is `True`.
        * `self.append` is `False`.

        Parameters:
        * `v` - a list of values from the command line.

        Returns:
        * `self.default`, if `v` is `None`.
        * A `list` where each item `x` from `v` is set to `self.type(x)`.

        Exceptions:
        * `CallError`, if `self.restrict` is `True` and any item is not in `self.choices`.
        '''

    @overload
    def __call__(
        self,
        v: 'list[list[str] | None]',
    ) -> 'list[list[object] | None]':
        '''
        Parse the command line value. This overload is called if:
        * `self.multiple` is `True`.
        * `self.append` is `True`.

        Parameters:
        * `v` - a list of lists of values from the command line associated with the argument.

        Returns:
        * A `list[list]` where each list `l` from `v` is converted to:
           * `self.default`, if `l` is `None`.
           * A `list` where each item `x` from `l` is converted to `self.type(x)`.

        Exceptions:
        * `CallError`, if `self.restrict` is `True` and any item is not in `self.choices`.
        '''


class App:
    '''
    Represents a command.
    '''

    @property
    def name(self) -> 'str':
        '''
        The command's name.

        Defaults:
        * `''`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @name.setter
    def name(self, v: 'str | None') -> 'None':
        ...

    @property
    def help(self) -> 'str':
        '''
        The command's short description.

        Defaults:
        * `''`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @help.setter
    def help(self, v: 'str | None') -> 'None':
        ...

    @property
    def prolog(self) -> 'str':
        '''
        The command's detailed description before arguments.

        Defaults:
        * `self.help`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @prolog.setter
    def prolog(self, v: 'str | None') -> 'None':
        ...

    @property
    def epilog(self) -> 'str':
        '''
        The command's detailed description after arguments.

        Defaults:
        * `''`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @epilog.setter
    def epilog(self, v: 'str | None') -> 'None':
        ...

    @property
    def helper(self) -> 'AppHelper':
        '''
        The command's help text generator.

        Defaults:
        * `AppHelper()`.

        Exceptions:
        * `TypeError`, if the type is not `AppHelper` or `None`.
        '''

    @helper.setter
    def helper(self, v: 'AppHelper | None') -> 'None':
        ...

    @property
    def args(self) -> 'list[Arg]':
        '''
        The command's arguments.

        Defaults:
        * `[]`.
        '''

    @property
    def apps(self) -> 'list[App]':
        '''
        The command's subcommands.

        Defaults:
        * `[]`.
        '''

    def __init__(
        self,
        name: 'str | None' = None,
        help: 'str | None' = None,
        prolog: 'str | None' = None,
        epilog: 'str | None' = None,
        helper: 'AppHelper | None' = None,
    ) -> 'None':
        '''
        The constructor. Sets each field in the declaration order.

        Parameters:
        * `name` - corresponds to `App.name`.
        * `help` - corresponds to `App.help`.
        * `prolog` - corresponds to `App.prolog`.
        * `epilog` - corresponds to `App.epilog`.
        * `helper` - corresponds to `App.helper`.
        '''

    def __call__(
        self,
        args: 'dict[Arg]',
        apps: 'list[App]',
    ) -> 'None':
        '''
        Run the command.
        * This function is called by `main()` on each command from the command line.
        * The base implementation does nothing, the subclasses are supposed to override it.
        * `CallError` has to be raised to notify about any errors.

        Parameters:
        * `args` - A dictionary of `Arg` and its parsed command line value.
        * `apps` - A list of commands that are mentioned in the command line, starting from the leftmost one.
        '''


class ArgHelper:
    '''
    An argument description generator.
    '''

    @property
    def choices(self) -> 'bool':
        '''
        Whether to append the `Arg.choices` to the help text.

        Defaults:
        * `True`.

        Exceptions:
        * `TypeError`, if the type is not `bool` or `None`.
        '''

    @choices.setter
    def choices(self, v: 'bool | None') -> 'None':
        ...

    @property
    def default(self) -> 'bool':
        '''
        Whether to append the `Arg.default` to the help text.

        Defaults:
        * `True`.

        Exceptions:
        * `TypeError`, if the type is not `bool` or `None`.
        '''

    @default.setter
    def default(self, v: 'bool | None') -> 'None':
        ...

    def text_help(self, arg: 'Arg') -> 'str':
        '''
        Generate the argument's description.

        Parameters:
        * `arg` - the argument to use for the generation.

        Returns:
        * `arg.help` with the following appended if `arg.flag` is `False`:
           * `arg.default`, if `self.default` is `True`.
           * `arg.choices`, if `self.choices` is `True`.
        '''

    def text_usage(self, arg: 'Arg') -> 'str':
        '''
        Generate the argument's usage (stylized name).

        Parameters:
        * `arg` - the argument to use for the generation.

        Returns:
        * A `str` with the following text combined:
           * `-sopt`, if `arg.sopt` is set.
           * `--lopt`, if `arg.lopt` is set.
           * A stylized `arg.name`:
                  * `name` repeated `arg.count` times, if its type is `int`.
                  * `[name]`, if `arg.count` is `'?'`.
                  * `[name...]`, if `arg.count` is `'*'`.
                  * `name [name...]`, if `arg.count` is `'+'`.
                  * `[name]...`, if `arg.count` is `'~'`.
        '''

    def __init__(
        self,
        choices: 'bool | None' = None,
        default: 'bool | None' = None,
    ) -> 'None':
        '''
        The constructor. Sets each field in the declaration order.

        Parameters:
        * `choices` - corresponds to `self.choices`.
        * `default` - corresponds to `self.default`.
        '''


class AppHelper:
    '''
    A command description generator.
    '''

    @property
    def lopt(self) -> 'str':
        '''
        The long option name for the help argument. Similar to `Arg.lopt`.

        Defaults:
        * `''`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @lopt.setter
    def lopt(self, v: 'str | None') -> 'None':
        ...

    @property
    def sopt(self) -> 'str':
        '''
        The short option name for the help argument. Similar to `Arg.sopt`.

        Defaults:
        * `''`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @sopt.setter
    def sopt(self, v: 'str | None') -> 'None':
        ...

    @property
    def help(self) -> 'str':
        '''
        The help text for the help argument. Similar to `Arg.help`.

        Defaults:
        * `''`.

        Exceptions:
        * `TypeError` if the type is not `str` or `None`.
        '''

    @help.setter
    def help(self, v: 'str | None') -> 'None':
        ...

    def text_help(
        self,
        apps: 'list[App]',
        name: 'str',
    ) -> 'str':
        '''
        Generate the command's full help text.

        Parameters:
        * `apps` - a list of commands mentioned in the command line. The text is generated for the last one.
        * `name` - a name to use for the first command in `apps`.

        Returns:
        * A `str`, combination of the following:
           * `self.text_usage(apps, name)`.
           * `apps[-1].prolog`.
           * `self.section_apps("Commands", apps[-1].apps)`.
           * `self.section_args("Positional arguments", args)`, where `args` - positional arguments from `apps[-1].args`.
           * `self.section_args("Optional arguments", args)`, where `args` - optional arguments from `apps[-1].args` and the help option, if set.
           * `apps[-1].epilog`.
        '''

    def text_usage(
        self,
        apps: 'list[App]',
        name: 'str',
    ) -> 'str':
        '''
        Generate the command's full usage text.

        Parameters:
        * `apps` - a list of commands mentioned in the command line. The usage text is generated for the last one.
        * `name` - a name to use for the first command in `apps`.

        Returns:
        * A `str` that combines:
           * All the commands from the command line (the arguments omitted).
           * The last command's optional arguments with `required` set to `True`.
           * The last command's positional arguments.
        '''

    def section_apps(
        self,
        title: 'str',
        apps: 'list[App]',
    ) -> 'str':
        '''
        Generate the command's text for subcommands.

        Parameters:
        * `title` - a title for the section.
        * `apps`  - a list of `App` to generate the text for.

        Returns:
        * `''` if `apps` is empty.
        * A `str` that is a bullet list from `app` in `apps`: `app.name` and `app.help`.
        '''

    def section_args(
        self,
        title: 'str',
        args: 'list[Arg]',
    ) -> 'str':
        '''
        Generate the command's text for arguments.

        Parameters:
        * `title` - a title for the section.
        * `args`  - a list of `Arg` to generate the text for.

        Returns:
        * `''` if `args` is empty.
        * A `str` that is a bullet list from `arg` in `args`: `arg.helper.text_usage(arg)` and `arg.helper.text_help(arg)`.
        '''

    def __init__(
        self,
        lopt: 'str | None' = 'help',
        sopt: 'str | None' = 'h',
        help: 'str | None' = 'Show the help text and exit.',
    ) -> 'None':
        '''
        The constructor. Sets each field in the declaration order.

        Parameters:
        * `lopt` - corresponds to `self.lopt`.
        * `sopt` - corresponds to `self.sopt`.
        * `help` - corresponds to `self.help`.
        '''


class CallError:
    '''
    An exception to raise when there is an error during parsing or execution.
    '''

    @property
    def text(self) -> 'str':
        '''
        The error text.

        Defaults:
        * `''`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        '''

    @text.setter
    def text(self, v: 'str | None') -> 'None':
        ...

    @property
    def code(self) -> 'int':
        '''
        The error exit code.

        Defaults:
        * `1`.

        Exceptions:
        * `TypeError`, if the type is not `str` or `None`.
        * `ValueError`, if the value is not in range `[0; 255]`.
        '''

    @code.setter
    def code(self, v: 'int | None') -> 'None':
        ...

    def __init__(
        self,
        text: 'str | None' = None,
        code: 'int | None' = None,
    ) -> 'None':
        '''
        The constructor. Sets each field in the declaration order.

        Parameters:
        * `text` - corresponds to `self.text`.
        * `code` - corresponds to `self.code`.
        '''


def main(
    app: 'App',
    argv: 'list[str]' = sys.argv,
) -> 'None':
    '''
    A complete runtime of the command. It does the following:
    * Construction. `app` is translated to `argparse.ArgumentParser` and sanity checks are performed.
      `app.name` is set to `os.path.basename(argv[0])` if empty.
    * Parsing. `argv` is translated to `args` and `apps` for `App.__call__()`.
    * Execution. `sys.exit()` is always called, so there is no return. The flow depends on the presence of the help option:
       * If mentioned, only the text is printed to stdout.
       * If not mentioned, `x(args, apps)` is called for each `x` in `apps`.

    Parameters:
    * `app`  - an `App` to translate to `argparse.ArgumentParser`.
    * `argv` - the command line including the command name, defaults to `sys.argv`.

    Exceptions:
    * Construction. All exceptions are not intercepted.
       * `ValueError`, if any `App` has empty `App.name`.
       * `ValueError`, if any `App` have the same `App.name`.
       * `ValueError`, if any positional `Arg` has empty `Arg.name`.
       * `ValueError`, if any positional `Arg` have the same `Arg.name`.
       * `ValueError`, if any optional `Arg` or `App.helper` have the same `lopt` or `sopt`.
    * Parsing. `CallError` is intercepted and printed with the usage to stderr, followed by `sys.exit()`. Other exceptions are not intercepted.
       * `SystemExit`, on a custom `CallError` from `App.__call__()`, code `CallError.code`.
       * `SystemExit`, on a missing subcommand, code `1`.
       * `SystemExit`, on an unknown subcommand, code `1`.
       * `SystemExit`, on a missing argument, code `1`.
       * `SystemExit`, on an unknown argument, code `1`.
       * `SystemExit`, if there are less values, code `1`.
    * Execution. `CallError` is intercepted and printed to stderr, followed by `sys.exit()`. Other exceptions are not intercepted.
       * `SystemExit`, on a custom `CallError` from `App.__call__()`, code `CallError.code`.
       * `SystemExit`, on the help command, code `0`.
       * `SystemExit`, on execution without errors, code `0`.
    '''


def raise_t(
    value: 'object',
    types: 'type | tuple[type]',
    topic: 'str',
) -> 'None':
    '''
    Raise a consistently formatted `TypeError`.

    Parameters:
    * `value` - an `object` to check.
    * `types` - types to check against.
    * `topic` - a name or description of `value` that is being checked.

    Exceptions:
    * `TypeError`, if `type(value)` is not in `types`.
    '''


def raise_v(
    value: 'object',
    error: 'bool',
    topic: 'str',
    extra: 'str',
) -> 'None':
    '''
    Raise a consistently formatted `ValueError`.

    Parameters:
    * `value` - an `object` to mention as the actual value.
    * `error` - whether to raise, `True` or `False`.
    * `topic` - a name or description of `value` that is being checked.
    * `extra` - extra information, must be provided.

    Exceptions:
    * `ValueError`, if `error` is `True`.
    '''
