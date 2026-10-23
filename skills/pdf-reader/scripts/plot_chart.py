#!/home/lebaoquan/.local/share/pipx/venvs/hermes-agent/bin/python
"""
Chart & Plot Generator Helper Script
Generates clean publication-grade charts from extracted PDF data using Matplotlib.
"""

import sys
import json
import argparse
import matplotlib.pyplot as plt

def generate_chart(data: dict, output_file: str = "/tmp/chart.png", chart_type: str = "bar") -> str:
    title = data.get("title", "Generated Chart")
    x_label = data.get("x_label", "X")
    y_label = data.get("y_label", "Y")
    labels = data.get("labels", [])
    values = data.get("values", [])

    if not labels or not values:
        raise ValueError("Data must include non-empty 'labels' and 'values' arrays.")

    plt.figure(figsize=(9, 5), dpi=150)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    if chart_type == "bar":
        bars = plt.bar(labels, values, color="#3498db", edgecolor="#2980b9", width=0.55)
        plt.bar_label(bars, padding=3, fmt="%.1f" if any(isinstance(v, float) for v in values) else "%d")
    elif chart_type == "line":
        plt.plot(labels, values, marker="o", color="#2ecc71", linewidth=2.5, markersize=6)
        for i, txt in enumerate(values):
            plt.annotate(str(txt), (labels[i], values[i]), textcoords="offset points", xytext=(0, 7), ha='center')
    elif chart_type == "pie":
        plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=140, colors=plt.cm.Paired.colors)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    plt.title(title, fontsize=14, fontweight="bold", pad=12)
    if chart_type != "pie":
        plt.xlabel(x_label, fontsize=11, labelpad=8)
        plt.ylabel(y_label, fontsize=11, labelpad=8)
        plt.xticks(rotation=25 if len(str(labels[0])) > 5 else 0)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return output_file

def main():
    parser = argparse.ArgumentParser(description="Generate charts from JSON data.")
    parser.add_argument("json_data", help="JSON string or path to JSON file containing chart data")
    parser.add_argument("--out", "-o", default="/tmp/chart.png", help="Output image file path")
    parser.add_argument("--type", "-t", choices=["bar", "line", "pie"], default="bar", help="Chart type")
    args = parser.parse_args()

    try:
        if args.json_data.strip().startswith("{"):
            data = json.loads(args.json_data)
        else:
            with open(args.json_data) as f:
                data = json.load(f)
        out_path = generate_chart(data, args.out, args.type)
        print(f"✓ Chart generated successfully: {out_path}")
    except Exception as e:
        print(f"Error generating chart: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
