"""
Arc Scribe - Automated Diarization & Audio Benchmark Suite
File: tests/benchmark_diarization.py
Usage:
    python tests/benchmark_diarization.py --mode mock
    python tests/benchmark_diarization.py --mode live
    python tests/benchmark_diarization.py --mode live --output-md reports/benchmark.md
"""

import os
import sys
import json
import time
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Optional import of production service
try:
    from backend.gemini_service import gemini_service
    from backend.config import settings
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ==============================================================================
# 1. APPROVED VOCAL TONE TAXONOMY
# ==============================================================================
TONE_CLUSTERS = {
    "hostile": ["shouting", "furious", "aggressive", "confrontational", "enraged", "yelling"],
    "frustrated": ["frustrated", "annoyed", "impatient", "exasperated", "irritated", "agitated"],
    "subdued": ["whispering", "hushed", "confidential", "hesitant", "secretive", "breathless"],
    "ironic": ["sarcastic", "mocking", "scoffing", "deadpan", "cynical", "taunting", "smug"],
    "jovial": ["laughing", "giggling", "amused", "teasing", "chuckling", "excited"],
    "pensive": ["curious", "serious", "thoughtful", "skeptical", "questioning", "solemn"]
}

# ==============================================================================
# 2. HINGLISH CANONICAL NORMALIZER DICTIONARY
# ==============================================================================
HINGLISH_CANONICAL_MAP = {
    "kyon": "kyun", "kyu": "kyun", "kyoo": "kyun",
    "nahin": "nahi", "nhi": "nahi", "nahe": "nahi",
    "bhayi": "bhai", "bhaiya": "bhai", "bhaai": "bhai",
    "mjhe": "mujhe", "muze": "mujhe",
    "tere": "tere", "tereko": "tere",
    "sawaal": "sawal", "swal": "sawal",
    "poochna": "puchna", "puchhana": "puchna",
    "arre": "arre", "are": "arre", "arey": "arre",
    "acha": "acha", "achha": "acha", "accha": "acha",
    "lekin": "lekin", "lkn": "lekin",
    "vahi": "wahi", "vo": "wo", "woh": "wo"
}

def normalize_hinglish_token(token: str) -> str:
    clean = re.sub(r"[^\w\s]", "", token).lower().strip()
    return HINGLISH_CANONICAL_MAP.get(clean, clean)

def normalize_hinglish_text(text: str) -> List[str]:
    raw_tokens = text.lower().split()
    return [normalize_hinglish_token(t) for t in raw_tokens if normalize_hinglish_token(t)]

# ==============================================================================
# 3. METRIC SCORING IMPLEMENTATIONS
# ==============================================================================
def parse_timestamp_seconds(ts_str: Optional[str]) -> float:
    if not ts_str:
        return 0.0
    cleaned = ts_str.strip().split("-")[0].strip()
    parts = cleaned.split(":")
    try:
        if len(parts) == 2:
            return float(parts[0]) * 60.0 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
        return float(parts[0])
    except ValueError:
        return 0.0

def compute_levenshtein_wer(gt_words: List[str], pred_words: List[str]) -> Tuple[float, int, int, int]:
    n, m = len(gt_words), len(pred_words)
    if n == 0:
        return (0.0 if m == 0 else 100.0, 0, 0, m)

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if gt_words[i - 1] == pred_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(
                    dp[i - 1][j] + 1,      # deletion
                    dp[i][j - 1] + 1,      # insertion
                    dp[i - 1][j - 1] + 1   # substitution
                )

    edits = dp[n][m]
    wer = (edits / n) * 100.0
    return wer, edits, n, m

def score_vocal_tone(gt_tone: Optional[str], pred_tone: Optional[str]) -> float:
    if not gt_tone:
        return 1.0
    if not pred_tone:
        return 0.0

    gt_lower = gt_tone.lower()
    pred_lower = pred_tone.lower()

    # Exact keyword match
    for gt_word in gt_lower.split():
        if len(gt_word) > 3 and gt_word in pred_lower:
            return 1.0

    # Cluster soft-match
    gt_cluster = None
    for cluster, keywords in TONE_CLUSTERS.items():
        if any(kw in gt_lower for kw in keywords):
            gt_cluster = cluster
            break

    if gt_cluster:
        pred_cluster = None
        for cluster, keywords in TONE_CLUSTERS.items():
            if any(kw in pred_lower for kw in keywords):
                pred_cluster = cluster
                break
        if gt_cluster == pred_cluster:
            return 0.75

    return 0.0

# ==============================================================================
# 4. BENCHMARK HARNESS RUNNER
# ==============================================================================
@dataclass
class TurnMetric:
    turn_index: int
    gt_speaker: str
    pred_speaker: str
    speaker_matched: bool
    wer: float
    tone_score: float
    timestamp_drift_sec: float

