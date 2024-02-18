import os
import sys
from argparse import Action, ArgumentParser, REMAINDER, SUPPRESS
from typing import Iterable


try:
    from argcomplete.completers import BaseCompleter as Completer
    from argcomplete.completers import SuppressCompleter as CompleterNone
    from argcomplete.completers import ChoicesCompleter as CompleterList
    from argcomplete.completers import FilesCompleter as CompleterPath
    from argcomplete import autocomplete
except:
    class Completer:
        def __init__(self) -> 'None':
            ...

        def __call__(self, *args, **kwds) -> 'list[str]':
            ...

    class CompleterNone(Completer):
        def __init__(self) -> 'None':
            ...

        def __call__(self, *args, **kwds) -> 'list[str]':
            ...

    class CompleterList(Completer):
        def __init__(self, v: 'list[str]') -> 'None':
            ...

        def __call__(self, *args, **kwds) -> 'list[str]':
            ...

    class CompleterPath(Completer):
        def __init__(self) -> 'None':
            ...

        def __call__(self, *args, **kwds) -> 'list[str]':
            ...

    def autocomplete(*args, **kwds) -> 'None':
        ...


class Arg:
    @property
    def name(self) -> 'str':
        return self.__name

    @name.setter
    def name(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'Arg.name')
        # Set.
        self.___name = v or ''
        self.__name = self.___name or self.lopt.upper() or self.sopt.upper()

    @property
    def lopt(self) -> 'str':
        return self.__lopt

    @lopt.setter
    def lopt(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'Arg.lopt')
        # Set.
        self.__lopt = v or ''
        self.name = self.___name
        self.suppress = self.__suppress
        self.required = self.__required
        self.append = self.__append

    @property
    def sopt(self) -> 'str':
        return self.__sopt

    @sopt.setter
    def sopt(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'Arg.sopt')
        raise_v(f'"{v}"',
                len(v or '') > 1,
                'Arg.sopt',
                'Must not exceed one character.')
        # Set.
        self.__sopt = v or ''
        self.name = self.___name
        self.suppress = self.__suppress
        self.required = self.__required
        self.append = self.__append

    @property
    def help(self) -> 'str':
        return self.__help

    @help.setter
    def help(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'Arg.help')
        # Set.
        self.__help = v or ''

    @property
    def helper(self) -> 'ArgHelper':
        return self.__helper

    @helper.setter
    def helper(self, v: 'ArgHelper | None') -> 'None':
        # Validate.
        raise_t(v, (ArgHelper, type(None)), 'Arg.helper')
        # Set.
        self.__helper = v or ArgHelper()

    @property
    def type(self) -> 'type':
        return self.__type

    @type.setter
    def type(self, v: 'type | None') -> 'None':
        # Validate.
        V = 'Arg.type'
        raise_t(v, (type, type(None)), V)
        if v is not None:
            M = f'Must match self.default:'
            if isinstance(self.default, list) and self.default:
                M = f'{M} {type(self.default[0]).__name__}.'
                raise_v(v.__name__, not isinstance(self.default[0], v), V, M)
            elif not isinstance(self.default, list) and self.default is not None:
                M = f'{M} {type(self.default).__name__}.'
                raise_v(v.__name__, not isinstance(self.default, v), V, M)
        # Set.
        self.___type = v
        self.__type = self.___type
        if self.flag:
            self.__type = bool
        elif self.__type is None:
            if isinstance(self.default, list) and self.default:
                self.__type = type(self.default[0])
            elif not isinstance(self.default, list) and self.default is not None:
                self.__type = type(self.default)
            else:
                self.__type = str
        if self.___completer is None:
            self.completer = None

    @property
    def count(self) -> 'int | str':
        return self.__count

    @count.setter
    def count(self, v: 'int | str | None') -> 'None':
        # Validate.
        V = 'Arg.count'
        raise_t(v, (int, str, type(None)), V)
        if self.optional:
            if isinstance(v, int):
                M = f'Must be non-negative for optional.'
                raise_v(v, v < 0, V, M)
            if isinstance(v, str):
                M = f'Must be "?", "*" or "+" for optional.'
                raise_v(f'"{v}"', v not in ['?', '*', '+'], V, M)
        if self.positional:
            if isinstance(v, int):
                M = f'Must be positive for positional.'
                raise_v(v, v <= 0, V, M)
            if isinstance(v, str):
                M = f'Must be "?", "*", "+" or "~" for positional.'
                raise_v(f'"{v}"', v not in ['?', '*', '+', '~'], V, M)
        if isinstance(self.default, list):
            l = len(self.default)
            if v == '+':
                M = f'Must allow zero values, self.default is empty.'
                raise_v(f'"{v}"', l == 0, V, M)
            if isinstance(v, int):
                M = f'Must match the number of values in self.default: {l}.'
                raise_v(v, v != l, V, M)
        # Set.
        self.___count = v
        v = self.__count
        self.__count = self.___count
        if self.__count is None:
            self.__count = '*' if isinstance(self.default, list) else 1
        self.type = self.___type
        if self.___default is None and self.__count is not v:
            self.default = None

    @property
    def default(self) -> 'object | list | None':
        return self.__default

    @default.setter
    def default(self, v: 'object | list | None') -> 'None':
        # Validate.
        V = 'Arg.default'
        if isinstance(v, Iterable) and not isinstance(v, str):
            v = [x for x in v]
        if self.___type is not None:
            if isinstance(v, list):
                for i in range(len(v)):
                    raise_t(v[i], self.type, f'{V}[{i}]')
            else:
                raise_t(v, (self.type, type(None)), V)
        if self.___count is not None:
            if isinstance(v, list):
                if self.single:
                    raise TypeError(
                        f'{V}: Invalid type: list. Must be: object, None.')
                if isinstance(self.count, int):
                    M = f'Must match self.count: {self.count}.'
                    O = Exception(f'len() is {len(v)}')
                    raise_v(O, len(v) != self.count, V, M)
                elif self.count == '+':
                    M = 'Must have at least one item, self.count is "+".'
                    raise_v(v, not v, V, M)
            elif self.multiple:
                raise_t(v, (list, type(None)), V)
        # Set.
        self.___default = v
        self.__default = self.___default
        if self.__default is None:
            if self.flag:
                self.__default = False
            elif self.___count in ['*', '~']:
                self.__default = []
        if self.___count is None:
            self.count = None
        if self.___type is None:
            self.type = None

    @property
    def choices(self) -> 'dict[str, str]':
        return self.__choices

    @choices.setter
    def choices(self, v: 'list | dict | None') -> 'None':
        # Validate.
        raise_t(v, (Iterable, type(None)), 'Arg.choices')
        # Set.
        self.__choices = {}
        if isinstance(v, dict):
            self.__choices = {str(x): str(y) for x, y in v.items()}
        elif v:
            self.__choices = {str(x): '' for x in v}
        if self.___completer is None:
            self.completer = None

    @property
    def restrict(self) -> 'bool':
        return self.__restrict

    @restrict.setter
    def restrict(self, v: 'bool | None') -> 'None':
        # Validate.
        raise_t(v, (bool, type(None)), 'Arg.restrict')
        # Set.
        self.__restrict = True if v is None else v

    @property
    def suppress(self) -> 'bool':
        return self.__suppress

    @suppress.setter
    def suppress(self, v: 'bool | None') -> 'None':
        # Validate.
        raise_t(v, (bool, type(None)), 'Arg.suppress')
        # Set.
        self.__suppress = False if self.positional else bool(v)

    @property
    def required(self) -> 'bool':
        return self.__required

    @required.setter
    def required(self, v: 'bool | None') -> 'None':
        # Validate.
        raise_t(v, (bool, type(None)), 'Arg.required')
        # Set.
        self.__required = self.positional or bool(v)

    @property
    def append(self) -> 'bool':
        return self.__append

    @append.setter
    def append(self, v: 'bool | None') -> 'None':
        # Validate.
        raise_t(v, (bool, type(None)), 'Arg.append')
        # Set.
        self.__append = False if self.positional else bool(v)

    @property
    def completer(self) -> 'Completer':
        return self.__completer

    @completer.setter
    def completer(self, v: 'Completer | None') -> 'None':
        # Validate.
        raise_t(v, (Completer, type(None)), 'Arg.completer')
        # Set.
        self.___completer = v
        self.__completer = self.___completer
        if self.__completer is None:
            if self.choices:
                self.__completer = CompleterList(self.choices)
            elif issubclass(self.type, str):
                self.__completer = CompleterPath()
            else:
                self.__completer = CompleterNone()

    @property
    def optional(self) -> 'bool':
        return bool(self.sopt or self.lopt)

    @property
    def positional(self) -> 'bool':
        return not self.optional

    @property
    def flag(self) -> 'bool':
        return self.count == 0

    @property
    def single(self) -> 'bool':
        return self.count == 1 or self.count == '?'

    @property
    def multiple(self) -> 'bool':
        return not (self.flag or self.single)

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
        # Actual value.
        self.___name: 'str | None' = None
        # No lopt.
        # No sopt.
        # No help.
        # No helper.
        self.___type: 'type | None' = None
        self.___count: 'int | str | None' = None
        self.___default: 'object | list | None' = None
        # No choices.
        # No restrict.
        # No suppress.
        # No required.
        # No append.
        self.___completer: 'Completer | None' = None
        # Cached value.
        self.__name: 'str' = ''
        self.__lopt: 'str' = ''
        self.__sopt: 'str' = ''
        self.__help: 'str' = ''
        self.__helper: 'ArgHelper' = ArgHelper()
        self.__type: 'type' = str
        self.__count: 'int | str' = 1
        self.__default: 'object | list | None' = None
        self.__choices: 'dict[str, str]' = {}
        self.__restrict: 'bool' = True
        self.__suppress: 'bool' = False
        self.__required: 'bool' = True
        self.__append: 'bool' = False
        self.__completer: 'Completer' = CompleterPath()
        # Set the fields.
        self.name = name
        self.lopt = lopt
        self.sopt = sopt
        self.help = help
        self.helper = helper
        self.type = type
        self.count = count
        self.default = default
        self.choices = choices
        self.restrict = restrict
        self.suppress = suppress
        self.required = required
        self.append = append
        self.completer = completer

    def __call__(
        self,
        v: 'bool | int | str | list | list[list] | None',
    ) -> 'bool | int | object | list | list[list] | None':
        if self.flag:
            if not self.append:
                return self.__call___bool(v)
            else:
                return self.__call___int(v)
        if self.single:
            if not self.append:
                return self.__call___str(v)
            else:
                return self.__call___list(v)
        if self.multiple:
            if not self.append:
                return self.__call___list_str(v)
            else:
                return self.__call___list_list(v)

    def __call___bool(self, v: 'bool') -> 'bool':
        return not self.default if v else self.default

    def __call___int(self, v: 'int') -> 'int':
        return v

    def __call___str(self, v: 'str | None') -> 'object | None':
        if self.restrict and self.choices:
            if v is not None and v not in self.choices:
                raise CallError(
                    f'Invalid value of argument {self.__strname()}: {v}. '
                    f'Must be one of:{self.__strchoices()}',
                    1)
        return self.default if v is None else self.type(v)

    def __call___list(self, v: 'list[str | None]') -> 'list[object | None]':
        if self.restrict and self.choices:
            for i in range(len(v)):
                if v[i] is not None and v[i] not in self.choices:
                    raise CallError(
                        f'Invalid value of argument {self.__strname()}[{i}]: {v[i]}. '
                        f'Must be one of:{self.__strchoices()}',
                        1)
        return [self.default if x is None else self.type(x) for x in v]

    def __call___list_str(self, v: 'list[str] | None') -> 'list[object] | None':
        if self.restrict and self.choices and v is not None:
            for i in range(len(v)):
                if v[i] not in self.choices:
                    raise CallError(
                        f'Invalid value of argument {self.__strname()}[{i}]: {v[i]}. '
                        f'Must be one of:{self.__strchoices()}',
                        1)
        return self.default if v is None else [self.type(x) for x in v]

    def __call___list_list(self, v: 'list[list[str] | None]') -> 'list[list[object] | None]':
        if self.restrict and self.choices:
            for i in range(len(v)):
                for j in range(len(v[i] if v[i] else [])):
                    if v[i][j] not in self.choices:
                        raise CallError(
                            f'Invalid value of argument {self.__strname()}[{i}][{j}]: {v[i][j]}. '
                            f'Must be one of:{self.__strchoices()}',
                            1)
        return [(self.default if not l else [self.type(x) for x in l]) for l in v]

    def __strname(self) -> 'str':
        if self.lopt:
            return f'--{self.lopt}'
        if self.sopt:
            return f'-{self.sopt}'
        return self.name

    def __strchoices(self) -> 'str':
        return '\n * ' + '\n * '.join(self.choices)


