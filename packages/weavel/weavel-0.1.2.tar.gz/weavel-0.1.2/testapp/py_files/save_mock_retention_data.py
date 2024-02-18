
import os
import json
import asyncio

async def main():
    dataset = []
    with open("../chat_alpaca/retention_dataset.json", "r") as json_file:
        for line in json_file:
            dataset.append(json.loads(line))    

    from weavel import create_client

    client = create_client()

    for data in dataset: # trace 139 ~ 163
        print(data["id"])
        if data["trace_uuid"] is None:
            trace_uuid = client.start_trace(data["user_uuid"], data["created_at"])
        else:
            trace_uuid = data["trace_uuid"]

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