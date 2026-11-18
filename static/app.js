/**
 * ARC SCRIBE • Pure Voice Instrument Engine (v4.0.0)
 * Single Action Focus: Record ➔ Stop ➔ Analyze ➔ Raw Dialogue Script
 */

const InstrumentState = {
  isRecording: false,
  isPaused: false,
  mediaRecorder: null,
  audioStream: null,
  audioContext: null,
  analyserNode: null,
  animationFrameId: null,
  recordedChunks: [],
  currentAudioBlob: null,
  recordingStartTime: 0,
  timerInterval: null,
  wakeLock: null,
  dialogueData: []
};

// Canvas Multi-Band Waveform Ribbon Visualizer
function initWaveformVisualizer(stream) {
  const canvas = document.getElementById('waveformCanvas');
  const canvasCtx = canvas.getContext('2d');
  
  // Set real canvas pixel resolution
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * window.devicePixelRatio || 720;
  canvas.height = rect.height * window.devicePixelRatio || 180;

  if (!InstrumentState.audioContext) {
    InstrumentState.audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (InstrumentState.audioContext.state === 'suspended') {
    InstrumentState.audioContext.resume();
  }

  const source = InstrumentState.audioContext.createMediaStreamSource(stream);
  InstrumentState.analyserNode = InstrumentState.audioContext.createAnalyser();
  InstrumentState.analyserNode.fftSize = 128;
  InstrumentState.analyserNode.smoothingTimeConstant = 0.8;
  source.connect(InstrumentState.analyserNode);

  const bufferLength = InstrumentState.analyserNode.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  function renderWaveform() {
    InstrumentState.animationFrameId = requestAnimationFrame(renderWaveform);
    InstrumentState.analyserNode.getByteFrequencyData(dataArray);

    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

    const barWidth = (canvas.width / bufferLength) * 1.8;
    let x = 0;
    const centerY = canvas.height / 2;

    for (let i = 0; i < bufferLength; i++) {
      const val = dataArray[i] / 255;
      const barHeight = val * (canvas.height * 0.42);

      // Multi-band color blending: Speaker 1 Amber & Speaker 2 Amethyst
      const gradient = canvasCtx.createLinearGradient(0, centerY - barHeight, 0, centerY + barHeight);
      if (i < bufferLength / 2) {
        gradient.addColorStop(0, '#F59E0B');
        gradient.addColorStop(1, 'rgba(245, 158, 11, 0.2)');
      } else {
        gradient.addColorStop(0, '#A78BFA');
        gradient.addColorStop(1, 'rgba(167, 139, 250, 0.2)');
      }

      canvasCtx.fillStyle = gradient;
      
      // Mirror reflection ribbon around center Y
      canvasCtx.fillRect(x, centerY - barHeight, barWidth - 4, barHeight * 2 || 2);
      x += barWidth;
    }
  }

  renderWaveform();
}

function stopWaveformVisualizer() {
  if (InstrumentState.animationFrameId) {
    cancelAnimationFrame(InstrumentState.animationFrameId);
  }
  const canvas = document.getElementById('waveformCanvas');
  if (canvas) {
    const canvasCtx = canvas.getContext('2d');
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

// Mobile Screen WakeLock API
async function requestScreenWakeLock() {
  if ('wakeLock' in navigator) {
    try {
      InstrumentState.wakeLock = await navigator.wakeLock.request('screen');
    } catch (err) {
      console.warn('Wake Lock request warning:', err);
    }
  }
}

function releaseScreenWakeLock() {
  if (InstrumentState.wakeLock) {
    InstrumentState.wakeLock.release().catch(() => {});
    InstrumentState.wakeLock = null;
  }
}

// Timer Logic
function startTimer() {
  clearInterval(InstrumentState.timerInterval);
  InstrumentState.timerInterval = setInterval(() => {
    if (!InstrumentState.isPaused) {
      const elapsedSec = Math.floor((Date.now() - InstrumentState.recordingStartTime) / 1000);
      const minutes = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
      const seconds = String(elapsedSec % 60).padStart(2, '0');
      document.getElementById('timerDisplay').textContent = `${minutes}:${seconds}`;
    }
  }, 500);
}

function resetTimer() {
  clearInterval(InstrumentState.timerInterval);
  document.getElementById('timerDisplay').textContent = '00:00';
}

// Recording State Machine
async function startRecording() {
  try {
    const constraints = {
      audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: true,
        channelCount: 1,
      }
    };

    InstrumentState.audioStream = await navigator.mediaDevices.getUserMedia(constraints);
    initWaveformVisualizer(InstrumentState.audioStream);
    await requestScreenWakeLock();

    let mimeType = 'audio/webm;codecs=opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = MediaRecorder.isTypeSupported('audio/mp4') ? 'audio/mp4' : '';
    }

    InstrumentState.recordedChunks = [];
    InstrumentState.mediaRecorder = mimeType 
      ? new MediaRecorder(InstrumentState.audioStream, { mimeType }) 
      : new MediaRecorder(InstrumentState.audioStream);

    InstrumentState.mediaRecorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) {
        InstrumentState.recordedChunks.push(e.data);
      }
    };

    InstrumentState.mediaRecorder.start(1000); // 1-second slices
    InstrumentState.isRecording = true;
    InstrumentState.isPaused = false;
    InstrumentState.recordingStartTime = Date.now();

    startTimer();

    // UI Updates
    document.getElementById('recordingSection').classList.add('recording-live');
    document.getElementById('recordTriggerWrap').style.display = 'none';
    document.getElementById('activeControls').style.display = 'flex';
    document.getElementById('analyzeStation').style.display = 'none';
    document.getElementById('processingState').style.display = 'none';
    document.getElementById('statePill').textContent = 'RECORDING LIVE';
  } catch (err) {
    console.error('Microphone access failed:', err);
    alert('Microphone permission required to record: ' + err.message);
  }
}

