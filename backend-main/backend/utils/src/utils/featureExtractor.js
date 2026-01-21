/**
 * Calculate 11 keystroke features for XGBoost model
 * Features: ks_count, ks_rate, dwell_mean, dwell_std, flight_mean, flight_std,
 *           digraph_mean, digraph_std, backspace_rate, wps, wpm
 */
export const calculateFeatures = (keystrokeData) => {
  const { dwellTimes, flightTimes, backspaceCount, totalTime, text } = keystrokeData;
  
  // Helper: Calculate mean
  const mean = (arr) => {
    if (!arr || arr.length === 0) return 0;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
  };
  
  // Helper: Calculate standard deviation
  const std = (arr) => {
    if (!arr || arr.length === 0) return 0;
    const avg = mean(arr);
    const variance = arr.reduce((sum, val) => sum + Math.pow(val - avg, 2), 0) / arr.length;
    return Math.sqrt(variance);
  };

  // 1. ks_count - Total keystrokes
  const ks_count = dwellTimes.length;

  // 2. ks_rate - Keystrokes per second
  const totalTimeInSeconds = totalTime / 1000;
  const ks_rate = totalTimeInSeconds > 0 ? ks_count / totalTimeInSeconds : 0;

  // 3. dwell_mean - Average key hold time (ms)
  const dwell_mean = mean(dwellTimes);

  // 4. dwell_std - Standard deviation of dwell times
  const dwell_std = std(dwellTimes);

  // 5. flight_mean - Average time between key releases (ms)
  const flight_mean = mean(flightTimes);

  // 6. flight_std - Standard deviation of flight times
  const flight_std = std(flightTimes);

  // 7 & 8. digraph_mean & digraph_std
  // Digraph = dwell time of first key + flight time to next key
  const digraphs = [];
  for (let i = 0; i < dwellTimes.length - 1; i++) {
    digraphs.push(dwellTimes[i] + (flightTimes[i] || 0));
  }
  const digraph_mean = mean(digraphs);
  const digraph_std = std(digraphs);

  // 9. backspace_rate - Backspaces per keystroke
  const backspace_rate = ks_count > 0 ? backspaceCount / ks_count : 0;

  // 10. wps - Words per second
  const wordCount = text.trim().split(/\s+/).filter(w => w.length > 0).length;
  const wps = totalTimeInSeconds > 0 ? wordCount / totalTimeInSeconds : 0;

  // 11. wpm - Words per minute
  const wpm = wps * 60;

  return {
    ks_count,
    ks_rate,
    dwell_mean,
    dwell_std,
    flight_mean,
    flight_std,
    digraph_mean,
    digraph_std,
    backspace_rate,
    wps,
    wpm
  };
};