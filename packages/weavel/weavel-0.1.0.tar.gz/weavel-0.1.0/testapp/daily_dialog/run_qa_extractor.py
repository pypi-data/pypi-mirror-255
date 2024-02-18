from typing import Dict, List, Optional, Any
from promptmodel import FunctionModel, init
import os
import json
import asyncio
from asyncio import Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

dataset = []

with open("daily_dialog_with_template.json", "r") as f:
    for line in f:
        dataset.append(json.loads(line))

init(use_cache=False)

# question_extractor = FunctionModel("question_extractor")
answer_extractor = FunctionModel("answer_extractor")
info_extractor = FunctionModel("info_extractor")

# Ensure the directory exists
results_dir = "daily_dialog_result"
os.makedirs(results_dir, exist_ok=True)

async def worker(queue: Queue):
    while True:
        data = await queue.get()
        result_path = os.path.join(results_dir, f"{data['trace_uuid']}.json")
        try:
            if not os.path.exists(result_path):  # Only process if result doesn't exist
                response = await run_dialog(data)
                res = data.copy()
                res["dialog"] = response
                # Save result to a file named after the data's uuid
                with open(result_path, "w") as f:
                    f.write(json.dumps(res))
            else:
                print(f"Result for {data['trace_uuid']} already exists. Skipping.")
            queue.task_done()
        except Exception as e:
            print(f"Error processing {data['trace_uuid']}: {e}")
            queue.task_done()
        
