#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 16:48:14 2022

@author: joao

General checks to validate arguments
"""


def check_set(arg, iterable, err_str, include=True):
    """Check existence argument

    arg = argument
    iterable = list/set/tuple/other iterable of possible values
    err_str = name for error reporting
    """

    if not isinstance(err_str, str):
        raise TypeError(
            f"String provided in set check is not a str: \
                        {str(type(err_str))}"
        )

    try:
        list_arg = list(iterable)
    except:
        raise TypeError(
            f'Provided set of values for set check of "{err_str}" is not \
                iterable (or at least could not be \
            converted to string): {str(type(iterable))}'
        )


#    if include == True:
#        if arg not in list_arg:
#                        raise ValueError(
#                f'Argument "{arg}" provided in set check of "{err_str}" is not in set'
#            )
#    else:
#        if arg in list_arg:
#            raise ValueError(
#                f'Argument "{arg}" provided in set check of "{err_str}" is not in set'
#            )


def check_type(arg, typ, err_str):
    """Check type of argument

    arg = argument
    typ = expected type (possibly multiple per argument)
    err_str = name for error reporting
    """

    if not isinstance(err_str, str):
        raise TypeError(
            f"String provided in check type is not a str: \
                        {str(type(err_str))}"
        )

    if not isinstance(typ, list):
        if not isinstance(typ, type):
            raise TypeError(
                f"Type provided for {err_str} is not a type: \
                            {str(type(typ))}"
            )
        if not isinstance(arg, typ):
            raise TypeError(
                f"Type of {err_str} is not a {str(typ)}: \
                            {str(type(arg))}"
            )
    else:
        if not any(isinstance(typ_elem, type) for typ_elem in typ):
            raise TypeError(
                f'Type provided for "{err_str}" is \
                            not a type: {str(typ)}'
            )
        if not any(isinstance(arg, typ_elem) for typ_elem in typ):
            raise TypeError(
                f'Type of "{err_str}" is not in {str(typ)}\
                            : {str(type(arg))}'
            )


def check_value(arg1, arg2, op, err_str):
    """Check relation between two arguments"""
    check_types([arg1, err_str, op], [type(arg2), str, str], "value check str args")

    if not eval(f"a {op} b", {"a": arg1, "b": arg2}):
        raise ValueError(
            f'Values constraint "{err_str}" not satisfied: '
            f"{str(arg1)} {op} {str(arg2)} not true"
        )


def check_types(arg_list: list, type_list: list, err_str: str):
    """Check type of list of arguments

    arg_list = list of arguments
    type_list = expected types (possibly multiple per argument)
    err_str = name of list for error reporting
    """

    check_type(arg_list, list, f'list of arguments to check types "{err_str}"')
    check_type(type_list, list, f'list of types to check types "{err_str}"')
    check_type(err_str, str, f'name of list to check types "{err_str}"')
    if not (len(arg_list) == len(type_list)):
        raise ValueError(
            f'length of arguments "{err_str}" differ: \
                         {len(arg_list)} == {len(type_list)}'
        )

    for k, (arg, typ) in enumerate(zip(arg_list, type_list)):
        if not isinstance(typ, list):
            typ = [typ]
        for typ_elem in typ:
            check_type(typ_elem, type, "list of types for one argument")
        check_type(arg, typ, f'position {str(k)} of "{err_str}"')
