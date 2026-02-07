import gradio as gr
from gradio_pdf import PDF
from chat_stream_core.chatbot import TravelAgencyChatbot
from typing import Any


def build_ui(
    *, bot: TravelAgencyChatbot, system_msg_types: dict[str, str], model_to_select: list[str], extract_text_from_file
) -> gr.Blocks:
    with gr.Blocks(title="맞춤형 여행 일정 플래너") as res:
        gr.Markdown("맞춤형 여행 일정 계획 도우미")

        with gr.Row():
            with gr.Column(scale=4, min_width=360):
                gr.Markdown("파일 업로드")
                upload = gr.File(
                    label="PDF / Excel / Text 업로드",
                    file_types=[".pdf", ".xlsx", ".xls", ".txt", ".csv", ".json", ".md", ".log", ".yaml", ".yml"],
                )
                pdf_view = PDF(label="PDf 미리보기")
                file_context = gr.Textbox(label="추출 텍스트", lines=14)
            with gr.Column(scale=6, min_width=520):
                gr.Markdown("여행에 대해서 물어보세요")
                with gr.Accordion("설정", open=True):
                    system_type = gr.Dropdown(
                        label="여행스타일을 골라보세요", choices=list(system_msg_types.keys()), value="기본"
                    )
                    model_name = gr.Dropdown(label="AI model선택", choices=model_to_select, value="gpt-4o-mini")
                    with gr.Row():
                        temperature = gr.Slider(0.0, 1.0, value=0.3, step=0.05, label="Temperature")
                        top_p = gr.Slider(0.1, 1.0, value=0.9, step=0.05, label="Top_P")
                    with gr.Row():
                        presence_penalty = gr.Slider(-2.0, 2.0, value=0.3, step=0.1, label="presence_penalty")
                        frequency_penalty = gr.Slider(-2.0, 2.0, value=0.3, step=0.1, label="frequency_penalty")
                chat = gr.ChatInterface(
                    fn=bot.answer_invoke,
                    multimodal=True,
                    textbox=gr.MultimodalTextbox(
                        placeholder="텍스트를 입력하거나 이미지를 업로드 하세요.",
                        file_count="multiple",
                        file_types=["image"],
                    ),
                    additional_inputs=[
                        system_type,
                        model_name,
                        temperature,
                        top_p,
                        presence_penalty,
                        frequency_penalty,
                        file_context,
                    ],
                    title="맞춤형 여행 일정 플래너",
                    description="예: '서울 2박 3일 감성여행 일정 짜줘. 예상 50만원, 카페랑 산책 좋아해.'",
                    analytics_enabled=False,
                )

        def on_upload(upload_file: Any) -> tuple[str, str]:
            """Change upload type into path and text.

            Args:
                upload_file (Any): The uploaded file

            Returns:
                tuple[str, str]: It has file path if the uploaded file is PDF. else, it will return None and text only.
            """

            if not upload_file:
                return None, ""
            pdf_path, text = extract_text_from_file(upload_file.name)

            return pdf_path, text

        upload.change(on_upload, inputs=[upload], outputs=[pdf_view, file_context])

    return res