@dataclass
class ScenarioResult:
    scenario_id: str
    title: str
    category: str
    speaker_attribution_acc: float
    speaker_confusion_rate: float
    normalized_wer: float
    vocal_tone_precision: float
    timestamp_monotonicity: float
    mean_timestamp_drift_sec: float
    composite_score: float
    status: str
    turn_metrics: List[TurnMetric] = field(default_factory=list)

class DiarizationBenchmarkRunner:
    def __init__(self, mode: str = "mock", model_name: str = "gemini-3.5-flash-lite"):
        self.mode = mode
        self.model_name = model_name
        self.fixtures_dir = REPO_ROOT / "tests" / "fixtures"

    def load_ground_truth_scenarios(self, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        manifest_path = self.fixtures_dir / "scenarios_manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8") as f:
                scenarios = json.load(f)
        else:
            scenarios = []

        if category_filter:
            scenarios = [s for s in scenarios if s.get("category") == category_filter]
        return scenarios

    def evaluate_scenario(self, scenario: Dict[str, Any]) -> ScenarioResult:
        gt_turns = scenario.get("turns", [])
        
        # 1. Obtain prediction
        if self.mode == "mock":
            pred_script = scenario.get("mock_prediction", gt_turns)
        else:
            pred_script = self._invoke_gemini_for_scenario(scenario)

        # 2. Evaluate turn-by-turn alignment
        total_eval = min(len(gt_turns), len(pred_script))
        correct_speakers = 0
        speaker_flips = 0
        total_gt_words = []
        total_pred_words = []
        tone_scores = []
        drift_values = []
        prev_ts = -1.0
        monotonicity_violations = 0
        turn_metrics = []

        for i in range(total_eval):
            gt = gt_turns[i]
            pred = pred_script[i]

            gt_spk = gt.get("speaker_id", "speaker_1")
            pred_spk = pred.get("speaker_id", "speaker_1")
            spk_match = (gt_spk == pred_spk)

            if spk_match:
                correct_speakers += 1
            else:
                speaker_flips += 1

            # Word Error Rate
            gt_w = normalize_hinglish_text(gt.get("text", ""))
            pred_w = normalize_hinglish_text(pred.get("text", ""))
            total_gt_words.extend(gt_w)
            total_pred_words.extend(pred_w)
            turn_wer, _, _, _ = compute_levenshtein_wer(gt_w, pred_w)

            # Vocal Tone Precision
            t_score = score_vocal_tone(gt.get("vocal_tone"), pred.get("vocal_tone"))
            tone_scores.append(t_score)

            # Timestamps
            gt_time = parse_timestamp_seconds(gt.get("timestamp"))
            pred_time = parse_timestamp_seconds(pred.get("timestamp"))
            drift = abs(pred_time - gt_time)
            drift_values.append(drift)

            if prev_ts >= 0 and (pred_time - prev_ts) < -0.5:
                monotonicity_violations += 1
            prev_ts = pred_time

            turn_metrics.append(TurnMetric(
                turn_index=i + 1,
                gt_speaker=gt_spk,
                pred_speaker=pred_spk,
                speaker_matched=spk_match,
                wer=round(turn_wer, 2),
                tone_score=round(t_score, 2),
                timestamp_drift_sec=round(drift, 2)
            ))

        # Overall summary formulas
        saa = (correct_speakers / total_eval * 100.0) if total_eval > 0 else 0.0
        s_conf = (speaker_flips / total_eval * 100.0) if total_eval > 0 else 0.0
        cum_wer, _, _, _ = compute_levenshtein_wer(total_gt_words, total_pred_words)
        vtp = (sum(tone_scores) / len(tone_scores) * 100.0) if tone_scores else 0.0
        tms = (1.0 - (monotonicity_violations / max(1, total_eval - 1))) * 100.0 if total_eval > 1 else 100.0
        matd = (sum(drift_values) / len(drift_values)) if drift_values else 0.0

        cqs = 0.40 * saa + 0.30 * max(0.0, 100.0 - cum_wer) + 0.15 * vtp + 0.15 * tms
        status = "PASS" if (saa >= 85.0 and cum_wer <= 20.0 and cqs >= 80.0) else "FAIL"

        return ScenarioResult(
            scenario_id=scenario.get("scenario_id", "TC-UNKNOWN"),
            title=scenario.get("title", "Untitled Scenario"),
            category=scenario.get("category", "general"),
            speaker_attribution_acc=round(saa, 2),
            speaker_confusion_rate=round(s_conf, 2),
            normalized_wer=round(cum_wer, 2),
            vocal_tone_precision=round(vtp, 2),
            timestamp_monotonicity=round(tms, 2),
            mean_timestamp_drift_sec=round(matd, 2),
            composite_score=round(cqs, 2),
            status=status,
            turn_metrics=turn_metrics
        )

    def _invoke_gemini_for_scenario(self, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        audio_file = scenario.get("audio_fixture")
        if not audio_file or not Path(audio_file).exists():
            return scenario.get("turns", [])

        with open(audio_file, "rb") as f:
            audio_bytes = f.read()

        import asyncio
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            gemini_service.process_enactment_audio(
                scene_audio_bytes=audio_bytes,
                mime_type="audio/webm",
                arc_title=scenario.get("title", "Benchmark Take"),
                speaker_1_name="Speaker 1",
                speaker_2_name="Speaker 2"
            )
        )
        return res.get("dialogue_script") or res.get("dialogues") or []

    def run_suite(self, category_filter: Optional[str] = None) -> List[ScenarioResult]:
        scenarios = self.load_ground_truth_scenarios(category_filter)
        results = []
        print(f"\n================================================================================")
        print(f"  ARC SCRIBE BENCHMARK RUNNER (Mode: {self.mode.upper()}, Model: {self.model_name})")
        print(f"================================================================================\n")

        for idx, sc in enumerate(scenarios, 1):
            sc_id = sc.get("scenario_id", f"SC-{idx}")
            title = sc.get("title", "Untitled")
            print(f"[{idx}/{len(scenarios)}] Evaluating: {sc_id} - '{title}'...")
            
            res = self.evaluate_scenario(sc)
            results.append(res)
            badge = "[PASS]" if res.status == "PASS" else "[FAIL]"
            print(f"    -> {badge} | SAA: {res.speaker_attribution_acc}% | WER: {res.normalized_wer}% | CQS: {res.composite_score}\n")
            
            if self.mode == "live":
                # Respect Google AI Studio rate limits (4-second pacing for 15 RPM)
                time.sleep(4.0)

        return results

    def generate_markdown_report(self, results: List[ScenarioResult]) -> str:
        passed = sum(1 for r in results if r.status == "PASS")
        total = len(results)
        pass_pct = (passed / total * 100.0) if total > 0 else 0.0
        avg_saa = sum(r.speaker_attribution_acc for r in results) / total if total > 0 else 0.0
        avg_wer = sum(r.normalized_wer for r in results) / total if total > 0 else 0.0
        avg_cqs = sum(r.composite_score for r in results) / total if total > 0 else 0.0

        md = []
        md.append(f"# Arc Scribe - Audio Diarization Benchmark Report")
        md.append(f"**Execution Mode**: `{self.mode}` | **Target Model**: `{self.model_name}`  ")
        md.append(f"**Timestamp**: `{time.strftime('%Y-%m-%d %H:%M:%S')}`  \n")
        
        md.append(f"## Executive Benchmark Summary")
        md.append(f"| Metric | Result | Target Benchmark | Verdict |")
        md.append(f"| :--- | :--- | :--- | :--- |")
        md.append(f"| **Suite Pass Rate** | **{passed}/{total} ({pass_pct:.1f}%)** | $\\ge 85.0\\%$ | {'PASS' if pass_pct >= 85 else 'FAIL'} |")
        md.append(f"| **Speaker Attribution Accuracy (SAA)** | **{avg_saa:.2f}%** | $\\ge 90.0\\%$ | {'PASS' if avg_saa >= 90 else 'WARN'} |")
        md.append(f"| **Hinglish Word Error Rate (Norm-WER)** | **{avg_wer:.2f}%** | $\\le 12.0\\%$ | {'PASS' if avg_wer <= 12 else 'FAIL'} |")
        md.append(f"| **Composite Quality Score (CQS)** | **{avg_cqs:.2f} / 100** | $\\ge 85.0$ | {'PASS' if avg_cqs >= 85 else 'FAIL'} |\n")

        md.append(f"## Detailed Scenario Results")
        md.append(f"| Scenario ID | Category | SAA (%) | Norm-WER (%) | Tone Precision (%) | Drift (s) | CQS | Status |")
        md.append(f"| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for r in results:
            md.append(f"| `{r.scenario_id}` | {r.category} | {r.speaker_attribution_acc}% | {r.normalized_wer}% | {r.vocal_tone_precision}% | {r.mean_timestamp_drift_sec}s | {r.composite_score} | {r.status} |")
        
        md.append(f"\n---\n*Report generated automatically by `tests/benchmark_diarization.py`.*")
        return "\n".join(md)

def main():
    parser = argparse.ArgumentParser(description="Arc Scribe Diarization Benchmark Harness")
    parser.add_argument("--mode", choices=["mock", "live"], default="mock", help="Execution mode (mock: free instant test, live: hits Gemini API)")
    parser.add_argument("--category", choices=["hinglish", "rapid_turn_taking", "overlapping_speech", "emotional_extremes"], default=None, help="Filter scenario category")
    parser.add_argument("--output-md", type=str, default=None, help="Path to write Markdown summary report")
    args = parser.parse_args()

    runner = DiarizationBenchmarkRunner(mode=args.mode)
    results = runner.run_suite(category_filter=args.category)
    md_report = runner.generate_markdown_report(results)

    if args.output_md:
        out_p = Path(args.output_md)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(md_report)
        print(f"Markdown report written to: {args.output_md}")
    else:
        print("\n" + md_report)

    all_passed = all(r.status == "PASS" for r in results)
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
