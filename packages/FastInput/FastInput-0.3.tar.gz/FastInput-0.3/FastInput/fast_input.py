"""Input with validation

This script allows to simplify the input validation of a user using the input() method.

This file can also be imported as a module and contains the following
functions:

    * input_with_valiation - returns the input of the user according to the validation parameter povided
    * input_for_confirmation - method used to ask for user confirmation
"""

from enum import Enum
from collections import namedtuple

class InputType(Enum):
    """
        A class used to enumerate the available type for validation

        """

    INTEGER = 'integer'
    FLOAT = 'float'
    STRING = 'string'
    BOOL = 'boolean'

def input_for_confirmation(prompt:str, default_value:bool=None):
    """
            Parameters
            ----------
            prompt : str
                The prompt displayed asking for a user input
            default_value : bool
                The default value returned if empty input
    """


    choice = input_with_validation(prompt,InputType.BOOL,False if default_value is None else True)
    if choice is None:
        return default_value
    return choice

def input_with_validation(prompt:str, type: str, can_be_empty=False, lower_bound=None, upper_bound=None):
    """
            Parameters
            ----------
            prompt : str
                The prompt displayed asking for a user input
            type : str
                The type of variable that will be return by the function ['integer','float','boolean' or 'string']
            can_be_empty : bool, optional
                Define if the user input can be None (default is False)
            lower_bound : str, optional
                Define the lower bound of acceptable input. Will be cast to 'type' provided in argument (default is None)
            upper_bound : str, optional
                Define the upper bound of acceptable input. Will be cast to 'type' provided in argument (default is None)
    """

    try:
        if not lower_bound is None:
            if type == InputType.INTEGER:
                lower_bound = int(lower_bound)
            elif type == InputType.FLOAT:
                lower_bound = float(lower_bound)
    except:
        raise ValueError("Your lower bound do not match your type : {type}".format(type=type.value))
    try:
        if not upper_bound is None:
            if type == InputType.INTEGER:
                upper_bound = int(upper_bound)
            elif type == InputType.FLOAT:
                upper_bound = float(upper_bound)
    except:
        raise ValueError("Your upper bound do not match your type : {type}".format(type=type.value))
    if not lower_bound is None and not upper_bound is None:
        if lower_bound == upper_bound:
            return lower_bound
        elif lower_bound > upper_bound:
            raise ValueError("Your upper bound is lower than your lower bound ({low} > {up})".format(low=lower_bound,up=upper_bound))

    promptF = prompt + "\n"
    if not lower_bound is None or not upper_bound is None:
        promptF += "("
        if not lower_bound is None:
            promptF += " >= {low} ".format(low=lower_bound)
            if not upper_bound is None:
                promptF += "and <= {up} ".format(up=upper_bound)
        else:
            promptF += " <= {up} ".format(up=upper_bound)
        promptF += ")\n"
    choice = input(promptF)
    choice_cast = None
    while choice_cast is None:
        if can_be_empty and len(choice) == 0:
            return None
        elif not can_be_empty and len(choice) == 0:
            while len(choice) == 0:
                print("Your answer cannot be empty.")
                choice=input()
        try:
            if type == InputType.INTEGER:
                choice_cast = int(choice)
            elif type == InputType.FLOAT:
                choice_cast = float(choice)
            elif type == InputType.STRING:
                choice_cast = str(choice)
            elif type == InputType.BOOL:
                if choice.lower() in ['y','o','yes','oui']:
                    return True
                elif choice.lower() in ['n','no','non']:
                    return False
                else:
                    print("Unknown answer please answer with yes or no")
                    choice = input()
            valid_border = False
            if not lower_bound is None:
                if choice_cast < lower_bound:
                    print("Wrong choice. Please provide an answer >= {low}".format(low=lower_bound))
                    choice_cast = None
                    choice=input()
                else:
                    valid_border = True
            else:
                valid_border = True 
            if valid_border and not upper_bound is None:
                if choice_cast > upper_bound:
                    print("Wrong choice. Please provide an answer <= {up}".format(up=upper_bound))
                    choice_cast = None
                    choice=input()
                else:
                    return choice_cast
                
        except:
            print("Wrong choice type. Please provide an answer of type : {type}".format(type=type.value))
            choice=input()
    return choice_cast

def input_within_list(list, as_selection=False):
    """
            Parameters
            ----------
            list : Array
                Define the list of choice you want to propose
            as_selection: bool, optional
    """

    if len(list) == 0:
        print("The choice list is empty")
        return None
    elif len(list) == 1:
        print("The programmer choose for you!")
        return list[0]
    else:
        if as_selection:
            prompt = "Choose a value among :"
            count = 1
            for s in list:
                prompt += f"\n  {count}. {s}"
                count += 1
            choice=input_with_validation(prompt,InputType.INTEGER,False,1,len(list))
            return list[choice]
        else:
            prompt = "Choose a value among : "+str(list)
            retry = True
            while retry:
                choice=input_with_validation(prompt,InputType.STRING,False)
                for c in list:
                    try:
                        if type(c) is int:
                            val = int(choice)
                        elif type(c) is float:
                            val = float(choice)
                        elif type(c) is str:
                            val = str(choice)
                        elif type(c) is bool:        
                            if choice in ['True']:
                                val = True
                            elif choice in ['False']:
                                val = False
                            else:
                                val = None
                        #print(f"{c} - {val}")
                        if val == c:
                            return val
                    except:
                        #the chosen type do not match
                        #print(f"{c} + {type(c)}")
                        retry = True
                print("Your choice is not in the list")
if __name__ == "__main__":
    #example code
    InitForm = namedtuple("InitForm", ["user", "id","id2","id3" ])

    myInitForm = InitForm(
        input_with_validation("What is your user?", InputType.STRING)
        , input_with_validation("Provide your id", InputType.INTEGER,False,0)
        , input_with_validation("Provide your id2", InputType.INTEGER,False,None,10)
        , input_with_validation("Provide your id3 any integer", InputType.INTEGER)
        )

    print(myInitForm)

    input_for_confirmation("Do you like this app?")
     
    list=[1,2,"test",False]
    input_within_list(list)

    list=[1,2,"test",True]
    input_within_list(list,True)