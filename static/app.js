/**
 * ARC SCRIBE • Client Application Engine
 * Mobile-First Audio Recording, Sibling Calibration & Gemini AI Scribe
 */

// State Management
const AppState = {
  isRecording: false,
  isPaused: false,
  mediaRecorder: null,
  audioStream: null,
  audioContext: null,
  analyserNode: null,
  animationFrameId: null,
  recordedChunks: [],
  recordingStartTime: 0,
  timerInterval: null,
  wakeLock: null,
  activeTab: 'scriptTab',
  speaker1Calibrated: false,
  speaker2Calibrated: false,
};

// IndexedDB Local-First Persistence
const DB_NAME = 'ArcScribeDB';
const DB_VERSION = 1;
let db = null;

function initIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (e) => {
      const database = e.target.result;
      if (!database.objectStoreNames.contains('recordings')) {
        database.createObjectStore('recordings', { keyPath: 'id', autoIncrement: true });
      }
    };
    request.onsuccess = (e) => {
      db = e.target.result;
      resolve(db);
    };
    request.onerror = (e) => reject(e);
  });
}

async function saveChunkLocally(blob) {
  if (!db) return;
  const tx = db.transaction(['recordings'], 'readwrite');
  const store = tx.objectStore('recordings');
  store.add({ timestamp: Date.now(), chunk: blob });
}

// Mobile Screen WakeLock API
async function requestWakeLock() {
  if ('wakeLock' in navigator) {
    try {
      AppState.wakeLock = await navigator.wakeLock.request('screen');
      const shield = document.getElementById('wakeShield');
      const text = document.getElementById('wakeText');
      if (shield) shield.classList.add('active');
      if (text) text.textContent = 'Screen Awake (Active)';
      
      AppState.wakeLock.addEventListener('release', () => {
        if (shield) shield.classList.remove('active');
        if (text) text.textContent = 'WakeLock Released';
      });
    } catch (err) {
      console.warn('Wake Lock request failed:', err);
    }
  }
}

function releaseWakeLock() {
  if (AppState.wakeLock) {
    AppState.wakeLock.release().catch(() => {});
    AppState.wakeLock = null;
  }
}

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible' && AppState.isRecording) {
    requestWakeLock();
  }
});

// Canvas Audio Visualizer
function initVisualizer(stream) {
  const canvas = document.getElementById('waveformCanvas');
  const canvasCtx = canvas.getContext('2d');
  
  if (!AppState.audioContext) {
    AppState.audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  
  if (AppState.audioContext.state === 'suspended') {
    AppState.audioContext.resume();
  }
  
  const source = AppState.audioContext.createMediaStreamSource(stream);
  AppState.analyserNode = AppState.audioContext.createAnalyser();
  AppState.analyserNode.fftSize = 128;
  source.connect(AppState.analyserNode);

  const bufferLength = AppState.analyserNode.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  function draw() {
    AppState.animationFrameId = requestAnimationFrame(draw);
    AppState.analyserNode.getByteFrequencyData(dataArray);

    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

    const barWidth = (canvas.width / bufferLength) * 1.6;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * (canvas.height * 0.7);

      // Dual gradient: Amber to Violet
      const gradient = canvasCtx.createLinearGradient(0, canvas.height, 0, canvas.height - barHeight);
      gradient.addColorStop(0, 'rgba(245, 158, 11, 0.2)');
      gradient.addColorStop(0.5, 'rgba(245, 158, 11, 0.8)');
      gradient.addColorStop(1, 'rgba(139, 92, 246, 0.9)');

      canvasCtx.fillStyle = gradient;
      canvasCtx.fillRect(x, canvas.height - barHeight, barWidth - 2, barHeight);

      // Mirror reflection effect
      canvasCtx.fillStyle = 'rgba(245, 158, 11, 0.1)';
      canvasCtx.fillRect(x, canvas.height - 2, barWidth - 2, barHeight * 0.2);

      x += barWidth;
    }
  }

  draw();
}