class App:
    @property
    def name(self) -> 'str':
        return self.__name

    @name.setter
    def name(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'App.name')
        # Set.
        self.__name = v or ''

    @property
    def help(self) -> 'str':
        return self.__help

    @help.setter
    def help(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'App.help')
        # Set.
        self.__help = v or ''

    @property
    def prolog(self) -> 'str':
        return self.__prolog

    @prolog.setter
    def prolog(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'App.prolog')
        # Set.
        self.__prolog = v or self.help

    @property
    def epilog(self) -> 'str':
        return self.__epilog

    @epilog.setter
    def epilog(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'App.epilog')
        # Set.
        self.__epilog = v or ''

    @property
    def helper(self) -> 'AppHelper':
        return self.__helper

    @helper.setter
    def helper(self, v: 'AppHelper | None') -> 'None':
        # Validate.
        raise_t(v, (AppHelper, type(None)), 'App.helper')
        # Set.
        self.__helper = v or AppHelper()

    @property
    def args(self) -> 'list[Arg]':
        return self.__args

    @property
    def apps(self) -> 'list[App]':
        return self.__apps

    def __init__(
        self,
        name: 'str | None' = None,
        help: 'str | None' = None,
        prolog: 'str | None' = None,
        epilog: 'str | None' = None,
        helper: 'AppHelper | None' = None,
    ) -> 'None':
        self.__name = ''
        self.__help = ''
        self.__prolog = ''
        self.__epilog = ''
        self.__helper = AppHelper()
        self.__args = []
        self.__apps = []
        self.name = name
        self.help = help
        self.prolog = prolog
        self.epilog = epilog
        self.helper = helper

    def __call__(
        self,
        args: 'dict[Arg]',
        apps: 'list[App]',
    ) -> 'None':
        ...


