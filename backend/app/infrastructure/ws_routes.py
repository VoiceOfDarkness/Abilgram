import logging
from datetime import datetime
from typing import Dict

import socketio

logger = logging.getLogger(__name__)


class ChatNamespace(socketio.AsyncNamespace):
    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.active_users: Dict[str, str] = {}
        self.online_users: Dict[str, bool] = {}

    async def on_connect(self, sid, environ):
        logging.info(f"[CONNECT] New connection, SID: {sid}")

    async def on_set_user_id(self, sid, data):
        user_id = data.get("user_id")
        logging.info(f"[USER ID] {user_id}")

        if user_id:
            if self.active_users.get(sid) == user_id:
                logging.info(f"[SKIP] SID {sid} already assigned to User ID {user_id}")
                return

            existing_sids = [
                key
                for key, value in self.active_users.items()
                if value == user_id and key != sid
            ]

            for old_sid in existing_sids:
                self.active_users.pop(old_sid, None)
                try:
                    await self.disconnect(old_sid)
                    logging.info(
                        f"[DISCONNECT OLD] Disconnected old session SID: {old_sid}"
                    )
                except Exception as e:
                    logging.error(f"Error disconnecting old session: {e}")

            self.active_users[sid] = user_id
            self.online_users[user_id] = True
            logging.info(f"[SET USER ID] SID: {sid} -> User ID: {user_id}")
            logging.info(f"[ACTIVE USERS] {self.active_users}")

    async def on_get_online_users(self, sid):
        logging.info(f"[GET ONLINE USERS] Request from SID: {sid}")
        logging.info(f"[ONLINE USERS] Current online users: {self.online_users}")
        online_users = {key: value for key, value in self.online_users.items()}
        await self.emit("online_users", online_users, room=sid)

    async def on_disconnect(self, sid):
        user_id = self.active_users.pop(sid, None)
        self.online_users.pop(user_id, None)
        logging.info(f"[DISCONNECT] SID: {sid}, User ID: {user_id} disconnected")

    async def on_chat(self, sid, data):

        user_id = data.get("user_id")

        logging.info(f"[ACTIVE USERS] {self.active_users}")

        if not user_id or not data:
            return

        await self.emit("new_chat", data["chat"])

    async def on_message(self, sid, data):
        recipient_id = data.get("recipient_id")
        message = data.get("message")
        sender_id = self.active_users.get(sid)

        logging.info(f"[USER DATA FROM MESSAGE] {data} and {sender_id}")

        if not all([recipient_id, message, sender_id]):
            logging.warning("Invalid message data")
            return

        if sid not in self.active_users:
            logging.warning(f"Unauthorized message attempt from SID: {sid}")
            return

        recipient_sid = next(
            (s for s, u in self.active_users.items() if u == recipient_id), None
        )

        if recipient_sid:
            message_data = {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "content": message,
                "created_at": datetime.now().isoformat(),
            }
            await self.emit("new_message", message_data, room=recipient_sid)
            logging.info(f"Message from {sender_id} sent to {recipient_id}")
        else:
            logging.warning(f"Recipient {recipient_id} not connected")
