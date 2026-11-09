import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = Path("/home/nvisscher/GIT/social-media-data-map/results/02_taxonomy/verduyn2020_accuracy_validation.json")

OUTPUT_DIR = Path("/home/nvisscher/GIT/social-media-data-map/results/02_taxonomy/verduyn_visualisations")
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

with INPUT_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

platforms = list(data.keys())


# ============================================================
# 1. ACCURACY: EXACT VS COLLAPSED
# ============================================================

exact_accuracy = [
    data[platform]["exact"]["accuracy"]
    for platform in platforms
]

collapsed_accuracy = [
    data[platform]["collapsed"]["accuracy"]
    for platform in platforms
]

x = np.arange(len(platforms))
width = 0.36

fig, ax = plt.subplots(figsize=(10, 6))

ax.bar(
    x - width / 2,
    exact_accuracy,
    width,
    label="Exact"
)

ax.bar(
    x + width / 2,
    collapsed_accuracy,
    width,
    label="Collapsed"
)

ax.set_ylabel("Accuracy")
ax.set_xlabel("Platform")
ax.set_title("Verduyn Taxonomy Accuracy by Platform")

ax.set_xticks(x)
ax.set_xticklabels(
    [platform.capitalize() for platform in platforms]
)

ax.set_ylim(0, 1)

ax.legend()
ax.grid(axis="y", alpha=0.25)

# Add values above bars
for i, value in enumerate(exact_accuracy):
    ax.text(
        i - width / 2,
        value + 0.02,
        f"{value:.2f}",
        ha="center"
    )

for i, value in enumerate(collapsed_accuracy):
    ax.text(
        i + width / 2,
        value + 0.02,
        f"{value:.2f}",
        ha="center"
    )

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "accuracy_exact_vs_collapsed.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 2. EXACT CLASSIFICATION: F1 BY PLATFORM
# ============================================================

labels_exact = data[platforms[0]]["exact"]["labels"]

fig, ax = plt.subplots(figsize=(12, 7))

for platform in platforms:

    f1 = [
        data[platform]["exact"]["classification_report"][label]["f1-score"]
        for label in labels_exact
    ]

    ax.plot(
        labels_exact,
        f1,
        marker="o",
        label=platform.capitalize()
    )

ax.set_ylabel("F1 score")
ax.set_xlabel("Class")
ax.set_title("Exact Taxonomy: F1 Score by Platform")

ax.set_ylim(0, 1)

ax.legend()
ax.grid(axis="y", alpha=0.25)

plt.xticks(
    rotation=30,
    ha="right"
)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "exact_f1_by_class.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 3. COLLAPSED CLASSIFICATION: F1 BY PLATFORM
# ============================================================

labels_collapsed = data[platforms[0]]["collapsed"]["labels"]

fig, ax = plt.subplots(figsize=(10, 6))

for platform in platforms:

    f1 = [
        data[platform]["collapsed"]["classification_report"][label]["f1-score"]
        for label in labels_collapsed
    ]

    ax.plot(
        labels_collapsed,
        f1,
        marker="o",
        label=platform.capitalize()
    )

ax.set_ylabel("F1 score")
ax.set_xlabel("Class")
ax.set_title("Collapsed Taxonomy: F1 Score by Platform")

ax.set_ylim(0, 1)

ax.legend()
ax.grid(axis="y", alpha=0.25)

plt.xticks(
    rotation=20,
    ha="right"
)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "collapsed_f1_by_class.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 4. PRECISION / RECALL / F1 FOR EACH PLATFORM
# ============================================================

metrics = [
    "precision",
    "recall",
    "f1-score"
]

for platform in platforms:

    report = data[platform]["collapsed"]["classification_report"]

    values = {
        metric: [
            report[label][metric]
            for label in labels_collapsed
        ]
        for metric in metrics
    }

    x = np.arange(len(labels_collapsed))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 6))

    for i, metric in enumerate(metrics):

        ax.bar(
            x + (i - 1) * width,
            values[metric],
            width,
            label=metric.replace("-", " ").title()
        )

    ax.set_ylabel("Score")
    ax.set_xlabel("Class")

    ax.set_title(
        f"{platform.capitalize()}: Collapsed Taxonomy Metrics"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels_collapsed)

    ax.set_ylim(0, 1)

    ax.legend()
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR /
        f"{platform}_collapsed_precision_recall_f1.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# ============================================================
# 5. COLLAPSED CONFUSION MATRICES
# ============================================================

for platform in platforms:

    cm = np.array(
        data[platform]["collapsed"]["confusion_matrix"]["matrix"]
    )

    labels = data[platform]["collapsed"]["confusion_matrix"]["labels"]

    fig, ax = plt.subplots(figsize=(7, 6))

    im = ax.imshow(cm)

    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))

    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")

    ax.set_title(
        f"{platform.capitalize()}: Collapsed Confusion Matrix"
    )

    # Add numbers to cells
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):

            ax.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center"
            )

    fig.colorbar(
        im,
        ax=ax,
        label="Count"
    )

    plt.setp(
        ax.get_xticklabels(),
        rotation=30,
        ha="right"
    )

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR /
        f"{platform}_collapsed_confusion_matrix.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# ============================================================
# 6. EXACT CONFUSION MATRICES
# ============================================================

for platform in platforms:

    cm = np.array(
        data[platform]["exact"]["confusion_matrix"]["matrix"]
    )

    labels = data[platform]["exact"]["confusion_matrix"]["labels"]

    fig, ax = plt.subplots(figsize=(8, 7))

    im = ax.imshow(cm)

    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))

    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)

    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")

    ax.set_title(
        f"{platform.capitalize()}: Exact Confusion Matrix"
    )

    # Add numbers to cells
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):

            ax.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center"
            )

    fig.colorbar(
        im,
        ax=ax,
        label="Count"
    )

    plt.setp(
        ax.get_xticklabels(),
        rotation=30,
        ha="right"
    )

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR /
        f"{platform}_exact_confusion_matrix.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
    plt.close()


# ============================================================
# 7. CLASS DISTRIBUTION
# ============================================================

fig, ax = plt.subplots(figsize=(10, 6))

support_data = {
    platform: [
        data[platform]["collapsed"]["classification_report"]
        [label]["support"]
        for label in labels_collapsed
    ]
    for platform in platforms
}

x = np.arange(len(labels_collapsed))

width = 0.8 / len(platforms)

for i, platform in enumerate(platforms):

    ax.bar(
        x + (i - len(platforms) / 2 + 0.5) * width,
        support_data[platform],
        width,
        label=platform.capitalize()
    )

ax.set_ylabel("Number of observations")
ax.set_xlabel("Class")

ax.set_title(
    "Class Distribution in Validation Data"
)

ax.set_xticks(x)
ax.set_xticklabels(labels_collapsed)

ax.legend()
ax.grid(axis="y", alpha=0.25)

fig.tight_layout()

fig.savefig(
    OUTPUT_DIR / "class_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# DONE
# ============================================================

print()
print("Visualisations created successfully.")
print(f"Output directory: {OUTPUT_DIR.resolve()}")