class ArgHelper:
    @property
    def choices(self) -> 'bool':
        return self.__choices

    @choices.setter
    def choices(self, v: 'bool | None') -> 'None':
        # Validate.
        raise_t(v, (bool, type(None)), 'ArgHelper.choices')
        # Set.
        self.__choices = True if v is None else v

    @property
    def default(self) -> 'bool':
        return self.__default

    @default.setter
    def default(self, v: 'bool | None') -> 'None':
        # Validate.
        raise_t(v, (bool, type(None)), 'ArgHelper.default')
        # Set.
        self.__default = True if v is None else v

    def text_help(self, arg: 'Arg') -> 'str':
        result = arg.help
        # Do not append anything for flag.
        if arg.flag:
            return result
        # Append default.
        if self.default and arg.default is not None and arg.default != []:
            if result:
                result += '\n'
            result += 'Default: '
            items = [arg.default] if arg.single else arg.default
            result += ' '.join('""' if x == '' else str(x) for x in items)
        # Append choices.
        if self.choices and arg.choices:
            if result:
                result += '\n'
            if arg.restrict:
                result += 'Allowed values:'
            else:
                result += 'Possible values:'
            w = max(len(x) for x in arg.choices)
            p = ' ' * (w + 6)
            for x, y in arg.choices.items():
                if y:
                    result += f'\n * {x:{w}}'
                    lines = y.split('\n')
                    result += f' - {lines[0]}'
                    for i in range(1, len(lines)):
                        result += f'\n{p}{lines[i]}'
                else:
                    result += f'\n * {x}'
        return result

    def text_usage(self, arg: 'Arg') -> 'str':
        result = ''
        if arg.sopt:
            result += f'-{arg.sopt}'
        if arg.lopt:
            if result:
                result += '/'
            result += f'--{arg.lopt}'
        result += ' '
        if isinstance(arg.count, int):
            result += ' '.join([arg.name] * arg.count)
        elif arg.count == '?':
            result += f'[{arg.name}]'
        elif arg.count == '*':
            result += f'[{arg.name}...]'
        elif arg.count == '+':
            result += f'{arg.name} [{arg.name}...]'
        elif arg.count == '~':
            result += f'[{arg.name}]...'
        return result.strip(' ')

    def __init__(
        self,
        choices: 'bool | None' = None,
        default: 'bool | None' = None,
    ) -> 'None':
        self.__choices = None
        self.__default = None
        self.choices = choices
        self.default = default


