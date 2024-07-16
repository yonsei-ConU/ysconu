import sqlite3
from datetime import datetime, timedelta
from random import randint, random
from typing import Optional

from discord import Member, Embed, DMChannel
from discord.ext.commands import Cog
from discord.ext.commands import cooldown, BucketType
from discord.ext.commands import command, has_permissions
import time
from .fun import check_tier
import math

from .achieve import grant_check, grant
from ..db import db

from discord.app_commands import command as slash, choices, Choice
from ..utils.send import send

today = ((time.time() + 32400) // 86400)
first_place = ""

# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2015-2019 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio
import discord

import itertools
import inspect
import re
from collections import OrderedDict, namedtuple

# Needed for the setup.py script
__version__ = '1.0.0-a'


class MenuError(Exception):
    pass


class CannotEmbedLinks(MenuError):
    def __init__(self):
        super().__init__('Bot does not have embed links permission in this channel.')


class CannotSendMessages(MenuError):
    def __init__(self):
        super().__init__('Bot cannot send messages in this channel.')


class CannotAddReactions(MenuError):
    def __init__(self):
        super().__init__('Bot cannot add reactions in this channel.')


class CannotReadMessageHistory(MenuError):
    def __init__(self):
        super().__init__('Bot does not have Read Message History permissions in this channel.')


class Position:
    __slots__ = ('number', 'bucket')

    def __init__(self, number, *, bucket=1):
        self.bucket = bucket
        self.number = number

    def __lt__(self, other):
        if not isinstance(other, Position) or not isinstance(self, Position):
            return NotImplemented

        return (self.bucket, self.number) < (other.bucket, other.number)

    def __eq__(self, other):
        return isinstance(other, Position) and other.bucket == self.bucket and other.number == self.number

    def __le__(self, other):
        r = Position.__lt__(other, self)
        if r is NotImplemented:
            return NotImplemented
        return not r

    def __gt__(self, other):
        return Position.__lt__(other, self)

    def __ge__(self, other):
        r = Position.__lt__(self, other)
        if r is NotImplemented:
            return NotImplemented
        return not r

    def __repr__(self):
        return '<{0.__class__.__name__}: {0.number}>'.format(self)


class Last(Position):
    __slots__ = ()

    def __init__(self, number=0):
        super().__init__(number, bucket=2)


class First(Position):
    __slots__ = ()

    def __init__(self, number=0):
        super().__init__(number, bucket=0)


_custom_emoji = re.compile(r'<?(?P<animated>a)?:?(?P<name>[A-Za-z0-9\_]+):(?P<id>[0-9]{13,21})>?')


def _cast_emoji(obj, *, _custom_emoji=_custom_emoji):
    if isinstance(obj, discord.PartialEmoji):
        return obj

    obj = str(obj)
    match = _custom_emoji.match(obj)
    if match is not None:
        groups = match.groupdict()
        animated = bool(groups['animated'])
        emoji_id = int(groups['id'])
        name = groups['name']
        return discord.PartialEmoji(name=name, animated=animated, id=emoji_id)
    return discord.PartialEmoji(name=obj, id=None, animated=False)


class Button:
    """Represents a reaction-style button for the :class:`Menu`.

    There are two ways to create this, the first being through explicitly
    creating this class and the second being through the decorator interface,
    :func:`button`.

    The action must have both a ``self`` and a ``payload`` parameter
    of type :class:`discord.RawReactionActionEvent`.

    Attributes
    ------------
    emoji: :class:`discord.PartialEmoji`
        The emoji to use as the button. Note that passing a string will
        transform it into a :class:`discord.PartialEmoji`.
    action
        A coroutine that is called when the button is pressed.
    skip_if: Optional[Callable[[:class:`Menu`], :class:`bool`]]
        A callable that detects whether it should be skipped.
        A skipped button does not show up in the reaction list
        and will not be processed.
    position: :class:`Position`
        The position the button should have in the initial order.
        Note that since Discord does not actually maintain reaction
        order, this is a best effort attempt to have an order until
        the user restarts their client. Defaults to ``Position(0)``.
    lock: :class:`bool`
        Whether the button should lock all other buttons from being processed
        until this button is done. Defaults to ``True``.
    """
    __slots__ = ('emoji', '_action', '_skip_if', 'position', 'lock')

    def __init__(self, emoji, action, *, skip_if=None, position=None, lock=True):
        self.emoji = _cast_emoji(emoji)
        self.action = action
        self.skip_if = skip_if
        self.position = position or Position(0)
        self.lock = lock

    @property
    def skip_if(self):
        return self._skip_if

    @skip_if.setter
    def skip_if(self, value):
        if value is None:
            self._skip_if = lambda x: False
            return

        try:
            menu_self = value.__self__
        except AttributeError:
            self._skip_if = value
        else:
            # Unfurl the method to not be bound
            if not isinstance(menu_self, Menu):
                raise TypeError('skip_if bound method must be from Menu not %r' % menu_self)

            self._skip_if = value.__func__

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        try:
            menu_self = value.__self__
        except AttributeError:
            pass
        else:
            # Unfurl the method to not be bound
            if not isinstance(menu_self, Menu):
                raise TypeError('action bound method must be from Menu not %r' % menu_self)

            value = value.__func__

        if not inspect.iscoroutinefunction(value):
            raise TypeError('action must be a coroutine not %r' % value)

        self._action = value

    def __call__(self, menu, payload):
        if self.skip_if(menu):
            return
        return self._action(menu, payload)

    def __str__(self):
        return str(self.emoji)

    def is_valid(self, menu):
        return not self.skip_if(menu)


def button(emoji, **kwargs):
    """Denotes a method to be button for the :class:`Menu`.

    The methods being wrapped must have both a ``self`` and a ``payload``
    parameter of type :class:`discord.RawReactionActionEvent`.

    The keyword arguments are forwarded to the :class:`Button` constructor.

    Example
    ---------

    .. code-block:: python3

        class MyMenu(Menu):
            async def send_initial_message(self, ctx, channel):
                return await channel.send(f'Hello {ctx.author}')

            @button('\\N{THUMBS UP SIGN}')
            async def on_thumbs_up(self, payload):
                await self.message.edit(content=f'Thanks {self.ctx.author}!')

            @button('\\N{THUMBS DOWN SIGN}')
            async def on_thumbs_down(self, payload):
                await self.message.edit(content=f"That's not nice {self.ctx.author}...")

    Parameters
    ------------
    emoji: Union[:class:`str`, :class:`discord.PartialEmoji`]
        The emoji to use for the button.
    """

    def decorator(func):
        func.__menu_button__ = _cast_emoji(emoji)
        func.__menu_button_kwargs__ = kwargs
        return func

    return decorator


class _MenuMeta(type):
    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # This is needed to maintain member order for the buttons
        return OrderedDict()

    def __new__(cls, name, bases, attrs, **kwargs):
        buttons = []
        new_cls = super().__new__(cls, name, bases, attrs)

        inherit_buttons = kwargs.pop('inherit_buttons', True)
        if inherit_buttons:
            # walk MRO to get all buttons even in subclasses
            for base in reversed(new_cls.__mro__):
                for elem, value in base.__dict__.items():
                    try:
                        value.__menu_button__
                    except AttributeError:
                        continue
                    else:
                        buttons.append(value)
        else:
            for elem, value in attrs.items():
                try:
                    value.__menu_button__
                except AttributeError:
                    continue
                else:
                    buttons.append(value)

        new_cls.__menu_buttons__ = buttons
        return new_cls

    def get_buttons(cls):
        buttons = OrderedDict()
        for func in cls.__menu_buttons__:
            emoji = func.__menu_button__
            buttons[emoji] = Button(emoji, func, **func.__menu_button_kwargs__)
        return buttons


class Menu(metaclass=_MenuMeta):
    r"""An interface that allows handling menus by using reactions as buttons.

    Buttons should be marked with the :func:`button` decorator. Please note that
    this expects the methods to have a single parameter, the ``payload``. This
    ``payload`` is of type :class:`discord.RawReactionActionEvent`.

    Attributes
    ------------
    timeout: :class:`float`
        The timeout to wait between button inputs.
    delete_message_after: :class:`bool`
        Whether to delete the message after the menu interaction is done.
    clear_reactions_after: :class:`bool`
        Whether to clear reactions after the menu interaction is done.
        Note that :attr:`delete_message_after` takes priority over this attribute.
        If the bot does not have permissions to clear the reactions then it will
        delete the reactions one by one.
    check_embeds: :class:`bool`
        Whether to verify embed permissions as well.
    ctx: Optional[:class:`commands.Context`]
        The context that started this pagination session or ``None`` if it hasn't
        been started yet.
    bot: Optional[:class:`commands.Bot`]
        The bot that is running this pagination session or ``None`` if it hasn't
        been started yet.
    message: Optional[:class:`discord.Message`]
        The message that has been sent for handling the menu. This is the returned
        message of :meth:`send_initial_message`. You can set it in order to avoid
        calling :meth:`send_initial_message`\, if for example you have a pre-existing
        message you want to attach a menu to.
    """

    def __init__(self, *, timeout=180.0, delete_message_after=False,
                 clear_reactions_after=False, check_embeds=False, message=None):

        self.timeout = timeout
        self.delete_message_after = delete_message_after
        self.clear_reactions_after = clear_reactions_after
        self.check_embeds = check_embeds
        self._can_remove_reactions = False
        self.__tasks = []
        self._running = True
        self.message = message
        self.ctx = None
        self.bot = None
        self._author_id = None
        self._buttons = self.__class__.get_buttons()
        self._lock = asyncio.Lock()
        self._event = asyncio.Event()

    @discord.utils.cached_property
    def buttons(self):
        """Retrieves the buttons that are to be used for this menu session.

        Skipped buttons are not in the resulting dictionary.

        Returns
        ---------
        Mapping[:class:`str`, :class:`Button`]
            A mapping of button emoji to the actual button class.
        """
        buttons = sorted(self._buttons.values(), key=lambda b: b.position)
        return {
            button.emoji: button
            for button in buttons
            if button.is_valid(self)
        }

    def add_button(self, button, *, react=False):
        """|maybecoro|

        Adds a button to the list of buttons.

        If the menu has already been started then the button will
        not be added unless the ``react`` keyword-only argument is
        set to ``True``. Note that when this happens this function
        will need to be awaited.

        If a button with the same emoji is added then it is overridden.

        .. warning::

            If the menu has started and the reaction is added, the order
            property of the newly added button is ignored due to an API
            limitation with Discord and the fact that reaction ordering
            is not guaranteed.

        Parameters
        ------------
        button: :class:`Button`
            The button to add.
        react: :class:`bool`
            Whether to add a reaction if the menu has been started.
            Note this turns the method into a coroutine.

        Raises
        ---------
        MenuError
            Tried to use ``react`` when the menu had not been started.
        discord.HTTPException
            Adding the reaction failed.
        """

        self._buttons[button.emoji] = button

        if react:
            if self.__tasks:
                async def wrapped():
                    # Add the reaction
                    try:
                        await self.message.add_reaction(button.emoji)
                    except discord.HTTPException:
                        raise
                    else:
                        # Update the cache to have the value
                        self.buttons[button.emoji] = button

                return wrapped()

            async def dummy():
                raise MenuError('Menu has not been started yet')

            return dummy()

    def remove_button(self, emoji, *, react=False):
        """|maybecoro|

        Removes a button from the list of buttons.

        This operates similar to :meth:`add_button`.

        Parameters
        ------------
        emoji: Union[:class:`Button`, :class:`str`]
            The emoji or the button to remove.
        react: :class:`bool`
            Whether to remove the reaction if the menu has been started.
            Note this turns the method into a coroutine.

        Raises
        ---------
        MenuError
            Tried to use ``react`` when the menu had not been started.
        discord.HTTPException
            Removing the reaction failed.
        """

        if isinstance(emoji, Button):
            emoji = emoji.emoji
        else:
            emoji = _cast_emoji(emoji)

        self._buttons.pop(emoji, None)

        if react:
            if self.__tasks:
                async def wrapped():
                    # Remove the reaction from being processable
                    # Removing it from the cache first makes it so the check
                    # doesn't get triggered.
                    self.buttons.pop(emoji, None)
                    await self.message.remove_reaction(emoji, self.__me)

                return wrapped()

            async def dummy():
                raise MenuError('Menu has not been started yet')

            return dummy()

    def clear_buttons(self, *, react=False):
        """|maybecoro|

        Removes all buttons from the list of buttons.

        If the menu has already been started then the buttons will
        not be removed unless the ``react`` keyword-only argument is
        set to ``True``. Note that when this happens this function
        will need to be awaited.

        Parameters
        ------------
        react: :class:`bool`
            Whether to clear the reactions if the menu has been started.
            Note this turns the method into a coroutine.

        Raises
        ---------
        MenuError
            Tried to use ``react`` when the menu had not been started.
        discord.HTTPException
            Clearing the reactions failed.
        """

        self._buttons.clear()

        if react:
            if self.__tasks:
                async def wrapped():
                    # A fast path if we have permissions
                    if self._can_remove_reactions:
                        try:
                            del self.buttons
                        except AttributeError:
                            pass
                        finally:
                            await self.message.clear_reactions()
                        return

                    # Remove the cache (the next call will have the updated buttons)
                    reactions = list(self.buttons.keys())
                    try:
                        del self.buttons
                    except AttributeError:
                        pass

                    for reaction in reactions:
                        await self.message.remove_reaction(reaction, self.__me)

                return wrapped()

            async def dummy():
                raise MenuError('Menu has not been started yet')

            return dummy()

    def should_add_reactions(self):
        """:class:`bool`: Whether to add reactions to this menu session."""
        return len(self.buttons)

    def _verify_permissions(self, ctx, channel, permissions):
        if not permissions.send_messages:
            raise CannotSendMessages()

        if self.check_embeds and not permissions.embed_links:
            raise CannotEmbedLinks()

        self._can_remove_reactions = permissions.manage_messages
        if self.should_add_reactions():
            if not permissions.add_reactions:
                raise CannotAddReactions()
            if not permissions.read_message_history:
                raise CannotReadMessageHistory()

    def reaction_check(self, payload):
        """The function that is used to check whether the payload should be processed.
        This is passed to :meth:`discord.ext.commands.Bot.wait_for <Bot.wait_for>`.

        There should be no reason to override this function for most users.

        Parameters
        ------------
        payload: :class:`discord.RawReactionActionEvent`
            The payload to check.

        Returns
        ---------
        :class:`bool`
            Whether the payload should be processed.
        """
        if payload.message_id != self.message.id:
            return False
        if payload.user_id not in {self.bot.owner_id, self._author_id, *self.bot.owner_ids}:
            return False

        return payload.emoji in self.buttons

    async def _internal_loop(self):
        try:
            self.__timed_out = False
            loop = self.bot.loop
            # Ensure the name exists for the cancellation handling
            tasks = []
            while self._running:
                tasks = [
                    asyncio.ensure_future(self.bot.wait_for('raw_reaction_add', check=self.reaction_check)),
                    asyncio.ensure_future(self.bot.wait_for('raw_reaction_remove', check=self.reaction_check))
                ]
                done, pending = await asyncio.wait(tasks, timeout=self.timeout, return_when=asyncio.FIRST_COMPLETED)
                for task in pending:
                    task.cancel()

                if len(done) == 0:
                    raise asyncio.TimeoutError()

                # Exception will propagate if e.g. cancelled or timed out
                payload = done.pop().result()
                loop.create_task(self.update(payload))

        # NOTE: Removing the reaction ourselves after it's been done when
        # mixed with the checks above is incredibly racy.
        # There is no guarantee when the MESSAGE_REACTION_REMOVE event will
        # be called, and chances are when it does happen it'll always be
        # after the remove_reaction HTTP call has returned back to the caller
        # which means that the stuff above will catch the reaction that we
        # just removed.

        # For the future sake of myself and to save myself the hours in the future
        # consider this my warning.

        except asyncio.TimeoutError:
            self.__timed_out = True
        finally:
            self._event.set()

            # Cancel any outstanding tasks (if any)
            for task in tasks:
                task.cancel()

            try:
                await self.finalize(self.__timed_out)
            except Exception:
                pass
            finally:
                self.__timed_out = False

            # Can't do any requests if the bot is closed
            if self.bot.is_closed():
                return

            # Wrap it in another block anyway just to ensure
            # nothing leaks out during clean-up
            try:
                if self.delete_message_after:
                    return await self.message.delete()

                if self.clear_reactions_after:
                    if self._can_remove_reactions:
                        return await self.message.clear_reactions()

                    for button_emoji in self.buttons:
                        try:
                            await self.message.remove_reaction(button_emoji, self.__me)
                        except discord.HTTPException:
                            continue
            except Exception:
                pass

    async def update(self, payload):
        """|coro|

        Updates the menu after an event has been received.

        Parameters
        -----------
        payload: :class:`discord.RawReactionActionEvent`
            The reaction event that triggered this update.
        """
        button = self.buttons[payload.emoji]
        if not self._running:
            return

        try:
            if button.lock:
                async with self._lock:
                    if self._running:
                        await button(self, payload)
            else:
                await button(self, payload)
        except Exception:
            # TODO: logging?
            import traceback
            traceback.print_exc()

    async def start(self, ctx, *, channel=None, wait=False):
        """|coro|

        Starts the interactive menu session.

        Parameters
        -----------
        ctx: :class:`Context`
            The invocation context to use.
        channel: :class:`discord.abc.Messageable`
            The messageable to send the message to. If not given
            then it defaults to the channel in the context.
        wait: :class:`bool`
            Whether to wait until the menu is completed before
            returning back to the caller.

        Raises
        -------
        MenuError
            An error happened when verifying permissions.
        discord.HTTPException
            Adding a reaction failed.
        """

        # Clear the buttons cache and re-compute if possible.
        try:
            del self.buttons
        except AttributeError:
            pass

        self.bot = bot = ctx.bot
        self.ctx = ctx
        self._author_id = ctx.author.id
        channel = channel or ctx.channel
        is_guild = isinstance(channel, discord.abc.GuildChannel)
        me = ctx.guild.me if is_guild else ctx.bot.user
        permissions = channel.permissions_for(me)
        self.__me = discord.Object(id=me.id)
        self._verify_permissions(ctx, channel, permissions)
        self._event.clear()
        msg = self.message
        if msg is None:
            self.message = msg = await self.send_initial_message(ctx, channel)

        if self.should_add_reactions():
            # Start the task first so we can listen to reactions before doing anything
            for task in self.__tasks:
                task.cancel()
            self.__tasks.clear()

            self._running = True
            self.__tasks.append(bot.loop.create_task(self._internal_loop()))

            async def add_reactions_task():
                for emoji in self.buttons:
                    await msg.add_reaction(emoji)

            self.__tasks.append(bot.loop.create_task(add_reactions_task()))

            if wait:
                await self._event.wait()

    async def finalize(self, timed_out):
        """|coro|

        A coroutine that is called when the menu loop has completed
        its run. This is useful if some asynchronous clean-up is
        required after the fact.

        Parameters
        --------------
        timed_out: :class:`bool`
            Whether the menu completed due to timing out.
        """
        return

    async def send_initial_message(self, ctx, channel):
        """|coro|

        Sends the initial message for the menu session.

        This is internally assigned to the :attr:`message` attribute.

        Subclasses must implement this if they don't set the
        :attr:`message` attribute themselves before starting the
        menu via :meth:`start`.

        Parameters
        ------------
        ctx: :class:`Context`
            The invocation context to use.
        channel: :class:`discord.abc.Messageable`
            The messageable to send the message to.

        Returns
        --------
        :class:`discord.Message`
            The message that has been sent.
        """
        raise NotImplementedError

    def stop(self):
        """Stops the internal loop."""
        self._running = False
        for task in self.__tasks:
            task.cancel()
        self.__tasks.clear()


class PageSource:
    """An interface representing a menu page's data source for the actual menu page.

    Subclasses must implement the backing resource along with the following methods:

    - :meth:`get_page`
    - :meth:`is_paginating`
    - :meth:`format_page`
    """

    async def _prepare_once(self):
        try:
            # Don't feel like formatting hasattr with
            # the proper mangling
            # read this as follows:
            # if hasattr(self, '__prepare')
            # except that it works as you expect
            self.__prepare
        except AttributeError:
            await self.prepare()
            self.__prepare = True

    async def prepare(self):
        """|coro|

        A coroutine that is called after initialisation
        but before anything else to do some asynchronous set up
        as well as the one provided in ``__init__``.

        By default this does nothing.

        This coroutine will only be called once.
        """
        return

    def is_paginating(self):
        """An abstract method that notifies the :class:`MenuPages` whether or not
        to start paginating. This signals whether to add reactions or not.

        Subclasses must implement this.

        Returns
        --------
        :class:`bool`
            Whether to trigger pagination.
        """
        raise NotImplementedError

    def get_max_pages(self):
        """An optional abstract method that retrieves the maximum number of pages
        this page source has. Useful for UX purposes.

        The default implementation returns ``None``.

        Returns
        --------
        Optional[:class:`int`]
            The maximum number of pages required to properly
            paginate the elements, if given.
        """
        return None

    async def get_page(self, page_number):
        """|coro|

        An abstract method that retrieves an object representing the object to format.

        Subclasses must implement this.

        .. note::

            The page_number is zero-indexed between [0, :meth:`get_max_pages`),
            if there is a maximum number of pages.

        Parameters
        -----------
        page_number: :class:`int`
            The page number to access.

        Returns
        ---------
        Any
            The object represented by that page.
            This is passed into :meth:`format_page`.
        """
        raise NotImplementedError

    async def format_page(self, menu, page):
        """|maybecoro|

        An abstract method to format the page.

        This method must return one of the following types.

        If this method returns a ``str`` then it is interpreted as returning
        the ``content`` keyword argument in :meth:`discord.Message.edit`
        and :meth:`discord.abc.Messageable.send`.

        If this method returns a :class:`discord.Embed` then it is interpreted
        as returning the ``embed`` keyword argument in :meth:`discord.Message.edit`
        and :meth:`discord.abc.Messageable.send`.

        If this method returns a ``dict`` then it is interpreted as the
        keyword-arguments that are used in both :meth:`discord.Message.edit`
        and :meth:`discord.abc.Messageable.send`. The two of interest are
        ``embed`` and ``content``.

        Parameters
        ------------
        menu: :class:`Menu`
            The menu that wants to format this page.
        page: Any
            The page returned by :meth:`PageSource.get_page`.

        Returns
        ---------
        Union[:class:`str`, :class:`discord.Embed`, :class:`dict`]
            See above.
        """
        raise NotImplementedError


class MenuPages(Menu):
    """A special type of Menu dedicated to pagination.

    Attributes
    ------------
    current_page: :class:`int`
        The current page that we are in. Zero-indexed
        between [0, :attr:`PageSource.max_pages`).
    """

    def __init__(self, source, **kwargs):
        self._source = source
        self.current_page = 0
        super().__init__(**kwargs)

    @property
    def source(self):
        """:class:`PageSource`: The source where the data comes from."""
        return self._source

    async def change_source(self, source):
        """|coro|

        Changes the :class:`PageSource` to a different one at runtime.

        Once the change has been set, the menu is moved to the first
        page of the new source if it was started. This effectively
        changes the :attr:`current_page` to 0.

        Raises
        --------
        TypeError
            A :class:`PageSource` was not passed.
        """

        if not isinstance(source, PageSource):
            raise TypeError('Expected {0!r} not {1.__class__!r}.'.format(PageSource, source))

        self._source = source
        self.current_page = 0
        if self.message is not None:
            await source._prepare_once()
            await self.show_page(0)

    def should_add_reactions(self):
        return self._source.is_paginating()

    async def _get_kwargs_from_page(self, page):
        value = await discord.utils.maybe_coroutine(self._source.format_page, self, page)
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return {'content': value, 'embed': None}
        elif isinstance(value, discord.Embed):
            return {'embed': value, 'content': None}

    async def show_page(self, page_number):
        page = await self._source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        await self.message.edit(**kwargs)

    async def send_initial_message(self, ctx, channel):
        """|coro|

        The default implementation of :meth:`Menu.send_initial_message`
        for the interactive pagination session.

        This implementation shows the first page of the source.
        """
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await channel.send(**kwargs)

    async def start(self, ctx, *, channel=None, wait=False):
        await self._source._prepare_once()
        await super().start(ctx, channel=channel, wait=wait)

    async def show_checked_page(self, page_number):
        max_pages = self._source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(page_number)
            elif max_pages > page_number >= 0:
                await self.show_page(page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def show_current_page(self):
        if self._source.is_paginating():
            await self.show_page(self.current_page)

    def _skip_double_triangle_buttons(self):
        max_pages = self._source.get_max_pages()
        if max_pages is None:
            return True
        return max_pages <= 2

    @button('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f',
            position=First(0), skip_if=_skip_double_triangle_buttons)
    async def go_to_first_page(self, payload):
        """go to the first page"""
        await self.show_page(0)

    @button('\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f', position=First(1))
    async def go_to_previous_page(self, payload):
        """go to the previous page"""
        await self.show_checked_page(self.current_page - 1)

    @button('\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f', position=Last(0))
    async def go_to_next_page(self, payload):
        """go to the next page"""
        await self.show_checked_page(self.current_page + 1)

    @button('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f',
            position=Last(1), skip_if=_skip_double_triangle_buttons)
    async def go_to_last_page(self, payload):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(self._source.get_max_pages() - 1)

    @button('\N{BLACK SQUARE FOR STOP}\ufe0f', position=Last(2))
    async def stop_pages(self, payload):
        """stops the pagination session."""
        self.stop()


class ListPageSource(PageSource):
    """A data source for a sequence of items.

    This page source does not handle any sort of formatting, leaving it up
    to the user. To do so, implement the :meth:`format_page` method.

    Attributes
    ------------
    entries: Sequence[Any]
        The sequence of items to paginate.
    per_page: :class:`int`
        How many elements are in a page.
    """

    def __init__(self, entries, *, per_page):
        self.entries = entries
        self.per_page = per_page

        pages, left_over = divmod(len(entries), per_page)
        if left_over:
            pages += 1

        self._max_pages = pages

    def is_paginating(self):
        """:class:`bool`: Whether pagination is required."""
        return len(self.entries) > self.per_page

    def get_max_pages(self):
        """:class:`int`: The maximum number of pages required to paginate this sequence."""
        return self._max_pages

    async def get_page(self, page_number):
        """Returns either a single element of the sequence or
        a slice of the sequence.

        If :attr:`per_page` is set to ``1`` then this returns a single
        element. Otherwise it returns at most :attr:`per_page` elements.

        Returns
        ---------
        Union[Any, List[Any]]
            The data returned.
        """
        if self.per_page == 1:
            return self.entries[page_number]
        else:
            base = page_number * self.per_page
            return self.entries[base:base + self.per_page]


_GroupByEntry = namedtuple('_GroupByEntry', 'key items')


class GroupByPageSource(ListPageSource):
    """A data source for grouped by sequence of items.

    This inherits from :class:`ListPageSource`.

    This page source does not handle any sort of formatting, leaving it up
    to the user. To do so, implement the :meth:`format_page` method.

    Parameters
    ------------
    entries: Sequence[Any]
        The sequence of items to paginate and group.
    key: Callable[[Any], Any]
        A key function to do the grouping with.
    sort: :class:`bool`
        Whether to sort the sequence before grouping it.
        The elements are sorted according to the ``key`` function passed.
    per_page: :class:`int`
        How many elements to have per page of the group.
    """

    def __init__(self, entries, *, key, per_page, sort=True):
        self.__entries = entries if not sort else sorted(entries, key=key)
        nested = []
        self.nested_per_page = per_page
        for k, g in itertools.groupby(self.__entries, key=key):
            g = list(g)
            if not g:
                continue
            size = len(g)

            # Chunk the nested pages
            nested.extend(_GroupByEntry(key=k, items=g[i:i + per_page]) for i in range(0, size, per_page))

        super().__init__(nested, per_page=1)

    async def get_page(self, page_number):
        return self.entries[page_number]

    async def format_page(self, menu, entry):
        """An abstract method to format the page.

        This works similar to the :meth:`ListPageSource.format_page` except
        the return type of the ``entry`` parameter is documented.

        Parameters
        ------------
        menu: :class:`Menu`
            The menu that wants to format this page.
        entry
            A namedtuple with ``(key, items)`` representing the key of the
            group by function and a sequence of paginated items within that
            group.

        Returns
        ---------
        :class:`dict`
            A dictionary representing keyword-arguments to pass to
            the message related calls.
        """
        raise NotImplementedError


def _aiter(obj, *, _isasync=inspect.iscoroutinefunction):
    cls = obj.__class__
    try:
        async_iter = cls.__aiter__
    except AttributeError:
        raise TypeError('{0.__name__!r} object is not an async iterable'.format(cls))

    async_iter = async_iter(obj)
    if _isasync(async_iter):
        raise TypeError('{0.__name__!r} object is not an async iterable'.format(cls))
    return async_iter


class AsyncIteratorPageSource(PageSource):
    """A data source for data backed by an asynchronous iterator.

    This page source does not handle any sort of formatting, leaving it up
    to the user. To do so, implement the :meth:`format_page` method.

    Parameters
    ------------
    iter: AsyncIterator[Any]
        The asynchronous iterator to paginate.
    per_page: :class:`int`
        How many elements to have per page.
    """

    def __init__(self, iterator, *, per_page):
        self.iterator = _aiter(iterator)
        self.per_page = per_page
        self._exhausted = False
        self._cache = []

    async def _iterate(self, n):
        it = self.iterator
        cache = self._cache
        for i in range(0, n):
            try:
                elem = await it.__anext__()
            except StopAsyncIteration:
                self._exhausted = True
                break
            else:
                cache.append(elem)

    async def prepare(self, *, _aiter=_aiter):
        # Iterate until we have at least a bit more single page
        await self._iterate(self.per_page + 1)

    def is_paginating(self):
        """:class:`bool`: Whether pagination is required."""
        return len(self._cache) > self.per_page

    async def _get_single_page(self, page_number):
        if page_number < 0:
            raise IndexError('Negative page number.')

        if not self._exhausted and len(self._cache) <= page_number:
            await self._iterate((page_number + 1) - len(self._cache))
        return self._cache[page_number]

    async def _get_page_range(self, page_number):
        if page_number < 0:
            raise IndexError('Negative page number.')

        base = page_number * self.per_page
        max_base = base + self.per_page
        if not self._exhausted and len(self._cache) <= max_base:
            await self._iterate((max_base + 1) - len(self._cache))

        entries = self._cache[base:max_base]
        if not entries and max_base > len(self._cache):
            raise IndexError('Went too far')
        return entries

    async def get_page(self, page_number):
        """Returns either a single element of the sequence or
        a slice of the sequence.

        If :attr:`per_page` is set to ``1`` then this returns a single
        element. Otherwise it returns at most :attr:`per_page` elements.

        Returns
        ---------
        Union[Any, List[Any]]
            The data returned.
        """
        if self.per_page == 1:
            return await self._get_single_page(page_number)
        else:
            return await self._get_page_range(page_number)


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=10)

    async def write_page(self, menu, offset, fields=[]):
        len_data = len(self.entries)

        embed = Embed(title="경험치 랭킹!",
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.icon_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} of {len_data:,} members.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        offset = (menu.current_page * self.per_page) + 1

        fields = []
        # table = ("\n".join(f"{idx+offset}. {self.ctx.bot.guild.get_member(entry[0])} (레벨: {entry[2]} | 경험치: {entry[1]})"
        #		for idx, entry in enumerate(entries)))

        table = ("\n".join(f"{idx + offset}. <@{entry[0]}> (레벨: {entry[2]} | 경험치: {entry[1]} | 경험치 부스트: {entry[3]})"
                           for idx, entry in enumerate(entries)))

        fields.append(("리더보드", table))

        return await self.write_page(menu, offset, fields)


def to_visual_string(string_to_convert, member, level):
    string_to_convert.replace("<멤버_사용자명#태그>", str(member))
    string_to_convert = string_to_convert.replace("<멤버_이름>", str(member.display_name))
    string_to_convert = string_to_convert.replace("<멤버_멘션>", str(member.mention))
    string_to_convert = string_to_convert.replace("<레벨>", str(level))

    return string_to_convert


class Exp(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_xp(self, message):
        temp = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ? AND GuildID = ?", message.author.id,
                         message.guild.id)
        if temp is None:
            await asyncio.sleep(10)
            try:
                db.execute("INSERT INTO exp (UserID, GuildID, invited_by) VALUES (?, ?, 772274871563583499)",
                           message.author.id, message.guild.id)
            except sqlite3.IntegrityError:
                pass
            db.commit()

            temp = db.record("SELECT XP, Level, XPLock FROM exp WHERE UserID = ? AND GuildID = ?", message.author.id,
                             message.guild.id)

        xp = int(temp[0])
        lvl = int(temp[1])
        xplock = temp[2]

        if datetime.now() > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, message, xp, lvl):
        xpboost = db.record("SELECT XPBoost FROM exp WHERE UserID = ? AND GuildID = ?", message.author.id,
                            message.guild.id)
        channelboost = db.record("SELECT ChannelBoost FROM channels WHERE ChannelID = ?", message.channel.id) or None
        try:
            min_xp, max_xp, guild_type, levelup_channel, cool, levelup_message = db.record(
                "SELECT min_xp, max_xp, guild_type, levelup_channel, XPcool, levelup_message FROM guilds WHERE GuildID = ?",
                message.guild.id)
        except TypeError:
            if not message.is_system():
                db.execute("INSERT INTO guilds (GuildID) VALUES (?)", message.guild.id)
                db.commit()
            min_xp, max_xp, guild_type, levelup_channel, cool, levelup_message = 13, 36, 0, 0, 60, "​"
        if channelboost is not None:
            channelboost = channelboost[0]
        else:
            channelboost = 1.0
        try:
            xp_min = round(min_xp * xpboost[0] * channelboost)
        except OverflowError:
            return
        xp_max = round(max_xp * xpboost[0] * channelboost)
        xp_to_add = randint(xp_min, xp_max)
        if message.guild.id == 743101101401964647:
            db.execute("UPDATE serverstat SET total_exp = total_exp + ? WHERE day = ?", xp_to_add,
                       ((time.time() + 32400) // 86400))
        new_lvl = int((math.sqrt(8 * (xp + xp_to_add) + 25) / 20) - 0.25)
        if new_lvl > lvl:
            if message.guild.id == 743101101401964647:
                if new_lvl >= 1:
                    l = grant_check("공식서버 입문자", message.author.id)
                    if l == 1:
                        await grant(message, "공식서버 입문자", "공식서버에서 1레벨을 달성하세요")
                if new_lvl >= 5:
                    l = grant_check("공식서버 활동자", message.author.id)
                    if l == 1:
                        await grant(message, "공식서버 활동자", "공식서버에서 5레벨을 달성하세요")
                if new_lvl >= 16:
                    l = grant_check("공식서버 고렙", message.author.id)
                    if l == 1:
                        await grant(message, "공식서버 고렙", "공식서버에서 16레벨을 달성해 태양계 바깥으로 이동 범위를 넓혀나가세요")
                if new_lvl >= 30:
                    l = grant_check("공식서버 고인물", message.author.id)
                    if l == 1:
                        await grant(message, "공식서버 고인물", "공식서버에서 30레벨을 달성하세요")
                if new_lvl >= 62:
                    l = grant_check("공식서버 초고렙", message.author.id)
                    if l == 1:
                        await grant(message, "공식서버 초고렙", "공식서버에서 62레벨을 달성해 태양계는 물론 우리 은하 바깥으로 이동 범위를 넓혀나가세요")
                if new_lvl >= 100:
                    l = grant_check("공식서버 정복자", message.author.id)
                    if l == 1:
                        await grant(message, "공식서버 정복자", "공식서버에서 100레벨을 달성해 우주 전체를 정복하세요")
            try:
                if levelup_channel == 1:
                    await message.channel.send(to_visual_string(levelup_message, message.author, new_lvl))
                elif levelup_channel != 0:
                    levelup_channel = self.bot.get_channel(levelup_channel)
                    await levelup_channel.send(to_visual_string(levelup_message, message.author, new_lvl))
                await self.check_lvl_rewards(message, new_lvl)
            except AttributeError:
                pass

        if guild_type & 1 == 1:
            db.execute(
                "UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ?, Money = Money + ? WHERE UserID = ? AND GuildID = ?",
                xp_to_add, new_lvl, (datetime.now() + timedelta(seconds=cool)).isoformat(), xp_to_add,
                message.author.id, message.guild.id)
        else:
            try:
                db.execute(
                    "UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ? AND GuildID = ?",
                    xp_to_add, new_lvl, (datetime.now() + timedelta(seconds=cool)).isoformat(), message.author.id,
                    message.guild.id)
            except OverflowError:
                return

        db.commit()

    async def check_lvl_rewards(self, message, lvl):
        roles = db.records("SELECT RoleID, role_info FROM roles WHERE GuildID = ? AND role_type = 1", message.guild.id)
        for role in roles:
            role_to_add = message.guild.get_role(role[0])
            if lvl >= role[1] and role_to_add not in message.author.roles:
                await message.author.add_roles(role_to_add)

    @command(name="레벨역할")
    async def level_role(self, ctx, activity: Optional[str] = "목록", page: Optional[int] = 1):
        if activity == "목록":
            lvroles = db.records(
                "SELECT RoleID, role_info FROM roles WHERE GuildID = ? AND role_type = 1 ORDER BY role_info ASC",
                ctx.guild.id)
            tjfaud = ""
            now_people = 1
            for role in lvroles:
                if now_people >= 10 * int(page) - 9:
                    tjfaud = tjfaud + f"{role[1]} 레벨 도달 시: {ctx.guild.get_role(role[0]).name} 역할 지급\n"
                now_people += 1
                if now_people == 10 * int(page) + 1:
                    break
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 역할이 없는 것 같아요!"
            await send(ctx, 
                embed=Embed(color=ctx.author.color, title=f"{ctx.guild.name}의 레벨업 보상 역할 목록", description=tjfaud))
        elif activity == "추가":
            if not ctx.author.guild_permissions.value & 8:
                await send(ctx, "이 명령어를 실행할 권한이 없어요!")
                return
            await send(ctx, "몇 레벨에 도달하면 역할을 주게 만들까요?")
            try:
                msg1 = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                try:
                    lvl = int(msg1.content)
                finally:
                    pass
            except asyncio.TimeoutError:
                await send(ctx, "레벨업 역할을 추가하지 않기로 했어요.")
                return
            await send(ctx, f"{lvl}레벨에 도달하면 어느 역할을 주게 만들 건가요?\n**역할 멘션의 형태로 입력해 주세요!**")
            try:
                msg2 = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                rolecheck = re.compile("<@&[0-9]{18,19}>")
                matchcheck = rolecheck.match(msg2.content)
                if not matchcheck:
                    await send(ctx, "역할 멘션의 형태로 보내 주세요!")
                    return
                if msg2.content[22].isdigit():
                    role = int(msg2.content[3:22])
                else:
                    role = int(msg2.content[3:21])
            except asyncio.TimeoutError:
                await send(ctx, "레벨업 역할을 추가하지 않기로 했어요.")
                return
            db.execute("INSERT INTO roles (RoleID, GuildID, role_type, role_info) VALUES (?, ?, 1, ?)", role,
                       ctx.guild.id, lvl)
            await send(ctx, f"{ctx.guild.name}에서는 이제부터 {lvl}레벨에 도달하면 {ctx.guild.get_role(role).mention} 역할을 받아요!")
            db.commit()
        elif activity == "삭제":
            if not ctx.author.guild_permissions.value & 8:
                await send(ctx, "이 명령어를 실행할 권한이 없어요!")
                return
            await send(ctx, "어떤 레벨역할을 삭제할 건가요?\n역할 자체가 지워지지는 않아요")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=20,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                role = int(msg.content[3:21])
            except asyncio.TimeoutError:
                await send(ctx, "레벨업 역할을 삭제하지 않기로 했어요.")
                return
            roles = db.records("SELECT RoleID FROM roles WHERE GuildID = ? AND role_type = 1", ctx.guild.id)
            for role_to_check in roles:
                if role_to_check[0] == role:
                    break
            else:
                await send(ctx, f"그 역할은 레벨업 역할에 포함되어 있지 않아요!")
                return
            db.execute("DELETE FROM roles WHERE RoleID = ?", role)
            await send(ctx, "해당 레벨역할을 삭제했어요. 역할 자체가 지워진 건 아니에요!")
            db.commit()
        else:
            await send(ctx, "`커뉴야 레벨역할 <목록/추가/삭제>")

    @command(name="레벨업채널")
    @has_permissions(administrator=True)
    async def set_lvup_channel(self, ctx, activity: Optional[str] = "조회"):
        lv = db.record("SELECT levelup_channel FROM guilds WHERE GuildID = ?", ctx.guild.id)
        lv = lv[0]
        if activity == "조회":
            if lv == 1:
                await send(ctx, f"현재 {ctx.guild.name}의 레벨업 알림 채널이 없어요!")
                return
            elif lv != 0:
                await send(ctx, f"현재 {ctx.guild.name}의 레벨업 알림 채널은 <#{lv}>(이)에요!")
                return
            else:
                await send(ctx, f"현재 {ctx.guild.name}에서는 레벨업을 해도 알림이 표시되지 않아요!")
                return
        elif activity == "초기화":
            await send(ctx, f"이제 {ctx.guild.name}의 레벨업 알림 채널이 없고 메세지가 보내진 채널에 알림이 와요!")
            ch = 1
        elif activity == "설정":
            await send(ctx, "어느 채널을 레벨업 채널로 설정할 건가요?")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                ch = msg.content[2:20]
            except asyncio.TimeoutError:
                await send(ctx, "레벨업 채널을 설정하지 않기로 했어요.")
                return
            await send(ctx, f"이제 {ctx.guild.name}의 레벨업 알림 채널은 <#{msg.content[2:20]}>(이)에요!")
        elif activity == "끔":
            await send(ctx, f"이제 {ctx.guild.name}에서는 레벨업을 해도 알림이 표시되지 않아요!")
            ch = 0
        else:
            await send(ctx, "`커뉴야 레벨업채널 <조회/설정/초기화>`")
            return
        db.execute("UPDATE guilds SET levelup_channel = ? WHERE GuildID = ?", ch, ctx.guild.id)
        db.commit()

    @command(name="경험치범위", aliases=["경범위", "경험범위"])
    @has_permissions(administrator=True)
    async def exp_range(self, ctx, activity: Optional[str] = "조회"):
        minexp, maxexp = db.record("SELECT min_xp, max_xp FROM guilds WHERE GuildID = ?", ctx.guild.id)
        if activity == "조회":
            await send(ctx, f"현재 {ctx.guild.name}에서는 {minexp} 부터 {maxexp} 까지의 경험치를 얻을 수 있어요!")
        elif activity == "설정":
            await send(ctx, "설정할 최소 경험치를 말해 주세요!")
            try:
                minmsg = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                newmin = int(minmsg.content)
            except asyncio.TimeoutError:
                await send(ctx, "경험치 범위를 설정하지 않기로 했어요..")
                return
            await send(ctx, "설정할 최대 경험치를 말해 주세요!")
            try:
                maxmsg = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
                newmax = int(maxmsg.content)
            except asyncio.TimeoutError:
                await send(ctx, "경험치 범위를 설정하지 않기로 했어요..")
                return
            if newmin > newmax:
                await send(ctx, "설정하려는 최소 경험치가 설정하려는 최대 경험치보다 커요! 최소 경험치를 더 작게 설정해 주세요.")
                return
            if newmin < 0:
                await send(ctx, "최소 경험치를 0 이상으로 설정해 주세요!")
                return
            try:
                db.execute("UPDATE guilds SET min_xp = ?, max_xp = ? WHERE GuildID = ?", newmin, newmax, ctx.guild.id)
                db.commit()
            except OverflowError:
                await send(ctx, "설정하려는 경험치의 양이 너무 커요! 좀 더 작게 설정해 주세요")
                return
            await send(ctx, f"경험치범위 설정을 완료했어요! 이제 {ctx.guild.name}에서는 챗을 칠 때마다 {newmin}부터 {newmax}까지의 경험치를 얻을 수 있어요!")
        else:
            await send(ctx, "`커뉴야 경험치범위 <조회/설정>`")

    @command(name="경험치쿨타임", aliases=["경험치쿨탐", "경험치쿨", "경쿨"])
    @has_permissions(administrator=True)
    async def set_exp_cooldown(self, ctx, activity: Optional[str] = "조회"):
        cool = db.record("SELECT XPcool FROM Guilds WHERE GuildID = ?", ctx.guild.id)
        cool = cool[0]
        if activity == "조회":
            await send(ctx, f"현재 {ctx.guild.name}에서는 {cool}초에 한 번만 경험치를 받을 수 있어요!")
        elif activity == "설정":
            await send(ctx, "설정할 경험치 쿨타임을 말해 주세요!")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    timeout=10,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "경험치 쿨타임 변경을 취소했어요.")
                return
            try:
                newcool = int(msg.content)
            except ValueError:
                await send(ctx, "숫자로만 입력해 주세요! (초 단위로)")
                return
            if newcool < 1:
                await send(ctx, "경험치 쿨타임은 자연수로만 설정할 수 있어요!")
                return
            db.execute("UPDATE guilds SET XPcool = ? WHERE GuildID = ?", newcool, ctx.guild.id)
            db.commit()
            await send(ctx, f"경험치 쿨타임 변경을 완료했어요! 이제 {ctx.guild.name}에서는 {newcool}초에 한 번만 경험치를 받을 수 있어요!")
        else:
            await send(ctx, "`커뉴야 경쿨 <조회/설정>`")

    @command(name="30렙색")
    async def lv_30_color(self, ctx):
        if ctx.guild.id != 743101101401964647: return
        lvl = db.record("SELECT Level FROM exp WHERE UserID = ? AND GuildID = ?", ctx.author.id, ctx.guild.id)
        lvl = lvl[0]
        if lvl >= 30:
            lv_30_role = ctx.guild.get_role(769923258022887494)
            if lv_30_role in ctx.author.roles:
                await ctx.author.remove_roles(lv_30_role)
                await send(ctx, "30레벨 색 장착 해제 성공!")
            else:
                await ctx.author.add_roles(lv_30_role)
                await send(ctx, "30레벨 색 장착 성공!")
        else:
            await send(ctx, "30레벨 이상만 쓸 수 있는 색이야.")

    @command(name="60렙색")
    async def lv_60_color(self, ctx):
        if ctx.guild.id != 743101101401964647: return
        lvl = db.record("SELECT Level FROM exp WHERE UserID = ? AND GuildID = ?", ctx.author.id, ctx.guild.id)
        lvl = lvl[0]
        if lvl >= 60:
            lv_30_role = ctx.guild.get_role(765570766951284786)
            if lv_30_role in ctx.author.roles:
                await ctx.author.remove_roles(lv_30_role)
                await send(ctx, "60레벨 색 장착 해제 성공!")
            else:
                await ctx.author.add_roles(lv_30_role)
                await send(ctx, "60레벨 색 장착 성공!")
        else:
            await send(ctx, "60레벨 이상만 쓸 수 있는 색이야.")

    @command(name="90렙색")
    async def lv_90_color(self, ctx):
        if ctx.guild.id != 743101101401964647: return
        lvl = db.record("SELECT Level FROM exp WHERE UserID = ? AND GuildID = ?", ctx.author.id, ctx.guild.id)
        lvl = lvl[0]
        if lvl >= 90:
            lv_30_role = ctx.guild.get_role(765570878573641728)
            if lv_30_role in ctx.author.roles:
                await ctx.author.remove_roles(lv_30_role)
                await send(ctx, "90레벨 색 장착 해제 성공!")
            else:
                await ctx.author.add_roles(lv_30_role)
                await send(ctx, "90레벨 색 장착 성공!")
        else:
            await send(ctx, "90레벨 이상만 쓸 수 있는 색이야.")

    @command(name="150렙색")
    async def lv_150_color(self, ctx):
        if ctx.guild.id != 743101101401964647: return
        lvl = db.record("SELECT Level FROM exp WHERE UserID = ? AND GuildID = ?", ctx.author.id, ctx.guild.id)
        lvl = lvl[0]
        if lvl >= 60:
            lv_30_role = ctx.guild.get_role(788294915267625001)
            if lv_30_role in ctx.author.roles:
                await ctx.author.remove_roles(lv_30_role)
                await send(ctx, "150레벨 색 장착 해제 성공!")
            else:
                await ctx.author.add_roles(lv_30_role)
                await send(ctx, "150레벨 색 장착 성공!")
        else:
            await send(ctx, "150레벨 이상만 쓸 수 있는 색이야.")

    @command(name="레벨", aliases=["렙"])
    @cooldown(2, 1, BucketType.user)
    async def display_level(self, ctx, *, target: Optional[Member]):
        target = target or ctx.author

        xp, lvl = db.record("SELECT XP, Level FROM exp WHERE UserID = ? AND GuildID = ?", target.id, ctx.guild.id) or (
        None, None)
        ids = db.column("SELECT UserID FROM exp WHERE GuildID = ? ORDER BY XP DESC", ctx.guild.id)

        if lvl is not None:
            rank = ids.index(target.id) + 1
            sangwee = rank / len(ids) * 100
            now_exp = xp - lvl ** 2 * 50 - 25 * lvl
            exp_rksrur = ((lvl + 1) ** 2 * 50 + 25 * (lvl + 1)) - (lvl ** 2 * 50 + 25 * lvl)
            embed = discord.Embed(colour=0xffd6fe)
            embed.add_field(name=f"{target.display_name} 의 레벨 정보", value="​", inline=False)
            embed.add_field(name="레벨", value=f"{lvl:}", inline=True)
            embed.add_field(name="경험치", value=f"{now_exp:,} / {exp_rksrur:,} ({round(now_exp / exp_rksrur * 100, 1)}%)",
                            inline=True)
            embed.add_field(name="레벨업까지 남은 경험치", value=f"{(exp_rksrur - now_exp):,}", inline=False)
            embed.add_field(name="총 경험치", value=f"{xp:,}", inline=False)
            embed.set_thumbnail(url=target.avatar_url)
            try:
                embed.add_field(name="등수", value=f"{rank} 등 (상위 {round(sangwee, 3)}%)", inline=False)
            except ValueError:
                pass
            # if rank != 1:
            #     next_rank = db.record("SELECT XP FROM exp WHERE UserID = ? AND GuildID = ?", ids[rank - 2],
            #                           ctx.guild.id)
            #     next_rank_delta = next_rank[0] - now_exp
            #     embed.add_field(name="등수 상승까지 더 필요한 경험치", value=f"{next_rank_delta:,}")
            await send(ctx, embed=embed)

        else:
            await send(ctx, "0렙, 꼴등")

    @command(name="돈")
    async def display_money(self, ctx, *, target: Optional[Member]):
        type = db.record("SELECT guild_type FROM guilds WHERE GuildID = ?", ctx.guild.id)
        if type[0] & 1 != 1: return
        target = target or ctx.author

        money = db.record("SELECT Money FROM exp WHERE UserID = ? AND GuildID = ?", target.id, ctx.guild.id)
        money = money[0]

        if money is not None:
            embed = discord.Embed(colour=0xffd6fe)
            embed.add_field(name=f"{target.display_name} 의 돈 정보", value="​", inline=False)
            embed.add_field(name="가진 돈", value=f"{money:,}<:treasure:811456823248027648>", inline=True)
            embed.set_thumbnail(url=target.avatar_url)
            await send(ctx, embed=embed)

            if target == ctx.author and money >= 1000000:
                l = grant_check("공식서버 만수르", ctx.author.id)
                if l == 1:
                    await grant(ctx, "공식서버 만수르", "공식서버에서 돈 1,000,000 이상을 가지세요")

    @command(name="리더보드")
    async def display_leaderboard(self, ctx, jong_mok: Optional[str] = "경험치", pg: Optional[int] = 1):
        if jong_mok == "경험치":
            records = db.records("SELECT UserID, XP, Level, XPBoost FROM exp WHERE GuildID = ? ORDER BY XP DESC",
                                 ctx.guild.id)

            menu = MenuPages(source=HelpMenu(ctx, records),
                             clear_reactions_after=False)
            await menu.start(ctx)
        elif jong_mok in ["잡초키우기", "잡키"]:
            records = db.records("SELECT UserID, zl, zf FROM games WHERE zl IS NOT NULL ORDER BY zl DESC LIMIT ?, ?",
                                 10 * int(pg) - 10, 10)
            tjfaud = ""
            now_people = int(pg) * 10 - 9
            for record in records:
                tjfaud = tjfaud + f"{now_people}. <@{record[0]}> (잡초 레벨: {int(record[1])} | 비료 개수: {record[2]})  \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=0x00ff7f, title="잡초키우기 랭킹!", description=tjfaud))
        elif jong_mok in ["우주탐험", "우탐"]:
            records = db.records(
                "SELECT UserID, explore_level FROM games WHERE explore_level != 0 ORDER BY explore_level DESC LIMIT ?, ?",
                10 * int(pg) - 10, 10)
            tjfaud = ""
            now_people = 10 * int(pg) - 9
            for record in records:
                tjfaud = tjfaud + f"{now_people}. <@{record[0]}> (탐험 레벨: {record[1]}) \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=0x4849c3, title="우주탐험 랭킹!", description=tjfaud))
        elif jong_mok in ["묵찌빠", "묵"]:
            records = db.records(
                "SELECT UserID, mook_chi_pa_mmr FROM games WHERE mook_chi_pa_mmr != 4000 ORDER BY mook_chi_pa_mmr DESC LIMIT ?, ?",
                10 * pg - 10, 10)
            tjfaud = ""
            now_people = 10 * pg - 9
            for record in records:
                tier, num = check_tier(record[0])
                tjfaud = tjfaud + f"{now_people}. <@{record[0]}> (티어: {tier} {num} | 점수: {record[1]}) \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=ctx.author.color, title="묵찌빠 랭킹!", description=tjfaud))
            return
        elif jong_mok in ["서버강화", "섭강"]:
            records = db.records(
                "SELECT GuildID, enchant_level FROM guilds WHERE enchant_level != 0 ORDER BY enchant_level DESC LIMIT ?, ?",
                10 * pg - 10, 10)
            tjfaud = ""
            now_servers = 10 * pg - 9
            for record in records:
                tjfaud = tjfaud + f"{now_servers}. {self.bot.get_guild(record[0]).name} (강화 레벨: {record[1]}) \n"
                now_servers += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 서버가 없는 것 같아요!"
            await send(ctx, embed=Embed(color=ctx.author.color, title="강화 랭킹!", description=tjfaud))
        elif jong_mok == "돈":
            records = db.records("SELECT UserID, Money FROM exp WHERE GuildID = ? ORDER BY Money DESC LIMIT ?, ?",
                                 ctx.guild.id, 10 * pg - 10, 10)
            tjfaud = ""
            now_people = 10 * pg - 9
            for record in records:
                tjfaud = tjfaud + f"{now_people}. {self.bot.get_user(record[0]).name} (가진 돈: {record[1]}) \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=ctx.author.color, title="돈 랭킹!", description=tjfaud))
        elif jong_mok == "경부":
            records = db.records("SELECT UserID, XPBoost FROM exp WHERE GuildID = ? ORDER BY XPBoost DESC LIMIT ?, ?",
                                 ctx.guild.id, 10 * pg - 10, 10)
            tjfaud = ""
            now_people = 10 * pg - 9
            for record in records:
                tjfaud = tjfaud + f"{now_people}. {self.bot.get_user(record[0]).name} (경험치 부스트: {record[1]}) \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=ctx.author.color, title="경험치 부스트 랭킹!", description=tjfaud))
        elif jong_mok == "퀴즈":
            records = db.records(
                "SELECT UserID, quiz_mmr FROM games WHERE quiz_mmr != 0 ORDER BY quiz_mmr DESC LIMIT ?, ?",
                10 * int(pg) - 10, 10)
            tjfaud = ""
            now_people = 10 * int(pg) - 9
            for record in records:
                tjfaud = tjfaud + f"{now_people}. <@{record[0]}> (퀴즈 점수: {record[1]}) \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=0x4849c3, title="퀴즈 랭킹!", description=tjfaud))
        elif jong_mok == "오목":
            records = db.records(
                "SELECT UserID, omok_mmr FROM games WHERE omok_mmr != 0 ORDER BY omok_mmr DESC LIMIT ?, ?",
                10 * int(pg) - 10, 10)
            tjfaud = ""
            now_people = 10 * int(pg) - 9
            for record in records:
                tjfaud = tjfaud + f"{now_people}. <@{record[0]}> (오목 점수: {record[1]}) \n"
                now_people += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 사람이 없는 것 같아요!"
            await send(ctx, embed=Embed(color=0x4849c3, title="오목 랭킹!", description=tjfaud))
        elif jong_mok == '도전과제':
            score_info = db.records(
                "SELECT * FROM (SELECT UserID, count(name) as n FROM achievement_progress GROUP BY UserID) ORDER BY n DESC LIMIT 10")
            tjfaud = ""
            ids = []
            scores = []
            for uid, score in score_info:
                ids.append(uid)
                scores.append(score)
            for uid in ids:
                a = ids.index(uid)
                b = scores[a]
                c = scores.index(b) + 1
                tjfaud += '\n' * (c != 1) + f"{c}. {self.bot.get_user(uid)} (달성한 도전 과제 {b}개)"
            embed = Embed(color=0xffd6fe, title=f"전체 도전과제 랭킹", description=tjfaud)
            await send(ctx, embed=embed)
        elif jong_mok == '커뉴핑크':
            score_info = db.records(
                "SELECT UserID, total_exp FROM conupink_user_info ORDER BY total_exp DESC LIMIT 10")
            tjfaud = ""
            ids = []
            scores = []
            for uid, score in score_info:
                ids.append(uid)
                scores.append(score)
            for uid in ids:
                a = ids.index(uid)
                b = scores[a]
                c = scores.index(b) + 1
                tjfaud += '\n' * (c != 1) + f"{c}. {self.bot.get_user(uid)} (총 경험치 {b})"
            embed = Embed(color=0xffd6fe, title=f"커뉴핑크 경험치 랭킹", description=tjfaud)
            await send(ctx, embed=embed)
        else:
            await send(ctx, "경험치(또는 빈칸), 돈, 경부, 서버강화, 잡초키우기, 우주탐험, 퀴즈, 오목, 도전과제, 커뉴핑크")

    @command(name="경험치부스트", aliases=["경부"])
    async def display_exp_boost(self, ctx, *, target: Optional[Member]):
        target = target or ctx.author
        boost = db.record("SELECT XPBoost FROM exp WHERE UserID = ? AND GuildID = ?", target.id, ctx.guild.id)
        boost = boost[0]

        embed = discord.Embed(color=0xffd6fe)
        embed.add_field(name=f"{target.display_name}의 경험치 부스트", value=f"{boost}")
        embed.set_footer(text=f"요청한 이 {ctx.author}")
        await ctx.channel.send(embed=embed)

    @command(name="상점")
    async def display_shop(self, ctx, activity: Optional[str], *, item: Optional[str]):
        if ctx.guild.id != 743101101401964647: return
        embed = discord.Embed(colour=0xffd6fe)
        delta = 0
        dtype = 0
        if not activity:
            items = db.records("SELECT name, created_by, cost, amount FROM items")
            for item in items:
                embed.add_field(name=item[0],
                                value=f"가격: {item[2]}\n팔기로 한 사람: {self.bot.get_user(item[1])}\n남은 재고: {'무제한' if item[3] == -1 else item[3]}")
            await send(ctx, embed=embed)
        elif activity == "등록":
            current = db.records("SELECT name FROM items WHERE created_by = ?", ctx.author.id)
            if len(current) == 3:
                await send(ctx, "한 번에 팔 수 있는 아이템 개수가 최대에 도달했어요!")
                return
            if item:
                msg1 = item
            else:
                await send(ctx, "팔 아이템 이름을 말해주세요! (최대 32글자)")
                try:
                    msg1 = await self.bot.wait_for(
                        "message",
                        timeout=30,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                except asyncio.TimeoutError:
                    await send(ctx, "아이템 등록을 취소했어요.")
                    return
                msg1 = msg1.content
            if len(msg1) > 32:
                await send(ctx, "아이템 이름이 너무 길어요!")
                return
            for tem in current:
                if tem[0] == msg1:
                    await send(ctx, "아이템명이 중복돼요!")
                    return
            await send(ctx, "아이템의 설명을 적어 주세요!")
            try:
                msg2 = await self.bot.wait_for(
                    "message",
                    timeout=120,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "아이템 등록을 취소했어요.")
                return
            msg2 = msg2.content
            if len(msg2) > 255:
                await send(ctx, "아이템 설명이 너무 길어요!")
                return
            await send(ctx, 
                "아이템의 가격을 정해 주세요!다음과 같은 입력들을 인식해요:\n10000: 10000의 가격으로 판매합니다.\n10000+1000: 처음에는 10000으로 팔고 한 번 팔릴 때마다 가격을 1000씩 증가시킵니다.\n10000*2: 처음에는 10000으로 팔고 한 번 팔릴 때마다 가격을 2배씩 증가시킵니다. (만약 정수가 나오지 않으면 반올림합니다.)")
            try:
                msg5 = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "아이템 등록을 취소했어요.")
                return
            try:
                msg3 = str(int(msg5.content))
            except ValueError:
                plus = re.compile("\d*[+]\d*")
                multi = re.compile("\d*[*]\d*")
                if plus.match(msg5.content) or multi.match(msg5.content):
                    msg3 = msg5.content
                else:
                    await send(ctx, "올바르지 않은 입력 방식이에요!")
                    return
            await send(ctx, "아이템을 몇 개나 팔 건지 결정해 주세요! (-1을 입력해 무제한으로 설정)")
            try:
                msg4 = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                )
            except asyncio.TimeoutError:
                await send(ctx, "아이템 등록을 취소했어요.")
                return
            try:
                msg4 = int(msg4.content)
            except TypeError:
                await send(ctx, "올바르지 않은 입력 방식이에요!")
                return
            if msg4 == 0 or msg4 < -1:
                await send(ctx, "올바르지 않은 입력 방식이에요!")
                return
            db.execute("INSERT INTO items (name, description, created_by, cost, amount) VALUES (?, ?, ?, ?, ?)", msg1,
                       msg2, ctx.author.id, msg3, msg4)
            db.commit()
            await send(ctx, "등록을 완료했어요!")
        elif activity == "삭제":
            if item:
                msg4 = item
            else:
                await send(ctx, "삭제할 아이템 이름을 말해 주세요!")
                try:
                    msg4 = await self.bot.wait_for(
                        "message",
                        timeout=30,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                    msg4 = msg4.content
                except asyncio.TimeoutError:
                    await send(ctx, "아이템 삭제를 취소했어요.")
                    return
            for current in db.records("SELECT name FROM items WHERE created_by = ?", ctx.author.id):
                if current[0] == msg4:
                    break
            else:
                await send(ctx, "해당 아이템을 팔고 있지 않아요!")
                return
            db.execute("DELETE FROM items WHERE name = ? AND created_by = ?", msg4, ctx.author.id)
            await send(ctx, "아이템 삭제를 완료했어요!")
            return
        elif activity == "신고":
            if item:
                msg5 = item
            else:
                await send(ctx, "어떤 아이템을 신고하실 건가요?")
                try:
                    msg5 = await self.bot.wait_for(
                        "message",
                        timeout=30,
                        check=lambda message: message.author == ctx.author and ctx.channel == message.channel
                    )
                    msg5 = msg5.content
                except asyncio.TimeoutError:
                    await send(ctx, "아이템 신고를 취소했어요.")
                    return
            if not db.record("SELECT name FROM items WHERE name = ?", msg5)[0]:
                await send(ctx, "존재하지 않는 아이템명이에요!")
                return
            await send(ctx, "신고를 완료했어요!")
            await self.bot.get_channel(823393077376581654).send(f"{ctx.author}님이 아이템을 신고함\n신고한 템: {msg5}")

    @command(name="서버강화", aliases=["섭강"])
    @cooldown(1, 60, BucketType.guild)
    async def enchant_server(self, ctx, extra: Optional[str], page: Optional[int] = 1):
        server_level = db.record("SELECT enchant_level FROM guilds WHERE GuildID = ?", ctx.guild.id)[0]
        if ctx.author.bot:
            await self.bot.get_channel(823393077376581654).send(
                f'봇으로 서버강화 시도, 서버 아이디: {ctx.guild.id}, 현재 레벨: {server_level}')
            await send(ctx, "봇으로 서버강화를 시도했습니다. 당분간 이 서버에서 오는 서버강화 시도는 무시됩니다. 기간은 이전에 몇 번이나 같은 행동을 했는지에 따라 결정됩니다.")
            db.execute("UPDATE guilds SET enchant_level = -1 WHERE GuildID = ?", ctx.guild.id)
            return
        if server_level == -1:
            return
        temp = random()
        probability = max(1 - 0.01 * server_level, 0.1)
        embed = Embed(color=ctx.author.color)
        if temp < probability:
            server_level += 1
            embed.add_field(name="강화 성공!", value=f"{server_level}레벨로 강화되었습니다!")
        else:
            embed.add_field(name="강화 실패...", value=f"현재 레벨: {server_level}")
        probability = probability * 100
        probability = round(probability)
        probability = int(probability)
        embed.set_footer(text=f"강화 성공 확률 {probability}%")
        await send(ctx, embed=embed)
        db.execute("UPDATE guilds SET enchant_level = ? WHERE GuildID = ?", server_level, ctx.guild.id)
        db.commit()
        if extra in ["리더보드", "릳"]:
            records = db.records(
                "SELECT GuildID, enchant_level FROM guilds WHERE enchant_level != 0 ORDER BY enchant_level DESC LIMIT ?, ?",
                10 * page - 10, 10)
            tjfaud = ""
            now_servers = 10 * page - 9
            for record in records:
                tjfaud = tjfaud + f"{now_servers}. {self.bot.get_guild(record[0]).name} (강화 레벨: {record[1]}) \n"
                now_servers += 1
            if tjfaud == "":
                tjfaud = "선택하신 페이지에는 서버가 없는 것 같아요!"
            await send(ctx, embed=Embed(color=ctx.author.color, title="강화 랭킹!", description=tjfaud))
        db.commit()

    @command(name="초대횟수")
    async def my_invites(self, ctx, *, target: Optional[Member]):
        target = target or ctx.author
        invite_score = db.record("SELECT invite_score FROM exp WHERE UserID = ? AND GuildID = ?", target.id,
                                 ctx.guild.id)
        invite_score = invite_score[0]
        ids = db.column("SELECT UserID FROM exp WHERE GuildID = ? ORDER BY invite_score DESC", ctx.guild.id)
        rank = ids.index(target.id) + 1
        embed = Embed(color=ctx.author.color)
        embed.add_field(name=f"{target.display_name} 의 초대 정보", value="​", inline=False)
        embed.add_field(name="초대 횟수", value=f"{invite_score}", inline=True)
        embed.add_field(name="등수", value=f"{rank}등")
        embed.set_thumbnail(url=target.avatar_url)
        await send(ctx, embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            print('("exp")')

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            if not isinstance(message.channel, DMChannel):
                await self.process_xp(message)


async def setup(bot):
    await bot.add_cog(Exp(bot))
