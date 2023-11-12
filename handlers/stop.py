from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.methods.send_message import SendMessage
import main
from chat_engine.processor import interface


router = Router()

@router.message(Command('stop'))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/stop` command
    """
    status = interface.process_user_stop(income_user_chat_id=message.chat.id)
    active_chat_exists = status.get('chat_id') # Companion chat id
    service_message = status.get('Service message')

    if active_chat_exists:
        await SendMessage(chat_id=active_chat_exists, text='Your companion left the chat').as_(main.bot)
        await message.answer(text='You successfully left from chat')

    else:
        await message.answer(text=service_message)