function pauseRecording() {
  if (!InstrumentState.mediaRecorder || !InstrumentState.isRecording) return;

  if (!InstrumentState.isPaused) {
    InstrumentState.mediaRecorder.pause();
    InstrumentState.isPaused = true;
    document.getElementById('pauseIcon').textContent = '▶';
    document.getElementById('pauseLabel').textContent = 'RESUME';
    document.getElementById('statePill').textContent = 'PAUSED';
  } else {
    InstrumentState.mediaRecorder.resume();
    InstrumentState.isPaused = false;
    document.getElementById('pauseIcon').textContent = '⏸';
    document.getElementById('pauseLabel').textContent = 'PAUSE';
    document.getElementById('statePill').textContent = 'RECORDING LIVE';
  }
}

function stopRecording() {
  if (!InstrumentState.mediaRecorder) return;

  InstrumentState.mediaRecorder.onstop = () => {
    const mime = InstrumentState.mediaRecorder.mimeType || 'audio/webm';
    InstrumentState.currentAudioBlob = new Blob(InstrumentState.recordedChunks, { type: mime });
    
    // Stop mic stream & visualizer
    if (InstrumentState.audioStream) {
      InstrumentState.audioStream.getTracks().forEach(t => t.stop());
    }
    stopWaveformVisualizer();
    releaseScreenWakeLock();
    clearInterval(InstrumentState.timerInterval);

    // UI to Analyze Ready
    document.getElementById('recordingSection').classList.remove('recording-live');
    document.getElementById('activeControls').style.display = 'none';
    document.getElementById('analyzeStation').style.display = 'flex';
    document.getElementById('statePill').textContent = 'AUDIO CAPTURED • READY TO ANALYZE';
  };

  InstrumentState.mediaRecorder.stop();
  InstrumentState.isRecording = false;
}

function discardAndReset() {
  InstrumentState.currentAudioBlob = null;
  InstrumentState.recordedChunks = [];
  resetTimer();
  document.getElementById('analyzeStation').style.display = 'none';
  document.getElementById('recordTriggerWrap').style.display = 'flex';
  document.getElementById('statePill').textContent = 'TAP TO RECORD';
}

// AI Dialogue Analysis Trigger
async function analyzeDialogue() {
  if (!InstrumentState.currentAudioBlob) return;

  document.getElementById('analyzeStation').style.display = 'none';
  document.getElementById('processingState').style.display = 'flex';
  document.getElementById('statePill').textContent = 'AI ANALYZING...';

  const formData = new FormData();
  formData.append('audio', InstrumentState.currentAudioBlob, 'dialogue_enactment.webm');
  formData.append('arc_title', 'Raw Voice Session');
  formData.append('speaker_1_name', 'Speaker 1');
  formData.append('speaker_1_char', 'Speaker 1');
  formData.append('speaker_2_name', 'Speaker 2');
  formData.append('speaker_2_char', 'Speaker 2');

  try {
    const response = await fetch('/api/process-audio', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Analysis failed');
    }

    const data = await response.json();
    renderScriptResults(data);
  } catch (err) {
    console.error('Analysis error:', err);
    alert('Analysis failed: ' + err.message + '\n\nPlease verify your GEMINI_API_KEY in arc-scribe/.env.');
    document.getElementById('processingState').style.display = 'none';
    document.getElementById('analyzeStation').style.display = 'flex';
    document.getElementById('statePill').textContent = 'READY TO ANALYZE';
  }
}

