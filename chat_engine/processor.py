from typing import Union, List, Dict, Optional
import sqlite3
from storage.sqlite3DB import db

class QueueModel:
    def __init__(self) -> None:
        self.users_list = []
        
    @property
    def ready_to_chat(self):
        return len(self.users_list) == 2
    
    def append(self, value: int):
        self.users_list.append(value)

    def __repr__(self) -> str:
        return f"Chat. Users: {self.users_list} Ready to chat: {self.ready_to_chat}"

class ChatBase:
    def __init__(self, db: sqlite3) -> None:
        """Initialize Sqlite3 Active chat DB interface object"""

        self.db = db

    def _get_chat_users(self, user_id)-> Optional[List]:
        """Method search for user IDs in active chat DB 
        
        :param user_id: search argument for db to search
        :return: both active chat user IDs by searching one of them - if found
        
        """
        recieved_data = self.db.get_data_by_user_id(user_id=user_id)
        
        if recieved_data:
            recieved_data = [user_id for user_id in recieved_data[0]]
            return recieved_data
    
    def _get_companion_id(self, query_user_id: int, users_collection: List[int])-> int:
        """Method to get companion chat_id (user_id) for Active chat companions list

        :param query_user_id: known users_id
        :param users_collection: Active chat companions list
        return: unknown companion chat_id
        
        """
        users_collection.remove(query_user_id)
        return users_collection[0]
    
    def user_in_active_chat(self, user_id: int, return_companion_id:bool=False)-> Union[bool, int]:
        """Method detects is user present in Active chat DB

        :param user_id: chat id which presense checks into Active chat DB
        :param return_companion_id: argument to return 
            companion chat id instead of True 
            if user_id is present in Active chat DB
        
        :return: bool by default - is user_id present in Active chat DB
            companion chat id - if user_id present in Active chat DB and return_companion_id == True
        
        """
        user_in_db = self._get_chat_users(user_id)
       
        if user_in_db and return_companion_id:
            return self._get_companion_id(query_user_id=user_id, users_collection=user_in_db)

        elif user_in_db:
            return True

        else:
            return False
    
    def add_users_to_active_chat(self, users_collection: List[int]) -> None:
        """Method add two chat IDs from users_collection to DB"""

        self.db.insert_data(f'{str(users_collection[0])}, {str(users_collection[1])}')
    
    def delete_users_from_active_chat(self, user_id: int) -> None:
        """Method delete both chat IDs (user_id and companion) DB using user_id"""

        self.db.delete_data_by_user_id(user_id)


