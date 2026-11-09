import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = Path("/home/nvisscher/GIT/social-media-data-map/results/01_id_standardisation/std_ids_test_results_ES_NL_LT_RO.json")

OUTPUT_DIR = Path("/home/nvisscher/GIT/social-media-data-map/results/01_id_standardisation/std_ids_visualisations")
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

with INPUT_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

platform_data = data["platforms"]
pooled = data["pooled"]

platforms = list(platform_data.keys())


# Clean platform names
platform_names = [
    platform.replace("std_ids_ES_NL_LT_RO_", "").capitalize()
    for platform in platforms
]


# ============================================================
# 1. ACCURACY BY PLATFORM
# ============================================================

accuracies = [
    platform_data[platform]["accuracy_percentage"]
    for platform in platforms
]

fig, ax = plt.subplots(figsize=(9, 6))

bars = ax.bar(
    platform_names,
    accuracies
)

ax.set_ylabel("Accuracy (%)")
ax.set_xlabel("Platform")
ax.set_title("ID Standardisation Accuracy by Platform")

ax.set_ylim(0, 105)

# Add values above bars
for bar, accuracy in zip(bars, accuracies):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{accuracy:.1f}%",
        ha="center",
        va="bottom"
    )

ax.grid(
    axis="y",
    alpha=0.25
)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "accuracy_by_platform.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 2. ACCURACY BY PLATFORM + POOLED ACCURACY
# ============================================================

pooled_accuracy = pooled["accuracy_percentage"]

fig, ax = plt.subplots(figsize=(9, 6))

bars = ax.bar(
    platform_names,
    accuracies
)

# Pooled accuracy reference line
ax.axhline(
    pooled_accuracy,
    linestyle="--",
    linewidth=1.5,
    label=f"Pooled accuracy ({pooled_accuracy:.1f}%)"
)

ax.set_ylabel("Accuracy (%)")
ax.set_xlabel("Platform")
ax.set_title("ID Standardisation Accuracy by Platform")

ax.set_ylim(0, 105)

for bar, accuracy in zip(bars, accuracies):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{accuracy:.1f}%",
        ha="center",
        va="bottom"
    )

ax.legend()

ax.grid(
    axis="y",
    alpha=0.25
)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "accuracy_by_platform_pooled.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 3. CORRECT VS INCORRECT CASES
# ============================================================

correct = [
    platform_data[platform]["total_correct"]
    for platform in platforms
]

incorrect = [
    platform_data[platform]["total_incorrect"]
    for platform in platforms
]

x = np.arange(len(platform_names))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 6))

bars_correct = ax.bar(
    x - width / 2,
    correct,
    width,
    label="Correct"
)

bars_incorrect = ax.bar(
    x + width / 2,
    incorrect,
    width,
    label="Incorrect"
)

ax.set_ylabel("Number of cases")
ax.set_xlabel("Platform")
ax.set_title("Correct and Incorrect ID Standardisation Cases")

ax.set_xticks(x)
ax.set_xticklabels(platform_names)

ax.legend()

ax.grid(
    axis="y",
    alpha=0.25
)

# Add numbers
for bar in bars_correct:
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        str(int(bar.get_height())),
        ha="center"
    )

for bar in bars_incorrect:
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        str(int(bar.get_height())),
        ha="center"
    )

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "correct_vs_incorrect.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 4. ERROR RATE BY PLATFORM
# ============================================================

error_rates = [
    platform_data[platform]["error_rate_percentage"]
    for platform in platforms
]

fig, ax = plt.subplots(figsize=(9, 6))

bars = ax.bar(
    platform_names,
    error_rates
)

ax.set_ylabel("Error rate (%)")
ax.set_xlabel("Platform")
ax.set_title("ID Standardisation Error Rate by Platform")

ax.set_ylim(0, max(error_rates) + 5)

for bar, error_rate in zip(bars, error_rates):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.2,
        f"{error_rate:.1f}%",
        ha="center",
        va="bottom"
    )

ax.grid(
    axis="y",
    alpha=0.25
)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "error_rate_by_platform.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 5. INCORRECT CASES: SIMILARITY
# ============================================================

mean_similarity = [
    platform_data[platform]["incorrect_mean_similarity"]
    for platform in platforms
]

median_similarity = [
    platform_data[platform]["incorrect_median_similarity"]
    for platform in platforms
]

# Replace None with NaN so matplotlib can handle it
mean_similarity = [
    np.nan if value is None else value
    for value in mean_similarity
]

median_similarity = [
    np.nan if value is None else value
    for value in median_similarity
]

x = np.arange(len(platform_names))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 6))

bars_mean = ax.bar(
    x - width / 2,
    mean_similarity,
    width,
    label="Mean similarity"
)

bars_median = ax.bar(
    x + width / 2,
    median_similarity,
    width,
    label="Median similarity"
)

ax.set_ylabel("Similarity")
ax.set_xlabel("Platform")

ax.set_title(
    "Similarity of Incorrectly Standardised IDs"
)

ax.set_xticks(x)
ax.set_xticklabels(platform_names)

ax.set_ylim(0, 1)

ax.legend()

ax.grid(
    axis="y",
    alpha=0.25
)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "incorrect_similarity.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 6. INCORRECT ESTIMATED IDs PRESENT IN CATEGORY LIST
# ============================================================

present_percentages = [
    platform_data[platform][
        "incorrect_estimated_id_present_in_list_percentage"
    ]
    for platform in platforms
]

present_percentages = [
    np.nan if value is None else value
    for value in present_percentages
]

fig, ax = plt.subplots(figsize=(9, 6))

bars = ax.bar(
    platform_names,
    present_percentages
)

ax.set_ylabel(
    "Percentage of incorrect cases (%)"
)

ax.set_xlabel("Platform")

ax.set_title(
    "Incorrect IDs Present in the Candidate ID List"
)

ax.set_ylim(0, 105)

for bar, value in zip(bars, present_percentages):

    if not np.isnan(value):

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{value:.1f}%",
            ha="center",
            va="bottom"
        )

ax.grid(
    axis="y",
    alpha=0.25
)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "incorrect_ids_present_in_list.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("ID STANDARDISATION RESULTS")
print("=" * 60)

for platform, name in zip(platforms, platform_names):

    result = platform_data[platform]

    print(
        f"{name:12s} | "
        f"Accuracy: {result['accuracy_percentage']:.2f}% | "
        f"Correct: {result['total_correct']:3d} | "
        f"Incorrect: {result['total_incorrect']:3d}"
    )

print("-" * 60)

print(
    f"Pooled       | "
    f"Accuracy: {pooled['accuracy_percentage']:.2f}% | "
    f"Correct: {pooled['total_correct']:3d} | "
    f"Incorrect: {pooled['total_incorrect']:3d}"
)

print("=" * 60)

print()
print(
    f"Visualisations saved to: "
    f"{OUTPUT_DIR.resolve()}"
)