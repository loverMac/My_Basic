# BASIC Interpreter in Python

A lightweight interpreter for running classic BASIC programs, implemented in Python 3.

## Overview

This interpreter provides a faithful implementation of core BASIC language features while maintaining modern code standards. It supports both traditional numbered and modern unnumbered programming styles.

## Technical Specifications

### Supported Features

- **Program Structure**:
  - Line numbers (optional)
  - Multi-statement lines
  - Comments (`REM` or `!`)

- **I/O Operations**:
  - `PRINT` with formatting (`;`, `,`)
  - `INPUT` for user input
  - `DATA`/`READ` for embedded data

- **Control Flow**:
  - `GOTO` for unconditional jumps
  - `IF...THEN` for conditionals
  - `FOR...NEXT` loops

- **Variables**:
  - Scalar variables (implicit declaration)
  - Numeric and string values
  - Basic expressions

### Implementation Details

- **Parser**: Recursive descent with lookahead
- **Memory Model**: Single global namespace
- **Execution**: Direct interpretation (no compilation)

## Usage

### Command Line Interface

```bash
python3 basic.py program.bas [options]

Supported Options
Option	Description
-d	Enable debug output
-t	Show execution trace
Example Programs
1. Hello World
basic

10 PRINT "Hello, World"
20 END

2. Fibonacci Sequence
basic

LET A = 1
LET B = 1
FOR I = 1 TO 10
    PRINT A
    LET C = A + B
    LET A = B
    LET B = C
NEXT I

Limitations

    No support for:

        Arrays

        User-defined functions

        File I/O operations

        Advanced string manipulation

    Current restrictions:

        Single-precision floating point only

        1024 line limit per program

        No line editing during input

Development Notes

The interpreter follows a clean architecture with separate:

    Lexical analysis

    Syntax parsing

    Execution components

Error handling provides detailed messages with line number references.
License

MIT License. See LICENSE file for details.
text


This version maintains a professional technical documentation style while being comprehensive. Key features:

1. Clear section organization
2. Technical accuracy
3. Concise feature listings
4. Practical examples
5. Honest limitations disclosure
6. Proper formatting for code samples

The markdown structure ensures good readability both in source form and when rendered by documentation systems.