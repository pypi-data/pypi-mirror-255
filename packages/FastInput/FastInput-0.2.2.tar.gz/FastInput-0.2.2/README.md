**A Python library to simplify the input from user**

This library is a wrapper arround the input method. It allows to very the input according to the selected type, lower or upper bound provided.

*Instalation*

```
pip install FastInput
```

*Usage*
Asking for an integer value between 0 and 4:
```python
import FastInput as fi

yourChoice = fi.input_with_validation("Provide your id", InputType.INTEGER,False,0,4))
```
Asking for a string:
```python
import FastInput as fi

yourChoice = fi.input_with_validation("What is your name", InputType.STRING,False))
```
Asking for a user validation:
```python
import FastInput as fi

yourChoice = fi.input_for_confirmation("Do you agree?[Y/n]", True))
```

*Result*

```
python FastInput/fast_input.py
What is your user?

Your answer cannot be empty.
Alex
Provide your id
( >= 0 )
-1
Wrong choice. Please provide an answer >= 0
0
Provide your id2
( <= 10 )
12
Wrong choice. Please provide an answer <= 10
a
Wrong choice type. Please provide an answer of type : integer

Your answer cannot be empty.
5
Provide your id3 any integer
w
Wrong choice type. Please provide an answer of type : integer
123
InitForm(user='Alex', id=0, id2=5, id3=123)
Do you like this app?
Yes
```