class AppHelper:
    @property
    def lopt(self) -> 'str':
        return self.__lopt

    @lopt.setter
    def lopt(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'AppHelper.lopt')
        # Set.
        self.__lopt = v or ''

    @property
    def sopt(self) -> 'str':
        return self.__sopt

    @sopt.setter
    def sopt(self, v: 'str | None') -> 'None':
        # Validate.
        V = 'AppHelper.sopt'
        raise_t(v, (str, type(None)), V)
        raise_v(f'"{v}"',
                len(v or '') > 1,
                V,
                'Must not exceed one character.')
        # Set.
        self.__sopt = v or ''

    @property
    def help(self) -> 'str':
        return self.__help

    @help.setter
    def help(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'AppHelper.help')
        # Set.
        self.__help = v or ''

    def text_help(
        self,
        apps: 'list[App]',
        name: 'str',
    ) -> 'str':
        parts = [self.text_usage(apps, name)]
        parts.append(apps[-1].prolog)
        parts.append(self.section_apps('Commands', apps[-1].apps))
        args = [x for x in apps[-1].args if x.positional]
        parts.append(self.section_args('Positional arguments', args))
        args = [x for x in apps[-1].args if x.optional]
        if self.sopt or self.lopt:
            args.append(Arg(
                lopt=self.lopt,
                sopt=self.sopt,
                help=self.help,
                count=0,
            ))
        parts.append(self.section_args('Optional arguments', args))
        parts.append(apps[-1].epilog)
        parts = [x for x in parts if x]
        return '\n\n'.join(parts) + '\n'

    def text_usage(
        self,
        apps: 'list[App]',
        name: 'str',
    ) -> 'str':
        names = [x.name for x in apps]
        names[0] = names[0] or name
        result = ' '.join(names)
        args_opt = [x for x in apps[-1].args if x.required and x.optional]
        args_pos = [x for x in apps[-1].args if x.positional]
        if args_opt:
            result += ' ' + ' '.join(
                [f'{{{x.helper.text_usage(x)}}}' for x in args_opt])
        if args_pos:
            result += ' ' + ' '.join(
                [x.helper.text_usage(x) for x in args_pos])
        if apps[-1].apps:
            result += ' {...}'
        return result

    def section_apps(
        self,
        title: 'str',
        apps: 'list[App]',
    ) -> 'str':
        if not apps:
            return ''
        result = f'{title}:' if title else ''
        w = max(len(str(x.name)) for x in apps)
        p = ' ' * (w + 6)
        for app in apps:
            if app.help:
                result += f'\n  {app.name:{w}}'
                lines = app.help.split('\n')
                result += f'    {lines[0]}'
                for i in range(1, len(lines)):
                    result += f'\n{p}{lines[i]}'
            else:
                result += f'\n  {app.name}'
        return result.lstrip('\n')

    def section_args(
        self,
        title: 'str',
        args: 'list[Arg]',
    ) -> 'str':
        if not args:
            return ''
        result = f'{title}:' if title else ''
        info = {x.helper.text_usage(x): x.helper.text_help(x) for x in args}
        w = max(len(x) for x in info)
        p = ' ' * (w + 6)
        for name, help in info.items():
            if help:
                result += f'\n  {name:{w}}'
                lines = help.split('\n')
                result += f'    {lines[0]}'
                for i in range(1, len(lines)):
                    result += f'\n{p}{lines[i]}'
            else:
                result += f'\n  {name}'
        return result.lstrip('\n')

    def __init__(
        self,
        lopt: 'str | None' = 'help',
        sopt: 'str | None' = 'h',
        help: 'str | None' = 'Show the help text and exit.',
    ) -> 'None':
        self.lopt = lopt
        self.sopt = sopt
        self.help = help


