from typing import List

import pytest

from papfa.consumers import consumer, BaseConsumer
from papfa.dtos import Record


@pytest.fixture
def fake_consumer():
    class FakeConsumer(BaseConsumer):
        def consume(self):
            return True

        def get_meta_data(self):
            return {}

    return FakeConsumer()


@pytest.fixture
def simple_consumer(fake_consumer):
    @consumer("topic", consumer_strategy=fake_consumer)
    def consumer_function(messages: List[Record]):
        return len(messages)

    return consumer_function

@pytest.fixture
def consumer_with_multiple_topics(fake_consumer):
    @consumer(topic=["topic1", "topic2"], consumer_strategy=fake_consumer)
    def consumer_function(messages: List[Record]):
        return len(messages)

    return consumer_function


def test_simple_consumer_normal_call(simple_consumer):
    assert simple_consumer([]) == 0


def test_simple_consumer_consume(simple_consumer):
    assert simple_consumer.consume() == 1


def test_consumer_with_multiple_topics_normal_call(consumer_with_multiple_topics):
    assert consumer_with_multiple_topics([]) == 0


def test_consumer_with_multiple_topics_consume(consumer_with_multiple_topics):
    assert consumer_with_multiple_topics.consume() == 1
