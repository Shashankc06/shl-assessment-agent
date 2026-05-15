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

    # Refuse off-topic questions
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

    # Build conversation context
    conversation_text = ""

    for msg in messages:

        conversation_text += (
            f"{msg['role']}: "
            f"{msg['content']}\n"
        )

    # Retrieve assessments
    retrieved_results = search_assessments(
        latest_message,
        top_k=10
    )

    retrieved_text = ""

    for item in retrieved_results:

        retrieved_text += f"""
        Assessment Name: {item.get('name', 'Unknown')}
        URL: {item.get('url', '')}
        Description: {item.get('description', '')}
        Remote Testing Support: {item.get('remote_support', 'Unknown')}
        Adaptive/IRT Support: {item.get('adaptive_support', 'Unknown')}
        Duration: {item.get('duration', 'Unknown')}
        Test Type: {item.get('test_type', 'Assessment')}
        """

    # Handle comparison requests
    if detect_comparison(latest_message):

        comparison_prompt = f"""
        {SYSTEM_PROMPT}

        User asked for assessment comparison.

        Conversation:
        {conversation_text}

        Retrieved assessments:
        {retrieved_text}

        Instructions:
        - Compare only using retrieved information
        - Explain key differences clearly
        - Mention duration, adaptive support,
          remote testing support if available
        - Keep response concise and professional
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
        - Understand the user's hiring needs
        - Recommend the most suitable SHL assessments
        - Mention why each assessment fits
        - Ask clarification questions if needed
        - Stay grounded only in retrieved data
        - Keep response professional and concise
        """

        response = model.generate_content(
            recommendation_prompt
        )

    # Build recommendation list
    recommendations = []

    for item in retrieved_results:

        recommendations.append({
            "name": item.get("name", "Unknown Assessment"),
            "url": item.get("url", ""),
            "test_type": item.get("test_type", "Assessment"),
            "duration": item.get("duration", "Unknown"),
            "remote_support": item.get(
                "remote_support",
                "Unknown"
            ),
            "adaptive_support": item.get(
                "adaptive_support",
                "Unknown"
            )
        })

    # Limit recommendations between 1 and 10
    recommendations = recommendations[:10]

    # Clarification fallback
    if len(recommendations) == 0:

        return {
            "reply": (
                "I could not find a strong assessment "
                "match. Could you specify the role, "
                "skills, experience level, or job type?"
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    return {
        "reply": response.text,
        "recommendations": recommendations,
        "end_of_conversation": False
    }