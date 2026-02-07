from ui.layout import build_ui
from dotenv import load_dotenv
from config import SYSTEM_MSG_TYPES, MODEL_TO_SELECT
from chat_stream_core.chatbot import TravelAgencyChatbot
from data_io.files import extract_text_from_file
from ui import layout

load_dotenv()
travel_agency_bot = TravelAgencyChatbot()

app = build_ui(
    bot=travel_agency_bot,
    system_msg_types=SYSTEM_MSG_TYPES,
    model_to_select=MODEL_TO_SELECT,
    extract_text_from_file=extract_text_from_file,
)

if __name__ == "__main__":
    app.launch()
