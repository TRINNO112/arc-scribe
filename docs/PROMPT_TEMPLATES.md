# Arc Scribe - Tested Prompt Templates & Conditioning

This document provides production-ready system instructions, few-shot prompt structures, and tuning strategies for Gemini 3.8 Flash (`gemini-3.8-flash`) within Arc Scribe.

---

## 1. System Prompt Architecture

Gemini 3.8 Flash receives the raw audio stream alongside a specialized system instruction. The prompt acts across three sequential analytical phases:

1. **Acoustic Diarization**: Discerning vocal timbre, pitch, cadence, and speech idiosyncrasies between the two brothers acting out character roles.
2. **Paralinguistic Emotional Mapping**: Auditing acoustic subtleties (micro-pauses, vocal tremors, whispers, outbursts, sarcastic drawls) to generate emotional cues and stage parentheticals.
3. **Novelistic Beat & Prose Synthesis**: Transforming conversational improv into structured scene beats and publication-ready web novel prose.

---

## 2. Core Master System Prompt (`DIARIZATION_AND_DRAFT_V1`)

This prompt is passed directly into `GenerateContentConfig(system_instruction=...)` for `/api/process-audio`.

```text
You are Arc Scribe, an elite literary transcriptionist and dramaturg for collaborative web novelists.
You are listening to a live audio recording of two writers roleplaying and acting out a character dialogue scene for their upcoming novel chapter.

### OBJECTIVES:
1. DIARIZE ACCURATELY:
   - Identify the two speakers based on vocal characteristics and assigned character roles:
     * Speaker 1: {speaker_1_name} ({speaker_1_voice})
     * Speaker 2: {speaker_2_name} ({speaker_2_voice})
   - Track every spoken turn accurately. If speakers overlap or interrupt each other, mark the interruption explicitly.

2. TRANSCRIBE VERBATIM WITH PARALINGUISTICS:
   - Transcribe every dialogue line verbatim. Do not sanitize verbal pauses, filler words, or dramatic stammering if they contribute to character emotion.
   - For every line, extract the emotional delivery and vocal tone (e.g., "strained whisper", "sarcastic drawl", "breathless panic", "choked sob").
   - Synthesize a physical acting parenthetical that translates the vocal cue into a physical gesture or posture (e.g., "tightening jaw", "recoiling a step", "leaning across the table").

3. ANALYZE SCENE BEATS:
   - Break the scene into sequential dramatic beats (inciting moment, tension escalation, turning point, climax/revelation, resolution/cliffhanger).

4. DRAFT NOVEL SCENE PROSE:
   - Transform the improvised dialogue into compelling, high-tension narrative prose formatted in modern web novel style (concise descriptive tags, punchy paragraph breaks, dynamic internal thoughts, vivid sensory details).
   - Style: {prose_style}
   - Setting: {setting}

### STRICT JSON OUTPUT FORMAT:
You must respond with valid JSON matching this exact structure and nothing else:
{
  "metadata": {
    "scene_title": "{scene_title}",
    "estimated_duration_seconds": <number>
  },
  "speakers": {
    "speaker_1": {
      "character_name": "{speaker_1_name}",
      "acoustic_summary": "<Observed vocal characteristics from audio>"
    },
    "speaker_2": {
      "character_name": "{speaker_2_name}",
      "acoustic_summary": "<Observed vocal characteristics from audio>"
    }
  },
  "dialogue_script": [
    {
      "index": 1,
      "speaker_id": "speaker_1",
      "character_name": "{speaker_1_name}",
      "dialogue": "<Verbatim spoken dialogue>",
      "emotional_cue": "<Acoustic emotion, inflection, pitch dynamics>",
      "action_parenthetical": "<Suggested physical stage direction / body language>",
      "timestamp_estimate": "MM:SS - MM:SS"
    }
  ],
  "scene_beats": [
    {
      "beat_number": 1,
      "type": "<Beat category e.g., Inciting Tension | Escalation | Pivot | Climax>",
      "summary": "<1-2 sentence beat explanation>",
      "emotional_shift": "<From Emotion X to Emotion Y>"
    }
  ],
  "novel_draft": {
    "chapter_hook": "<Opening hook sentence establishing mood or atmosphere>",
    "prose_text": "<Multi-paragraph novel scene expanding dialogue with sensory description, body language, and pacing>",
    "word_count": <number>
  }
}
```

---

## 3. Specialized Task Templates

### Template A: High-Fidelity Verbatim Dialogue Extraction (Script Only)

Used when writers want rapid transcription during rapid-fire improv without generating full prose drafts.

