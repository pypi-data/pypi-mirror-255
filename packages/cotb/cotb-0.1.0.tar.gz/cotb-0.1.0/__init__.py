# coding: utf-8

from __future__ import annotations

if False:
    from typing import Any



_package_data: dict[str, Any] = dict(
    full_package_name='cotb',
    version_info=(0, 1, 0),
    __version__='0.1.0',
    version_timestamp='2024-02-09 19:44:09',
    author='Anthon van der Neut',
    author_email='a.van.der.neut@ruamel.eu',
    url='https://sourceforge.net/p/click-outside-the-box/',
    description='cotb is a short name for click-outside-the-box, a program register and replay clicks for online card gaming',
    keywords='pypi gaming',
    entry_points='cotb=click_outside_the_box.__main__:main',
    license='Copyright Ruamel bvba 2007-2024',
    since=2024,
    install_requires=['click_outside_the_box', ],
    tox=dict(env='3',),  # *->all p->pypy
    python_requires='>=3.8',
)  # NOQA


version_info = _package_data['version_info']
__version__ = _package_data['__version__']