function stopVisualizer() {
  if (AppState.animationFrameId) {
    cancelAnimationFrame(AppState.animationFrameId);
  }
  const canvas = document.getElementById('waveformCanvas');
  const canvasCtx = canvas.getContext('2d');
  canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
}

// Audio Recording Lifecycle
async function startRecording() {
  try {
    const audioConstraints = {
      audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: true,
        channelCount: 1,
      }
    };

    AppState.audioStream = await navigator.mediaDevices.getUserMedia(audioConstraints);
    initVisualizer(AppState.audioStream);
    await requestWakeLock();

    // Codec detection
    let mimeType = 'audio/webm;codecs=opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4';
      } else {
        mimeType = '';
      }
    }

    AppState.recordedChunks = [];
    AppState.mediaRecorder = mimeType ? new MediaRecorder(AppState.audioStream, { mimeType }) : new MediaRecorder(AppState.audioStream);

    AppState.mediaRecorder.ondataavailable = async (e) => {
      if (e.data && e.data.size > 0) {
        AppState.recordedChunks.push(e.data);
        await saveChunkLocally(e.data);
      }
    };

    // Slices audio every 10s for local resilience
    AppState.mediaRecorder.start(10000);
    AppState.isRecording = true;
    AppState.isPaused = false;
    AppState.recordingStartTime = Date.now();

    startTimer();
    updateControlsUI();
  } catch (err) {
    console.error('Error starting recording:', err);
    alert('Microphone access denied or audio recording failed: ' + err.message);
  }
}

function pauseRecording() {
  if (AppState.mediaRecorder && AppState.isRecording) {
    if (!AppState.isPaused) {
      AppState.mediaRecorder.pause();
      AppState.isPaused = true;
      document.getElementById('recordingState').textContent = 'Paused • Improv on Hold';
      document.getElementById('pauseBtn').querySelector('.btn-label').textContent = 'Resume';
    } else {
      AppState.mediaRecorder.resume();
      AppState.isPaused = false;
      document.getElementById('recordingState').textContent = 'Recording • Acting Live';
      document.getElementById('pauseBtn').querySelector('.btn-label').textContent = 'Pause';
    }
  }
}

async function finishAndScribe() {
  if (!AppState.mediaRecorder) return;

  AppState.isRecording = false;
  clearInterval(AppState.timerInterval);
  releaseWakeLock();
  stopVisualizer();

  document.getElementById('recordingState').textContent = 'Finalizing Audio...';

  AppState.mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(AppState.recordedChunks, { type: AppState.mediaRecorder.mimeType || 'audio/webm' });
    if (AppState.audioStream) {
      AppState.audioStream.getTracks().forEach(track => track.stop());
    }

    updateControlsUI();
    await sendAudioToGemini(audioBlob);
  };

  AppState.mediaRecorder.stop();
}

// Timer
function startTimer() {
  const timerDisplay = document.getElementById('recordingTimer');
  AppState.timerInterval = setInterval(() => {
    if (!AppState.isPaused) {
      const elapsed = Math.floor((Date.now() - AppState.recordingStartTime) / 1000);
      const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
      const secs = String(elapsed % 60).padStart(2, '0');
      timerDisplay.textContent = `${mins}:${secs}`;
    }
  }, 500);
}

// UI State Toggles
function updateControlsUI() {
  const recordBtn = document.getElementById('recordBtn');
  const pauseBtn = document.getElementById('pauseBtn');
  const finishBtn = document.getElementById('finishBtn');
  const stateTag = document.getElementById('recordingState');

  if (AppState.isRecording) {
    recordBtn.disabled = true;
    recordBtn.classList.add('recording');
    pauseBtn.disabled = false;
    finishBtn.disabled = false;
    stateTag.textContent = 'Recording • Acting Live';
  } else {
    recordBtn.disabled = false;
    recordBtn.classList.remove('recording');
    pauseBtn.disabled = true;
    finishBtn.disabled = true;
    stateTag.textContent = 'Standby • Ready to Enact';
    document.getElementById('recordingTimer').textContent = '00:00';
  }
}

