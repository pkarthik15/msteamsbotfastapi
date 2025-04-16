import os
from openai import OpenAI
from fastapi import FastAPI, Request, Response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
client = OpenAI()


APP_ID = os.environ.get("APP_ID", "")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
TENANT_ID = os.environ.get("TENANT_ID", "")

adapter_settings = BotFrameworkAdapterSettings(app_id=APP_ID, app_password=APP_PASSWORD, channel_auth_tenant=TENANT_ID)
adapter = BotFrameworkAdapter(adapter_settings)


async def handle_turn(turn_context: TurnContext):
    user_query = turn_context.activity.text
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": user_query}],
    )
    await turn_context.send_activity(response.choices[0].message.content)


@app.post("/api/messages")
async def messages(request: Request) -> Response:
    body = await request.body()

    activity = Activity().deserialize(await request.json())

    if activity.type == "conversationUpdate":
        print("connection successful")
        return Response(status_code=200)

    auth_header = request.headers.get("Authorization", "")

    async def call_bot(context: TurnContext):
        await handle_turn(context)

    try:
        
        await adapter.process_activity(activity, auth_header, call_bot)
        return Response(status_code=200)
    except Exception as e:
        print(f"Error: {e}")
        return Response(status_code=500, content=str(e))
