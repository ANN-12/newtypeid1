export const calculateFeatures = ({ dwellTimes, flightTimes, backspaceCount, totalTime, text }) => {
  const mean = (arr) => arr.length === 0 ? 0 : arr.reduce((sum, val) => sum + val, 0) / arr.length;
  
  const std = (arr) => {
    if (arr.length === 0) return 0;
    const avg = mean(arr);
    const squareDiffs = arr.map(value => Math.pow(value - avg, 2));
    return Math.sqrt(mean(squareDiffs));
  };

  const keystrokeCount = text.length;
  const keystrokeRate = totalTime > 0 ? (keystrokeCount / (totalTime / 1000)) : 0;
  
  const dwellMean = mean(dwellTimes);
  const dwellStd = std(dwellTimes);
  
  const flightMean = mean(flightTimes);
  const flightStd = std(flightTimes);
  
  const digraphMean = flightMean;
  const digraphStd = flightStd;
  
  const backspaceRate = keystrokeCount > 0 ? (backspaceCount / keystrokeCount) : 0;
  
  const wordCount = text.trim().split(/\s+/).length;
  const timeInSeconds = totalTime / 1000;
  const wps = timeInSeconds > 0 ? (wordCount / timeInSeconds) : 0;
  const wpm = wps * 60;

  return {
    ks_count: keystrokeCount,
    ks_rate: Number(keystrokeRate.toFixed(4)),
    dwell_mean: Number(dwellMean.toFixed(4)),
    dwell_std: Number(dwellStd.toFixed(4)),
    flight_mean: Number(flightMean.toFixed(4)),
    flight_std: Number(flightStd.toFixed(4)),
    digraph_mean: Number(digraphMean.toFixed(4)),
    digraph_std: Number(digraphStd.toFixed(4)),
    backspace_rate: Number(backspaceRate.toFixed(4)),
    wps: Number(wps.toFixed(4)),
    wpm: Number(wpm.toFixed(4))
  };
};