# Copyright (C) 2020 Patrick Godwin
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at
# <https://mozilla.org/MPL/2.0/>.
#
# SPDX-License-Identifier: MPL-2.0

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Callable, ClassVar, List, Optional, Union

from . import path

PROTECTED_CONDOR_VARS = {"input", "output", "rootdir"}


@dataclass
class Argument:
    """Defines a command-line argument (positional).

    This provides some extra functionality over defining command line
    argument explicitly, in addition to some extra parameters which
    sets how condor interprets how to handle them within the DAG
    and within submit descriptions.

    Parameters
    ----------
    name
        The option name. Since this is a positional argument, it is not
        used explicitly in the command, but is needed to define
        variable names within jobs.
    argument
        The positional argument value(s) used in a command.
    track
        Whether to track files defined here and used externally within
        jobs to determine parent-child relationships when nodes specify
        this option as an input or output. On by default.
    suppress
        Whether to hide this option. Used externally within jobs to
        determine whether to define job arguments. This is typically used
        when you want to track file I/O used by a job but isn't directly
        specified in their commands. Off by default.

    Examples
    --------
    >>> Argument("command", "run").vars()
    'run'

    >>> files = ["input_1.txt", "input_2.txt"]
    >>> Argument("input-files", files).vars()
    'input_1.txt input_2.txt'

    """

    name: str
    argument: Union[int, float, str, List]
    track: bool = True
    suppress: bool = False
    static: ClassVar[bool] = False
    _args: List[str] = field(init=False)

    def __post_init__(self) -> None:
        # check against list of protected condor names/characters,
        # rename condor variables name to avoid issues
        self.condor_name = self.name.replace("-", "_")
        if self.condor_name in PROTECTED_CONDOR_VARS:
            self.condor_name += "_"

        if isinstance(self.argument, str) or not isinstance(self.argument, Iterable):
            self.argument = [self.argument]
        self._args = [str(arg) for arg in self.argument]

    def args(self) -> List[str]:
        return self._args

    def vars(self, basename: Union[bool, Callable[[str], bool]] = False) -> str:
        args = []
        for arg in self._args:
            args.append(path.normalize(arg, basename))
        return " ".join(args)

    def files(self, basename: Union[bool, Callable[[str], bool]] = False) -> str:
        args = []
        for arg in self._args:
            args.append(path.normalize(arg, basename))
        return ",".join(args)

    def remaps(self) -> str:
        args = []
        for arg in self._args:
            if (normalized := path.normalize(arg, path.is_abs_or_url)) != arg:
                args.append(f"{normalized}={arg}")
        return ";".join(args)


@dataclass
class Option:
    """Defines a command-line option (long form).

    This provides some extra functionality over defining command line
    options explicitly, in addition to some extra parameters which
    sets how condor interprets how to handle them within the DAG
    and within submit descriptions.

    Parameters
    ----------
    name
        The option name to be used in a command.
    argument
        The argument value(s) used in a command.
    track
        Whether to track files defined here and used externally within
        jobs to determine parent-child relationships when nodes specify
        this option as an input or output. On by default.
    suppress
        Whether to hide this option. Used externally within jobs to
        determine whether to define job arguments. This is typically used
        when you want to track file I/O used by a job but isn't directly
        specified in their commands. Off by default.
    prefix
        The option prefix to use, e.g. for --verbose, -- is the prefix.
        Uses -- by default.

    Examples
    --------
    >>> Option("verbose").vars()
    '--verbose'

    >>> Option("input-type", "file").vars()
    '--input-type file'

    >>> Option("ifos", ["H1", "L1", "V1"]).vars()
    '--ifos H1 --ifos L1 --ifos V1'

    """

    name: str
    argument: Optional[Union[int, float, str, List]] = None
    track: Optional[bool] = True
    suppress: Optional[bool] = False
    prefix: Optional[str] = "--"
    static: ClassVar[bool] = False
    _args: List[str] = field(init=False)

    def __post_init__(self) -> None:
        # check against list of protected condor names/characters,
        # rename condor variables name to avoid issues
        self.condor_name = self.name.replace("-", "_")
        if self.condor_name in PROTECTED_CONDOR_VARS:
            self.condor_name += "_"

        if self.argument is not None:
            if isinstance(self.argument, str) or not isinstance(
                self.argument, Iterable
            ):
                self.argument = [self.argument]
            self._args = [str(arg) for arg in self.argument]

    def args(self) -> List[str]:
        return self._args

    def vars(self, basename: Union[bool, Callable[[str], bool]] = False) -> str:
        if self.argument is None:
            return f"{self.prefix}{self.name}"
        args = []
        for arg in self._args:
            args.append(f"{self.prefix}{self.name} {path.normalize(arg, basename)}")
        return " ".join(args)

    def files(self, basename: Union[bool, Callable[[str], bool]] = False) -> str:
        args = []
        for arg in self._args:
            args.append(path.normalize(arg, basename))
        return ",".join(args)

    def remaps(self) -> str:
        args = []
        for arg in self._args:
            if (normalized := path.normalize(arg, path.is_abs_or_url)) != arg:
                args.append(f"{normalized}={arg}")
        return ";".join(args)


@dataclass
class Literal:
    """Defines a command-line literal.

    This provides some extra functionality over defining command line
    argument explicitly, in addition to some extra parameters which
    sets how condor interprets how to handle them within the DAG
    and within submit descriptions.

    Parameters
    ----------
    argument
        The positional argument value(s) used in a command.
    track
        Whether to track files defined here and used externally within
        jobs to determine parent-child relationships when nodes specify
        this option as an input or output. On by default.

    Examples
    --------
    >>> Literal("run").vars()
    'run'

    >>> Literal("/path/to/input_1.txt").remaps()
    'input_1.txt=/path/to/input_1.txt'

    """

    argument: Union[int, float, str]
    track: bool = True
    static: ClassVar[bool] = True

    @property
    def name(self) -> str:
        return str(self.argument)

    def args(self) -> List[str]:
        return [self.name]

    def vars(self, basename: Union[bool, Callable[[str], bool]] = False) -> str:
        return path.normalize(self.name, basename)

    def files(self, basename: Union[bool, Callable[[str], bool]] = False) -> str:
        return path.normalize(self.name, basename)

    def remaps(self) -> str:
        if (normalized := path.normalize(self.name, path.is_abs_or_url)) != self.name:
            return f"{normalized}={self.name}"
        else:
            return ""
