/**
 * ARC SCRIBE • Pure Voice Instrument & Audio Scribe Engine (v5.0.0)
 * Real-Time Streaming Server Telemetry • Synchronized Audio Player • Inline Editing & History
 */

// Global State
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
};

// ==========================================================================
// 1. REAL-TIME SERVER STREAMING TELEMETRY INGESTION
// ==========================================================================
class TelemetryStreamConsumer {
  constructor(options = {}) {
    this.endpoint = options.endpoint || '/api/process-audio-stream';
    this.onTelemetry = options.onTelemetry || (() => {});
    this.onResult = options.onResult || (() => {});
    this.onError = options.onError || (() => {});
    this.abortController = null;
  }

  async processAudio(audioBlob, metadata = {}) {
    this.abort();
    this.abortController = new AbortController();

    const formData = new FormData();
    formData.append('audio', audioBlob, 'dialogue_enactment.webm');
    formData.append('arc_title', metadata.arcTitle || 'Raw Voice Session');
    formData.append('speaker_1_name', metadata.speaker1Name || 'Speaker 1');
    formData.append('speaker_2_name', metadata.speaker2Name || 'Speaker 2');

    try {
      const response = await fetch(this.endpoint, {
        method: 'POST',
        body: formData,
        signal: this.abortController.signal
      });

      if (!response.ok) {
        let errorDetail = `HTTP ${response.status} ${response.statusText}`;
        try {
          const errJson = await response.json();
          errorDetail = errJson.detail || errorDetail;
        } catch (_) {
          const errText = await response.text();
          if (errText) errorDetail = errText;
        }
        throw new Error(errorDetail);
      }

      if (!response.body) {
        throw new Error('ReadableStream not supported by browser environment.');
      }

      await this.readNDJSONStream(response.body);

    } catch (err) {
      if (err.name === 'AbortError') return;
      this.onError(err);
    } finally {
      this.abortController = null;
    }
  }

  async readNDJSONStream(stream) {
    const reader = stream.getReader();
    const decoder = new TextDecoder('utf-8');
    let lineBuffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        lineBuffer += decoder.decode(value, { stream: true });
        const lines = lineBuffer.split('\n');
        lineBuffer = lines.pop(); // Retain incomplete fragment

        for (const rawLine of lines) {
          const line = rawLine.trim();
          if (!line) continue;
          this.routePayload(line);
        }
      }

      lineBuffer += decoder.decode();
      if (lineBuffer.trim()) {
        this.routePayload(lineBuffer.trim());
      }
    } finally {
      reader.releaseLock();
    }
  }

  routePayload(jsonString) {
    try {
      const payload = JSON.parse(jsonString);

      switch (payload.type) {
        case 'telemetry':
          this.onTelemetry({
            step: payload.step || 1,
            totalSteps: payload.total_steps || 4,
            pct: payload.pct || 0,
            msg: payload.msg || ''
          });
          break;

        case 'result':
          this.onResult(payload.data || payload);
          break;

        case 'error':
          this.onError(new Error(payload.msg || 'Processing error encountered on server'));
          break;

        default:
          console.warn('Unknown streaming event payload:', payload);
      }
    } catch (parseErr) {
      console.error('Failed to parse NDJSON frame:', jsonString, parseErr);
    }
  }

  abort() {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }
}

// ==========================================================================
// 2. SYNCHRONIZED AUDIO PLAYER, DIALOGUE SCRUBBER & INLINE EDITING
// ==========================================================================
class AudioDialogueController {
  constructor() {
    this.audioEl = document.getElementById('sessionAudioElement');
    this.playToggleBtn = document.getElementById('audioPlayToggleBtn');
    this.playToggleIcon = document.getElementById('playToggleIcon');
    this.progressRail = document.getElementById('audioProgressRail');
    this.progressFill = document.getElementById('audioProgressFill');
    this.timeDisplay = document.getElementById('audioTimeDisplay');
    this.streamContainer = document.getElementById('scriptStream');

    this.currentSession = null;
    this.turns = [];
    this.activeTurnIndex = -1;
    this.isScrubbing = false;
    this.currentBlobUrl = null;

    this.bindPlayerEvents();
    this.bindScrubberEvents();
  }

