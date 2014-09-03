# {one line to give the program's name and a brief idea of what it does.}
# Copyright (C) {year}  {name of author}
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
import os
from pathlib import Path
import shutil

import click

'''notabene -- Note well

Stitch together individual note files with templates.
'''

VERSION = '0.0.1'
USER_DATA_DIR = Path(click.get_app_dir('notabene'))
USER_TEMPLATE = USER_DATA_DIR / 'template.tex'
PACKAGE_TEMPLATE = Path(__file__).resolve().parents[0] / 'template.tex'


@click.group()
def main():
    '''Stitch together individual note files with templates.'''

    # Ensure that the udser template exists before running any subcommands.
    try:
        if not USER_TEMPLATE.exists():
            if not USER_DATA_DIR.exists():
                USER_DATA_DIR.mkdir(parents=True)
            shutil.copyfile(str(PACKAGE_TEMPLATE), str(USER_TEMPLATE))
    except OSError as e:
        click.echo('Could not create user template ({0}): {1}'.format(USER_TEMPLATE, e.strerror), err=True)


@main.command(name='new')
@click.argument('subject')
@click.option('--edit', is_flag=True, help='Edit the template after intialization.')
def new_subject(subject, edit):
    '''Create and initialize a new subject directory in `SUBJECT'.'''

    subject_path = Path(subject)

    try:
        subject_path.mkdir()
    except OSError as e:
        click.echo('Could not initialize subject directory: {0}'.format(e.strerror), err=True)
        os.exit(1)

    template_path = subject_path / 'template.tex'

    try:
        shutil.copyfile(str(USER_TEMPLATE), str(template_path))
    except OSError as e:
        click.echo('Could not copy template: {0}'.format(e.strerror), err=True)
        os.exit(1)

    if edit:
        click.edit(filename=str(template_path))


@main.command()
@click.option('--editor', help='Specify the editor to use.')
def note(editor):
    '''Create a note for the current date and open it in your editor.

    If a note already exists for the current date, it is not overwritten.
    '''

    date = datetime.now()

    filename = Path(date.strftime('%Y-%m-%d.tex'))

    click.edit(editor=editor, filename=filename)
