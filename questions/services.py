from topics.models import Topic


def save_question_topics(
    question,
    selected_topics,
    new_topic_names,
):
    topics_to_attach = list(selected_topics)

    for topic_name in new_topic_names:
        topic = Topic.objects.filter(name__iexact=topic_name).first()

        if topic is None:
            topic = Topic.objects.create(name=topic_name)

        topics_to_attach.append(topic)

    # Prevent the same topic from being attached twice.
    unique_topics = {topic.id: topic for topic in topics_to_attach}

    question.topics.set(unique_topics.values())
