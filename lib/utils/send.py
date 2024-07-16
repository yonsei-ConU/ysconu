from discord.ext.commands import Context
from discord import Interaction


async def send(where, content='', *args, **kwargs):
    """
    Sends a message to the specified location.

    Parameters:
    - where: Can be a Context or Interaction object.
    - content: The content of the message to send.
    - *args: Additional positional arguments to pass to the send method.
    - **kwargs: Additional keyword arguments to pass to the send method.
    """
    if isinstance(where, Context):
        # Remove 'embeds' and 'ephemeral' if present in kwargs for context
        kwargs.pop('embeds', None)
        kwargs.pop('ephemeral', None)
        await where.send(content, *args, **kwargs)
    elif isinstance(where, Interaction):
        await where.response.send_message(content, *args, **kwargs)
    else:
        raise ValueError("The 'where' parameter must be either a Context or Interaction object.")


def convert_ctx(ctx):
    if isinstance(ctx, Context):
        author = ctx.author
    else:
        author = ctx.user
    return author
