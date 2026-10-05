"""Score a model answer: python3 score.py '["2023-03-08",...]'

Metric: penalty |reference position − answer position|;
if the date is not in the reference top 5, is a duplicate, or the position is empty — penalty 5. score = 1 − sum / 25.
"""
import json
import sys
from pathlib import Path

TOP_N = 5


def top_n_score(reference, answer, n):
    pos_ref = {x: i + 1 for i, x in enumerate(reference[:n])}
    seen, penalty = set(), 0
    for i in range(n):
        x = answer[i] if i < len(answer) else None
        penalty += abs(pos_ref[x] - (i + 1)) if x in pos_ref and x not in seen else n
        seen.add(x)
    return penalty, 1 - penalty / (n * n)


truth = json.loads((Path(__file__).parent / "answer.json").read_text())
answer = [str(d).strip() for d in json.loads(sys.argv[1])]
penalty, score = top_n_score(truth, answer, TOP_N)
print(f"reference: {json.dumps(truth, separators=(',', ':'))}")
print(f"answer:    {json.dumps(answer, separators=(',', ':'))}")
print(f"penalty {penalty}, score = {score:.3f}")
