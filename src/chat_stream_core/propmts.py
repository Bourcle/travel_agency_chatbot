from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def build_prompt() -> ChatPromptTemplate:
    """Generate Chat prompt template for travel planner

    Returns:
        ChatPromptTemplate: Built prompt template
    """

    res = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_message}"),
            MessagesPlaceholder("chat_history"),
            (
                "system",
                "Generate a personalized travel inicerary that matches the preferences of user. Respond in Korean.",
            ),
            ("human", "{user_input}"),
        ]
    )

    return res
