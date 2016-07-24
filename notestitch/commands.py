# notestitch -- Build sets of notes with PDFLatex.
# Copyright (C) 2014  Barret Rennie
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

import atexit
from datetime import datetime
import os
from pathlib import Path
import shutil
import subprocess
import sys

import click
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from lockfile import AlreadyLocked, LockFile

'''notestitch -- Note well

Stitch together individual note files with templates.
'''

VERSION = '0.0.1'
USER_DATA_DIR = Path(click.get_app_dir('notestitch'))
USER_TEMPLATE = USER_DATA_DIR / 'template.tex'
PACKAGE_TEMPLATE = Path(__file__).resolve().parents[0] / 'template.tex'


@click.group()
def main():
    '''Stitch together individual note files with templates.'''

    # Ensure that the user template exists before running any subcommands.
    try:
        if not USER_TEMPLATE.exists():
            if not USER_DATA_DIR.exists():
                USER_DATA_DIR.mkdir(parents=True)
            shutil.copyfile(str(PACKAGE_TEMPLATE), str(USER_TEMPLATE))
    except OSError as e:
        click.echo(
            'Could not create user template ({0}): {1}'.format(USER_TEMPLATE,
                                                               e.strerror),
            err=True)


@main.command()
@click.option('--edit', is_flag=True,
              help='Edit the template after intialization.')
def init(edit):
    '''Initialize a subject in the current directory.'''

    local_template = 'template.tex'

    try:
        shutil.copyfile(str(USER_TEMPLATE), local_template)
    except OSError as e:
        click.echo('Could not copy template: {0}'.format(e.strerror), err=True)
        sys.exit(1)

    if edit:
        click.edit(filename=local_template)


@main.command()
@click.option('--editor', help='Specify the editor to use.')
def note(editor):
    '''Create a note for the current date and open it in your editor.

    If a note already exists for the current date, it is not overwritten.
    '''

    date = datetime.now()

    filename = Path(date.strftime('%Y-%m-%d.tex'))

    click.edit(editor=editor, filename=filename)


@main.command()
@click.option('--date-range', nargs=2,
              help='Only build notes for the specific date range.')
@click.argument('date', nargs=-1)
def build(date_range, date):
    '''Build notes using pdflatex.

    Dates should be specified in ISO 8601 format: YYYY-MM-DD.'''

    def process_date_range(date):
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
            return date

        except ValueError:
            click.echo("Could not parse date `{0}': {1}".format(date,
                                                                e.strerror))
            sys.exit(1)

    lock = LockFile('.notestitch.lock')
    try:
        lock.acquire(0)

    except AlreadyLocked:
        click.echo(
            "Could not lock `.notebene.lock'. Is another process using it?",
            err=True)
        sys.exit(1)
    else:
        # We need to release the lock even if there is an exception.
        atexit.register(LockFile.release, lock)

    template_filename = Path('template.tex')

    all_notes = Path('.').glob('*.tex')

    notes = []  # The notes we will build with.

    for (i, note) in enumerate(all_notes):
        if note == template_filename:
            continue  # Skip over the template file.

        try:
            file_date = datetime.strptime(str(note), '%Y-%m-%d.tex')
            notes.append({'filename': note, 'date': file_date})

        except ValueError:
            click.echo(
                "File `{0}' was skipped as the filename is not an ISO 8601 "
                "date".format(note), err=True)

    if date_range:
        lower, upper = map(process_date_range, date_range)

        notes = filter(lambda note: lower <= note.date <= upper, notes)

    del all_notes

    dates = date
    for date in dates:
        if not date.endswith('.tex'):
            date += '.tex'

        try:
            file_date = datetime.strptime(date, '%Y-%m-%d.tex')

        except ValueError:
            click.echo(
                "Date `{0}' is not a valid ISO 8601 date".format(
                    date.rstrip('.tex')),
                err=True)
            sys.exit(1)

        filename = Path(date)

        if filename.exists():
            notes.append({'filename': filename, 'date': file_date})
        else:
            click.echo("File `{0}' does not exist; skipping.".format(filename),
                       err=True)

    if len(notes) == 0:
        click.echo('No notes to build.')
        sys.exit(0)

    for i in range(len(notes)):
        try:
            with notes[i]['filename'].open() as f:
                notes[i]['content'] = ''.join(f.readlines())

        except OSError as e:
            click.echo("Could not open `{0}': {1}".format(notes[i]['filename'],
                                                          e.strerror),
                       err=True)
            sys.exit(1)

    env = Environment(loader=FileSystemLoader('.'))
    env.block_start_string = '((*'
    env.block_end_string = '*))'
    env.variable_start_string = '((('
    env.variable_end_string = ')))'

    try:
        template = env.get_template('template.tex')

    except TemplateNotFound as e:
        click.echo(
            "Could not find `template.tex' -- is this a notestitch subject "
            "directory?", err=True)
        sys.exit(1)

    try:
        with open('notes.tex', 'w') as f:
            f.write(template.render(notes=notes))

    except OSError as e:
        click.echo("Could not write to `notes.tex': {1}".format(e.strerror))
        sys.exit(1)

    if subprocess.call(['pdflatex', 'notes.tex'], stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL) != 0:
        click.echo(
            'pdflatex returned non-zero; check notes.log for more '
            'information', err=True)

    try:
        os.unlink('notes.tex')
    except OSError as e:
        click.echo("Could not unlink `notes.tex'")
