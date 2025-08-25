from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .proctoring import ProctoringSystem, ProctoringLogger

app = FastAPI()

# Allow CORS for the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Assuming frontend runs on port 3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock AI and Interview Questions
interview_questions = [
    "Tell me about yourself.",
    "What are your strengths and weaknesses?",
    "Why are you interested in this role?",
    "Describe a challenging situation you faced at work and how you handled it.",
    "Where do you see yourself in 5 years?",
]

# Initialize Proctoring System
proctoring_logger = ProctoringLogger()
proctoring_system = ProctoringSystem(logger=proctoring_logger)

interview_state = {
    "current_question_index": 0,
    "interview_started": False,
}

@app.post("/start-interview")
async def start_interview():
    proctoring_system.start()
    proctoring_system.log_event("Interview started.")
    interview_state["current_question_index"] = 0
    interview_state["interview_started"] = True
    return {"question": interview_questions[0]}

@app.post("/interview")
async def handle_interview(request: Request):
    if not interview_state["interview_started"]:
        return {"error": "Interview not started."}, 400

    data = await request.json()
    user_answer = data.get("answer", "")

    proctoring_system.log_event(f"Received answer for question {interview_state['current_question_index'] + 1}: {user_answer}")

    interview_state["current_question_index"] += 1
    next_question_index = interview_state["current_question_index"]

    if next_question_index < len(interview_questions):
        next_question = interview_questions[next_question_index]
        return {"question": next_question}
    else:
        proctoring_system.stop()
        interview_state["interview_started"] = False
        return {"message": "Interview completed."}

@app.get("/")
def read_root():
    return {"Hello": "World"}