  static parseTimestampToSeconds(ts) {
    if (typeof ts === 'number') return ts;
    if (!ts || typeof ts !== 'string') return 0;
    const parts = ts.trim().split(':').map(Number);
    if (parts.some(isNaN)) return 0;
    if (parts.length === 1) return parts[0];
    if (parts.length === 2) return parts[0] * 60 + parts[1];
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
    return 0;
  }

  static formatSeconds(seconds) {
    if (isNaN(seconds) || seconds < 0 || !isFinite(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  loadSession(sessionData, audioBlob = null) {
    this.currentSession = sessionData;
    this.activeTurnIndex = -1;

    if (this.currentBlobUrl) {
      URL.revokeObjectURL(this.currentBlobUrl);
      this.currentBlobUrl = null;
    }

    const rawTurns = sessionData.dialogue_script || sessionData.dialogues || [];
    this.turns = rawTurns.map((turn, idx) => ({
      ...turn,
      index: idx,
      startSeconds: AudioDialogueController.parseTimestampToSeconds(turn.timestamp)
    }));

    if (audioBlob) {
      this.currentBlobUrl = URL.createObjectURL(audioBlob);
      this.audioEl.src = this.currentBlobUrl;
    } else if (sessionData.audio_url) {
      this.audioEl.src = sessionData.audio_url;
    } else if (sessionData.raw_audio_filename) {
      this.audioEl.src = `/api/recordings/${sessionData.raw_audio_filename}`;
    }

    this.audioEl.load();
    this.updateProgress(0, 0);
    this.renderCards();
    this.updateSpeakerCounts();
  }

  bindPlayerEvents() {
    this.playToggleBtn.addEventListener('click', () => this.togglePlay());
    this.audioEl.addEventListener('play', () => this.updatePlayIcon(true));
    this.audioEl.addEventListener('pause', () => this.updatePlayIcon(false));
    this.audioEl.addEventListener('ended', () => {
      this.updatePlayIcon(false);
      this.clearActiveHighlight();
      this.updateProgress(0, this.audioEl.duration || 0);
    });

    this.audioEl.addEventListener('timeupdate', () => {
      if (!this.isScrubbing) {
        this.updateProgress(this.audioEl.currentTime, this.audioEl.duration);
        this.syncActiveDialogue(this.audioEl.currentTime);
      }
    });

    this.audioEl.addEventListener('loadedmetadata', () => {
      this.updateProgress(0, this.audioEl.duration);
    });
  }

  togglePlay() {
    if (this.audioEl.paused) {
      this.audioEl.play().catch(e => console.warn('Audio playback error:', e));
    } else {
      this.audioEl.pause();
    }
  }

  updatePlayIcon(isPlaying) {
    if (isPlaying) {
      this.playToggleIcon.innerHTML = `
        <rect x="6" y="4" width="4" height="16"></rect>
        <rect x="14" y="4" width="4" height="16"></rect>
      `;
    } else {
      this.playToggleIcon.innerHTML = `
        <polygon points="5 3 19 12 5 21 5 3"></polygon>
      `;
    }
  }

  updateProgress(currentTime, duration) {
    const validDuration = (duration && isFinite(duration) && duration > 0) ? duration : 0;
    const pct = validDuration > 0 ? (currentTime / validDuration) * 100 : 0;
    this.progressFill.style.width = `${Math.min(100, Math.max(0, pct))}%`;
    this.timeDisplay.textContent = `${AudioDialogueController.formatSeconds(currentTime)} / ${AudioDialogueController.formatSeconds(validDuration)}`;
  }

  bindScrubberEvents() {
    const handleScrub = (e) => {
      const rect = this.progressRail.getBoundingClientRect();
      const pos = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
      const ratio = rect.width > 0 ? pos / rect.width : 0;
      const duration = this.audioEl.duration;

      if (duration && isFinite(duration)) {
        const targetTime = ratio * duration;
        this.audioEl.currentTime = targetTime;
        this.updateProgress(targetTime, duration);
        this.syncActiveDialogue(targetTime);
      }
    };

    this.progressRail.addEventListener('pointerdown', (e) => {
      this.isScrubbing = true;
      this.progressRail.setPointerCapture(e.pointerId);
      handleScrub(e);
    });

    this.progressRail.addEventListener('pointermove', (e) => {
      if (this.isScrubbing) handleScrub(e);
    });

    const finishScrub = (e) => {
      if (this.isScrubbing) {
        this.isScrubbing = false;
        try { this.progressRail.releasePointerCapture(e.pointerId); } catch (_) {}
      }
    };

    this.progressRail.addEventListener('pointerup', finishScrub);
    this.progressRail.addEventListener('pointercancel', finishScrub);
  }

  calculateActiveTurnIndex(currentTime) {
    if (!this.turns || this.turns.length === 0) return -1;
    if (currentTime < this.turns[0].startSeconds) return -1;

    for (let i = this.turns.length - 1; i >= 0; i--) {
      if (currentTime >= this.turns[i].startSeconds) return i;
    }
    return -1;
  }

  syncActiveDialogue(currentTime) {
    const nextIndex = this.calculateActiveTurnIndex(currentTime);
    if (nextIndex === this.activeTurnIndex) return;

    this.clearActiveHighlight();
    this.activeTurnIndex = nextIndex;

    if (this.activeTurnIndex !== -1) {
      const targetCard = this.streamContainer.querySelector(`.stream-card[data-index="${this.activeTurnIndex}"]`);
      if (targetCard) {
        targetCard.classList.add('is-active', 'playing');
        targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }

  clearActiveHighlight() {
    if (this.activeTurnIndex !== -1) {
      const oldCard = this.streamContainer.querySelector(`.stream-card[data-index="${this.activeTurnIndex}"]`);
      if (oldCard) oldCard.classList.remove('is-active', 'playing');
      this.activeTurnIndex = -1;
    }
  }

  seekToTurn(index) {
    const turn = this.turns[index];
    if (!turn) return;
    this.audioEl.currentTime = turn.startSeconds;
    this.updateProgress(turn.startSeconds, this.audioEl.duration || 0);
    this.syncActiveDialogue(turn.startSeconds);
    if (this.audioEl.paused) {
      this.audioEl.play().catch(e => console.warn('Autoplay error:', e));
    }
  }

  renderCards() {
    this.streamContainer.innerHTML = '';
    if (!this.turns || this.turns.length === 0) {
      this.streamContainer.innerHTML = '<div class="stream-card"><p class="dialogue-text-body">No dialogue turns detected in session take.</p></div>';
      return;
    }

    this.turns.forEach((turn, idx) => {
      const isSpeaker1 = turn.speaker_id === 'speaker_1' || (turn.speaker || '').toLowerCase().includes('speaker 1') || (turn.speaker || '').toLowerCase().includes('author 1');
      const card = document.createElement('div');
      card.className = `stream-card ${isSpeaker1 ? 'spk-1' : 'spk-2'}`;
      card.dataset.index = idx;

      const speakerName = turn.speaker || (isSpeaker1 ? 'Speaker 1' : 'Speaker 2');
      const tone = turn.vocal_tone ? `[${turn.vocal_tone}]` : '';
      const timestamp = turn.timestamp || '0:00';

      card.innerHTML = `
        <div class="card-top-row">
          <div class="card-speaker-meta">
            <span class="speaker-badge-text">${this.escapeHtml(speakerName)}</span>
            ${tone ? `<span class="tone-pill-tag">${this.escapeHtml(tone)}</span>` : ''}
            <span class="tone-pill-tag timestamp-badge" style="font-style: normal; cursor: pointer;" title="Jump audio to this timestamp">${this.escapeHtml(timestamp)}</span>
          </div>
          <div class="card-tools">
            <button class="icon-action-btn play-turn-btn" title="Play from this point">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
            </button>
            <button class="icon-action-btn edit-turn-btn" title="Edit dialogue text">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </button>
            <button class="icon-action-btn delete-btn delete-turn-btn" title="Delete this line">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>
        <div class="dialogue-text-body">${this.escapeHtml(turn.text || '')}</div>
      `;

      card.querySelector('.play-turn-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        this.seekToTurn(idx);
      });

      card.querySelector('.timestamp-badge').addEventListener('click', (e) => {
        e.stopPropagation();
        this.seekToTurn(idx);
      });

      card.querySelector('.delete-turn-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        this.deleteTurn(idx);
      });

      const editBtn = card.querySelector('.edit-turn-btn');
      const textBody = card.querySelector('.dialogue-text-body');
      const startEditing = () => this.openInlineEditor(card, idx, turn);

      editBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        startEditing();
      });
      textBody.addEventListener('dblclick', () => startEditing());

      this.streamContainer.appendChild(card);
    });
  }

  deleteTurn(index) {
    this.turns.splice(index, 1);
    this.turns.forEach((t, i) => t.index = i);
    this.currentSession.dialogue_script = this.turns;
    this.renderCards();
    this.updateSpeakerCounts();
    this.persistCurrentSession();
  }

  openInlineEditor(cardEl, index, turn) {
    if (cardEl.querySelector('.inline-edit-box')) return;

    const textBody = cardEl.querySelector('.dialogue-text-body');
    const previousText = turn.text || '';
    textBody.style.display = 'none';

    const editBox = document.createElement('div');
    editBox.className = 'inline-edit-box';
    editBox.innerHTML = `
      <textarea class="inline-edit-textarea" rows="3">${this.escapeHtml(previousText)}</textarea>
      <div class="inline-edit-actions">
        <button class="inline-cancel-btn" type="button">Cancel</button>
        <button class="inline-save-btn" type="button">Save</button>
      </div>
    `;

    cardEl.appendChild(editBox);
    const textarea = editBox.querySelector('.inline-edit-textarea');
    textarea.focus();
    textarea.setSelectionRange(textarea.value.length, textarea.value.length);

    const closeEditor = () => {
      editBox.remove();
      textBody.style.display = 'block';
    };

    const saveChanges = async () => {
      const updatedText = textarea.value.trim();
      turn.text = updatedText;
      textBody.textContent = updatedText;
      closeEditor();

      if (this.currentSession.dialogue_script) {
        this.currentSession.dialogue_script[index].text = updatedText;
      }
      this.updateSpeakerCounts();
      await this.persistCurrentSession();
    };

    editBox.querySelector('.inline-cancel-btn').addEventListener('click', closeEditor);
    editBox.querySelector('.inline-save-btn').addEventListener('click', saveChanges);

    textarea.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        saveChanges();
      } else if (e.key === 'Escape') {
        closeEditor();
      }
    });
  }

  async persistCurrentSession() {
    if (this.currentSession && this.currentSession.id) {
      try {
        await fetch(`/api/history/${encodeURIComponent(this.currentSession.id)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.currentSession)
        });
      } catch (err) {
        console.warn('Dialogue persistence warning:', err);
      }
    }
  }

  updateSpeakerCounts() {
    const spk1El = document.getElementById('statSpeaker1Count');
    const spk2El = document.getElementById('statSpeaker2Count');
    if (!spk1El && !spk2El) return;

    let spk1Count = 0;
    let spk2Count = 0;

    for (const turn of this.turns) {
      const isSpk1 = turn.speaker_id === 'speaker_1' || (turn.speaker || '').toLowerCase().includes('speaker 1') || (turn.speaker || '').toLowerCase().includes('author 1');
      if (isSpk1) spk1Count++;
      else spk2Count++;
    }

    if (spk1El) spk1El.textContent = `${spk1Count} ${spk1Count === 1 ? 'line' : 'lines'}`;
    if (spk2El) spk2El.textContent = `${spk2Count} ${spk2Count === 1 ? 'line' : 'lines'}`;
  }

  copyScriptToClipboard(buttonEl = null) {
    if (!this.turns || this.turns.length === 0) return;

    const transcript = this.turns.map(turn => {
      const tone = turn.vocal_tone ? ` [${turn.vocal_tone}]` : '';
      const ts = turn.timestamp ? ` (${turn.timestamp})` : '';
      return `${turn.speaker || 'Speaker'}${ts}${tone}:\n${turn.text || ''}`;
    }).join('\n\n');

    navigator.clipboard.writeText(transcript).then(() => {
      if (buttonEl) {
        const originalHtml = buttonEl.innerHTML;
        buttonEl.innerHTML = '<span>✓ Copied Script!</span>';
        setTimeout(() => { buttonEl.innerHTML = originalHtml; }, 2000);
      }
    });
  }

  exportMarkdownFile() {
    if (!this.turns || this.turns.length === 0) return;

    const sessionTitle = this.currentSession?.id?.replace(/\.json$/, '') || 'Arc_Scribe_Dialogue';
    const processedAt = this.currentSession?.processed_at || new Date().toISOString();
    const rawAudio = this.currentSession?.raw_audio_filename || 'Enactment take';

    let md = `# Arc Scribe • Dialogue Master\n`;
    md += `**Take:** \`${sessionTitle}\`  \n`;
    md += `**Audio Source:** \`${rawAudio}\`  \n`;
    md += `**Recorded At:** ${processedAt}  \n\n`;
    md += `---\n\n`;

    this.turns.forEach(turn => {
      const spk = turn.speaker || 'Speaker';
      const tone = turn.vocal_tone ? ` *(${turn.vocal_tone})*` : '';
      const ts = turn.timestamp ? `\`${turn.timestamp}\`` : '';
      md += `### ${spk} ${ts}${tone}\n\n`;
      md += `${turn.text || ''}\n\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${sessionTitle}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  async deleteCurrentTake() {
    if (!this.currentSession || !this.currentSession.id) return;
    if (!confirm('Are you sure you want to delete this recorded take and audio?')) return;

    try {
      await fetch(`/api/history/${encodeURIComponent(this.currentSession.id)}`, {
        method: 'DELETE'
      });
      returnToRecordNext();
      loadHistoryList();
    } catch (e) {
      alert('Delete failed: ' + e.message);
    }
  }

  escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }
}

// Instantiate Controllers
const audioController = new AudioDialogueController();

const streamConsumer = new TelemetryStreamConsumer({
  endpoint: '/api/process-audio-stream',
  onTelemetry: ({ step, totalSteps, pct, msg }) => {
    updateTelemetry(`STEP ${step}/${totalSteps}`, pct, msg);
  },
  onResult: (resultData) => {
    updateTelemetry('COMPLETE', 100, 'Formatting raw dialogue transcript...');
    setTimeout(() => {
      document.getElementById('recordingSection').style.display = 'none';
      document.getElementById('scriptSection').style.display = 'grid';
      document.getElementById('sessionTakeId').textContent = resultData.id || 'Current Take';

      audioController.loadSession(resultData, InstrumentState.currentAudioBlob);
      loadHistoryList();
    }, 350);
  },
  onError: (error) => {
    console.error('Streaming analysis error:', error);
    alert('Analysis failed: ' + error.message);
    document.getElementById('processingState').style.display = 'none';
    document.getElementById('analyzeStation').style.display = 'flex';
    document.getElementById('statePill').textContent = 'READY TO ANALYZE';
  }
});

function updateTelemetry(stepText, percent, statusMsg) {
  const stepEl = document.getElementById('telemetryStep');
  const percentEl = document.getElementById('telemetryPercent');
  const fillEl = document.getElementById('progressBarFill');
  const msgEl = document.getElementById('processingStatusMsg');
  if (stepEl) stepEl.textContent = stepText;
  if (percentEl) percentEl.textContent = `${percent}%`;
  if (fillEl) fillEl.style.width = `${percent}%`;
  if (msgEl) msgEl.textContent = statusMsg;
}

// ==========================================================================
// 3. AUDIO VISUALIZER & RECORDING ENGINE
// ==========================================================================
function initWaveformVisualizer(stream) {
  const canvas = document.getElementById('waveformCanvas');
  const canvasCtx = canvas.getContext('2d');
  
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

      const gradient = canvasCtx.createLinearGradient(0, centerY - barHeight, 0, centerY + barHeight);
      if (i < bufferLength / 2) {
        gradient.addColorStop(0, '#F59E0B');
        gradient.addColorStop(1, 'rgba(245, 158, 11, 0.2)');
      } else {
        gradient.addColorStop(0, '#A78BFA');
        gradient.addColorStop(1, 'rgba(167, 139, 250, 0.2)');
      }

      canvasCtx.fillStyle = gradient;
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

    InstrumentState.mediaRecorder.start(1000);
    InstrumentState.isRecording = true;
    InstrumentState.isPaused = false;
    InstrumentState.recordingStartTime = Date.now();

    startTimer();

    document.getElementById('recordingSection').classList.add('recording-live');
    document.getElementById('recordTriggerWrap').style.display = 'none';
    document.getElementById('activeControls').style.display = 'flex';
    document.getElementById('analyzeStation').style.display = 'none';
    document.getElementById('processingState').style.display = 'none';
    document.getElementById('statePill').textContent = 'RECORDING LIVE';
  } catch (err) {
    console.error('Microphone access failed:', err);
    alert('Microphone permission required: ' + err.message);
  }
}

function pauseRecording() {
  if (!InstrumentState.mediaRecorder || !InstrumentState.isRecording) return;

  if (!InstrumentState.isPaused) {
    InstrumentState.mediaRecorder.pause();
    InstrumentState.isPaused = true;
    document.getElementById('pauseLabel').textContent = 'RESUME';
    document.getElementById('statePill').textContent = 'PAUSED';
  } else {
    InstrumentState.mediaRecorder.resume();
    InstrumentState.isPaused = false;
    document.getElementById('pauseLabel').textContent = 'PAUSE';
    document.getElementById('statePill').textContent = 'RECORDING LIVE';
  }
}

function stopRecording() {
  if (!InstrumentState.mediaRecorder) return;

  InstrumentState.mediaRecorder.onstop = () => {
    const mime = InstrumentState.mediaRecorder.mimeType || 'audio/webm';
    InstrumentState.currentAudioBlob = new Blob(InstrumentState.recordedChunks, { type: mime });
    
    if (InstrumentState.audioStream) {
      InstrumentState.audioStream.getTracks().forEach(t => t.stop());
    }
    stopWaveformVisualizer();
    releaseScreenWakeLock();
    clearInterval(InstrumentState.timerInterval);

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

async function triggerLiveAnalysis() {
  if (!InstrumentState.currentAudioBlob) return;

  document.getElementById('analyzeStation').style.display = 'none';
  document.getElementById('processingState').style.display = 'flex';
  document.getElementById('statePill').textContent = 'AI ANALYZING...';

  updateTelemetry('STEP 1/4', 15, 'Preparing multi-band audio payload...');

  await streamConsumer.processAudio(InstrumentState.currentAudioBlob, {
    arcTitle: 'Raw Voice Session',
    speaker1Name: 'Speaker 1',
    speaker2Name: 'Speaker 2'
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

// ==========================================================================
// 4. HISTORY DRAWER MANAGEMENT
// ==========================================================================
async function loadHistoryList() {
  try {
    const res = await fetch('/api/history');
    if (!res.ok) return;
    const items = await res.json();
    
    const countBadge = document.getElementById('historyCountBadge');
    if (countBadge) countBadge.textContent = items.length;

    const listContainer = document.getElementById('historyList');
    listContainer.innerHTML = '';

    if (items.length === 0) {
      listContainer.innerHTML = '<p style="color: var(--text-muted); font-size: 0.8rem;">No past recorded takes yet.</p>';
      return;
    }

    items.forEach(item => {
      const card = document.createElement('div');
      card.className = 'history-item-card';

      const dateStr = item.processed_at ? new Date(item.processed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Saved Take';

      card.innerHTML = `
        <div class="history-item-top">
          <span class="history-item-date">${dateStr}</span>
          <span class="history-item-count">${item.dialogues_count || 0} lines</span>
        </div>
        <p class="history-item-preview">${item.preview || 'No dialogue preview'}</p>
      `;

      card.addEventListener('click', async () => {
        try {
          const detailRes = await fetch(`/api/history/${encodeURIComponent(item.id)}`);
          if (detailRes.ok) {
            const detailData = await detailRes.json();
            document.getElementById('historyDrawer').classList.remove('active');
            document.getElementById('historyOverlay').classList.remove('active');
            document.getElementById('recordingSection').style.display = 'none';
            document.getElementById('scriptSection').style.display = 'grid';
            document.getElementById('sessionTakeId').textContent = detailData.id || item.id;
            audioController.loadSession(detailData, null);
          }
        } catch (e) {
          console.error('History load error:', e);
        }
      });

      listContainer.appendChild(card);
    });
  } catch (err) {
    console.warn('History list fetch error:', err);
  }
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

// Calibration Status
async function checkCalibrationStatus() {
  try {
    const res = await fetch('/api/calibration/status');
    if (res.ok) {
      const data = await res.json();
      const badge = document.getElementById('calibrationBadge');
      const text = document.getElementById('calText');
      if (!badge || !text) return;
      if (data.fully_calibrated) {
        badge.className = 'cal-badge locked';
        text.textContent = 'ANCHORS LOCKED';
        badge.title = 'Speaker 1 and Speaker 2 acoustic baseline anchors verified';
      } else if (data.speaker_1_calibrated || data.speaker_2_calibrated) {
        badge.className = 'cal-badge';
        text.textContent = 'PARTIAL ANCHOR';
        badge.title = 'Single acoustic anchor locked; relative contrast active';
      } else {
        badge.className = 'cal-badge';
        text.textContent = 'UNCALIBRATED';
        badge.title = 'No anchors found. Using relative diarization';
      }
    }
  } catch (e) {
    console.warn('Calibration status fetch error:', e);
  }
}

// Event Bindings
document.addEventListener('DOMContentLoaded', () => {
  // Recording triggers
  document.getElementById('startRecordBtn').addEventListener('click', startRecording);
  document.getElementById('pauseRecordBtn').addEventListener('click', pauseRecording);
  document.getElementById('stopRecordBtn').addEventListener('click', stopRecording);
  document.getElementById('discardBtn').addEventListener('click', discardAndReset);
  document.getElementById('analyzeBtn').addEventListener('click', triggerLiveAnalysis);

  // Script actions
  document.getElementById('recordNextBtn').addEventListener('click', returnToRecordNext);
  document.getElementById('copyScriptBtn').addEventListener('click', (e) => {
    audioController.copyScriptToClipboard(e.currentTarget);
  });
  document.getElementById('downloadMarkdownBtn').addEventListener('click', () => {
    audioController.exportMarkdownFile();
  });
  document.getElementById('deleteCurrentTakeBtn').addEventListener('click', () => {
    audioController.deleteCurrentTake();
  });

  // History Drawer
  const historyDrawer = document.getElementById('historyDrawer');
  const historyOverlay = document.getElementById('historyOverlay');
  document.getElementById('openHistoryBtn').addEventListener('click', () => {
    historyDrawer.classList.add('active');
    historyOverlay.classList.add('active');
    loadHistoryList();
  });
  document.getElementById('closeHistoryBtn').addEventListener('click', () => {
    historyDrawer.classList.remove('active');
    historyOverlay.classList.remove('active');
  });
  historyOverlay.addEventListener('click', () => {
    historyDrawer.classList.remove('active');
    historyOverlay.classList.remove('active');
  });

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
    setTimeout(() => btn.textContent = 'Copy Network Link', 2000);
  });

  checkNetworkInfo();
  checkCalibrationStatus();
  loadHistoryList();
});
