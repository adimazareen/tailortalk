from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import appointment_agent
from .schemas import AppointmentRequest

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserMessage(BaseModel):
    text: str

@app.post("/chat")
async def chat(message: UserMessage):
    try:
        # Initialize the agent state
        initial_state = {
            "request": AppointmentRequest(user_input=message.text),
            "available_slots": [],
            "confirmed_appointment": None
        }
        
        # Execute the agent workflow
        result = appointment_agent.invoke(initial_state)
        
        # The last node should be generate_response which returns a dict with "response"
        if isinstance(result, dict) and "response" in result:
            return {"response": result["response"]}
        else:
            return {"response": "I encountered an error processing your request."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)