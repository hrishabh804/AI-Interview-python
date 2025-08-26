import requests
import socketio
import time

# --- Test Configuration ---
BASE_URL = "http://localhost:8000"
ROOM_ID = "test-room"
# --------------------------

sio = socketio.Client()
coding_question_received = None

@sio.event
def connect():
    print("Socket.IO connected!")
    sio.emit("join", {"roomId": ROOM_ID})
    print(f"Joined room: {ROOM_ID}")

@sio.event
def disconnect():
    print("Socket.IO disconnected.")

@sio.on('coding-question')
def on_coding_question(data):
    global coding_question_received
    print("Received coding question:")
    coding_question_received = data['question']
    print(coding_question_received)
    sio.disconnect()


def run_test():
    # 1. Connect to the Socket.IO server
    sio.connect(BASE_URL, socketio_path="/socket.io")

    # 2. Ask a coding question
    print("\nAsking for a coding question...")
    response = requests.post(f"{BASE_URL}/ask-coding-question", json={"roomId": ROOM_ID})
    if response.status_code == 200:
        print("Successfully asked for a coding question.")
    else:
        print(f"Error asking for coding question: {response.text}")
        sio.disconnect()
        return

    # Wait for the coding question to be received
    time.sleep(2) # Give server time to respond

    if not coding_question_received:
        print("\nDid not receive coding question.")
        return

    # 3. Prepare code and submit to /run-code
    print("\nSubmitting code to run...")
    # A correct solution for the "Two Sum" problem
    code_to_run = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return True
        seen[num] = i
    return False
"""

    payload = {
        "code": code_to_run,
        "function_name": coding_question_received['function_name'],
        "tests": coding_question_received['tests']
    }

    response = requests.post(f"{BASE_URL}/run-code", json=payload)

    # 4. Check the results
    if response.status_code == 200:
        results = response.json().get("results", [])
        print("\nReceived results:")
        all_passed = True
        for res in results:
            print(f"  Input: {res['input']}, Output: {res['output']}, Passed: {res['passed']}")
            if not res['passed']:
                all_passed = False

        if all_passed:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed.")
    else:
        print(f"\nError running code: {response.text}")


if __name__ == "__main__":
    run_test()
