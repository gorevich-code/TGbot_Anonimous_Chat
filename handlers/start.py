from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.methods.send_message import SendMessage
import main
from chat_engine.processor import interface


router = Router()

@router.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    status = interface.process_user_start(income_user_chat_id=message.chat.id)
    new_active_chat_created = status.get('chat_id') # Companion chat id
    service_message = status.get('Service message')

    if new_active_chat_created:
        await SendMessage(chat_id=new_active_chat_created, text=service_message).as_(main.bot)
        await message.answer(text=service_message)

    else:
        await message.answer(text=service_message)
