from typing import Optional

def inherit_docstring_from(parent, header: Optional[str] = None):
    """Decorator to inherit docstring from another function

    For example:
    ```python
    @inherit_docstring_from(parent_function)
    def my_function():
        pass
    ```
    
    """
    def decorator(func):
        if header:
            func.__doc__ += "\n" + header + "\n--------------------\n"
        func.__doc__ += parent.__doc__
        return func
    return decorator