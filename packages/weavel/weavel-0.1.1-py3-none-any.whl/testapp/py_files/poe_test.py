
import os
import json
import asyncio
from typing import Dict, List, Optional, Union

from fastapi_poe import QueryRequest, PartialResponse, ProtocolMessage

async def main():  

    from weavel import create_poe_client, WeavelPoeClient

    client: WeavelPoeClient = create_poe_client()
    
    user_request = QueryRequest(
        version="1.1",
        type="query",
        query=[
            ProtocolMessage(
                role="system", content="you are a helpful assistant"
            ),
            ProtocolMessage(
                role="user",
                content="Hello 1",
                timestamp=1706514709229521,
            )
        ],
        conversation_id="c_test_1",
        user_id="u_test_1",
        message_id="m_test_1",
        metadata="",
    )
    
    assistant_responses: List[PartialResponse] = [
        PartialResponse(
            text="Hi, ",
        ),
        PartialResponse(
            text="How are you? 1",
        ),
    ]
    
    client.log(user_request, assistant_responses)
    
    user_request = QueryRequest(
        version="1.1",
        type="query",
        query=[
            ProtocolMessage(
                role="system", content="you are a helpful assistant"
            ),
            ProtocolMessage(
                role="user",
                content="how to use sympy library?",
                timestamp=1706514709229521,
            )
        ],
        conversation_id="c_test_2",
        user_id="u_test_2",
        message_id="m_test_2",
        metadata="",
    )
    
    assistant_responses: List[PartialResponse] = [
        PartialResponse(
            text="You can use ",
        ),
        PartialResponse(
            text="sympy by pip install sympy.",
        ),
    ]
    
    client.log(user_request, assistant_responses)

    client.close()
    
if __name__ == "__main__":
    asyncio.run(main())