from chat_stream_core.session_mapper import SessionManager
from chat_stream_core.chatbot import TravelAgencyChatbot
from typing import Any, Generator, Callable
from utils.utils import ModelSettings
import gradio as gr


class ChatEventHandlers:
    def __init__(self, session_manager: SessionManager, bot: TravelAgencyChatbot, extract_text_from_file: Callable):
        self.session_manager = session_manager
        self.bot = bot
        self.extract_text_from_file = extract_text_from_file

    def get_session_choices(self) -> tuple[list[tuple[str, str]], str]:
        """Return session list and current session id to render UI

        Returns:
            tuple[list[tuple[str, str]], str]: Session list and current session id
        """

        res = (list(), "")
        sessions = self.session_manager.get_sessiones()
        choices = [(session["title"], session["id"]) for session in sessions]
        current_id = self.session_manager.current_session_id

        res = (choices, current_id)

        return res

    def create_new_session(self) -> tuple[list[str, str], str, list, str]:
        """Create New Chat session

        Returns:
            tuple[list[str, str], str, list, str]: (List of sessions, current session id, empty chat history, empty file context)
        """

        res = (list(), "", list(), "")

        self.session_manager.create_session()
        choices, current_id = self.get_session_choices()

        res = (choices, current_id, [], "")

        return res

    def switch_to_session(self, session_id: str) -> tuple[list, str]:
        """Switch to another selected session

        Args:
            session_id (str): Session Id would be switched

        Returns:
            tuple[list, str]: Chat history and file context
        """

        res = (list(), "")

        if not session_id:
            return res

        self.session_manager.set_current_session(session_id)
        session = self.session_manager.get_current_session()

        # Transfer history to UI format (user, assistant pair)
        chat_history = list()
        for index in range(0, len(session.history), 2):
            if index + 1 < len(session.history):
                user_msg = session.history[index]["content"]
                ai_msg = session.history[index + 1]["content"]
                chat_history.append([user_msg, ai_msg])

        res = (chat_history, session.file_context)

        return res

    def delete_session(self, session_id: str) -> tuple[list[tuple[str, str]], str, list, str]:
        """Delete Session

        Args:
            session_id (str): Session Id that will be deleted

        Returns:
            tuple[list[tuple[str, str]], str, list, str]: (selected session list, current session id, empty chat history, empty file context)
        """

        res = (list(), "", list(), "")

        if session_id:
            self.session_manager.delete_session(session_id)

        choices, current_id = self.get_session_choices()

        res = (choices, current_id, list(), "")

        return res

    def process_chat_message(self, message: Any, settings: ModelSettings) -> Generator[str, None, None]:
        """Generate Answer to user message or file

        Args:
            message (Any): User message or uploaded files
            settings (ModelSettings): AI model settings

        Yields:
            Generator[str, None, None]: Streaming answer chunks
        """

        session = self.session_manager.get_current_session()

        # Set the title of chat room if it's first message
        if not session.history:
            text = message.get("text") if isinstance(message, dict) else str(message)
            session.set_title_from_date_time(text)

        # Get file context
        file_ctx = session.file_context

        # Generate bot answer
        response_stream = self.bot.answer_invoke(
            message=message,
            chat_history=session.history,
            system_type=settings.system_type,
            model_name=settings.model_name,
            temperature=settings.temperature,
            top_p=settings.top_p,
            presence_penalty=settings.presence_penalty,
            frequence_penalty=settings.frequency_penalty,
            file_context=file_ctx,
        )

        # deal with streaming
        full_res = ""
        for chunk in response_stream:
            full_res = chunk
            yield chunk

        text = message.get("text") if isinstance(message, dict) else str(message)
        session.add_message("user", text)
        session.add_message("assistant", full_res)

    def update_settings(
        self,
        system_type: str,
        model_name: str,
        temperature: float,
        top_p: float,
        presence_penalty: float,
        frequency_penalty: float,
    ) -> ModelSettings:
        """Update model settings

        Args:
            system_type (str): system type.
            model_name (str): model name
            temperature (float): temperature
            top_p (float): top_p
            presence_penalty (float): presence penalty
            frequency_penalty (float): frequency penalty

        Returns:
            ModelSettings: updated settings
        """

        res = ModelSettings(
            system_type=system_type,
            model_name=model_name,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )

        return res

    def process_file_upload(self, upload_file: Any) -> tuple[str | None, str]:
        """Process file upload

        Args:
            upload_file (Any): Uploaded file

        Returns:
            tuple[str|None, str]: Path to pdf if uploaded file is pdf. Otherwise, Text.
        """

        res = (None, "")

        if not upload_file:
            return res

        pdf_path, text = self.extract_text_from_file(upload_file.name)

        session = self.session_manager.get_current_session()
        session.file_context = text

        res = (pdf_path, text)

        return res
