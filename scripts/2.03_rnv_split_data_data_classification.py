from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


def create_splits(
    annotation_dir,
    sample_dir,
    output_dir,
    test_size=0.20,
    random_state=42,
):
    annotation_dir = Path(annotation_dir)
    sample_dir = Path(sample_dir)
    output_dir = Path(output_dir)

    for platform_dir in sample_dir.iterdir():

        if not platform_dir.is_dir():
            continue

        platform = platform_dir.name

        # --------------------------------------------------
        # Find sample CSV ending with 100rows
        # --------------------------------------------------
        sample_files = list(
            platform_dir.glob("*100rows.csv")
        )

        if not sample_files:
            print(f"[WARNING] No 100rows CSV found for {platform}")
            continue

        sample_file = sample_files[0]

        # --------------------------------------------------
        # Find annotation XLSX ending with verduyn2020
        # --------------------------------------------------
        annotation_platform_dir = annotation_dir / platform

        annotation_files = list(
            annotation_platform_dir.glob("*verduyn2020.xlsx")
        )

        if not annotation_files:
            print(
                f"[WARNING] No verduyn2020 XLSX found for {platform}"
            )
            continue

        annotation_file = annotation_files[0]

        print(f"\nProcessing {platform}")
        print(f"  Sample:      {sample_file}")
        print(f"  Annotation:  {annotation_file}")

        # --------------------------------------------------
        # Load sample
        # --------------------------------------------------
        sample_df = pd.read_csv(sample_file)

        if "final_path" not in sample_df.columns:
            raise ValueError(
                f"'final_path' missing from {sample_file}"
            )

        # --------------------------------------------------
        # Load annotation
        # --------------------------------------------------
        annotation_df = pd.read_excel(annotation_file)

        if "final_path" not in annotation_df.columns:
            raise ValueError(
                f"'final_path' missing from {annotation_file}"
            )

        # --------------------------------------------------
        # Check for duplicate final_path
        # --------------------------------------------------
        if sample_df["final_path"].duplicated().any():
            raise ValueError(
                f"{platform}: duplicate final_path values "
                f"in sample data"
            )

        if annotation_df["final_path"].duplicated().any():
            raise ValueError(
                f"{platform}: duplicate final_path values "
                f"in annotation data"
            )

        # --------------------------------------------------
        # Create random 80/20 split from sample
        # --------------------------------------------------
        validation_df, test_df = train_test_split(
            sample_df,
            test_size=test_size,
            random_state=random_state,
            shuffle=True,
        )

        # final_path defines the split
        validation_paths = set(validation_df["final_path"])
        test_paths = set(test_df["final_path"])

        # --------------------------------------------------
        # Apply same split to annotation
        # --------------------------------------------------
        annotation_validation = annotation_df[
            annotation_df["final_path"].isin(validation_paths)
        ].copy()

        annotation_test = annotation_df[
            annotation_df["final_path"].isin(test_paths)
        ].copy()

        # --------------------------------------------------
        # Check for missing annotation paths
        # --------------------------------------------------
        annotation_paths = set(annotation_df["final_path"])

        missing_validation = validation_paths - annotation_paths
        missing_test = test_paths - annotation_paths

        if missing_validation:
            print(
                f"[WARNING] {platform}: "
                f"{len(missing_validation)} validation paths "
                f"not found in annotation"
            )

        if missing_test:
            print(
                f"[WARNING] {platform}: "
                f"{len(missing_test)} test paths "
                f"not found in annotation"
            )

        # --------------------------------------------------
        # Create output directories
        # --------------------------------------------------
        sample_validation_dir = (
            output_dir / "sample" / "validation" / platform
        )

        sample_test_dir = (
            output_dir / "sample" / "test" / platform
        )

        annotation_validation_dir = (
            output_dir / "annotation" / "validation" / platform
        )

        annotation_test_dir = (
            output_dir / "annotation" / "test" / platform
        )

        for directory in [
            sample_validation_dir,
            sample_test_dir,
            annotation_validation_dir,
            annotation_test_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # --------------------------------------------------
        # Save sample splits
        # --------------------------------------------------
        validation_df.to_csv(
            sample_validation_dir
            / f"{platform}_100rows_validation.csv",
            index=False,
        )

        test_df.to_csv(
            sample_test_dir
            / f"{platform}_100rows_test.csv",
            index=False,
        )

        # --------------------------------------------------
        # Save annotation splits
        # --------------------------------------------------
        annotation_validation.to_excel(
            annotation_validation_dir
            / f"{platform}_verduyn2020_validation.xlsx",
            index=False,
        )

        annotation_test.to_excel(
            annotation_test_dir
            / f"{platform}_verduyn2020_test.xlsx",
            index=False,
        )

        # --------------------------------------------------
        # Report
        # --------------------------------------------------
        print(f"  Sample total:          {len(sample_df)}")
        print(f"  Sample validation:     {len(validation_df)}")
        print(f"  Sample test:           {len(test_df)}")
        print(f"  Annotation validation: {len(annotation_validation)}")
        print(f"  Annotation test:       {len(annotation_test)}")



def main():
    create_splits(
    annotation_dir="/projects/prjs2007/data_donation/ddd_annotation/annotation/full",
    sample_dir="/projects/prjs2007/data_donation/ddd_annotation/sample/full",
    output_dir="/projects/prjs2007/data_donation/ddd_annotation",
    test_size=0.20,
    random_state=42,)


if __name__ == "__main__":
    main()

