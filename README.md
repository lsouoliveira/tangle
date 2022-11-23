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

```ruby > hello_world.rb
puts "hello, world!"
```

It could be tangle running the following command:

```bash
tangle example.md
```

The resulting file would be `hello_world.rb` with the content below:

```ruby
puts "hello, world!"
```
