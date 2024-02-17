"""
generate command:

- parse args.
- load templates from paths
- generate selected template


license-tool generate --license=apache copyright_year="YYYY" copyright_owner=""

license-tool generate --search --data=file:data.toml --license=apache

data.toml:
copyright_year="YYYY"
copyright_owner=""
"""

# generic data class for templates
import importlib.resources as ILR
import sys
from argparse import ArgumentParser
from pathlib import Path

import toml
from licere.constants import BUILTIN_LICENSES
from licere.document import Document


def load_licenses_from_path(path: Path) -> list[Document]:
    # load the path/meta.py
    # call the licenses() function to get licenses
    # inject data and License so we don't need to import
    # builtin licenses need special handling for importlib
    meta_path = path / "meta.py"

    variables = {}
    a = exec(meta_path.read_text(), variables)
    licenses = variables.get("licenses")()

    for license in licenses:
        license.path = path

    return licenses


def load_builtin_licenses() -> list[Document]:
    all_licenses = []

    for package in BUILTIN_LICENSES:
        f = __import__(f"{package}.meta", fromlist=[None])
        licenses = f.licenses()

        for license in licenses:
            license.builtin = True
            license.package = package
        all_licenses.extend(licenses)

    return all_licenses


def _set(*args):
    return set(args)


def render_string(string, data):
    import jinja2
    environment = jinja2.Environment()
    environment.undefined = jinja2.StrictUndefined
    environment.globals["set"] = _set
    template = environment.from_string(string)
    return template.render(**data)


def render_template_filesystem(path, name, data):
    import jinja2
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(path))
    environment.undefined = jinja2.StrictUndefined
    environment.globals["set"] = _set
    template = environment.get_template(name)
    return template.render(**data)


def render_template(license: Document, data):
    return render_template_filesystem(license.path, license.template, data)


def render_template_builtin(license: Document, data):
    #text = ILR.read_text(license.package, license.template)
    text = ILR.files(license.package).joinpath(license.template).read_text()
    return render_string(text, data)


def load_licenses(args):

    all_licenses = []
    all_licenses.extend(load_builtin_licenses())

    for path in args.search:
        path = Path(path).resolve(strict=False)
        if not path.exists():
            print(f"Missing search path {path}")
            sys.exit(-1)

        all_licenses.extend(load_licenses_from_path(path))
    return all_licenses


def main_generate(args, extra_args):

    all_licenses = load_licenses(args)

    name_map = {}

    # create mapping of aliases -> License
    alias_map = {}

    for l in all_licenses:
        for alias in l.aliases:
            alias_map[alias] = l

    # search in aliases and titles for matching license
    license = alias_map.get(args.license, name_map.get(args.license, None))

    if license is None:
        print(f"No license named: {args.license}")
        sys.exit(-1)

    all_data = {"license": license, **license.data}

    if args.data:
        for data in args.data:
            if data.startswith("file:"):
                path = Path(data[5:]).resolve(strict=False)
                if not path.exists():
                    print("Missing data file")
                    sys.exit(-1)
                if path.suffix in {".toml"}:
                    with path.open("r") as f:
                        d = toml.load(f)
                        all_data.update(d)
            else:
                pass

    for arg in extra_args:
        name, value = arg.split("=")
        all_data[name] = value

    names = []
    for required in license.requires:
        if required not in all_data:
            names.append(required)

    if names:
        for name in names:
            print(f"Undefined template variable: {name}")
        sys.exit(-1)

    #print("Rendering template", license.template)

    if license.builtin:
        rendered = render_template_builtin(license, all_data)
    else:
        rendered = render_template(license, all_data)

    file = None
    if args.file:
        file = open(Path(args.file).resolve())

    print(rendered, file=file)


def main_list(args, extra):
    all_licenses = load_licenses(args)

    for license in all_licenses:
        print(license.name, ":", license.aliases)


def parser():
    parser = ArgumentParser(
        prog="licere",
        description="""Generate licenses.""",
        epilog="""""",
    )

    subparsers = parser.add_subparsers(
        dest='command',
        title="commands",
        description="Valid commands",
        help="Commands you may enter.",
        required=True,
    )
    subparser = subparsers.add_parser(
        "generate", help="Generate a document.", description="Generate a document."
    )
    subparser.add_argument("--search", nargs="*", default=[])
    subparser.add_argument("--data", nargs="*")
    subparser.add_argument("--license")
    subparser.add_argument("--file")

    subparser = subparsers.add_parser(
        "list", help="List documents to generate", description="List documents to generate"
    )
    subparser.add_argument("--search", nargs="*", default=[])

    return parser


COMMANDS = {
    "generate": main_generate,
    "list": main_list,
}


def main():
    p = parser()
    args, extra_args = p.parse_known_args()

    try:
        COMMANDS[args.command.replace("-", "_")](args, extra_args)
    finally:
        pass


if __name__ == "__main__":
    main()
