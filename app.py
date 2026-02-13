from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
import time

app = FastAPI()

essay = (
    "Climate change is one of the most serious challenges facing humanity today. "
    "It is driven mainly by the burning of fossil fuels such as coal, oil, and gas, "
    "which releases greenhouse gases like carbon dioxide into the atmosphere. "
    "These gases trap heat and cause the planet’s average temperature to rise. "
    "As a result, we are witnessing melting glaciers, rising sea levels, stronger storms, "
    "and longer heatwaves across the world.\n\n"
    "One major argument is that climate change threatens food and water security. "
    "Changing rainfall patterns reduce crop yields, while droughts and floods destroy farmland. "
    "In addition, warming oceans affect fish populations, impacting coastal communities. "
    "Another key issue is human health. Rising temperatures increase the spread of diseases "
    "and make heat-related illnesses more common, especially in vulnerable populations.\n\n"
    "However, solutions exist. Transitioning to renewable energy sources like solar and wind "
    "can reduce emissions significantly. Governments can also encourage public transport, "
    "electric vehicles, and energy-efficient buildings. Individuals can contribute by reducing "
    "waste, conserving electricity, and supporting sustainable products.\n\n"
    "In conclusion, climate change is not a distant threat but a present reality. "
    "If governments, industries, and citizens work together, we can slow global warming "
    "and protect the environment for future generations."
)

@app.post("/stream")
async def stream_llm(request: Request):
    body = await request.json()
    stream = body.get("stream", False)

    if not stream:
        return {"error": "stream must be true"}

    def event_generator():
        try:
            words = essay.split(" ")
            buffer = ""

            for word in words:
                buffer += word + " "

                if len(buffer) > 120:
                    data = {"choices": [{"delta": {"content": buffer}}]}
                    yield f"data: {json.dumps(data)}\n\n"
                    buffer = ""
                    time.sleep(0.05)

            if buffer.strip():
                data = {"choices": [{"delta": {"content": buffer}}]}
                yield f"data: {json.dumps(data)}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            err_data = {"error": str(e)}
            yield f"data: {json.dumps(err_data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