// Render Results into Screen 2
function renderScriptResults(data) {
  document.getElementById('recordingSection').style.display = 'none';
  document.getElementById('scriptSection').style.display = 'flex';

  const stream = document.getElementById('scriptStream');
  stream.innerHTML = '';

  const dialogues = data.dialogue_script || [];
  InstrumentState.dialogueData = dialogues;

  if (dialogues.length === 0) {
    stream.innerHTML = '<div class="script-card"><p>No clear dialogue lines detected in audio.</p></div>';
    return;
  }

  dialogues.forEach((item, index) => {
    const card = document.createElement('div');
    const isSpeaker1 = (item.speaker_id === 'speaker_1' || (item.speaker || '').toLowerCase().includes('speaker 1') || (item.speaker || '').toLowerCase().includes('author 1'));
    card.className = `script-card ${isSpeaker1 ? 'speaker-1' : 'speaker-2'}`;

    const toneText = item.vocal_tone ? `[${item.vocal_tone}]` : '';
    const timeText = item.timestamp ? item.timestamp : '';

    card.innerHTML = `
      <div class="script-card-header">
        <span class="speaker-pill">${escapeHtml(item.speaker || (isSpeaker1 ? 'Speaker 1' : 'Speaker 2'))}</span>
        <span class="tone-badge">${escapeHtml(toneText)} ${timeText}</span>
      </div>
      <div class="script-line">${escapeHtml(item.text || '')}</div>
    `;

    stream.appendChild(card);
  });
}

function returnToRecordNext() {
  InstrumentState.currentAudioBlob = null;
  InstrumentState.recordedChunks = [];
  resetTimer();

  document.getElementById('scriptSection').style.display = 'none';
  document.getElementById('recordingSection').style.display = 'flex';
  document.getElementById('processingState').style.display = 'none';
  document.getElementById('analyzeStation').style.display = 'none';
  document.getElementById('activeControls').style.display = 'none';
  document.getElementById('recordTriggerWrap').style.display = 'flex';
  document.getElementById('statePill').textContent = 'TAP TO RECORD';
}

function copyRawScriptToClipboard() {
  if (!InstrumentState.dialogueData || InstrumentState.dialogueData.length === 0) return;

  const textLines = InstrumentState.dialogueData.map(d => {
    const tone = d.vocal_tone ? ` [${d.vocal_tone}]` : '';
    return `${d.speaker || 'Speaker'}${tone}: ${d.text || ''}`;
  }).join('\n\n');

  navigator.clipboard.writeText(textLines).then(() => {
    const btn = document.getElementById('copyScriptBtn');
    btn.innerHTML = '<span>✓ Copied!</span>';
    setTimeout(() => {
      btn.innerHTML = '<span>📋 Copy Script</span>';
    }, 2000);
  });
}

// Utility
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// Network / Mobile Link
async function checkNetworkInfo() {
  try {
    const res = await fetch('/api/network-ip');
    if (res.ok) {
      const data = await res.json();
      document.getElementById('modalMobileUrl').textContent = data.mobile_url;
      document.getElementById('networkIpText').textContent = data.local_ip;
    }
  } catch (e) {
    console.warn('Network IP fetch error:', e);
  }
}

// Event Bindings
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('startRecordBtn').addEventListener('click', startRecording);
  document.getElementById('pauseRecordBtn').addEventListener('click', pauseRecording);
  document.getElementById('stopRecordBtn').addEventListener('click', stopRecording);
  document.getElementById('discardBtn').addEventListener('click', discardAndReset);
  document.getElementById('analyzeBtn').addEventListener('click', analyzeDialogue);
  document.getElementById('recordNextBtn').addEventListener('click', returnToRecordNext);
  document.getElementById('copyScriptBtn').addEventListener('click', copyRawScriptToClipboard);

  // Network modal
  const networkModal = document.getElementById('networkModal');
  document.getElementById('networkShareBtn').addEventListener('click', () => {
    networkModal.style.display = 'flex';
  });
  document.getElementById('closeNetworkModalBtn').addEventListener('click', () => {
    networkModal.style.display = 'none';
  });
  document.getElementById('copyUrlBtn').addEventListener('click', () => {
    const url = document.getElementById('modalMobileUrl').textContent;
    navigator.clipboard.writeText(url);
    const btn = document.getElementById('copyUrlBtn');
    btn.textContent = '✓ Copied Link!';
    setTimeout(() => btn.textContent = '📋 Copy Link', 2000);
  });

  checkNetworkInfo();
});
