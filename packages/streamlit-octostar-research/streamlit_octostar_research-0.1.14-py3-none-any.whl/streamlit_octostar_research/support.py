def require(kwarg_name):
    """Decorator to enforce a required kwarg in a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if kwarg_name not in kwargs:
                raise ValueError(f"{kwarg_name} is a required parameter.")
            return func(*args, **kwargs)
        return wrapper
    return decorator