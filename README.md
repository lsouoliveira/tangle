# Tangle

A tool for exporting markdown code blocks to files.

## Requirements

- [Python 3.11.0](https://www.python.org/downloads/)

## Installation

Clone the repository, and use `pip` to install the project as a python package.

```bash
pip3 install .
```

## Usage

```bash
tangle <file>
```

## Example

A example markdown file named `example.md` using the `tangle` syntax:

![image](https://user-images.githubusercontent.com/30642647/203586964-dc892e05-7cdc-4d0a-a0ab-b5577fd7344c.png)

It could be tangle running the following command:

```bash
tangle example.md
```

A `hello_world.rb` file would be created at `~/` with the content below:

```ruby
puts "hello, world!"
```

## Changelog

### 1.1.0
- Add support for recursive tangle markdown files linked in the document
