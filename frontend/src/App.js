import React, { useState, useEffect } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import Webcam from 'react-webcam';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [isFinished, setIsFinished] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition
  } = useSpeechRecognition();

  useEffect(() => {
    if (!browserSupportsSpeechRecognition) {
      alert("Your browser does not support speech recognition. Please try Chrome.");
    }
  }, [browserSupportsSpeechRecognition]);

  const speak = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const startInterview = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/start-interview`);
      const { question } = response.data;
      setCurrentQuestion(question);
      speak(question);
      setInterviewStarted(true);
      resetTranscript();
      SpeechRecognition.startListening({ continuous: true });
    } catch (error) {
      console.error("Error starting interview:", error);
      alert("Could not start interview. Make sure the backend server is running.");
    }
    setIsLoading(false);
  };

  const submitAnswer = async () => {
    setIsLoading(true);
    SpeechRecognition.stopListening();
    try {
      const response = await axios.post(`${API_BASE_URL}/interview`, { answer: transcript });
      if (response.data.message) {
        // Interview finished
        setCurrentQuestion(response.data.message);
        speak(response.data.message);
        setIsFinished(true);
        setInterviewStarted(false);
      } else {
        const { question } = response.data;
        setCurrentQuestion(question);
        speak(question);
        resetTranscript();
        SpeechRecognition.startListening({ continuous: true });
      }
    } catch (error) {
      console.error("Error submitting answer:", error);
    }
    setIsLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Video Interview</h1>
        <div className="video-container">
          <Webcam audio={false} mirrored={true} />
        </div>

        {isFinished ? (
          <div className="finished-message">
            <h2>{currentQuestion}</h2>
            <p>Thank you for completing the interview.</p>
          </div>
        ) : interviewStarted ? (
          <div className="interview-container">
            <h2>Question:</h2>
            <p>{currentQuestion}</p>
            <div className="transcript-container">
              <h3>Your Answer:</h3>
              <p>{transcript}</p>
            </div>
            <div className="controls">
              <button onClick={submitAnswer} disabled={isLoading || !listening}>
                {isLoading ? 'Submitting...' : 'Submit Answer'}
              </button>
              <p>Mic: {listening ? 'on' : 'off'}</p>
            </div>
          </div>
        ) : (
          <div className="start-container">
            <p>Click the button to start your interview.</p>
            <button onClick={startInterview} disabled={isLoading}>
              {isLoading ? 'Starting...' : 'Start Interview'}
            </button>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