class CallError(RuntimeError):
    @property
    def text(self) -> 'str':
        return self.__text

    @text.setter
    def text(self, v: 'str | None') -> 'None':
        # Validate.
        raise_t(v, (str, type(None)), 'CallError.text')
        # Set.
        self.__text = v or ''

    @property
    def code(self) -> 'int':
        return self.__code

    @code.setter
    def code(self, v: 'int | None') -> 'None':
        # Validate.
        V = 'CallError.code'
        raise_t(v, (int, type(None)), V)
        if v is not None:
            raise_v(
                v,
                v < 0 or v > 255,
                V,
                'Must be from 0 to 255.',
            )
        # Set.
        self.__code = 1 if v is None else v

    def __init__(
        self,
        text: 'str | None' = None,
        code: 'int | None' = None,
    ) -> 'None':
        self.text = text
        self.code = code


class Help(Action):
    def __init__(self, *args, **kwds) -> 'None':
        self.apps: 'list[App]' = kwds.pop('apps')
        super().__init__(*args, **kwds)

    def __call__(self, *args, **kwds) -> 'None':
        print(self.apps[-1].helper.text_help(self.apps, ''))
        sys.exit(0)


class Parser(ArgumentParser):
    def __init__(self, *args, **kwds) -> 'None':
        apps: 'list[App]' = [x for x in kwds.pop('apps')]
        self.apps = apps
        super().__init__(*args, **kwds)
        self.app = self.apps[-1]
        # Validate.
        for i in range(len(self.app.apps)):
            self.init_validate_app(i)
        for i in range(len(self.app.args)):
            self.init_validate_arg(i)
        # Add help.
        args = []
        if self.app.helper.sopt:
            args.append(f'-{self.app.helper.sopt}')
        if self.app.helper.lopt:
            args.append(f'--{self.app.helper.lopt}')
        if args:
            self.add_argument(*args, action=Help, nargs=0, apps=self.apps)
        # Add args.
        for arg in self.app.args:
            self.init_add_arg(arg)
        # Add apps.
        if self.app.apps:
            self.sub = self.add_subparsers(
                dest=str(id(self.app)),
                metavar='{...}',
            )
            self.sub.required = True
            for app in self.app.apps:
                self.init_add_app(app)

    def parse(self, argv: 'list[str]') -> 'tuple[dict[Arg], list[App]]':
        ns = self.parse_args(argv[1:])
        # apps
        apps: 'list[App]' = []
        cmd = self.app
        while True:
            apps.append(cmd)
            name = getattr(ns, str(id(cmd)), None)
            if name is None:
                break
            for app in cmd.apps:
                if app.name == name:
                    cmd = app
                    break
        # args
        args: 'dict[Arg]' = {}
        for app in apps:
            for arg in app.args:
                vid = str(id(arg))
                if not hasattr(ns, vid):
                    continue
                v = getattr(ns, vid)
                try:
                    if arg.append:
                        if arg.flag:
                            args[arg] = arg(v or 0)
                        else:
                            args[arg] = arg(v or [])
                    else:
                        if arg.flag:
                            args[arg] = arg(bool(v))
                        else:
                            args[arg] = arg(v if v != [] else None)
                except CallError as e:
                    self.error(e)
        # Return the result.
        return (args, apps)

    def error(self, message: 'str | CallError') -> 'None':
        usage = self.app.helper.text_usage(self.apps, '')
        code = 1
        if isinstance(message, CallError):
            code = message.code
            message = message.text
        elif 'arguments are required' in message:
            message = self.error_missing(message)
        elif 'unrecognized arguments' in message:
            message = self.error_unknown(message)
        elif 'invalid choice' in message:
            message = self.error_choices(message)
        elif 'expected' in message:
            message = self.error_values(message)
        raise CallError(f'{usage}\n\n{message}', code)

    def init_validate_app(self, i: 'int') -> 'None':
        topic = 'main'
        app = self.app.apps[i]
        raise_v(
            value=self.app.name,
            error=bool(not app.name),
            topic=topic,
            extra=f'apps[{i}].name is empty.',
        )
        for j in range(i + 1, len(self.app.apps)):
            raise_v(
                value=self.app.name,
                error=(app.name == self.app.apps[j].name),
                topic=topic,
                extra=f'apps[{i}] and apps[{j}] have the same name: "{app.name}".',
            )

    def init_validate_arg(self, i: 'int') -> 'None':
        topic = 'main'
        arg = self.app.args[i]
        raise_v(
            value=self.app.name,
            error=bool(not arg.name),
            topic=topic,
            extra=f'args[{i}].name is empty.',
        )
        raise_v(
            value=self.app.name,
            error=(arg.lopt == self.app.helper.lopt and arg.lopt),
            topic=topic,
            extra=f'args[{i}] and help have the same lopt: "{arg.lopt}".',
        )
        raise_v(
            value=self.app.name,
            error=(arg.sopt == self.app.helper.sopt and arg.sopt),
            topic=topic,
            extra=f'args[{i}] and help have the same sopt: "{arg.sopt}".',
        )
        for j in range(i + 1, len(self.app.args)):
            if arg.positional:
                raise_v(
                    value=self.app.name,
                    error=(arg.name == self.app.args[j].name),
                    topic=topic,
                    extra=f'args[{i}] and args[{j}] have the same name: "{arg.name}".',
                )
                continue
            raise_v(
                value=self.app.name,
                error=(arg.lopt == self.app.args[j].lopt and arg.lopt),
                topic=topic,
                extra=f'args[{i}] and args[{j}] have the same lopt: "{arg.lopt}".',
            )

            raise_v(
                value=self.app.name,
                error=(arg.sopt == self.app.args[j].sopt and arg.sopt),
                topic=topic,
                extra=f'args[{i}] and args[{j}] have the same sopt: "{arg.sopt}".',
            )

    def init_add_arg(self, arg: 'Arg') -> 'None':
        args = []
        kwds = {'dest': str(id(arg))}
        # lopt and sopt
        if arg.sopt:
            args.append(f'-{arg.sopt}')
        if arg.lopt:
            args.append(f'--{arg.lopt}')
        # metavar
        if not arg.flag:
            kwds['metavar'] = arg.name
        # nargs
        if arg.count == '~':
            kwds['nargs'] = REMAINDER
        elif arg.count != 1 and arg.count != 0:
            kwds['nargs'] = arg.count
        # action
        if arg.flag:
            kwds['action'] = 'count' if arg.append else 'store_true'
        elif arg.append:
            kwds['action'] = 'append'
        # suppress
        if arg.suppress:
            kwds['default'] = SUPPRESS
        # required
        if arg.optional and arg.required:
            kwds['required'] = True
        # Add argument and set the completer.
        self.add_argument(*args, **kwds).completer = arg.completer

    def init_add_app(self, app: 'App') -> 'None':
        self.apps.append(app)
        self.sub.add_parser(
            app.name,
            apps=self.apps,
            allow_abbrev=False,
            add_help=False,
        )
        self.apps.pop()

    def error_missing(self, message: 'str') -> 'str':
        names = message.split(':')[1].split(',')
        names = [x.strip() for x in names]
        if '{...}' in names:
            names.remove('{...}')
            if not names:
                message = '\n * '.join(x.name for x in self.app.apps)
                return f'Missing subcommand. Choose from:\n * {message}'
        return f'Missing arguments: {", ".join(names)}.'

    def error_choices(self, message: 'str') -> 'str':
        message = '\n * '.join(x.name for x in self.app.apps)
        return f'Invalid subcommand. Choose from:\n * {message}'

    def error_unknown(self, message: 'str') -> 'str':
        names = message.split(':')[1].split(' ')[1:]
        names = [x.strip() for x in names]
        return f'Unknown arguments: {", ".join(names)}.'

    def error_values(self, message: 'str') -> 'str':
        parts = message.split(' ')
        parts.pop(0)
        parts[-1] = 'value' if parts[-1] == 'argument' else 'values'
        return ' '.join(parts) + '.'


