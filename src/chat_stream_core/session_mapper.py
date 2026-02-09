from datetime import datetime
from typing import Any
import uuid


class ChatSession:
    def __init__(self, session_id: str = None) -> None:
        self.session_id = session_id or str(uuid.uuid4())
        self.title = "New Session"
        self.created_at = datetime.now()
        self.history = list()
        self.file_context = ""

    def set_title_from_date_time(self, message: str):
        """Set chat title through its created date-time and first 10 letters of uesr message.

        Args:
            message (str): The first user message.
        """

        if self.title == "New Session" and message:
            first_ten_msg = message[:10] + ("..." if len(message) > 10 else "")
            date_time_tag = str(self.created_at.replace(" ", "_")).split(".")[0]
            self.title = f"{date_time_tag}_{first_ten_msg}"

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_history(self) -> list:
        res = self.history

        return res


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, ChatSession] = dict()
        self.current_session_id = None

    def create_session(self) -> str:
        """Create a New session

        Returns:
            str: Session ID
        """

        res = ""
        session = ChatSession()
        self.sessions[session.session_id] = session
        self.current_session_id = session.session_id

        res = session.session_id

        return res

    def get_current_session(self) -> ChatSession:
        """Get currently activated session

        Returns:
            ChatSession: Currently activated session (dict)
        """

        if not self.current_session_id or self.current_session_id not in self.sessions:
            self.create_session()

        res = self.sessions[self.current_session_id]

        return res

    def set_current_session(self, session_id: str):
        """Change current session

        Args:
            session_id (str): New selected session from list
        """

        if session_id in self.sessions:
            self.current_session_id = session_id

    def get_sessiones(self) -> list[dict[str, Any]]:
        """Get every session list from new to old

        Returns:
            list[dict[str, Any]]: List of sessions
        """

        res = list()

        sessions = sorted(self.sessions.values(), key=lambda x: x.created_at, reverse=True)

        res = [
            {"id": session.session_id, "title": session.title, "created_at": session.created_at} for session in sessions
        ]

        return res

    def delete_session(self, session_id: str):
        """Delete selected session

        Args:
            session_id (str): Selected session id
        """

        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                if self.sessions:
                    self.current_session_id = list(self.sessions.keys())[0]
                else:
                    self.create_session()
