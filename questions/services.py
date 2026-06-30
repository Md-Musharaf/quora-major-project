from topics.models import Topic


def save_question_topics(
    question,
    selected_topics,
    new_topic_names,
):
    topics_to_attach = list(selected_topics or [])

    # The form returns new_topics as a comma-separated string.
    if isinstance(new_topic_names, str):
        new_topic_names = [
            topic_name.strip()
            for topic_name in new_topic_names.split(",")
            if topic_name.strip()
        ]

    for topic_name in new_topic_names or []:
        topic = Topic.objects.filter(
            name__iexact=topic_name,
        ).first()

        if topic is None:
            topic = Topic.objects.create(
                name=topic_name,
            )

        topics_to_attach.append(topic)

    # Remove duplicate topics.
    unique_topics = {
        topic.id: topic
        for topic in topics_to_attach
    }

    question.topics.set(
        unique_topics.values(),
    )