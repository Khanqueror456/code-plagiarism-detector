from datasets import load_dataset

from app.services.code_comparison import compare_code


def main():

    dataset = load_dataset(
        "google/code_x_glue_cc_clone_detection_big_clone_bench",
        split="train",
        streaming=True
    )

    false_samples = []
    true_samples = []

    for sample in dataset:

        label = bool(sample["label"])

        if label is False and len(false_samples) < 5:
            false_samples.append(sample)

        elif label is True and len(true_samples) < 5:
            true_samples.append(sample)

        if (
            len(false_samples) == 5
            and len(true_samples) == 5
        ):
            break

    print("=" * 80)
    print("LABEL = FALSE")
    print("=" * 80)

    for i, sample in enumerate(false_samples):

        print(f"\n--- FALSE SAMPLE {i + 1} ---")

        print("ID1:", sample["id1"])
        print("ID2:", sample["id2"])
        print("Original label:", sample["label"])

        print("\nCODE A:")
        print(sample["func1"])

        print("\nCODE B:")
        print(sample["func2"])

        features = compare_code(
            sample["func1"],
            sample["func2"],
            "java",
            "java"
        )

        print("\nFEATURES:")
        print(features)

    print("\n")
    print("=" * 80)
    print("LABEL = TRUE")
    print("=" * 80)

    for i, sample in enumerate(true_samples):

        print(f"\n--- TRUE SAMPLE {i + 1} ---")

        print("ID1:", sample["id1"])
        print("ID2:", sample["id2"])
        print("Original label:", sample["label"])

        print("\nCODE A:")
        print(sample["func1"])

        print("\nCODE B:")
        print(sample["func2"])

        features = compare_code(
            sample["func1"],
            sample["func2"],
            "java",
            "java"
        )

        print("\nFEATURES:")
        print(features)


if __name__ == "__main__":
    main()