// Gemini Audio Processing API
async function sendAudioToGemini(audioBlob) {
  const banner = document.getElementById('processingBanner');
  const bannerStep = document.getElementById('processingStep');
  banner.style.display = 'flex';
  bannerStep.textContent = 'Gemini 3.5 Flash Lite is Scribing...';

  const formData = new FormData();
  formData.append('audio', audioBlob, 'enactment_scene.webm');
  formData.append('arc_title', document.getElementById('arcTitleInput').value.trim() || 'Untitled Arc');
  formData.append('scene_context', document.getElementById('sceneContextInput').value.trim());

  // Dynamic speaker & character values (No hardcoded names!)
  formData.append('speaker_1_name', document.getElementById('spk1Name').value.trim() || 'Author 1');
  formData.append('speaker_1_char', document.getElementById('spk1Char').value.trim() || 'Character A');
  formData.append('speaker_1_notes', document.getElementById('spk1Notes').value.trim());

  formData.append('speaker_2_name', document.getElementById('spk2Name').value.trim() || 'Author 2');
  formData.append('speaker_2_char', document.getElementById('spk2Char').value.trim() || 'Character B');
  formData.append('speaker_2_notes', document.getElementById('spk2Notes').value.trim());

  try {
    const response = await fetch('/api/process-audio', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server returned HTTP ${response.status}`);
    }

    const data = await response.json();
    renderResults(data);
  } catch (err) {
    console.error('Processing error:', err);
    alert('Audio processing failed: ' + err.message);
  } finally {
    banner.style.display = 'none';
  }
}

// Render Results to Output Studio
function renderResults(data) {
  // 1. Render Screenplay
  const scriptContainer = document.getElementById('scriptContainer');
  const dialogueCount = document.getElementById('dialogueCount');
  scriptContainer.innerHTML = '';

  const dialogues = data.dialogues || [];
  dialogueCount.textContent = dialogues.length;

  if (dialogues.length === 0) {
    scriptContainer.innerHTML = '<div class="empty-state"><p>No dialogue lines detected in audio take.</p></div>';
  } else {
    dialogues.forEach(turn => {
      const turnEl = document.createElement('div');
      turnEl.className = 'dialogue-turn';

      let cuesHtml = '';
      if (turn.vocal_tone) {
        cuesHtml += `<span class="cue-chip">${escapeHtml(turn.vocal_tone)}</span>`;
      }
      if (turn.physical_cue) {
        cuesHtml += `<span class="cue-chip cue-action">${escapeHtml(turn.physical_cue)}</span>`;
      }

      turnEl.innerHTML = `
        <div class="turn-header">
          <div class="turn-speaker-group">
            <span class="turn-character-name">${escapeHtml(turn.character)}</span>
            <span class="turn-speaker-name">(${escapeHtml(turn.speaker)})</span>
          </div>
          ${turn.timestamp ? `<span class="turn-timestamp">${escapeHtml(turn.timestamp)}</span>` : ''}
        </div>
        ${cuesHtml ? `<div class="turn-cues">${cuesHtml}</div>` : ''}
        <div class="turn-dialogue-text">${escapeHtml(turn.dialogue)}</div>
      `;
      scriptContainer.appendChild(turnEl);
    });
  }

  // 2. Render Novel Prose Draft
  const proseContainer = document.getElementById('proseContainer');
  proseContainer.innerHTML = '';
  if (data.novel_prose_draft) {
    const proseEl = document.createElement('div');
    proseEl.className = 'prose-content';
    proseEl.textContent = data.novel_prose_draft;
    proseContainer.appendChild(proseEl);
  } else {
    proseContainer.innerHTML = '<div class="empty-state"><p>No novel prose draft available.</p></div>';
  }

  // 3. Render Scene Beats
  const beatsContainer = document.getElementById('beatsContainer');
  beatsContainer.innerHTML = '';
  const beats = data.scene_beats || [];
  if (beats.length === 0) {
    beatsContainer.innerHTML = '<div class="empty-state"><p>No scene beats generated.</p></div>';
  } else {
    beats.forEach(beat => {
      const beatEl = document.createElement('div');
      beatEl.className = 'beat-card';
      const tension = beat.dramatic_tension || 'Medium';
      beatEl.innerHTML = `
        <div class="beat-header">
          <span class="beat-title">Beat ${beat.beat_number}: ${escapeHtml(beat.title)}</span>
          <span class="tension-pill tension-${tension}">${tension}</span>
        </div>
        <div class="turn-dialogue-text">${escapeHtml(beat.description)}</div>
      `;
      beatsContainer.appendChild(beatEl);
    });
  }
}

// 15-Second Guided Voice Calibration
let calRecorder = null;
let calChunks = [];
let calTimer = null;

function setupCalibration(speakerId, buttonId, timerId, statusId) {
  const btn = document.getElementById(buttonId);
  const timer = document.getElementById(timerId);
  const status = document.getElementById(statusId);

  btn.addEventListener('click', async () => {
    if (btn.classList.contains('recording')) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      calChunks = [];
      calRecorder = new MediaRecorder(stream);
      calRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) calChunks.push(e.data);
      };

      calRecorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(calChunks, { type: 'audio/webm' });
        
        btn.classList.remove('recording');
        btn.innerHTML = '⚡ Uploading...';

        const speakerNameInput = speakerId === 'speaker_1' ? document.getElementById('spk1Name') : document.getElementById('spk2Name');
        const speakerName = speakerNameInput ? speakerNameInput.value.trim() : speakerId;

        const formData = new FormData();
        formData.append('speaker_id', speakerId);
        formData.append('speaker_name', speakerName);
        formData.append('audio', blob, `${speakerId}_calibration.webm`);

        try {
          const res = await fetch('/api/calibrate-voice', { method: 'POST', body: formData });
          if (res.ok) {
            status.textContent = 'Enrolled ✓';
            status.classList.add('enrolled');
            btn.innerHTML = '✓ Re-record Sample';
            checkServerStatus();
          } else {
            btn.innerHTML = '● Record 15s Sample';
            alert('Calibration upload failed');
          }
        } catch (e) {
          btn.innerHTML = '● Record 15s Sample';
          alert('Calibration error: ' + e.message);
        }
      };

      calRecorder.start();
      btn.classList.add('recording');
      btn.innerHTML = '⏹ Recording Voice...';

      let secondsLeft = 15;
      timer.textContent = `0:00 / 0:15`;

      calTimer = setInterval(() => {
        secondsLeft--;
        const elapsed = 15 - secondsLeft;
        timer.textContent = `0:${String(elapsed).padStart(2, '0')} / 0:15`;

        if (secondsLeft <= 0) {
          clearInterval(calTimer);
          if (calRecorder && calRecorder.state === 'recording') {
            calRecorder.stop();
          }
        }
      }, 1000);

    } catch (err) {
      alert('Microphone access failed: ' + err.message);
    }
  });
}

// Check Server Status
async function checkServerStatus() {
  try {
    const res = await fetch('/api/status');
    if (!res.ok) return;
    const data = await res.json();

    const modelBadge = document.getElementById('modelBadge');
    if (modelBadge && data.model) {
      modelBadge.textContent = data.model;
    }

    const vaultIndicator = document.getElementById('vaultIndicator');
    if (vaultIndicator && (data.speaker_1_calibrated || data.speaker_2_calibrated)) {
      vaultIndicator.classList.add('calibrated');
    }

    const cal1Status = document.getElementById('calSpk1Status');
    const cal2Status = document.getElementById('calSpk2Status');
    if (cal1Status && data.speaker_1_calibrated) {
      cal1Status.textContent = 'Enrolled ✓';
      cal1Status.classList.add('enrolled');
    }
    if (cal2Status && data.speaker_2_calibrated) {
      cal2Status.textContent = 'Enrolled ✓';
      cal2Status.classList.add('enrolled');
    }
  } catch (e) {
    console.warn('Status check failed:', e);
  }
}

// Fetch Mobile LAN URL
async function fetchMobileUrl() {
  try {
    const res = await fetch('/api/network-ip');
    if (res.ok) {
      const data = await res.json();
      const ipText = document.getElementById('networkIpText');
      const modalUrl = document.getElementById('modalMobileUrl');
      if (ipText) ipText.textContent = `${data.local_ip}:${data.port}`;
      if (modalUrl) modalUrl.textContent = data.mobile_url;
    }
  } catch (e) {
    console.warn('Network IP check failed:', e);
  }
}

// Clipboard Helpers
function copyToClipboard(text, btnElement, successMsg) {
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    const originalText = btnElement.textContent;
    btnElement.textContent = successMsg;
    setTimeout(() => btnElement.textContent = originalText, 2000);
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Initialization & Event Listeners
document.addEventListener('DOMContentLoaded', async () => {
  await initIndexedDB();
  checkServerStatus();
  fetchMobileUrl();

  // Recording Controls
  document.getElementById('recordBtn').addEventListener('click', startRecording);
  document.getElementById('pauseBtn').addEventListener('click', pauseRecording);
  document.getElementById('finishBtn').addEventListener('click', finishAndScribe);

  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      document.getElementById(tabId).classList.add('active');
    });
  });

  // Modals
  const calModal = document.getElementById('calibrationModal');
  document.getElementById('calibrationVaultBtn').addEventListener('click', () => {
    // Sync speaker names to badges
    document.getElementById('calSpk1Badge').textContent = document.getElementById('spk1Name').value.trim() || 'SPEAKER 1';
    document.getElementById('calSpk2Badge').textContent = document.getElementById('spk2Name').value.trim() || 'SPEAKER 2';
    calModal.style.display = 'flex';
  });
  document.getElementById('closeModalBtn').addEventListener('click', () => calModal.style.display = 'none');

  const netModal = document.getElementById('networkModal');
  document.getElementById('networkShareBtn').addEventListener('click', () => netModal.style.display = 'flex');
  document.getElementById('closeNetworkModalBtn').addEventListener('click', () => netModal.style.display = 'none');

  document.getElementById('copyUrlBtn').addEventListener('click', (e) => {
    const url = document.getElementById('modalMobileUrl').textContent;
    copyToClipboard(url, e.target, '✓ Copied URL!');
  });

  // Copy Buttons for Studio
  document.getElementById('copyScriptBtn').addEventListener('click', (e) => {
    const text = Array.from(document.querySelectorAll('.dialogue-turn')).map(el => {
      const char = el.querySelector('.turn-character-name')?.textContent || '';
      const spk = el.querySelector('.turn-speaker-name')?.textContent || '';
      const dialogue = el.querySelector('.turn-dialogue-text')?.textContent || '';
      return `${char} ${spk}: "${dialogue}"`;
    }).join('\n\n');
    copyToClipboard(text, e.target, '✓ Script Copied!');
  });

  document.getElementById('copyProseBtn').addEventListener('click', (e) => {
    const text = document.querySelector('.prose-content')?.textContent || '';
    copyToClipboard(text, e.target, '✓ Prose Copied!');
  });

  document.getElementById('copyBeatsBtn').addEventListener('click', (e) => {
    const text = Array.from(document.querySelectorAll('.beat-card')).map(el => el.textContent.trim()).join('\n\n');
    copyToClipboard(text, e.target, '✓ Beats Copied!');
  });

  // Calibration Recorders
  setupCalibration('speaker_1', 'calRecBtn1', 'calTimer1', 'calSpk1Status');
  setupCalibration('speaker_2', 'calRecBtn2', 'calTimer2', 'calSpk2Status');
});