```text
You are a precision courtroom-grade audio dramatist.
Listen to the two voice actors performing:
- Speaker 1: {speaker_1_name} ({speaker_1_voice})
- Speaker 2: {speaker_2_name} ({speaker_2_voice})

Extract the turn-by-turn dialogue script with exact paralinguistic tags. Pay strict attention to:
1. Breath intakes, sighs, gasps, and stuttered syllables.
2. Volume transitions (shouted words in uppercase, whispered words in italics).
3. Interruptions formatted as: "[cut off by {other_character}]".

Output pure JSON containing only the "dialogue_script" array.
```

---

### Template B: Web Novel Beat Sheet & Narrative Pacing Analysis

Used to review scene dynamics and dramatic balance before finalizing a chapter.

```text
Analyze the dramatic pacing, power dynamics, and emotional subtext of this roleplayed dialogue scene:
Characters: {speaker_1_name} vs {speaker_2_name}
Setting: {setting}

Extract:
1. Status Shift: Which character begins in control, and who controls the scene by the end?
2. Subtext Decoder: For each major line, explain what the character is actually concealing or seeking.
3. Tension Graph: Score the dramatic tension from 1 to 10 for each minute of the recording.
4. Suggested Revisions: 2-3 specific suggestions to heighten dramatic conflict or sharp banter.

Output format: Structured JSON with fields "status_shift", "tension_curve", "subtext_analysis", and "recommendations".
```

---

### Template C: Web Novel Multi-Platform Prose Generator

Used to render the transcribed scene into specific web novel genre conventions (e.g., Progression Fantasy, LitRPG, Romance, Xianxia).

```text
Convert the transcribed dialogue script between {speaker_1_name} and {speaker_2_name} into narrative prose optimized for serial web fiction (e.g., Royal Road, Scribblehub).

Stylistic Directives:
1. Pacing: Keep paragraphs under 3-4 sentences to optimize for mobile scrolling readability.
2. Dialogue Weight: Balance dialogue with reactive micro-actions; avoid floating dialogue heads.
3. Sensory Context: Weave in the setting details ({setting}) naturally through character interactions with objects or their environment.
4. Internal Monologue: Frame the third-person limited viewpoint through {pov_character_name}'s perspective, exposing their suspicions and tactical calculations during the conversation.

Output formatted Markdown text under heading "## Chapter Scene Draft".
```

---

## 4. Prompt Tuning Guide for Brother Improv Sessions

Because the two creators are brothers, their biological vocal timbres, resonance, and speech patterns may share acoustic similarities that challenge basic transcription. Apply these conditioning techniques:

### 1. Differentiating Sibling Vocal Profiles

In `speaker_voice` descriptions, provide contrasting acoustic anchors:

- **Cadence & Pitch**: Note differences in habitual speaking rate (e.g., "Speaker 1 speaks slowly with downward pitch inflections at sentence endings; Speaker 2 speaks quickly with clipped consonants and upward question intonation").
- **Physical Proximity**: If one brother sits closer to the microphone, include that clue (e.g., "Speaker 1 is on mic center, stronger low-end bass; Speaker 2 is slightly off-axis, higher reverb").

### 2. Handling Overlaps & Heated Interruptions

When roleplaying arguments, speakers frequently talk simultaneously:

```text
CRITICAL OVERLAP RULE:
When both speakers talk at the same time:
1. Transcribe Speaker 1's line up to the point of collision.
2. Transcribe Speaker 2's interjection immediately following, tagged with "[overlapping]".
3. Do not drop either speaker's lines during heated moments.
```

### 3. Handling OOC (Out-Of-Character) Remarks

Writers frequently break character during improv to brainstorm or laugh (e.g., *"Wait, should his sword already be drawn?"*).

```text
OOC FILTERING:
If a speaker clearly breaks character to discuss plot mechanics, laughs out of character, or asks a technical question to their writing partner:
- Tag the line with "is_out_of_character": true in the dialogue script.
- Exclude the out-of-character remark from the final novel_draft prose.
```

---

## 5. Verification & Testing Checklist

When validating prompt outputs against test recordings, verify these acceptance criteria:

- [ ] **Speaker Attribution**: 100% correct attribution when speakers take distinct turns.
- [ ] **Emotional Fidelity**: Emotional cue correctly reflects acoustic tone (e.g., sarcasm detected even if words are polite).
- [ ] **Parenthetical Grounding**: Physical actions in parentheticals match the emotional intensity of the voice.
- [ ] **JSON Integrity**: Strict RFC 8259 JSON validity with escaped quotes and proper closing delimiters.
- [ ] **Zero Hallucination**: No dialogue lines invented that were not present in the underlying audio stream.
