
import os
import json
import asyncio

async def main():
    dataset = []
    with open("chat_alpaca/chatalpaca-1k-fixed.json", "r") as json_file:
        for line in json_file:
            dataset.append(json.loads(line))    

    from weavel import create_client

    client = create_client()

    sample_data = dataset[27]

    trace_uuid = client.start_trace(sample_data["user_uuid"], sample_data["created_at"])

    for message in sample_data["conversations"]:
        if message["role"] == "user":
            client.log.user_message(
                trace_uuid=trace_uuid,
                data_content=message["content"],
                timestamp=message["created_at"])
            print(message["content"])
        else:
            client.log.assistant_message(
                trace_uuid=trace_uuid,
                data_content=message["content"], 
                timestamp=message["created_at"]
            )
            print(message["content"])

    await asyncio.sleep(60)

    client.close()
    
if __name__ == "__main__":
    asyncio.run(main())