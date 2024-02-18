# PCIO

Input from stdin by format. Values can distrubuted on different lines.

``` python
import pcio

# Input two integer numbers as tuple
a,b=pcio.input('ii')

# Input a list of integer numbers
arr=pcio.input(100,'i')

# Input a list of pair float numbers
arr=pcio.input(100,'ff')

# Input one symbol
pcio.input(1)

# Input one line by default
s=pcio.input()
```
Function returns None on end of file and NaN if value is not a number.

Input Format|Description
--|--
i | Integer number, skip spaces before number
f | Float number, skip spaces before number
w | Word, skip spaces before word
c | One character as string
l | One line as a string
L | One line with new line as a string
a | All input as one string


Also specialized variants

``` python
import pcio

a=pcio.input_int()
b=pcio.input_float()
c=pcio.input_char()
d=pcio.input_word()
e=pcio.input_line()
```

Print by format (format not implemented yet)

``` python
# Print by format
pcio.print("Hello, {}!\n", "world")

# Print a list separated by space and new line
pcio.println(arr) 
```

Select input/output encoding (``utf-8``, ``cp1251`` or ``cp866``). Implemented for input only yet.

``` python
# Select encoding 
pcio.encoding('cp1251')
```