def main(
    app: 'App',
    argv: 'list[str]' = None,
) -> 'None':
    argv = argv or sys.argv
    argv = [str(x) for x in argv]
    if not app.name:
        app.name = os.path.basename(argv[0])
    # Construction.
    parser = Parser(
        app.name,
        apps=[app],
        allow_abbrev=False,
        add_help=False,
    )
    # Completion.
    autocomplete(
        argument_parser=parser,
        always_complete_options=False,
    )
    # Parsing.
    try:
        args, apps = parser.parse(argv)
    except CallError as e:
        print(e.text, file=sys.stderr)
        sys.exit(e.code)
    # Execution.
    try:
        for x in apps:
            x(args, apps)
    except CallError as e:
        print(e.text, file=sys.stderr)
        sys.exit(e.code)
    sys.exit(0)


def raise_t(
    value: 'object',
    types: 'type | tuple[type]',
    topic: 'str',
) -> 'None':
    def _name(t: 'type') -> 'str':
        name = getattr(t, '__name__', str(t))
        return name.split('.')[-1]

    if isinstance(types, type):
        types = (types,)
    if isinstance(value, types):
        return
    names = []
    for x in types:
        if x is type(None):
            names.append('None')
        else:
            names.append(_name(x))
    name = _name(type(value))
    raise TypeError(
        f'{topic}: Invalid type: {name}. '
        f'Must be: {", ".join(names)}.'
    )


def raise_v(
    value: 'object',
    error: 'bool',
    topic: 'str',
    extra: 'str',
) -> 'None':
    if not error:
        return
    raise ValueError(f'{topic}: Invalid value: {value}. {extra}')
