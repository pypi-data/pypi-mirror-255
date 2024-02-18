
import os
import json
import asyncio

async def main():
    dataset = []
    with open("../chat_alpaca/chatalpaca-1k-fixed.json", "r") as json_file:
        for line in json_file:
            dataset.append(json.loads(line))    

    from weavel import create_client

    client = create_client()

    for data in dataset[40:60]: # trace 119 ~ 138
        print(data["id"])
        trace_uuid = client.start_trace(data["user_uuid"], data["created_at"])

        for message in data["conversations"]:
            if message["role"] == "user":
                client.log.user_message(
                    trace_uuid=trace_uuid,
                    data_content=message["content"],
                    timestamp=message["created_at"])
            else:
                client.log.assistant_message(
                    trace_uuid=trace_uuid,
                    data_content=message["content"], 
                    timestamp=message["created_at"]
                )

    await asyncio.sleep(60)

    client.close()
    
if __name__ == "__main__":
    asyncio.run(main())