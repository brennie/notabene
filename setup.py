from setuptools import setup

import notestitch

setup(
    name='notestitch',
    version=notestitch.VERSION,
    description=notestitch.__doc__,
    url='https://github.com/brennie/notestitch',,
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License V3 or later '
        '(GPLv3+)',
        'Programming Language :: Python :: 3.4'
    ],
    install_requires=[
        'click',
        'jinja2',
        'lockfile'
    ],
    packages=['notestitch'],
    package_data={
        'notestitch': ['template.tex']
    },
    entry_points={
        'console_scripts': ['notestitch=notestitch.commands:main']
    })
