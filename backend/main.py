import socketio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .ai_models import ask_openai, ask_ollama
import logging
import random
from .coding_questions import QUESTIONS

logging.basicConfig(level=logging.INFO)
logging.info("Starting backend server...")

# Create a FastAPI app
app = FastAPI()
logging.info("FastAPI app created.")

# Allow CORS for the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.info("CORS middleware added.")

# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket_app = socketio.ASGIApp(sio)
app.mount("/socket.io", socket_app)
logging.info("Socket.IO server created and mounted.")


# Dictionary to hold room information
rooms = {}

@sio.event
async def connect(sid, environ):
    logging.info(f"Connected: {sid}")

@sio.event
async def disconnect(sid):
    logging.info(f"Disconnected: {sid}")
    # Remove user from any room they were in
    for room_id, members in list(rooms.items()):
        if sid in members:
            members.remove(sid)
            # if room is empty, delete it
            if not members:
                del rooms[room_id]
            await sio.emit("user-left", {"sid": sid}, room=room_id)
            break

@sio.on("join")
async def on_join(sid, data):
    room_id = data.get("roomId")
    logging.info(f"Received join event from {sid} for room {room_id}")
    if not room_id:
        return

    await sio.enter_room(sid, room_id)
    if room_id not in rooms:
        rooms[room_id] = []

    # Notify others in the room
    await sio.emit("user-joined", {"sid": sid, "members": rooms[room_id]}, room=room_id, skip_sid=sid)
    rooms[room_id].append(sid)
    logging.info(f"{sid} joined room {room_id}")


@sio.on("offer")
async def on_offer(sid, data):
    logging.info(f"Received offer from {sid} for {data['targetSid']}")
    # Forward offer to the target user
    await sio.emit("offer", data, room=data["targetSid"], skip_sid=sid)

@sio.on("answer")
async def on_answer(sid, data):
    logging.info(f"Received answer from {sid} for {data['targetSid']}")
    # Forward answer to the target user
    await sio.emit("answer", data, room=data["targetSid"], skip_sid=sid)

@sio.on("ice-candidate")
async def on_ice_candidate(sid, data):
    logging.info(f"Received ICE candidate from {sid} for {data['targetSid']}")
    # Forward ICE candidate to the target user
    await sio.emit("ice-candidate", data, room=data["targetSid"], skip_sid=sid)


@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    question = data.get("question")
    model = data.get("model")
    room_id = data.get("roomId")
    logging.info(f"Received question '{question}' for model '{model}' in room '{room_id}'")

    if not all([question, model, room_id]):
        return {"error": "Missing question, model, or roomId"}, 400

    if model == "openai":
        answer = ask_openai(question)
    elif model == "ollama":
        answer = ask_ollama(question)
    else:
        return {"error": "Invalid model specified"}, 400

    # Broadcast the answer to everyone in the room
    await sio.emit("question-answered", {"question": question, "answer": answer}, room=room_id)
    logging.info(f"Answered question '{question}' with answer '{answer}' in room '{room_id}'")
    return {"status": "success"}

@app.post("/ask-coding-question")
async def ask_coding_question(request: Request):
    data = await request.json()
    room_id = data.get("roomId")
    if not room_id:
        return {"error": "Missing roomId"}, 400

    question = random.choice(QUESTIONS)
    await sio.emit("coding-question", {"question": question}, room=room_id)
    return {"status": "success"}


@app.post("/run-code")
async def run_code(request: Request):
    data = await request.json()
    code = data.get("code")
    function_name = data.get("function_name")
    tests = data.get("tests")

    if not all([code, function_name, tests]):
        return {"error": "Missing code, function_name, or tests"}, 400

    results = []
    for test in tests:
        test_input = test["input"]
        expected_output = test["output"]

        try:
            # Create a dictionary to serve as the global scope for exec
            exec_globals = {}

            # Execute the user's code
            exec(code, exec_globals)

            # Get the user's function from the executed code
            user_function = exec_globals.get(function_name)

            if not user_function:
                results.append({"input": test_input, "output": f"Function '{function_name}' not found.", "passed": False})
                continue

            # Run the user's function with the test input
            output = user_function(*test_input)

            # Compare the output with the expected output
            if str(output) == str(expected_output):
                results.append({"input": test_input, "output": str(output), "expected": str(expected_output), "passed": True})
            else:
                results.append({"input": test_input, "output": str(output), "expected": str(expected_output), "passed": False})

        except Exception as e:
            results.append({"input": test_input, "output": str(e), "passed": False})

    return {"results": results}


@app.get("/")
def read_root():
    return {"Hello": "World"}

logging.info("Backend server script finished executing.")
