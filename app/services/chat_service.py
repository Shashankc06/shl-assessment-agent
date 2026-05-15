from app.retriever.retriever import search_assessments


def generate_reply(messages):

    latest_message = messages[-1]["content"]

    retrieved_results = search_assessments(
        latest_message,
        top_k=5
    )

    recommendations = []

    for item in retrieved_results:

        recommendations.append({
            "name": item.get("name", "Unknown Assessment"),
            "url": item.get("url", ""),
            "test_type": item.get("test_type", "Assessment")
        })

    # Generate intelligent response
    if len(recommendations) > 0:

        assessment_names = [
            item["name"]
            for item in recommendations
        ]

        reply = (
            "Based on your requirements, "
            "I recommend the following SHL assessments: "
            + ", ".join(assessment_names)
        )

    else:

        reply = (
            "I could not find exact matches. "
            "Please refine the job role, skills, "
            "or assessment requirements."
        )

    return {
        "reply": reply,
        "recommendations": recommendations,
        "end_of_conversation": False
    }