# CLI char counter

CharCounter is a command-line tool that counts the number of unique characters in a given string or a file containing a
sequence of characters.

## Usage

To use CharCounter, follow the instructions below:

### Installation

- Download package from _**PyPi**_ by following command:

```python -m pip install --index-url https://test.pypi.org/simple/ --no-deps example-package-shinumerde```

> Make sure you have Python installed on your machine.

### Running the Application:

- Navigate to the **app** directory:

```cd app```

- Run the application using the following command:

```python prog.py --string "your_sequence_here"```
    
    for a string sequence or the command below for proccessing sequence from a file

```python prog.py --file path/to/your/file.txt```

- Replace "your_sequence_here" with the actual string you want to analyze or provide the path to a file containing the sequence.

#### Options
- --string: Input a string for counting unique characters.
- --file: Input a file with a sequence for counting unique characters.

###### Example

```python char_counter.py --string "abbccd"```

This will output:

    2
which represents the number of unique characters in the given string.

### LICENSE
>This project is licensed under the GNU Public License - see the LICENSE file for details.