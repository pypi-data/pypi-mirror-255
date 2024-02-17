import asyncio
import uuid
from typing import Optional

import pytest
from llama_server_client import AsyncLlamaClient
from llama_server_client.schema import HealthCheck
from llama_server_client.client import LlamaClient
from llama_server_client.schema.completion import MessageRole, ChatCompletion
from llama_server_client.schema.completion import Message, ChatCompletionRequest
from llama_server_client.schema.session_state import SessionState, SessionStateRequest


def send_chat_completion_request(client: LlamaClient, request: ChatCompletionRequest) -> Optional[ChatCompletion]:
    return client.send_chat_completion_request(request)


@pytest.fixture
def setup_client():
    host = "tcp://localhost:5555"
    timeout = 360000
    client = AsyncLlamaClient(host=host, timeout=timeout)
    return client


@pytest.fixture
def setup_chat_completion_request() -> ChatCompletionRequest:
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    messages = [
        Message(role=MessageRole.system, content='You are a helpful assistant'),
        Message(role=MessageRole.user, content="What is the capital of Turkey?")
    ]
    stop = ["\n### Human:"]
    return ChatCompletionRequest(
        model='vicuna7b-1.5',
        messages=messages,
        temperature=0.8,
        n=256,
        stop=stop,
        user=user_id,
        key_values={"session": session_id}
    )


@pytest.fixture
def setup_session_state_request() -> SessionStateRequest:
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    return SessionStateRequest(
        session=session_id,
        user=user_id,
    )


@pytest.fixture()
def setup_title_generation_request() -> ChatCompletionRequest:
    messages = [
        Message(
            role=MessageRole.system,
            content="You are a helpful assistant. You generate a descriptive, short and meaningful title for the given "
                    "conversation.",
        ),
        Message(
            role=MessageRole.user,
            content=f"Question: What is the capital of France? Answer: The capital of France is Paris"
        )
    ]
    stop = ["\n ###Human:"]
    return ChatCompletionRequest(
        model='vicuna7b-1.5',
        messages=messages,
        temperature=0.8,
        n=256,
        stop=stop,
    )


@pytest.mark.asyncio
async def test_session_state_request(setup_client, setup_session_state_request):
    try:
        response: SessionState = await setup_client.send_session_state_request(setup_session_state_request)
        print(response.to_json_str())
        assert response is not None
        assert isinstance(response, SessionState)
    except TimeoutError as e:
        pytest.fail(str(e))


@pytest.mark.asyncio
async def test_health_check_request(setup_client):
    try:
        response: HealthCheck = await setup_client.send_health_check_request()
        print(response.to_json_str())
        assert response is not None
        assert isinstance(response, HealthCheck)
    except TimeoutError as e:
        pytest.fail(str(e))


@pytest.mark.asyncio
async def test_chat_completion_request(setup_client, setup_chat_completion_request):
    try:
        response: ChatCompletion = await setup_client.send_chat_completion_request(setup_chat_completion_request)
        print(response.to_json_str())
        assert response is not None
        assert isinstance(response, ChatCompletion)
    except TimeoutError as e:
        pytest.fail(str(e))


@pytest.mark.asyncio
async def test_title_generation_request(setup_client, setup_title_generation_request):
    try:
        response: ChatCompletion = await setup_client.send_chat_completion_request(setup_title_generation_request)
        print(response.to_json_str())
        assert response is not None
        assert isinstance(response, ChatCompletion)
    except TimeoutError as e:
        pytest.fail(str(e))


@pytest.mark.asyncio
async def test_mix_requests(setup_chat_completion_request, setup_title_generation_request):
    client1 = AsyncLlamaClient('tcp://localhost:5555', timeout=360000)
    client2 = AsyncLlamaClient('tcp://localhost:5555', timeout=360000)

    async def send_request(client, request):
        return await client.send_chat_completion_request(request)

    response1, response2 = await asyncio.gather(
        send_request(client1, setup_chat_completion_request),
        send_request(client2, setup_title_generation_request)
    )
    client1.close()
    client2.close()

    assert response1 is not None
    assert isinstance(response1, ChatCompletion)
    print(response1.to_json_str())
    assert response2 is not None
    assert isinstance(response2, ChatCompletion)
    print(response2.to_json_str())


if __name__ == "__main__":
    pytest.main()
