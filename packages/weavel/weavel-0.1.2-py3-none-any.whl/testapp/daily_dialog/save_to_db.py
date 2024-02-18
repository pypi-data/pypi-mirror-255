import os
import json

# count the number of files in the directory daily_dialog_result
dd_dataset = []
dd_count = 0
for root, dirs, files in os.walk("daily_dialog_result"):
    for file in files:
        if file.endswith(".json"):
            dd_count += 1
            with open(os.path.join(root, file), "r") as f:
                data = json.load(f)
                dd_dataset.append(data)

# count the number of files in the directory chat_alpaca_result
ca_dataset = []
ca_count = 0
for root, dirs, files in os.walk("chat_alpaca_result"):
    for file in files:
        if file.endswith(".json"):
            ca_count += 1
            with open(os.path.join(root, file), "r") as f:
                data = json.load(f)
                ca_dataset.append(data)
                
import supabase
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

client = supabase.create_client(url, key)

# for ca in ca_dataset:
#     for trace_data in ca["trace_data"]:
#         uuid = trace_data["uuid"]
#         question_topics = trace_data["question_topics"]
#         information_topics = trace_data["information_topics"]
#         for topic in question_topics:
#             if topic["value"] is None:
#                 topic["value"] = ""
#         for topic in information_topics:
#             if topic["value"] is None:
#                 topic["value"] = ""

#         (
#             client.table("conversation_analysis")
#             .insert(
#                 {
#                     "trace_data_uuid": uuid,
#                     "question_topics": question_topics,
#                     "information_topics": information_topics,
#                 }
#             )
#             .execute()
#         )

project_uuid = "b7c360b6-a862-4ff3-ad31-d8a620a201dc"

# make unit
unit = (
    client.table("unit")
    .insert(
        {
            "name": "daily_dialog",
            "description": "daily_dialog dataset",
            "project_uuid": project_uuid,
        }
    )
    .execute()
).data

unit_uuid = unit[0]["uuid"]

for i, dd in enumerate(dd_dataset):
    # save trace_data
    # make user
    
    user = (
        client.table("user")
        .insert(
            {
                "name": f"daily dialog User {i}",
                "project_uuid": project_uuid,
            }
        )
        .execute()
    ).data
    user_uuid = user[0]["uuid"]
    
    # make trace
    
    trace = (
        client.table("trace")
        .insert(
            {
                "user_uuid": user_uuid,
                "project_uuid": project_uuid,
                "created_at": dd["dialog"][0]["created_at"],
                "updated_at": dd["dialog"][-1]["created_at"],
            }
        )
        .execute()
    ).data
    
    trace_uuid = trace[0]["uuid"]
    
    for trace_data in dd["dialog"]:
        trace_data_in_db = (
            client.table("trace_data")
            .insert(
                {
                    "trace_uuid": trace_uuid,
                    "unit_uuid": unit_uuid,
                    "type": trace_data["type"],
                    "content": trace_data["content"],
                    "created_at": trace_data["created_at"],
                    "metadata": {'source': 'daily_dialog'},
                    "project_uuid": project_uuid,
                }   
            )
            .execute()
        ).data
        uuid = trace_data_in_db[0]["uuid"]
        
        question_topics = trace_data["question_topics"]
        information_topics = trace_data["information_topics"]
        for topic in question_topics:
            if topic["value"] is None:
                topic["value"] = ""
        for topic in information_topics:
            if topic["value"] is None:
                topic["value"] = ""

        (
            client.table("conversation_analysis")
            .insert(
                {
                    "trace_data_uuid": uuid,
                    "question_topics": question_topics,
                    "information_topics": information_topics,
                }
            )
        )