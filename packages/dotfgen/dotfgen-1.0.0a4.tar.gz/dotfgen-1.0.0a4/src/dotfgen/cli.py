# SPDX-FileCopyrightText: 2019 Rémy Taymans <remytms@tsmail.eu>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Generate dotfiles based on templates.
"""

import os
from os.path import expanduser
from pathlib import Path

import click
import sh
import yaml
from jinja2 import Template

TPL_SUFFIX = ".dftpl"
TPL_VALUES = "~/.dotfgen.yml"
XDG_CONFIG_HOME = os.environ.get(
    "XDG_CONFIG_HOME",
    str(Path.home() / ".config"),
)


def complete_tpls_search(ctx, args, incomplete):
    """
    Search all the templates found in:
        - ~/.config recursively
        - $XDG_CONFIG_HOME recursively
        - ~ not recursively
    Return only templates containing :incomplete in their path or name.
    """


def complete_tpls_recursive(ctx, args, incomplete):
    """
    Search for all the templates in the deepest directory found in
    :incomplete and that match the rest of the :incomplete when the
    deepest directory is substracted. Return a list of the result.
    """
    p = Path(incomplete).expanduser()
    if p.is_dir():
        cur_dir = p
        pattern = ""
    else:
        cur_dir = p.parent
        pattern = p.name
    return [
        str(f)
        for f in cur_dir.glob(f"**/*{TPL_SUFFIX}")
        if pattern in str(f.name)
    ]


def complete_tpls(ctx, args, incomplete):
    """
    Return a list of directories and templates contained in the deepest
    directory found in :incomplete and that match the rest of the
    :incomplete when the deepest directory is substracted. If the
    deepest directory is equal to XDG_CONFIG_HOME, than the search is
    done recursively.
    """
    p = Path(incomplete).expanduser()
    if p.is_dir():
        cur_dir = p
        pattern = ""
    else:
        cur_dir = p.parent
        pattern = p.name
    if cur_dir == Path(XDG_CONFIG_HOME):
        return complete_tpls_recursive(ctx, args, incomplete)
    return [
        str(f)
        for f in cur_dir.iterdir()
        if ((f.is_dir() or f.suffix == TPL_SUFFIX) and pattern in str(f.name))
    ]


@click.command()
@click.argument(
    "templates",
    type=click.Path(exists=True),
    nargs=-1,
    shell_complete=complete_tpls,
)
def main(templates):
    """
    Generate dotfiles based on templates.

    If TEMPLATES are given then only this templates will be used to
    generate config files. If no TEMPLATES is given then templates are
    searched in the dotfiles directory. The templates given in TEMPlATES
    must end with the `.dftpl` extension.

    Create a ~/.dotfgen.yml file that contain values for the templates.
    Create your templates of config file with a `.dftpl` extension.
    Run this script.
    """
    click.echo("Generating config file based on templates…")
    if templates:
        # Get templates from arguments
        df_names = list(templates)
    else:
        # Get dotfiles templates names
        df_names = sh.dotfiles("-l").split("\n")
        df_names = [fn.strip() for fn in df_names]
    # Filter to keep only templates with the TPL_SUFFIX extension
    dftpl_names = [fn for fn in df_names if fn.endswith(TPL_SUFFIX)]

    # Get dotfiles templates content
    dftpls = []
    for dftpl_name in dftpl_names:
        with open(expanduser(dftpl_name), "r", encoding="uft8") as file:
            dftpls.append(file.read())

    # Get values for templates
    with open(expanduser(TPL_VALUES), "r", encoding="utf8") as file:
        tpl_values = yaml.safe_load(file)

    # Generate new config files
    cfiles = [Template(dftpl).render(tpl_values) for dftpl in dftpls]

    # Write new config files
    for cfile, dftpl_name in zip(cfiles, dftpl_names):
        filename = dftpl_name[: -len(TPL_SUFFIX)]  # Remove suffix
        click.echo(f"Writing to : {filename}")
        with open(expanduser(filename), "w", encoding="utf8") as file:
            file.write(cfile)
    click.echo("Done")
