# Tangle

A tool for exporting markdown code blocks to files.

## Requirements

- [Python 3.11.0](https://www.python.org/downloads/)

## Installation

Clone the repository, and use `pip` to install the project as a python package.

## Usage

```bash
tangle <file>
```

## Example

`dotfiles.md`:

```markdown
# Dotfiles

## Bash config

```bash > ~/.bashrc 
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi
```
```

command line:

```bash
tangle bash.md
```

~/.bashrc:

```
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi
```
