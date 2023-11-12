from aiogram import Router
from aiogram.types import Message
from chat_engine.processor import interface
import main
router = Router()

@router.message()
async def out_of_flow_handler(message: Message) -> None:
    """
    This handler receives messages out of /start OR /stop command
    """

    status = interface.process_user_message(income_user_chat_id=message.chat.id)
    active_chat_exists = status.get('chat_id') # Companion chat id
    service_message = status.get('Service message')

    if active_chat_exists:
        await Message(
            chat=message.chat, 
            message_id=message.message_id, 
            date=message.date
            ).copy_to(chat_id=active_chat_exists).as_(main.bot)

    else:
        await message.answer(text=service_message)
