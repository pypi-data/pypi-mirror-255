# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

"""Query a program's list of features."""

from __future__ import annotations

import argparse
import dataclasses
import sys
from typing import Final


try:
    import simplejson as js
except ImportError:
    import json as js  # type: ignore[no-redef]

from . import defs
from . import expr as fexpr
from . import obtain
from . import parser as fparser
from . import version as fver


@dataclasses.dataclass(frozen=True)
class Config:
    """Runtime configuration for this program."""

    args: list[str]
    display_version: bool
    features_prefix: str
    option_name: str
    output_format: str

    program: str = "(unknown)"


def version() -> None:
    """Display program version information."""
    print(f"feature-check {defs.VERSION}")


def features() -> None:
    """Display program features information."""
    print(f"{defs.DEFAULT_PREFIX}feature-check={defs.VERSION} single=1.0 list=1.0 simple=1.0")


def output_tsv(data: dict[str, fver.Version]) -> None:
    """List the obtained features as tab-separated name/value pairs."""
    for feature in sorted(data.keys()):
        print(f"{feature}\t{data[feature].value}")


def output_json(data: dict[str, fver.Version]) -> None:
    """List the obtained features as a JSON object."""
    print(
        js.dumps(
            {name: value.value for name, value in data.items()},
            sort_keys=True,
            indent=2,
        )
    )


OUTPUT = {"tsv": output_tsv, "json": output_json}


def process(mode: defs.Mode, cfg: Config, data: dict[str, fver.Version]) -> None:
    """Perform the requested feature-check operation."""
    match mode:
        case defs.ModeList():
            OUTPUT[cfg.output_format](data)

        case defs.ModeSingle(feature, _):
            if feature in data:
                if cfg.display_version:
                    print(data[feature].value)
                sys.exit(0)
            else:
                sys.exit(1)

        case defs.ModeSimple(ast):
            res: Final = ast.evaluate(data)
            if not isinstance(res, fexpr.ResultBool):
                sys.exit(f"Internal error: did not expect a {type(res).__name__} object")
            sys.exit(not res.value)

        case _:
            sys.exit(f"Internal error: process(mode={mode!r}, cfg={cfg!r}, data={data!r}")


def main() -> None:
    """Parse command-line arguments, do things."""
    parser: Final = argparse.ArgumentParser(
        prog="feature-check",
        usage="""
    feature-check [-v] [-O optname] [-P prefix] program feature
    feature-check [-O optname] [-P prefix] program feature op version
    feature-check [-O optname] [-o json|tsv] [-P prefix] -l program
    feature-check -V | -h""",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="display program version information and exit",
    )
    parser.add_argument(
        "--features",
        action="store_true",
        help="display supported features and exit",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list the features supported by a program",
    )
    parser.add_argument(
        "-O",
        "--option-name",
        type=str,
        default=defs.DEFAULT_OPTION,
        help="the query-features option to pass",
    )
    parser.add_argument(
        "-o",
        "--output-format",
        default=defs.DEFAULT_OUTPUT_FMT,
        choices=sorted(OUTPUT.keys()),
        help="specify the output format for the list",
    )
    parser.add_argument(
        "-P",
        "--features-prefix",
        type=str,
        default=defs.DEFAULT_PREFIX,
        help="the features prefix in the program output",
    )
    parser.add_argument(
        "-v",
        "--display-version",
        action="store_true",
        help="display the feature version",
    )
    parser.add_argument("args", nargs="*", help="the program and features to test")

    args: Final = parser.parse_args()
    if args.version:
        version()
        sys.exit(0)
    if args.features:
        features()
        sys.exit(0)

    program: Final[str | None] = args.args.pop(0) if args.args else None
    cfg = Config(
        args=args.args,
        display_version=args.display_version,
        features_prefix=args.features_prefix,
        option_name=args.option_name,
        output_format=args.output_format,
    )

    if args.list:
        if program is None:
            parser.error("No program specified")
        cfg = dataclasses.replace(cfg, program=program)
        mode: defs.Mode = defs.ModeList()
    else:
        if program is None or len(cfg.args) < 1:
            parser.error("No program or feature specified")
        cfg = dataclasses.replace(cfg, program=program)
        expr = " ".join(cfg.args)
        try:
            mode = fparser.parse_expr(expr)
        except fparser.ParseError:
            parser.error("Only querying a single feature supported so far")

    try:
        data: Final = obtain.obtain_features(cfg.program, cfg.option_name, cfg.features_prefix)
    except obtain.ObtainError as exc:
        sys.exit(exc.code)

    process(mode, cfg, data)


if __name__ == "__main__":
    main()
