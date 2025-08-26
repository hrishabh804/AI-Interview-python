import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import VideoCall from './VideoCall';
import CodeEditor from './CodeEditor';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
    const [roomId, setRoomId] = useState('');
    const [joined, setJoined] = useState(false);
    const [question, setQuestion] = useState('');
    const [model, setModel] = useState('openai');
    const [log, setLog] = useState([]);
    const socketRef = useRef();
    const [codingQuestion, setCodingQuestion] = useState(null);
    const [code, setCode] = useState('');
    const [testResults, setTestResults] = useState([]);

    useEffect(() => {
        if (joined) {
            socketRef.current = io.connect("http://localhost:8000", { path: "/socket.io" });
            socketRef.current.on('question-answered', (data) => {
                setLog(prevLog => [...prevLog, `Q: ${data.question}`, `A: ${data.answer}`]);
            });
            socketRef.current.on('coding-question', (data) => {
                setCodingQuestion(data.question);
                setCode(data.question.template);
                setTestResults([]);
            });

            return () => {
                if(socketRef.current) {
                    socketRef.current.disconnect();
                }
            };
        }
    }, [joined]);

    const handleJoin = () => {
        if (roomId) {
            setJoined(true);
        }
    };

    const handleAsk = async () => {
        if (question && model && roomId) {
            await axios.post(`${API_BASE_URL}/ask`, { question, model, roomId });
            setQuestion('');
        }
    };

    const handleAskCodingQuestion = async () => {
        if (roomId) {
            await axios.post(`${API_BASE_URL}/ask-coding-question`, { roomId });
        }
    };

    const handleRunCode = async () => {
        if (code && codingQuestion) {
            const { function_name, tests } = codingQuestion;
            const response = await axios.post(`${API_BASE_URL}/run-code`, {
                code,
                function_name,
                tests,
            });
            setTestResults(response.data.results);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Multi-User Video Call with AI</h1>
                {!joined ? (
                    <div className="join-container">
                        <input
                            type="text"
                            placeholder="Enter Room ID"
                            value={roomId}
                            onChange={(e) => setRoomId(e.target.value)}
                        />
                        <button onClick={handleJoin}>Join Room</button>
                    </div>
                ) : (
                    <>
                        <h2>Room: {roomId}</h2>
                        <VideoCall roomId={roomId} />
                        <div className="qa-container">
                            <h3>Ask a Question</h3>
                            <div className="model-selector">
                                <label>
                                    <input
                                        type="radio"
                                        value="openai"
                                        checked={model === 'openai'}
                                        onChange={() => setModel('openai')}
                                    />
                                    OpenAI
                                </label>
                                <label>
                                    <input
                                        type="radio"
                                        value="ollama"
                                        checked={model === 'ollama'}
                                        onChange={() => setModel('ollama')}
                                    />
                                    Ollama
                                </label>
                            </div>
                            <textarea
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                placeholder="Type your question here..."
                            />
                            <button onClick={handleAsk}>Ask</button>
                        </div>
                        <div className="qa-container">
                            <button onClick={handleAskCodingQuestion}>Ask a Coding Question</button>
                        </div>
                        {codingQuestion && (
                            <div className="coding-challenge-container">
                                <h3>{codingQuestion.title}</h3>
                                <p>{codingQuestion.description}</p>
                                <CodeEditor code={code} setCode={setCode} />
                                <button onClick={handleRunCode}>Run Code</button>
                                {testResults.length > 0 && (
                                    <div className="results-container">
                                        <h4>Test Results</h4>
                                        {testResults.map((result, index) => (
                                            <div key={index} className={`result ${result.passed ? 'passed' : 'failed'}`}>
                                                <p>Input: {JSON.stringify(result.input)}</p>
                                                <p>Output: {result.output}</p>
                                                {!result.passed && <p>Expected: {result.expected}</p>}
                                                <p>Status: {result.passed ? 'Passed' : 'Failed'}</p>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                        <div className="log-container">
                            <h3>Interview Log</h3>
                            <div className="log">
                                {log.map((entry, index) => (
                                    <p key={index}>{entry}</p>
                                ))}
                            </div>
                        </div>
                    </>
                )}
            </header>
        </div>
    );
}

export default App;
