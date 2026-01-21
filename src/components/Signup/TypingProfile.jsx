import React, { useState, useRef } from "react";
import "./signup.css";

// 5 DIFFERENT SENTENCES for registration
const sentences = [
  "The quick brown fox jumps over the lazy dog",
  "Pack my box with five dozen liquor jugs",
  "How vexingly quick daft zebras jump",
  "Bright vixens jump; dozy fowl quack",
  "Sphinx of black quartz judge my vow"
];

const TypingProfile = ({ username, email, password, setPage }) => {
  const [attempt, setAttempt] = useState(1);
  const [text, setText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const currentSentence = sentences[attempt - 1];
  
  const keystrokeEvents = useRef([]);
  const startTime = useRef(null);

  const handleKeyDown = (e) => {
    // Don't record if submitting
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

  const handleSubmit = async () => {
    // Prevent double submission
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

    console.log('Calculated features:', features);

    setIsSubmitting(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: username,
          email: email,
          role: "student",
          password: password,
          keystroke_features: features,
          attempt: attempt
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        if (attempt < 5) {  // Changed from 3 to 5
          alert(`Attempt ${attempt}/5 completed!`);
          setAttempt(attempt + 1);
          setText("");
          keystrokeEvents.current = [];
          startTime.current = null;
          setIsSubmitting(false);
        } else {
          alert("Registration completed successfully! 🎉");
          setPage("signin");
        }
      } else {
        alert(`Error: ${data.error || 'Registration failed'}`);
        setIsSubmitting(false);
      }
    } catch (err) {
      console.error('Registration error:', err);
      alert("Backend connection failed. Make sure Flask is running on port 5000.");
      setIsSubmitting(false);
    }
  };

  return (
    <div className="signup-wrapper">
      <div className="signup-box">
        <h2>Create Typing Identity</h2>
        <p className="subtitle">Type the sentence below exactly as shown</p>
        
        <div className="sentence-box">{currentSentence}</div>
        
        <p className="attempt">
          Sentence {attempt} of 5
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
        
        <button onClick={handleSubmit} disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : attempt < 5 ? "Next Sentence" : "Complete Registration"}
        </button>
      </div>
    </div>
  );
};

export default TypingProfile;