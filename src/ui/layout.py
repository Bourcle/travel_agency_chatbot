import gradio as gr
from gradio_pdf import PDF
from chat_stream_core.chatbot import TravelAgencyChatbot
from chat_stream_core.session_mapper import SessionManager
from chat_stream_core.event_handler import ChatEventHandlers
from typing import Any
from utils.utils import ModelSettings


def build_ui(
    *, bot: TravelAgencyChatbot, system_msg_types: dict[str, str], model_to_select: list[str], extract_text_from_file
) -> gr.Blocks:

    session_manager = SessionManager()
    session_manager.create_session()  # Create init session

    with gr.Blocks(title="맞춤형 여행 일정 플래너", theme=gr.themes.Soft()) as res:
        gr.Markdown("맞춤형 여행 일정 계획 플래너")
        current_settings = gr.State(ModelSettings())
        handlers = ChatEventHandlers(session_manager, bot, extract_text_from_file)

        with gr.Tabs() as tabs:
            with gr.Tab("Chatting"):
                with gr.Row():
                    # left: Chatting room list
                    with gr.Column(scale=2, min_width=250):
                        gr.Markdown("### Chat History")
                        new_chat_button = gr.Button("+ New Conversation", variant="primary", size="sm")
                        sessions = gr.Radio(choices=[], label="", interactive=True, elem_id="session_list")
                        delete_session_button = gr.Button("- Delete Conversation", size="sm", variant="stop")

                    with gr.Column(scale=5):
                        gr.Markdown("### Ask whatever about Travel plan")
                        chatbot_display = gr.Chatbot(label="Current Chat..", height=500)
                        user_input = gr.MultimodalTextbox(
                            placeholder="Insert Message(메세지를 입력하세요).. (file, image, pdf available (가능))",
                            file_count="multiple",
                            file_types=[
                                "image",
                                ".pdf",
                                ".xlsx",
                                ".xls",
                                ".txt",
                                ".csv",
                                ".json",
                                ".md",
                                ".yml",
                                ".yaml",
                            ],
                            submit_btn=True,
                        )
                        with gr.Accordion("Preview attachment (첨부파일 미리보기)", open=False):
                            pdf_view = PDF(label="PDF preview(미리보기)")
                            file_context = gr.Textbox(label="Extracted text (추출된 텍스트)", lines=8)

            # setting tab
            with gr.Tab("Settings (설정)"):
                gr.Markdown("### Set AI model and Parameters (AI모델 및 파라미터 설정)")
                with gr.Row():
                    with gr.Column():
                        system_type = gr.Dropdown(
                            label="Select your Travel Style(여행스타일)",
                            choices=list(system_msg_types.keys()),
                            value="Basic(기본)",
                        )
                        model_name = gr.Dropdown(label="Select AI models", choices=model_to_select, value="gpt-4o-mini")
                    with gr.Column():
                        temperature = gr.Slider(0.0, 1.0, value=0.3, step=0.05, label="Creative level (창의성)")
                        top_p = gr.Slider(0.1, 1.0, value=0.9, step=0.05, label="Top_P (비정상 답변 제거)")
                        presence_penalty = gr.Slider(-2.0, 2.0, value=0.3, step=0.1, label="Presence penalty")
                        frequency_penalty = gr.Slider(
                            -2.0, 2.0, value=0.3, step=0.1, label="Frequency penalty (반복답변 방지)"
                        )

                save_settings_button = gr.Button("Save Settings(설정저장)", variant="primary")
                setting_status = gr.Markdown("")

        def on_new_chat() -> tuple:
            choices, current_id, history, ctx = handlers.create_new_session()
            return gr.Radio(choices=choices, value=current_id), history, ctx

        def on_switch_session(session_id: str) -> tuple:
            return handlers.switch_to_session(session_id)

        def on_delete_session(session_id: str) -> tuple:
            choices, current_id, history, ctx = handlers.delete_session(session_id)
            return gr.Radio(choices=choices, value=current_id), history, ctx

        def on_submit_message(message: Any, history: list, settings: ModelSettings) -> str:
            if not message:
                return history
            return list(handlers.process_chat_message(message, settings))[-1]

        def on_save_settings(
            sys_type: str, model: str, temp: float, top_p_val: float, pres_pen: float, freq_pen: float
        ) -> tuple:
            new_settings = handlers.update_settings(sys_type, model, temp, top_p_val, pres_pen, freq_pen)
            return new_settings, "Setting is Successfuly Saved! (설정이 저장되었습니다!)"

        # connect ui event
        new_chat_button.click(on_new_chat, outputs=[sessions, chatbot_display, file_context])
        sessions.change(on_switch_session, inputs=[sessions], outputs=[chatbot_display, file_context])
        delete_session_button.click(
            on_delete_session, inputs=[sessions], outputs=[sessions, chatbot_display, file_context]
        )
        user_input.submit(
            on_submit_message, inputs=[user_input, chatbot_display, current_settings], outputs=[chatbot_display]
        )
        save_settings_button.click(
            on_save_settings,
            inputs=[system_type, model_name, temperature, top_p, presence_penalty, frequency_penalty],
            outputs=[current_settings, setting_status],
        )

        return res
