"""
run_validation.py
=================

End-to-end validation of LLM category assignments for the Battery Talent Census.

This script:
  1. Draws a systematic sample of 200 responses from the Census Skills keyword list
  2. Runs each through the LLM classification pipeline (src/llm.py)
  3. Compares LLM assignments against the human-reviewed ground truth
  4. Prints a summary report with agreement metrics
  5. Saves the comparison as a CSV (data/processed/portable/validation_comparison.csv)

Prerequisites:
  - OPENAI_API_KEY set in a .env file at the repo root
  - pip install openai python-dotenv

Usage:
  cd /path/to/battery-talent-census
  python run_validation.py

Cost estimate: ~$0.01-0.02 (200 calls to gpt-4o-mini)
"""

import pickle
import csv
import os
import sys

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

KEYWORD_FILE = "data/processed/strlist_census_skills_20250111_130145.pkl"
HUMAN_REVIEW_FILE = "data/processed/portable/validation_census_skills_reviewed.csv"
OUTPUT_FILE = "data/processed/portable/validation_comparison.csv"
REPORT_FILE = "data/processed/portable/validation_report.txt"
SAMPLE_STEP = 13
SAMPLE_SIZE = 200

CATEGORIES = [
    "Battery Chemistry / Electrochemistry",
    "Materials Science and Characterization",
    "Battery Design",
    "Battery Manufacturing / Scale-up / Process Engineering",
    "Battery Testing / Failure Analysis / Quality Control",
    "Battery Management Systems (BMS)",
    "Data Science / Data Analysis / AI / Machine Learning",
    "Modeling / Simulation / Computational Tools",
    "Electrical Engineering / Power Electronics",
    "Thermal Management",
    "Programming / Software Development",
    "Project Management / Leadership / Teamwork",
    "Communication / Presentation Skills / Language Skills",
    "Business Skills / Marketing / Strategy / Market Knowledge",
    "Supply Chain / Logistics / Procurement",
    "Innovation / Creativity / Problem Solving",
    "Safety / Standards / Regulations / Compliance",
    "Soft Skills (e.g., flexibility, adaptability, resilience)",
    "Environmental Knowledge / Sustainability / Recycling",
    "Interdisciplinary / Cross-functional Collaboration",
]


def _safe_div(num, den):
    return num / den if den else 0.0


def compute_classification_metrics(comparison):
    # Only use rows with a clear human label and a successful LLM classification.
    # This excludes ambiguous/invalid human judgments from all accuracy metrics.
    eval_rows = [
        row for row in comparison
        if row["match"] in {"agree", "disagree"}
    ]

    labels = list(CATEGORIES)
    confusion = {true_label: {pred_label: 0 for pred_label in labels} for true_label in labels}

    for row in eval_rows:
        true_label = row["human_category"]
        pred_label = row["llm_category"]
        if true_label in confusion and pred_label in confusion[true_label]:
            confusion[true_label][pred_label] += 1

    total_eval = len(eval_rows)
    correct = sum(confusion[label][label] for label in labels)
    accuracy = _safe_div(correct, total_eval)

    per_class = []
    macro_precision_sum = 0.0
    macro_recall_sum = 0.0
    macro_f1_sum = 0.0
    macro_count = 0

    weighted_precision_sum = 0.0
    weighted_recall_sum = 0.0
    weighted_f1_sum = 0.0

    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)
        support = sum(confusion[label][other] for other in labels)

        precision = _safe_div(tp, tp + fp)
        recall = _safe_div(tp, tp + fn)
        f1 = _safe_div(2 * precision * recall, precision + recall)

        if support > 0:
            macro_precision_sum += precision
            macro_recall_sum += recall
            macro_f1_sum += f1
            macro_count += 1

            weighted_precision_sum += precision * support
            weighted_recall_sum += recall * support
            weighted_f1_sum += f1 * support

        per_class.append({
            "label": label,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        })

    macro_precision = _safe_div(macro_precision_sum, macro_count)
    macro_recall = _safe_div(macro_recall_sum, macro_count)
    macro_f1 = _safe_div(macro_f1_sum, macro_count)

    weighted_precision = _safe_div(weighted_precision_sum, total_eval)
    weighted_recall = _safe_div(weighted_recall_sum, total_eval)
    weighted_f1 = _safe_div(weighted_f1_sum, total_eval)

    # For single-label multiclass classification, micro metrics collapse to accuracy.
    micro_precision = accuracy
    micro_recall = accuracy
    micro_f1 = accuracy

    return {
        "total_eval": total_eval,
        "excluded_rows": len(comparison) - total_eval,
        "correct": correct,
        "accuracy": accuracy,
        "micro_precision": micro_precision,
        "micro_recall": micro_recall,
        "micro_f1": micro_f1,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_precision,
        "weighted_recall": weighted_recall,
        "weighted_f1": weighted_f1,
        "per_class": per_class,
        "confusion": confusion,
        "labels": labels,
    }

