
import json
from pathlib import Path

from data_pipeline import run_pipeline

OUTPUT_FILE = Path(__file__).parent / "january_results.json"


def main():
    results = run_pipeline()

    if not results.get("hourly"):
        raise RuntimeError("No hourly results returned by pipeline.")

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, allow_nan=False)

    print(f"Saved results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
