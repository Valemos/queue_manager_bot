from sqlalchemy import Column, Integer

from queue_bot.database import Session
from queue_bot.objects.registered_manager import get_chat_registered


class ADialogState:
    chat_id = Column(Integer)
    user_id = Column(Integer)

    def __init__(self, chat_id, user_id):
        self.chat_id = chat_id
        self.user_id = user_id

    @classmethod
    def get_or_create_state(cls, update):
        with Session() as session:
            info = get_chat_registered(update.effective_chat.id).get_update_user_info(update)
            if info.telegram_id is None:
                return None

            state = session.query(cls).where(chat_id=update.effective_chat.id,
                                             user_id=info.telegram_id).first()

            if state is None:
                with Session.begin() as inner_session:
                    state = cls(chat_id=update.effective_chat.id,
                                user_id=info.telegram_id)
                    inner_session.add(state)

            return state
