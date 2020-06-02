from decorator import decorator


@decorator
def trace(func, *args, **kwargs):
    result = func(*args, **kwargs)

    name = func.__name__

    # self не нужен
    if len(args) != 0:
        if hasattr(args[0], name):
            args = args[1::]

    arguments = ', '.join(str(arg) for arg in args)
    key_value = ', '.join(f'{key}={value}' for key, value in kwargs.items())
    comma = ', ' if len(arguments) > 0 and len(kwargs) > 0 else ''

    output = '' if result is None else f' => {result}'

    print(f'{name}({arguments}{comma}{key_value}){output}')

    return result