# ---------------------------------------------------------------------------
# Step 1: Load sample
# ---------------------------------------------------------------------------

def load_sample():
    print(f"Loading keywords from {KEYWORD_FILE}...")
    with open(KEYWORD_FILE, "rb") as f:
        keyword_list = pickle.load(f)
    indices = list(range(0, len(keyword_list), SAMPLE_STEP))[:SAMPLE_SIZE]
    sample = [(i, keyword_list[i]) for i in indices]
    print(f"  {len(keyword_list)} total keywords, sampled {len(sample)} (every {SAMPLE_STEP}th)")
    return sample

# ---------------------------------------------------------------------------
# Step 2: Load human review
# ---------------------------------------------------------------------------

def load_human_review():
    print(f"Loading human review from {HUMAN_REVIEW_FILE}...")
    human = {}
    with open(HUMAN_REVIEW_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            human[row["response_text"]] = {
                "category": row["reviewer_assigned_category"],
                "judgment": row["judgment"],
                "note": row.get("note", ""),
            }
    print(f"  {len(human)} reviewed entries loaded")
    return human

# ---------------------------------------------------------------------------
# Step 3: Run LLM classification
# ---------------------------------------------------------------------------

def run_llm_classification(sample):
    from src.llm import LLM

    llm = LLM()
    results = []

    for i, (idx, keyword) in enumerate(sample):
        print(f"  [{i+1:3d}/200] Classifying '{keyword}'...", end=" ")
        try:
            output = llm.classify_user_response(CATEGORIES, keyword)
            cat = output["result"]["category"]
            print(f"-> {cat}")
            results.append({"index": idx, "response_text": keyword, "llm_category": cat})
        except Exception as e:
            print(f"-> FAILED ({e})")
            results.append({"index": idx, "response_text": keyword, "llm_category": "FAILED"})

    return results

# ---------------------------------------------------------------------------
# Step 4: Compare and report
# ---------------------------------------------------------------------------

def compare_and_report(llm_results, human_review):
    comparison = []
    agree = 0
    disagree = 0
    human_ambiguous = 0
    human_invalid = 0
    llm_failed = 0

    for row in llm_results:
        text = row["response_text"]
        llm_cat = row["llm_category"]
        human = human_review.get(text, {})
        human_cat = human.get("category", "")
        human_judgment = human.get("judgment", "")

        if llm_cat == "FAILED":
            match = "llm_failed"
            llm_failed += 1
        elif human_judgment == "ambiguous":
            match = "human_ambiguous"
            human_ambiguous += 1
        elif human_judgment == "invalid":
            match = "human_invalid"
            human_invalid += 1
        elif llm_cat == human_cat:
            match = "agree"
            agree += 1
        else:
            match = "disagree"
            disagree += 1

        comparison.append({
            "index": row["index"],
            "response_text": text,
            "llm_category": llm_cat,
            "human_category": human_cat,
            "human_judgment": human_judgment,
            "match": match,
            "note": human.get("note", ""),
        })

    # Compute metrics
    # Denominator: only responses where human assigned a clear category
    assignable = agree + disagree
    total = len(comparison)

    metrics = compute_classification_metrics(comparison)

    summary = {
        "total": total,
        "assignable": assignable,
        "agree": agree,
        "disagree": disagree,
        "human_ambiguous": human_ambiguous,
        "human_invalid": human_invalid,
        "llm_failed": llm_failed,
        "metrics": metrics,
    }

    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(f"  Total sampled responses:         {total}")
    print(f"  Human assigned (clear category): {assignable} ({100*assignable/total:.1f}%)")
    print(f"  Human flagged ambiguous:         {human_ambiguous} ({100*human_ambiguous/total:.1f}%)")
    print(f"  Human flagged invalid:           {human_invalid} ({100*human_invalid/total:.1f}%)")
    print(f"  LLM classification failed:       {llm_failed}")
    print()
    print(f"  LLM-Human Agreement (of {assignable} assignable):")
    if assignable > 0:
        print(f"    Agree:    {agree:4d} ({100*agree/assignable:.1f}%)")
        print(f"    Disagree: {disagree:4d} ({100*disagree/assignable:.1f}%)")
        print()
        print("  Classification metrics (filtered eval set only):")
        print("    Excludes human judgments marked ambiguous/invalid.")
        print(f"    Eval rows used:      {metrics['total_eval']} (excluded: {metrics['excluded_rows']})")
        print(f"    Accuracy:          {metrics['accuracy']:.4f}")
        print(f"    Micro P/R/F1:      {metrics['micro_precision']:.4f} / {metrics['micro_recall']:.4f} / {metrics['micro_f1']:.4f}")
        print(f"    Macro P/R/F1:      {metrics['macro_precision']:.4f} / {metrics['macro_recall']:.4f} / {metrics['macro_f1']:.4f}")
        print(f"    Weighted P/R/F1:   {metrics['weighted_precision']:.4f} / {metrics['weighted_recall']:.4f} / {metrics['weighted_f1']:.4f}")
    print()

    # Show disagreements
    disagreements = [c for c in comparison if c["match"] == "disagree"]
    if disagreements:
        print(f"  DISAGREEMENTS ({len(disagreements)}):")
        print(f"  {'Response':<40s} {'LLM':<30s} {'Human':<30s}")
        print(f"  {'-'*40} {'-'*30} {'-'*30}")
        for d in disagreements:
            rt = d["response_text"][:38]
            lc = d["llm_category"][:28]
            hc = d["human_category"][:28]
            print(f"  {rt:<40s} {lc:<30s} {hc:<30s}")
    print()
    print("=" * 70)

    return comparison, summary

# ---------------------------------------------------------------------------
# Step 5: Save output
# ---------------------------------------------------------------------------

def save_comparison(comparison):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "index", "response_text", "llm_category",
                "human_category", "human_judgment", "match", "note",
            ],
        )
        writer.writeheader()
        writer.writerows(comparison)
    print(f"Comparison saved to {OUTPUT_FILE}")


