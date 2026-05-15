import os
import google.generativeai as genai

from dotenv import load_dotenv

from app.retriever.retriever import search_assessments
from app.prompts.system_prompt import SYSTEM_PROMPT

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)


def detect_off_topic(message):

    off_topic_keywords = [
        "weather",
        "politics",
        "movie",
        "cricket",
        "bitcoin",
        "legal advice"
    ]

    return any(
        word in message.lower()
        for word in off_topic_keywords
    )


def detect_comparison(message):

    comparison_words = [
        "compare",
        "difference",
        "vs",
        "better"
    ]

    return any(
        word in message.lower()
        for word in comparison_words
    )


def generate_reply(messages):

    latest_message = messages[-1]["content"]

    # Refuse off-topic
    if detect_off_topic(latest_message):

        return {
            "reply": (
                "I only assist with SHL "
                "assessment recommendations "
                "and comparisons."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    # Build full conversation context
    conversation_text = ""

    for msg in messages:

        conversation_text += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )

    # Retrieve based on latest query
    retrieved_results = search_assessments(
        latest_message,
        top_k=5
    )

    retrieved_text = ""

    for item in retrieved_results:

        retrieved_text += f"""
        Assessment Name: {item['name']}
        URL: {item['url']}
        Description: {item['description']}
        """

    # Comparison handling
    if detect_comparison(latest_message):

        comparison_prompt = f"""
        {SYSTEM_PROMPT}

        User asked for assessment comparison.

        Conversation:
        {conversation_text}

        Retrieved assessments:
        {retrieved_text}

        Compare the assessments using ONLY
        retrieved information.
        """

        response = model.generate_content(
            comparison_prompt
        )

    else:

        recommendation_prompt = f"""
        {SYSTEM_PROMPT}

        Conversation:
        {conversation_text}

        Retrieved SHL assessments:
        {retrieved_text}

        Instructions:
        - Understand the full conversation
        - Handle refinements naturally
        - Recommend suitable assessments
        - Ask clarification questions if needed
        - Stay grounded in retrieved data
        """

        response = model.generate_content(
            recommendation_prompt
        )

    recommendations = []

for item in retrieved_results:

    recommendations.append({
        "name": item.get("name", "Unknown Assessment"),
        "url": item.get("url", ""),
        "test_type": item.get("test_type", "Assessment")
    })

# Limit recommendations between 1 and 10
recommendations = recommendations[:10]

# Decide if clarification is needed
needs_clarification = (
    len(recommendations) == 0
)

if needs_clarification:

    return {
        "reply": (
            "Could you share more details about "
            "the role, seniority level, and "
            "required skills?"
        ),
        "recommendations": [],
        "end_of_conversation": False
    }

return {
    "reply": response.text.strip(),
    "recommendations": recommendations,
    "end_of_conversation": True
}