import inspect
import typer


def command_mixin(app, **kwargs):
    def wrapper(func):
        args = ''
        kw = ''
        kw_body = ''
        is_args = True  # skip first which is args
        for name, param in inspect.signature(func).parameters.items():
            if is_args:
                is_args = False
                continue
            if param.default is inspect.Parameter.empty:
                args += f',{name}'
            else:
                kw += f',{name}={repr(param.default)}'
                kw_body += f',{name}={name}'
        locals_ = dict(func=func, typer=typer, trans=lambda xl: [x if x.strip() else f'"{x}"' for x in xl])
        exec(f"def {func.__name__}(ctx: typer.Context{args}{kw}): return func(' '.join(trans(ctx.args)){args}{kw_body})",
             locals_)
        return app.command(
            **{
                'context_settings': {"allow_extra_args": True, "ignore_unknown_options": True},
                **kwargs
            }
        )(locals_[func.__name__])

    return wrapper

# no sub command
# @app.callback(invoke_without_command=True)

# no accepting args, get args from sys.argv
# @app.command(
#     context_settings=dict(resilient_parsing=True)
# )

# https://typer.tiangolo.com/tutorial/commands/one-or-multiple/#one-command-and-one-callback
# One command and one callback
# @app.callback()
# def callback():
#     pass
