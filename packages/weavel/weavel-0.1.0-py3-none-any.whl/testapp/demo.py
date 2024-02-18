from weavel import create_client, WeavelClient, Trace

client: WeavelClient = create_client()

user_uuid = client.create_user_uuid()
print(user_uuid)

client.track(user_uuid, "identifier", {"name": "Jon Doe", "email": "jondoe@email.com"})
trace: Trace = client.start_trace(user_uuid)
print(trace.trace_uuid)

trace.log_message("system", "you are a helpful assistant.", unit_name="testapp")

from openai import OpenAI
openai_client = OpenAI()

user_message = "what can you do for me?"
trace.log_message("user", user_message, unit_name="testapp")

client.track(user_uuid, "subscription", {"plan": "premium"})
client.track(user_uuid, "paid", {"amount": "1000"})

# res = openai_client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": user_message}
#     ]
# )

res = "I can assist you with a variety of tasks. I can help answer questions, provide information, give suggestions, assist with research, set reminders, manage your schedule, make reservations, provide translations, and much more. Just let me know what you need help with!"

# print(res.choices[0].message.content)

trace.log_message("assistant", res, unit_name="test_assistant")

# second_trace: Trace = client.start_trace(user_uuid)
# second_trace.log_message("user", "hello!", unit_name="second_testapp")
# second_trace.log_message("assistant", "I can help you with a variety of tasks.", unit_name="second_testapp")
# second_trace.log_message("system", "you are a helpful assistant.")

client.close()