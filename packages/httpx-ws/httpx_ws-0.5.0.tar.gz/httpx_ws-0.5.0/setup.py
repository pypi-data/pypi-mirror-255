# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='httpx-ws',
    version='0.5.0',
    description='WebSockets support for HTTPX',
    long_description='# HTTPX WS\n\n<p align="center">\n    <em>WebSockets support for HTTPX</em>\n</p>\n\n[![build](https://github.com/frankie567/httpx-ws/workflows/Build/badge.svg)](https://github.com/frankie567/httpx-ws/actions)\n[![codecov](https://codecov.io/gh/frankie567/httpx-ws/branch/main/graph/badge.svg?token=fL49kIvrj6)](https://codecov.io/gh/frankie567/httpx-ws)\n[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)\n[![PyPI version](https://badge.fury.io/py/httpx-ws.svg)](https://badge.fury.io/py/httpx-ws)\n[![Downloads](https://pepy.tech/badge/httpx-ws)](https://pepy.tech/project/httpx-ws)\n\n<p align="center">\n<a href="https://github.com/sponsors/frankie567"><img src="https://md-buttons.francoisvoron.com/button.svg?text=Buy%20me%20a%20coffee%20%E2%98%95%EF%B8%8F&bg=ef4444&w=200&h=50"></a>\n</p>\n\n---\n\n**Documentation**: <a href="https://frankie567.github.io/httpx-ws/" target="_blank">https://frankie567.github.io/httpx-ws/</a>\n\n**Source Code**: <a href="https://github.com/frankie567/httpx-ws" target="_blank">https://github.com/frankie567/httpx-ws</a>\n\n---\n\n## Installation\n\n```bash\npip install httpx-ws\n```\n\n## Features\n\n* [X] Sync and async client\n* [X] Helper methods to send text, binary and JSON data\n* [X] Helper methods to receive text, binary and JSON data\n* [X] Automatic ping/pong answers\n* [X] HTTPX transport to test WebSockets defined in ASGI apps\n* [X] Automatic keepalive ping\n* [X] `asyncio` and [Trio](https://trio.readthedocs.io/) support through [AnyIO](https://anyio.readthedocs.io/)\n\n## Contributors ✨\n\nThanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):\n\n<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable -->\n<table>\n  <tbody>\n    <tr>\n      <td align="center" valign="top" width="14.28%"><a href="http://francoisvoron.com"><img src="https://avatars.githubusercontent.com/u/1144727?v=4?s=100" width="100px;" alt="François Voron"/><br /><sub><b>François Voron</b></sub></a><br /><a href="#maintenance-frankie567" title="Maintenance">🚧</a> <a href="https://github.com/frankie567/httpx-ws/commits?author=frankie567" title="Code">💻</a></td>\n      <td align="center" valign="top" width="14.28%"><a href="http://kousikmitra.github.io"><img src="https://avatars.githubusercontent.com/u/15109533?v=4?s=100" width="100px;" alt="Kousik Mitra"/><br /><sub><b>Kousik Mitra</b></sub></a><br /><a href="https://github.com/frankie567/httpx-ws/commits?author=kousikmitra" title="Code">💻</a></td>\n      <td align="center" valign="top" width="14.28%"><a href="https://github.com/davidbrochart"><img src="https://avatars.githubusercontent.com/u/4711805?v=4?s=100" width="100px;" alt="David Brochart"/><br /><sub><b>David Brochart</b></sub></a><br /><a href="#platform-davidbrochart" title="Packaging/porting to new platform">📦</a></td>\n      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ysmu"><img src="https://avatars.githubusercontent.com/u/17018576?v=4?s=100" width="100px;" alt="ysmu"/><br /><sub><b>ysmu</b></sub></a><br /><a href="https://github.com/frankie567/httpx-ws/issues?q=author%3Aysmu" title="Bug reports">🐛</a></td>\n      <td align="center" valign="top" width="14.28%"><a href="https://samforeman.me"><img src="https://avatars.githubusercontent.com/u/5234251?v=4?s=100" width="100px;" alt="Sam Foreman"/><br /><sub><b>Sam Foreman</b></sub></a><br /><a href="https://github.com/frankie567/httpx-ws/issues?q=author%3Asaforem2" title="Bug reports">🐛</a></td>\n      <td align="center" valign="top" width="14.28%"><a href="http://maparent.ca/"><img src="https://avatars.githubusercontent.com/u/202691?v=4?s=100" width="100px;" alt="Marc-Antoine Parent"/><br /><sub><b>Marc-Antoine Parent</b></sub></a><br /><a href="https://github.com/frankie567/httpx-ws/issues?q=author%3Amaparent" title="Bug reports">🐛</a> <a href="https://github.com/frankie567/httpx-ws/commits?author=maparent" title="Code">💻</a></td>\n    </tr>\n  </tbody>\n</table>\n\n<!-- markdownlint-restore -->\n<!-- prettier-ignore-end -->\n\n<!-- ALL-CONTRIBUTORS-LIST:END -->\n\nThis project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!\n\n## Development\n\n### Setup environment\n\nWe use [Hatch](https://hatch.pypa.io/latest/install/) to manage the development environment and production build. Ensure it\'s installed on your system.\n\n### Run unit tests\n\nYou can run all the tests with:\n\n```bash\nhatch run test\n```\n\n### Format the code\n\nExecute the following command to apply linting and check typing:\n\n```bash\nhatch run lint\n```\n\n## License\n\nThis project is licensed under the terms of the MIT license.\n',
    author_email='François Voron <fvoron@gmail.com>',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP :: Session',
    ],
    install_requires=[
        'anyio',
        'httpcore>=0.17.3',
        'httpx>=0.23.1',
        'wsproto',
    ],
    packages=[
        'httpx_ws',
        'tests',
    ],
)
