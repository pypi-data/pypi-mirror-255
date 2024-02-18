import typer


def MutuallyExclusiveGroup(size=2):
    group = []

    def callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
        # Add cli option to group if it was called with a value
        if value is not None and param.name not in group:
            group.append(param.opts)
        if len(group) > size - 1:
            first_param = (group[:1] or [None])[0]
            raise typer.BadParameter(
                f"{param.name} is not allowed with {" / ".join(first_param)}"
            )
        return value

    return callback
