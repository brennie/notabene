from setuptools import setup

import notabene

setup(
    name='notabene',
    version=notabene.VERSION,
    description=notabene.__doc__,
    url='https://github.com/brennie/notabene',
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public LIcense V3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.4'
    ],
    install_requires=[
        'appdirs',
        'click',
        'jinja2'
    ],
    packages=['notabene'],
    entry_points={
        'console_scripts': ['notabene=notabene:main']
    })