#!/usr/bin/env python3

# TODO abstract this
# wrapped.__name__ = func.__name__
# Otherwise the function name cannot be registered

def list_to_string(func):
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            return ", ".join(result)
    # TODO abstract this
    wrapped.__name__ = func.__name__
    return wrapped

def html_list(func):
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            return "<ul>" + "".join("<li>" + li + "</li>" for li in result) + "</ul>"
    wrapped.__name__ = func.__name__
    return wrapped

def mathjax(func):
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            return "\(" + result + "\)"
    wrapped.__name__ = func.__name__
    return wrapped


def equation(func):
    def wrapped(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            return "\[" + result + "\]"
    wrapped.__name__ = func.__name__
    return wrapped