async def run_dialog(data: Dict) -> List[Dict]:
    print(f"START RUN {data['trace_uuid']}")
    # output format: dialog[i]["result"] = {questions: [], answers: {}}
    dialog: Dict[str, Any] = data["dialog"]
    res = dialog
    # for first message, run question_extractor
    # for subsequent messages, run answer_extractor and run question_extractor
    # try 3 times
    retry_count = 3
    
    retry_count = 3
    while True:
        i_response = await info_extractor.arun_and_parse(
            {
                "current_message" : dialog[0]["content"], 
                "previous_message" : None, 
                "questions": [],
                "previous_topics": []
            }
        )
        # print(i_response)
        if i_response.error is None or i_response.error == False:
            break
    
        if i_response.parsed_outputs == {} or i_response.parsed_outputs is None:
            try:
                parsed_raw_output: Dict = json.loads(i_response.api_response.choices[0].message.content)
                i_response.parsed_outputs = {"informations": parsed_raw_output}
                break
            except Exception as e:
                print(e)
                pass
            
        retry_count -= 1
        if retry_count == 0:
            print("Raise Exception: Failed to run info_extractor")
            raise Exception("Failed to run info_extractor")
    
    # print("-------------------------")
    # print("Extracted Informations")
    # print("-------------------------")
    
    res[0]["question_topics"] = []
    res[0]["information_topics"] = []
     
    res[0]["question_topics"] = [
        {
            "name": q_key,
            "value": q_val["value"],
            "related_to": q_val["related_to"]
        }
        for q_key, q_val in i_response.parsed_outputs["informations"].items() if q_val["type"] == "question"
    ]
    
    res[0]["information_topics"] = [
        {
            "name": info_key,
            "value": info_val["value"],
            "related_to": info_val["related_to"]
        }
        for info_key, info_val in i_response.parsed_outputs["informations"].items() if info_val["type"] == "information"
    ]

    for i in range(1, len(dialog)):
        print(i)
        retry_count = 3
        while True:
            a_response = await answer_extractor.arun_and_parse(
                {
                    "current_message" : dialog[i]["content"],
                    "previous_message" : dialog[i-1]["content"],
                    "questions": [question["name"] for question in dialog[i-1]["question_topics"]]
                }
            )
            # print(a_response)
            if a_response.error is None or a_response.error == False:
                break
            
            if a_response.parsed_outputs == {} or a_response.parsed_outputs is None:
                try:
                    parsed_raw_output = json.loads(a_response.api_response.choices[0].message.content)
                    a_response.parsed_outputs = {"answers": parsed_raw_output}
                    break
                except:
                    pass
                
            retry_count -= 1
            if retry_count == 0:
                print("Raise Exception: Failed to run answer_extractor")
                raise Exception("Failed to run answer_extractor")
        
        # print("-------------------------")
        # print("Extracted Answers")
        # print("-------------------------")
        
        retry_count = 3
        while True:
            i_response = await info_extractor.arun_and_parse(
                {
                    "current_message" : dialog[i]["content"], 
                    "previous_message" : dialog[i-1]["content"], 
                    "questions": [question["name"] for question in dialog[i-1]["question_topics"]],
                    "previous_topics": [info["name"] for info in dialog[i-1]["information_topics"]]
                }
            )
            # print(i_response)
            if i_response.error is None or i_response.error == False:
                break
        
            if i_response.parsed_outputs == {} or i_response.parsed_outputs is None:
                try:
                    parsed_raw_output = json.loads(i_response.api_response.choices[0].message.content)
                    i_response.parsed_outputs = {"informations": parsed_raw_output}
                    break
                except:
                    pass
                
            retry_count -= 1
            if retry_count == 0:
                print("Raise Exception: Failed to run info_extractor")
                raise Exception("Failed to run info_extractor")
            
        # print("-------------------------")
        # print("Extracted Informations")
        # print("-------------------------")
        
        # retry_count = 3
        # while True:
        #     q_response = question_extractor.run_and_parse(
        #         {
        #             "current_message" : dialog[i]["content"], 
        #             "previous_message" : dialog[i-1]["content"], 
        #             "previous_topics": dialog[i-1]["question_topics"] + dialog[i-1]["information_topics"]
        #         }
        #     )
        #     print(q_response)
        #     if q_response.error is None or q_response.error == False:
        #         break
            
        #     if q_response.parsed_outputs == {} or q_response.parsed_outputs is None:
        #         try:
        #             parsed_raw_output = json.loads(q_response.api_response.choices[0].message.content)
        #             q_response.parsed_outputs = {"questions": parsed_raw_output}
        #             break
        #         except:
        #             pass
        #     retry_count -= 1
        #     if retry_count == 0:
        #         print("Raise Exception: Failed to run question_extractor")
        #         raise Exception("Failed to run question_extractor")
            
        # print("-------------------------")
        # print("Extracted Questions")
        # print("-------------------------")
        
        res[i]["question_topics"] = []
        res[i]["information_topics"] = []
        
        res[i]["question_topics"] = [
            {
                "name": q_key,
                "value": q_val["value"],
                "related_to": q_val["related_to"]
            }
            for q_key, q_val in i_response.parsed_outputs["informations"].items() if q_val["type"] == "question"
        ]
        
        res[i]["information_topics"] = [
            {
                "name": info_key,
                "value": info_val["value"],
                "related_to": info_val["related_to"]
            }
            for info_key, info_val in i_response.parsed_outputs["informations"].items() if info_val["type"] == "information"
        ]
        
        res[i]["information_topics"] += [
            {
                "name": ans_key,
                "value": ans_val,
                "related_to": ans_key
            }
            for ans_key, ans_val in a_response.parsed_outputs["answers"].items()
        ]
        
        
    print(f"END RUN {data['trace_uuid']}")
    return res

async def main():
    queue = Queue()
    num_workers = 30  # Adjust based on your system's capabilities
    tasks = []

    for _ in range(num_workers):
        task = asyncio.create_task(worker(queue))
        tasks.append(task)

    filtered_dataset = []
    # Pre-execution filtering is now simplified
    for data in dataset:
        result_path = os.path.join(results_dir, f"{data['trace_uuid']}.json")
        if not os.path.exists(result_path):
            filtered_dataset.append(data)

    print(len(filtered_dataset))
    
    for data in filtered_dataset:
        await queue.put(data)
        
    await queue.join()
    for task in tasks:
        task.cancel()

    print("All workers are done!")
    
    
if __name__ == "__main__":

    asyncio.run(main())
