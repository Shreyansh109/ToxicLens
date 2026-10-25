"""Probes the model with hand-written sentences and identity-term templates.

These are small probes, not measurements. Run from the project root:
    python -m src.robustness_checks
"""
from pathlib import Path

import pandas as pd

from src.data_preprocessing import load_config
from src.predict import load_model, predict_texts

# (group, text, expected result). The expectations are a judgement, not ground truth.
CHALLENGE_SET = [
    ("slang, harmless", "This song absolutely slaps.", "non_toxic"),
    ("slang, harmless", "You're killing it at work lately!", "non_toxic"),
    ("slang, harmless", "That guitar solo was sick.", "non_toxic"),
    ("slang, harmless", "Damn, that sunset is gorgeous.", "non_toxic"),
    ("slang, harmless", "I'm dead, that meme is hilarious.", "non_toxic"),
    ("slang, harmless", "Bro you destroyed me in that game, well played.", "non_toxic"),

    ("misspellings", "you are such an id10t", "toxic"),
    ("misspellings", "u r so stup1d lol", "toxic"),
    ("misspellings", "go away you f*cking loser", "toxic"),
    ("misspellings", "shut up u moronn", "toxic"),
    ("misspellings", "thx 4 ur help, realy apreciate it", "non_toxic"),
    ("misspellings", "ur article edits r grate, thanx", "non_toxic"),

    ("ambiguous or quoted", "I hate Mondays.", "non_toxic"),
    ("ambiguous or quoted", "I hate it when my code doesn't compile.", "non_toxic"),
    ("ambiguous or quoted", "Calling someone an idiot is against the rules here.", "non_toxic"),
    ("ambiguous or quoted", "He said 'you are stupid' and I reported it.", "non_toxic"),
    ("ambiguous or quoted", "This plan is stupid and I disagree with it.", "non_toxic"),
    ("ambiguous or quoted", "I could kill for a coffee right now.", "non_toxic"),

    ("threats and violent words", "I'm going to kill you.", "toxic"),
    ("threats and violent words", "Watch your back, I know where you live.", "toxic"),
    ("threats and violent words", "I will destroy you at chess tonight.", "non_toxic"),
    ("threats and violent words", "If you come to my house again I'll hurt you.", "toxic"),

    ("romanised Hindi (limitation probe)", "tum bahut bekar insaan ho", "toxic"),
    ("romanised Hindi (limitation probe)", "bhai tu kamaal ka banda hai", "non_toxic"),
]

TEMPLATES = [
    "My neighbour is {}.",
    "I am {}.",
    "Many people at my school are {}.",
    "She is {} and works as a nurse.",
]
IDENTITY_TERMS = [
    "Muslim", "Christian", "Jewish", "Hindu", "Sikh", "Buddhist", "atheist",
    "black", "white", "Asian", "gay", "lesbian", "transgender", "straight",
    "disabled", "deaf", "blind", "old", "young",
]
CONTROL_TERMS = ["friendly", "tall", "busy", "tired"]


def run_challenge_set(pipeline, labels, config):
    texts = [text for _, text, _ in CHALLENGE_SET]
    results = predict_texts(texts, pipeline, labels, config)
    rows = []
    for (group, text, expected), res in zip(CHALLENGE_SET, results):
        rows.append({
            "group": group,
            "text": text,
            "expected": expected,
            "model": res["label"],
            "flagged": ", ".join(res["flagged_labels"]) or "none",
            "review": res["needs_human_review"],
            "match": res["label"] == expected,
        })
    return pd.DataFrame(rows)


def run_identity_probe(pipeline, labels, config):
    rows = []
    for group, terms in [("identity", IDENTITY_TERMS), ("control", CONTROL_TERMS)]:
        for term in terms:
            texts = [template.format(term) for template in TEMPLATES]
            results = predict_texts(texts, pipeline, labels, config)
            seen = sorted({l for r in results for l in r["flagged_labels"]})
            rows.append({
                "group": group,
                "term": term,
                "flagged_of_4": sum(r["label"] == "toxic" for r in results),
                "mean_toxic_score": sum(r["scores"]["toxic"] for r in results) / len(results),
                "labels_seen": ", ".join(seen) or "none",
            })
    table = pd.DataFrame(rows)
    return table.sort_values(["flagged_of_4", "mean_toxic_score"], ascending=False)


def main():
    config = load_config()
    pipeline, labels = load_model(config)
    reports_dir = Path(config["paths"].get("reports", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)

    challenge = run_challenge_set(pipeline, labels, config)
    for group, part in challenge.groupby("group", sort=False):
        print("=" * 70)
        print(f"{group}: {int(part['match'].sum())} of {len(part)} as expected")
        print("=" * 70)
        for _, r in part.iterrows():
            mark = "ok  " if r["match"] else "DIFF"
            print(f"[{mark}] {r['text']}")
            print(f"       expected: {r['expected']} | model: {r['model']} | "
                  f"flagged: {r['flagged']} | review: {r['review']}")
        print()
    print(f"Overall: {int(challenge['match'].sum())} of {len(challenge)} as expected")
    challenge.to_csv(reports_dir / "robustness_challenge_set.csv", index=False)

    identity = run_identity_probe(pipeline, labels, config)
    print()
    print("=" * 70)
    print("Identity-term probe (4 neutral sentences per term; a clean model flags none)")
    print("=" * 70)
    pd.set_option("display.width", 200)
    print(identity.round(3).to_string(index=False))
    identity.round(4).to_csv(reports_dir / "robustness_identity_probe.csv", index=False)
    print()
    print("Saved results to", reports_dir)


if __name__ == "__main__":
    main()