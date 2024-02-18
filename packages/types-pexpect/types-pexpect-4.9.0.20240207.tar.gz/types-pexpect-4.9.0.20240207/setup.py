from setuptools import setup

name = "types-pexpect"
description = "Typing stubs for pexpect"
long_description = '''
## Typing stubs for pexpect

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`pexpect`](https://github.com/pexpect/pexpect) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`pexpect`.

This version of `types-pexpect` aims to provide accurate annotations
for `pexpect==4.9.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/pexpect. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `994d22bfbb542956be24580323d5b4aeef822c77` and was tested
with mypy 1.8.0, pyright 1.1.342, and
pytype 2024.1.24.
'''.lstrip()

setup(name=name,
      version="4.9.0.20240207",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/pexpect.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['pexpect-stubs'],
      package_data={'pexpect-stubs': ['ANSI.pyi', 'FSM.pyi', '__init__.pyi', '_async.pyi', 'exceptions.pyi', 'expect.pyi', 'fdpexpect.pyi', 'popen_spawn.pyi', 'pty_spawn.pyi', 'pxssh.pyi', 'replwrap.pyi', 'run.pyi', 'screen.pyi', 'socket_pexpect.pyi', 'spawnbase.pyi', 'utils.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