def save_text_report(comparison, summary):
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    disagreements = [c for c in comparison if c["match"] == "disagree"]
    disagreement_examples = sorted(disagreements, key=lambda d: int(d["index"]))[:10]

    with open(REPORT_FILE, "w") as f:
        f.write("Battery Talent Census - Validation Report\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Total sampled responses:         {summary['total']}\n")
        if summary["total"] > 0:
            f.write(
                f"Human assigned (clear category): {summary['assignable']} "
                f"({100*summary['assignable']/summary['total']:.1f}%)\n"
            )
            f.write(
                f"Human flagged ambiguous:         {summary['human_ambiguous']} "
                f"({100*summary['human_ambiguous']/summary['total']:.1f}%)\n"
            )
            f.write(
                f"Human flagged invalid:           {summary['human_invalid']} "
                f"({100*summary['human_invalid']/summary['total']:.1f}%)\n"
            )
        else:
            f.write("Human assigned (clear category): 0 (0.0%)\n")
            f.write("Human flagged ambiguous:         0 (0.0%)\n")
            f.write("Human flagged invalid:           0 (0.0%)\n")

        f.write(f"LLM classification failed:       {summary['llm_failed']}\n\n")

        f.write(f"LLM-Human Agreement (of {summary['assignable']} assignable):\n")
        if summary["assignable"] > 0:
            f.write(
                f"  Agree:    {summary['agree']:4d} "
                f"({100*summary['agree']/summary['assignable']:.1f}%)\n"
            )
            f.write(
                f"  Disagree: {summary['disagree']:4d} "
                f"({100*summary['disagree']/summary['assignable']:.1f}%)\n"
            )
        else:
            f.write("  Agree:       0 (0.0%)\n")
            f.write("  Disagree:    0 (0.0%)\n")

        metrics = summary["metrics"]
        f.write("\nClassification metrics (filtered eval set only):\n")
        f.write("  Excludes human judgments marked ambiguous/invalid.\n")
        f.write(f"  Eval rows used:      {metrics['total_eval']} (excluded: {metrics['excluded_rows']})\n")
        f.write(f"  Accuracy:          {metrics['accuracy']:.6f}\n")
        f.write(
            "  Micro P/R/F1:      "
            f"{metrics['micro_precision']:.6f} / {metrics['micro_recall']:.6f} / {metrics['micro_f1']:.6f}\n"
        )
        f.write(
            "  Macro P/R/F1:      "
            f"{metrics['macro_precision']:.6f} / {metrics['macro_recall']:.6f} / {metrics['macro_f1']:.6f}\n"
        )
        f.write(
            "  Weighted P/R/F1:   "
            f"{metrics['weighted_precision']:.6f} / {metrics['weighted_recall']:.6f} / {metrics['weighted_f1']:.6f}\n"
        )

        f.write("\nPer-class metrics:\n")
        f.write("label,precision,recall,f1,support,tp,fp,fn\n")
        for row in metrics["per_class"]:
            label = row["label"].replace(",", ";")
            f.write(
                f"{label},{row['precision']:.6f},{row['recall']:.6f},"
                f"{row['f1']:.6f},{row['support']},{row['tp']},{row['fp']},{row['fn']}\n"
            )

        f.write("\nConfusion matrix (rows=true human, cols=predicted LLM):\n")
        header = "human\\pred," + ",".join(label.replace(",", ";") for label in metrics["labels"])
        f.write(header + "\n")
        for true_label in metrics["labels"]:
            row_counts = [str(metrics["confusion"][true_label][pred_label]) for pred_label in metrics["labels"]]
            f.write(true_label.replace(",", ";") + "," + ",".join(row_counts) + "\n")

        f.write("\nExample mismatches (sample):\n")
        if disagreement_examples:
            for d in disagreement_examples:
                f.write(f"- Response: {d['response_text']}\n")
                f.write(f"  LLM:      {d['llm_category']}\n")
                f.write(f"  Human:    {d['human_category']}\n")
                if d.get("note"):
                    f.write(f"  Note:     {d['note']}\n")
                f.write("\n")
        else:
            f.write("- None\n")

        f.write("\n")
        f.write(f"Disagreements ({len(disagreements)}):\n")
        if disagreements:
            for d in disagreements:
                f.write(f"- Response: {d['response_text']}\n")
                f.write(f"  LLM:      {d['llm_category']}\n")
                f.write(f"  Human:    {d['human_category']}\n")
                if d.get("note"):
                    f.write(f"  Note:     {d['note']}\n")
                f.write("\n")
        else:
            f.write("- None\n")

    print(f"Text report saved to {REPORT_FILE}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print()
    print("Battery Talent Census — LLM Category Assignment Validation")
    print("=" * 70)
    print()

    sample = load_sample()

    if not os.path.exists(HUMAN_REVIEW_FILE):
        print(f"\nERROR: Human review file not found: {HUMAN_REVIEW_FILE}")
        print("Run the validation_review_tool.html first to create this file.")
        sys.exit(1)

    human_review = load_human_review()

    print("\nRunning LLM classification on 200 samples...")
    print("(This calls gpt-4o-mini via the OpenAI API)\n")
    llm_results = run_llm_classification(sample)

    comparison, summary = compare_and_report(llm_results, human_review)
    save_comparison(comparison)
    save_text_report(comparison, summary)

    print("\nDone. To update the manuscript with these results:")
    print("  - Report the agreement rate in the Technical Validation section")
    print("  - Commit validation_comparison.csv to the repository")
    print()


if __name__ == "__main__":
    main()
