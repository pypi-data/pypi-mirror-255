import asyncio
import typing
from logging import getLogger

import Pyrofork
from Pyrofork import Client
from Pyrofork.errors import FloodWait, Forbidden, SlowmodeWait
from Pyrofork.methods import Decorators

from Abg.config import Config

from .utils import handle_error

HANDLER = Config.HANDLER
LOGGER = getLogger(__name__)


def command(
    self,
    cmd: typing.Union[str, list],
    is_disabled: typing.Union[bool, bool] = False,
    pm_only: typing.Union[bool, bool] = False,
    group_only: typing.Union[bool, bool] = False,
    self_admin: typing.Union[bool, bool] = False,
    self_only: typing.Union[bool, bool] = False,
    handler: typing.Optional[list] = None,
    filtercmd: typing.Union[Pyrofork.filters.Filter, Pyrofork.filters.Filter] = None,
    *args,
    **kwargs,
):
    """
    ### `@Client.on_cmd`
    - A decorater to Register Commands in simple way and manage errors in that Function itself, alternative for `@Pyrofork.Client.on_message(Pyrofork.filters.command('command'))`
    - Parameters:
    - cmd (str || list):
        - The command to be handled for a function

    - group_only (bool) **optional**:
        - If True, the command will only executed in Groups only, By Default False.

    - pm_only (bool) **optional**:
        - If True, the command will only executed in Private Messages only, By Default False.

    - self_only (bool) **optional**:
        - If True, the command will only excute if used by Self only, By Default False.

    - handler (list) **optional**:
        - If set, the command will be handled by the specified Handler, By Default `Config.HANDLERS`.

    - self_admin (bool) **optional**:
        - If True, the command will only executeed if the Bot is Admin in the Chat, By Default False

    - filtercmd (`~Pyrofork.filters`) **optional**:
        - Pyrofork Filters, hope you know about this, for Advaced usage. Use `and` for seaperating filters.

    #### Example
    .. code-block:: python
        import Pyrofork

        app = Pyrofork.Client(..)

        @app.on_cmd("start", is_disabled=False, group_only=False, pm_only=False, self_admin=False, self_only=False, Pyrofork.filters.chat("777000") and Pyrofork.filters.text)
        async def start(abg: Client, message):
            await message.reply_text(f"Hello {message.from_user.mention}")
    """
    if handler is None:
        handler = HANDLER
    if filtercmd:
        if self_only:
            filtercmd = (
                Pyrofork.filters.command(cmd, prefixes=handler)
                & filtercmd
                & Pyrofork.filters.me
            )
        else:
            filtercmd = (
                Pyrofork.filters.command(cmd, prefixes=handler)
                & filtercmd
                & Pyrofork.filters.me
            )
    else:
        if self_only:
            filtercmd = (
                Pyrofork.filters.command(cmd, prefixes=handler) & Pyrofork.filters.me
            )
        else:
            filtercmd = Pyrofork.filters.command(cmd, prefixes=handler)

    def wrapper(func):
        async def decorator(abg: Client, message: Pyrofork.types.Message):
            if is_disabled:
                return await message.reply_text(
                    "sᴏʀʀʏ, ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ʙʏ ᴏᴡɴᴇʀ."
                )
            if self_admin and message.chat.type != Pyrofork.enums.ChatType.SUPERGROUP:
                return await message.reply_text(
                    "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ɪɴ sᴜᴘᴇʀɢʀᴏᴜᴘs ᴏɴʟʏ."
                )
            if self_admin:
                me = await abg.get_chat_member(message.chat.id, (await abg.get_me()).id)
                if me.status not in (
                    Pyrofork.enums.ChatMemberStatus.OWNER,
                    Pyrofork.enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    return await message.reply_text(
                        "ɪ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ"
                    )
            if group_only and message.chat.type != Pyrofork.enums.ChatType.SUPERGROUP:
                return await message.reply_text(
                    "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ɪɴ sᴜᴘᴇʀɢʀᴏᴜᴘs ᴏɴʟʏ."
                )
            if pm_only and message.chat.type != Pyrofork.enums.ChatType.PRIVATE:
                return await message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ɪɴ ᴘᴍs ᴏɴʟʏ.")
            try:
                await func(abg, message, *args, **kwargs)
            except Pyrofork.StopPropagation:
                raise
            except Pyrofork.ContinuePropagation:
                pass
            except FloodWait as fw:
                LOGGER.warning(str(fw))
                await asyncio.sleep(fw.value)
                LOGGER.warning("Sleeping for {fw.value}, Due to flood")
            except (Forbidden, SlowmodeWait):
                LOGGER.warning(
                    f"Leaving chat : {message.chat.title} [{message.chat.id}], because doesn't have write permission."
                )
                return await message.chat.leave()
            except BaseException as e:
                return await handle_error(e, message)

        self.add_handler(
            Pyrofork.handlers.MessageHandler(callback=decorator, filters=filtercmd)
        )
        return decorator

    return wrapper


Decorators.on_cmd = command
