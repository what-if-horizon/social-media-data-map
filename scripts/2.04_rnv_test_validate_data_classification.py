from pathlib import Path
import json

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


def evaluate_verduyn(json_dir, csv_dir, output_file):

    json_dir = Path(json_dir)
    csv_dir = Path(csv_dir)

    results = {}

    # --------------------------------------------------
    # Label definitions
    # --------------------------------------------------
    exact_labels = {
        "active",
        "passive",
        "active-meta",
        "passive-meta",
        "other"
    }

    collapsed_labels = {
        "active",
        "passive",
        "other"
    }

    # --------------------------------------------------
    # Mapping for collapsed evaluation
    # --------------------------------------------------
    meta_mapping = {
        "active-meta": "active",
        "passive-meta": "passive"
    }

    # --------------------------------------------------
    # Loop over platforms
    # --------------------------------------------------
    for platform_dir in json_dir.iterdir():

        if not platform_dir.is_dir():
            continue

        platform = platform_dir.name

        # --------------------------------------------------
        # Find JSON starting with platform name
        # --------------------------------------------------
        json_files = list(
            platform_dir.glob(f"{platform}*.json")
        )

        if not json_files:
            print(f"[WARNING] No JSON found for {platform}")
            continue

        json_file = json_files[0]

        # --------------------------------------------------
        # Find human annotation XLSX
        # --------------------------------------------------
        csv_platform_dir = csv_dir / platform

        csv_files = list(
            csv_platform_dir.glob("*verduyn2020*")
        )

        if not csv_files:
            print(
                f"[WARNING] No verduyn2020 XLSX found "
                f"for {platform}"
            )
            continue

        csv_file = csv_files[0]

        print("\n" + "=" * 70)
        print(f"Processing {platform}")
        print(f"  JSON: {json_file}")
        print(f"  XLSX: {csv_file}")

        # ==================================================
        # Load JSON
        # ==================================================

        with open(json_file, "r") as f:
            json_data = json.load(f)

        json_df = pd.DataFrame(json_data)

        # ==================================================
        # Load human annotation XLSX
        # ==================================================

        csv_df = pd.read_excel(csv_file)

        # ==================================================
        # Check required columns
        # ==================================================

        required_json_columns = {
            "path",
            "category",
            "rationale"
        }

        required_csv_columns = {
            "final_path",
            "Answer"
        }

        missing_json = (
            required_json_columns
            - set(json_df.columns)
        )

        missing_csv = (
            required_csv_columns
            - set(csv_df.columns)
        )

        if missing_json:
            raise ValueError(
                f"{json_file} is missing columns: "
                f"{missing_json}"
            )

        if missing_csv:
            raise ValueError(
                f"{csv_file} is missing columns: "
                f"{missing_csv}"
            )

        # ==================================================
        # Check duplicate paths
        # ==================================================

        json_duplicates = (
            json_df["path"].duplicated().sum()
        )

        csv_duplicates = (
            csv_df["final_path"].duplicated().sum()
        )

        if json_duplicates > 0:
            print(
                f"[WARNING] {platform}: "
                f"{json_duplicates} duplicate path values "
                f"in JSON"
            )

        if csv_duplicates > 0:
            print(
                f"[WARNING] {platform}: "
                f"{csv_duplicates} duplicate final_path "
                f"values in XLSX"
            )

        # ==================================================
        # Match JSON and XLSX on final_path
        # ==================================================

        json_df = json_df.rename(
            columns={"path": "final_path"}
        )

        merged = json_df[
            [
                "final_path",
                "category",
                "rationale"
            ]
        ].merge(
            csv_df[
                [
                    "final_path",
                    "Answer"
                ]
            ],
            on="final_path",
            how="inner"
        )

        # ==================================================
        # Match statistics
        # ==================================================

        json_paths = set(json_df["final_path"])
        csv_paths = set(csv_df["final_path"])

        unmatched_json = json_paths - csv_paths
        unmatched_csv = csv_paths - json_paths

        print(f"\n  JSON rows:       {len(json_df)}")
        print(f"  XLSX rows:       {len(csv_df)}")
        print(f"  Matched rows:    {len(merged)}")
        print(f"  Unmatched JSON:  {len(unmatched_json)}")
        print(f"  Unmatched XLSX:  {len(unmatched_csv)}")

        # ==================================================
        # Normalize labels
        # ==================================================

        merged["Answer"] = (
            merged["Answer"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        merged["category"] = (
            merged["category"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # ==================================================
        # 1. EXACT 5-CLASS EVALUATION
        # ==================================================

        valid_exact = (
            merged["Answer"].isin(exact_labels)
            & merged["category"].isin(exact_labels)
        )

        evaluated_exact = merged[valid_exact]

        y_true_exact = evaluated_exact["Answer"]
        y_pred_exact = evaluated_exact["category"]

        print("\n" + "-" * 60)
        print("EXACT 5-CLASS EVALUATION")
        print("-" * 60)

        print(f"  Evaluated: {len(evaluated_exact)}")
        print(f"  Invalid:   {(~valid_exact).sum()}")

        print("\n  Human labels:")
        print(
            y_true_exact.value_counts().to_string()
        )

        print("\n  Inference labels:")
        print(
            y_pred_exact.value_counts().to_string()
        )

        # --------------------------------------------------
        # Exact incorrect predictions
        # --------------------------------------------------

        incorrect_exact = evaluated_exact[
            y_true_exact != y_pred_exact
        ]

        if len(incorrect_exact) > 0:

            print(
                f"\n  Incorrect predictions "
                f"({len(incorrect_exact)}):"
            )

            for _, row in incorrect_exact.iterrows():

                print(
                    f"    final_path: {row['final_path']}"
                )

                print(
                    f"      True:       {row['Answer']}"
                )

                print(
                    f"      Predicted:  {row['category']}"
                )

                print(
                    f"      Rationale:  {row['rationale']}"
                )

        else:
            print("\n  No incorrect predictions.")

        # --------------------------------------------------
        # Exact metrics
        # --------------------------------------------------

        if len(evaluated_exact) > 0:

            exact_accuracy = accuracy_score(
                y_true_exact,
                y_pred_exact
            )

            exact_report = classification_report(
                y_true_exact,
                y_pred_exact,
                labels=[
                    "passive",
                    "active",
                    "passive-meta",
                    "active-meta",
                    "other"
                ],
                output_dict=True,
                zero_division=0
            )

            exact_cm = confusion_matrix(
                y_true_exact,
                y_pred_exact,
                labels=[
                    "passive",
                    "active",
                    "passive-meta",
                    "active-meta",
                    "other"
                ]
            )

            print(
                f"\n  Exact accuracy: "
                f"{exact_accuracy:.4f}"
            )

        else:

            exact_accuracy = None
            exact_report = {}
            exact_cm = []

        # ==================================================
        # 2. COLLAPSED 3-CLASS EVALUATION
        # ==================================================

        collapsed = merged.copy()

        # --------------------------------------------------
        # Collapse meta labels
        # --------------------------------------------------

        collapsed["Answer_collapsed"] = (
            collapsed["Answer"]
            .replace(meta_mapping)
        )

        collapsed["category_collapsed"] = (
            collapsed["category"]
            .replace(meta_mapping)
        )

        # --------------------------------------------------
        # Valid labels after collapsing
        #
        # active-meta  -> active
        # passive-meta -> passive
        # other        -> other
        # --------------------------------------------------

        valid_collapsed = (
            collapsed["Answer_collapsed"].isin(
                collapsed_labels
            )
            &
            collapsed["category_collapsed"].isin(
                collapsed_labels
            )
        )

        evaluated_collapsed = collapsed[
            valid_collapsed
        ]

        y_true_collapsed = (
            evaluated_collapsed["Answer_collapsed"]
        )

        y_pred_collapsed = (
            evaluated_collapsed["category_collapsed"]
        )

        print("\n" + "-" * 60)
        print("COLLAPSED 3-CLASS EVALUATION")
        print("-" * 60)

        print("  active-meta  -> active")
        print("  passive-meta -> passive")
        print("  other        -> other")

        print(
            f"\n  Evaluated: "
            f"{len(evaluated_collapsed)}"
        )

        print(
            f"  Invalid:   "
            f"{(~valid_collapsed).sum()}"
        )

        print("\n  Human labels after collapsing:")
        print(
            y_true_collapsed.value_counts().to_string()
        )

        print("\n  Inference labels after collapsing:")
        print(
            y_pred_collapsed.value_counts().to_string()
        )

        # --------------------------------------------------
        # Collapsed incorrect predictions
        # --------------------------------------------------

        incorrect_collapsed = evaluated_collapsed[
            y_true_collapsed != y_pred_collapsed
        ]

        if len(incorrect_collapsed) > 0:

            print(
                f"\n  Incorrect predictions "
                f"({len(incorrect_collapsed)}):"
            )

            for _, row in incorrect_collapsed.iterrows():

                print(
                    f"    final_path: {row['final_path']}"
                )

                print(
                    f"      True:               "
                    f"{row['Answer']}"
                )

                print(
                    f"      True collapsed:     "
                    f"{row['Answer_collapsed']}"
                )

                print(
                    f"      Predicted:          "
                    f"{row['category']}"
                )

                print(
                    f"      Predicted collapsed:"
                    f" {row['category_collapsed']}"
                )

                print(
                    f"      Rationale:          "
                    f"{row['rationale']}"
                )

        else:

            print("\n  No incorrect predictions.")

        # --------------------------------------------------
        # Collapsed metrics
        # --------------------------------------------------

        if len(evaluated_collapsed) > 0:

            collapsed_accuracy = accuracy_score(
                y_true_collapsed,
                y_pred_collapsed
            )

            collapsed_report = classification_report(
                y_true_collapsed,
                y_pred_collapsed,
                labels=[
                    "passive",
                    "active",
                    "other"
                ],
                output_dict=True,
                zero_division=0
            )

            collapsed_cm = confusion_matrix(
                y_true_collapsed,
                y_pred_collapsed,
                labels=[
                    "passive",
                    "active",
                    "other"
                ]
            )

            print(
                f"\n  Collapsed accuracy: "
                f"{collapsed_accuracy:.4f}"
            )

        else:

            collapsed_accuracy = None
            collapsed_report = {}
            collapsed_cm = []

        # ==================================================
        # Save platform results
        # ==================================================

        results[platform] = {

            "json_file": str(json_file),
            "csv_file": str(csv_file),

            "n_json_rows": len(json_df),
            "n_csv_rows": len(csv_df),
            "n_matched": len(merged),

            "n_unmatched_json": len(unmatched_json),
            "n_unmatched_csv": len(unmatched_csv),

            # ----------------------------------------------
            # Exact 5-class results
            # ----------------------------------------------

            "exact": {
                "labels": [
                    "passive",
                    "active",
                    "passive-meta",
                    "active-meta",
                    "other"
                ],

                "n_evaluated": len(
                    evaluated_exact
                ),

                "n_invalid": int(
                    (~valid_exact).sum()
                ),

                "accuracy": exact_accuracy,

                "classification_report": exact_report,

                "confusion_matrix": {
                    "labels": [
                        "passive",
                        "active",
                        "passive-meta",
                        "active-meta",
                        "other"
                    ],
                    "matrix": exact_cm.tolist()
                }
            },

            # ----------------------------------------------
            # Collapsed 3-class results
            # ----------------------------------------------

            "collapsed": {
                "mapping": {
                    "active-meta": "active",
                    "passive-meta": "passive",
                    "other": "other"
                },

                "labels": [
                    "passive",
                    "active",
                    "other"
                ],

                "n_evaluated": len(
                    evaluated_collapsed
                ),

                "n_invalid": int(
                    (~valid_collapsed).sum()
                ),

                "accuracy": collapsed_accuracy,

                "classification_report": collapsed_report,

                "confusion_matrix": {
                    "labels": [
                        "passive",
                        "active",
                        "other"
                    ],
                    "matrix": collapsed_cm.tolist()
                }
            }
        }

    # ======================================================
    # Save all platform results
    # ======================================================

    with open(output_file, "w") as f:

        json.dump(
            results,
            f,
            indent=4
        )

    print(
        f"\nResults saved to: {output_file}"
    )


def main():

    evaluate_verduyn(
        json_dir=(
            "/projects/prjs2007/data_donation/"
            "ddd_annotation/inference/"
            "02_path_classification/test"
        ),

        csv_dir=(
            "/projects/prjs2007/data_donation/"
            "ddd_annotation/annotation/test"
        ),

        output_file=(
            "/home/nvisscher/GIT/"
            "social-media-data-map/results/"
            "02_data_classification/"
            "verduyn2020_accuracy_test.json"
        )
    )


if __name__ == "__main__":
    main()