class UsersHandler:
    
    chat_queue = []
    chat_base = ChatBase(db)
        
    def _user_present_in_chat_queue(self, income_user_chat_id: int):
        """Method return bool is income_user_chat_id is present is chat_queue
        
        :param income_user_chat_id: User chat ID which presens need to detect
        :return: income_user_chat_id presense state

        """
        if income_user_chat_id in self.chat_queue:
            return True
        else:
            False
            
    def _add_user_to_chat_or_queue(self, income_user_chat_id: int) -> Dict:
        """Method handle adding chat ID within 2 options:
        1. chat_queue list is EMPTY: User chat ID who sent /add command - will be added to chat queue list
        2. chat_queue list is NOT EMPTY: User chat ID who sent /add command and first user from
           chat_queue list will be added to Active Chat DB AND user from chat_queue list who added to 
           Active Chat DB - will be removed from chat_queue list
        
        :param income_user_chat_id: User chat ID who sent /add command
        :return: Dict with Service Message if income_user_chat_id added to chat queue 
                 OR Dict with companion chat ID if new Active Chat recorded to DB
    
        """
        if not self.chat_queue:
            # For case if not chat id exists in queue - user will be first in chat queue
            self.chat_queue.append(income_user_chat_id)
            output = {'Service message': 'You are already in chat queue - please wait for companion.'}

        else:
            # Both users are ready to communicate
            # Need to inform both users IF companion found - they can chat
            companion_id = self.chat_queue.pop(0)
            self.chat_base.add_users_to_active_chat([income_user_chat_id, companion_id])
            output = {
                'chat_id': companion_id, 
                'Service message': 
                'Anonimous companion for you is found. Message here.'+
                '\n\nSend /stop to exit from chat with anonimous companion'
            }
        
        return output

    def _get_user_status(self, income_user_chat_id) -> Dict:
        """Method detect user status and return string with status name of None if not recognized status
        
        :param income_user_chat_id: user id for search into chat queue and active chat base
        :param income_user_chat_id: return or not companion chat id if status is: in active chat
        :return: Dict status if found, else None
        
        """
        user_status = {}
        in_active_chat = self.chat_base.user_in_active_chat(income_user_chat_id, True)
        print(f'in_active_chat {in_active_chat}')
        if in_active_chat:
            user_status.update({'status': 'in_active_chat', 'companion_chat_id': in_active_chat} )

        elif self._user_present_in_chat_queue(income_user_chat_id): # if in queue
            user_status.update({'status': 'in_queue'})

        return user_status
    
    def process_user_start(self, income_user_chat_id: int) -> Dict:
        """
        Method handle /start command within 3 user states:

        - in queue: return Service Message about user is already in chat queue
        - in active chat: return Service Message about user is already in Active Chat with companion
        - no status: add user to chat queue if it is empty OR 
                     create Active Chat with chat ID which already recorded into chat queue earlier AND
                     return Service Message about Active Chat is already created

        :param income_user_chat_id: Chat ID user who sends /add comand
        :return: Dict with companion chat ID if Active Chat created or Dict with Service Message else
        
        """
        user_status = self._get_user_status(income_user_chat_id)
        process_result = {}
        match user_status.get('status'):

            case 'in_queue':
                process_result.update(
                    {'Service message': 
                     'Warning! You are already in chat queue - please wait for companion.'
                    }
                )

            case 'in_active_chat':
                process_result.update({'Service message': 'Warning! You are already in chat now.'})

            case _:
                process_result.update(self._add_user_to_chat_or_queue(income_user_chat_id))
        
        return process_result

    def process_user_message(self, income_user_chat_id) -> Dict:
        """
        Method handle message without any command within 3 user states:

        - in queue: return Service Message about user is in chat queue - need to wait for companion
        - in active chat: return companion chat ID
        - no status: return Service Message about user is not in active chat

        :param income_user_chat_id: Chat ID user who sends message
        :return: Dict with existing user chat ID IF Active Chat created 
                 OR Dict with Service Message ELSE
        
        """
        user_status = self._get_user_status(income_user_chat_id)
        process_result = {}
        match user_status.get('status'):

            case 'in_queue':
                process_result.update({
                    'Service message': 'You are in queue now. Please wait for companion.'+
                    '\n\nAlso you can exit queue by sending /stop command'
                })

            case 'in_active_chat':
                process_result.update({'chat_id': user_status['companion_chat_id']})

            case _:
                process_result.update({
                    'Service message': 'You are not in the active chat. ' +
                    'Please send the /start command to be placed in '+
                    'chat queue to wait for random anonimous user to chat with.'
                })
        
        return process_result

    def process_user_stop(self, income_user_chat_id) -> Dict:
        """
        Method handle /stop command within 3 user states:

        - in queue: delete user who sends /stop command from chat_queue and return Service Message about it
        - in active chat: delete both users from DB chat record and return companion chat ID
        - no status: return Service Message that Command not take effect

        :param user_chat_id: Chat ID user who sends /stop comand
        :return: Dict with existing user chat ID IF Active Chat created 
                 OR Dict with Service Message ELSE
        
        """
        user_status = self._get_user_status(income_user_chat_id)
        process_result = {}
        match user_status.get('status'):

            case 'in_queue':
                self.chat_queue.remove(income_user_chat_id)
                process_result.update({
                    'Service message': 
                    'Wait for companion stopped. You was deleted from chat queue.'
                })

            case 'in_active_chat':
                self.chat_base.delete_users_from_active_chat(income_user_chat_id)
                process_result.update({'chat_id': user_status['companion_chat_id']})

            case _:
                process_result.update({
                    'Service message': 
                    'You are not in the chat or wait for companion queue. Command not take effect.'
                })
        
        return process_result

interface = UsersHandler()