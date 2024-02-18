import inspect


class FuncSet:
    def __init__(self, result, *func_list):
        self.func_list = list(func_list)
        self.result = result or None

    def __call__(self, *args, **kwargs):
        result = []
        for func in self.func_list:
            result.append(func(*args, **kwargs))
        if self.result:
            return self.result(result)
        return result

    def append(self, func):
        self.func_list.append(func)


class FuncAnyArgs:
    def __init__(self, func, default=None):
        self.func = func
        self.default = default
        args, kwargs = get_args_kwargs(func)
        self.args_count = len(args)
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        kwargs = {k: kwargs.get(k, v) for k, v in self.kwargs.items()}
        args = [args[i] if i < len(args) else self.default for i in range(self.args_count)]
        return self.func(*args, **kwargs)


def get_args_kwargs(func):
    args = []
    kwargs = {}
    for key, value in inspect.signature(func).parameters.items():
        if value.default is inspect.Signature.empty:
            args.append(key)
        else:
            kwargs[key] = value.default
    return args, kwargs


if __name__ == "__main__":
    FuncAnyArgs(lambda x, y: print(x, y), 'default')(0)
