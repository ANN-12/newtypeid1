import React, { useState, useRef } from "react";
import "./signin.css";

// 2 SENTENCES for login verification (changed from 5)
const LOGIN_SENTENCES = [
  "Two driven jocks help fax my big quiz",
  "Five quacking zephyrs jolt my wax bed"
];

const TypingLogin = ({ setPage }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginMethod, setLoginMethod] = useState("typing");
  const [step, setStep] = useState("username");
  const [attempt, setAttempt] = useState(1);
  const [text, setText] = useState("");
  const [allFeatures, setAllFeatures] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const currentSentence = LOGIN_SENTENCES[attempt - 1];
  
  const keystrokeEvents = useRef([]);
  const startTime = useRef(null);

  const handleUsernameSubmit = () => {
    if (!username.trim()) {
      alert("Please enter your username");
      return;
    }
    
    if (loginMethod === "password") {
      setStep("password");
    } else {
      setStep("typing");
    }
  };

  const handlePasswordLogin = async () => {
    if (!password.trim()) {
      alert("Please enter your password");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/login-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: username,
          password: password
        })
      });

      const data = await response.json();
      
      if (response.ok && data.access_granted) {
        alert(`Welcome back, ${username}! ✅`);
        setPage("home");
      } else {
        alert(`Login failed! ❌\n\n${data.error || 'Invalid username or password'}`);
        setPassword("");
        setIsSubmitting(false);
      }
    } catch (err) {
      console.error('Login error:', err);
      alert("Backend connection failed. Make sure Flask is running on port 5000.");
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e) => {
    if (isSubmitting) return;
    
    if (!startTime.current) {
      startTime.current = Date.now();
    }

    keystrokeEvents.current.push({
      key: e.key,
      type: "down",
      time: Date.now()
    });
  };

  const handleKeyUp = (e) => {
    if (isSubmitting) return;
    
    keystrokeEvents.current.push({
      key: e.key,
      type: "up",
      time: Date.now()
    });
  };

  const calcMean = (arr) => arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;
  
  const calcStd = (arr) => {
    if (arr.length < 2) return 25;
    const mean = calcMean(arr);
    const variance = arr.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / arr.length;
    return Math.sqrt(variance);
  };

  const calculateFeatures = () => {
    const key_downs = keystrokeEvents.current.filter(e => e.type === "down");
    const key_ups = keystrokeEvents.current.filter(e => e.type === "up");

    if (key_downs.length < 10) {
      return null;
    }

    const dwells = [];
    for (let i = 0; i < Math.min(key_downs.length, key_ups.length); i++) {
      const dwell = key_ups[i].time - key_downs[i].time;
      if (dwell > 0 && dwell < 2000) dwells.push(dwell);
    }

    const flights = [];
    for (let i = 0; i < key_downs.length - 1; i++) {
      const flight = key_downs[i + 1].time - key_ups[i].time;
      if (flight > 0 && flight < 3000) flights.push(flight);
    }

    const digraphs = [];
    for (let i = 0; i < key_downs.length - 1; i++) {
      const digraph = key_downs[i + 1].time - key_downs[i].time;
      if (digraph > 0 && digraph < 4000) digraphs.push(digraph);
    }

    const total_time_ms = key_downs[key_downs.length - 1].time - key_downs[0].time;
    const total_time_sec = total_time_ms / 1000;
    const total_time_min = total_time_sec / 60;

    const backspace_count = keystrokeEvents.current.filter(e => e.key === 'Backspace').length;

    return {
      ks_count: key_downs.length,
      ks_rate: key_downs.length / Math.max(total_time_sec, 1),
      dwell_mean: calcMean(dwells) || 120,
      dwell_std: calcStd(dwells),
      flight_mean: calcMean(flights) || 150,
      flight_std: calcStd(flights),
      digraph_mean: calcMean(digraphs) || 135,
      digraph_std: calcStd(digraphs),
      backspace_rate: backspace_count / Math.max(keystrokeEvents.current.length, 1) || 0.02,
      wps: text.split(' ').length / Math.max(total_time_sec, 1) || 15,
      wpm: (text.length / 5) / Math.max(total_time_min, 1) || 90
    };
  };

  const handleTypingSubmit = async () => {
    if (isSubmitting) return;
    
    if (text.toLowerCase().trim() !== currentSentence.toLowerCase().trim()) {
      alert("Sentence doesn't match. Please type it exactly.");
      return;
    }

    const features = calculateFeatures();
    
    if (!features) {
      alert("Not enough typing data. Please type the full sentence.");
      return;
    }

    const updatedFeatures = [...allFeatures, features];
    setAllFeatures(updatedFeatures);

    if (attempt < 2) {  // Changed from 3 to 2
      alert(`Sentence ${attempt}/2 completed!`);
      setAttempt(attempt + 1);
      setText("");
      keystrokeEvents.current = [];
      startTime.current = null;
    } else {
      setIsSubmitting(true);
      
      try {
        const response = await fetch("http://127.0.0.1:5000/api/login-hybrid", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: username,
            keystroke_features_list: updatedFeatures
          })
        });

        const data = await response.json();
        
        if (response.ok && data.access_granted) {
          const method = data.method === "ML_MODEL" ? "ML Model (High Accuracy)" : "Database Match";
          alert(`✅ Welcome back, ${username}!\n\nVerified using: ${method}\nConfidence: ${(data.confidence * 100).toFixed(1)}%`);
          setPage("home");
        } else {
          const reason = data.method === "ML_MODEL" 
            ? `ML Model predicted: ${data.predicted_user}` 
            : `Database similarity too low: ${(data.similarity * 100).toFixed(1)}%`;
          alert(`❌ Access Denied!\n\n${reason}\n\nYour typing pattern doesn't match ${username}.`);
          setStep("username");
          setAttempt(1);
          setText("");
          setAllFeatures([]);
          keystrokeEvents.current = [];
          startTime.current = null;
          setIsSubmitting(false);
        }
      } catch (err) {
        console.error('Login error:', err);
        alert("Backend connection failed. Make sure Flask is running on port 5000.");
        setIsSubmitting(false);
      }
    }
  };

  return (
    <div className="signin-wrapper">
      <div className="signin-box">
        {step === "username" && (
          <>
            <h2>Verify your identity</h2>
            <p className="subtitle">Enter your username to begin verification</p>
            
            <input
              type="text"
              placeholder="Enter Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleUsernameSubmit()}
              autoFocus
            />
            
            <button onClick={handleUsernameSubmit}>Continue</button>
            
            <p 
              className="password-link" 
              onClick={() => setLoginMethod(loginMethod === "typing" ? "password" : "typing")}
              style={{ cursor: 'pointer', color: '#14b8a6', marginTop: '1rem' }}
            >
              {loginMethod === "typing" ? "Login with password instead?" : "Login with typing pattern instead?"}
            </p>
          </>
        )}

        {step === "password" && (
          <>
            <h2>Password Login</h2>
            <p className="subtitle">Enter your password to sign in</p>
            
            <input
              type="password"
              placeholder="Enter Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handlePasswordLogin()}
              disabled={isSubmitting}
              autoFocus
            />
            
            <button onClick={handlePasswordLogin} disabled={isSubmitting}>
              {isSubmitting ? "Verifying..." : "Sign In"}
            </button>
            
            <p 
              className="password-link" 
              onClick={() => {
                setStep("username");
                setLoginMethod("typing");
                setPassword("");
              }}
              style={{ cursor: 'pointer', color: '#14b8a6', marginTop: '1rem' }}
            >
              Back to typing verification
            </p>
          </>
        )}

        {step === "typing" && (
          <>
            <h2>Verify Typing Pattern</h2>
            <p className="subtitle">Type the sentence below to verify your identity</p>
            
            <div className="sentence-box">{currentSentence}</div>
            
            <p className="attempt">
              Sentence {attempt} of 2
              <span style={{ marginLeft: '20px', color: '#666', fontSize: '14px' }}>
                ({keystrokeEvents.current.length} keys recorded)
              </span>
            </p>
            
            <input
              type="text"
              placeholder="Type the sentence here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              onKeyUp={handleKeyUp}
              disabled={isSubmitting}
              autoFocus
            />
            
            <button onClick={handleTypingSubmit} disabled={isSubmitting}>
              {isSubmitting ? "Verifying..." : attempt < 2 ? "Next Sentence" : "Verify Identity"}
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default TypingLogin;