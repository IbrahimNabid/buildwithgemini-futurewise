"""Chart generation tool for Futurewise rendering matplotlib PNGs to Cloud Storage."""

import datetime
import io
import json
import secrets
from typing import Any, Dict, List, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from google.cloud import storage

FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-7459370ad109"
GCS_ASSETS_BUCKET = "futurewise-assets-qwiklabs-gcp-04-7459370ad109"


def make_chart(
    chart_type: str,
    title: str,
    labels: List[str],
    values: List[float],
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    secondary_values: Optional[List[float]] = None,
    secondary_label: Optional[str] = None,
) -> str:
    """Renders a clean matplotlib chart as PNG, uploads it to GCS, and returns its public URL.

    Args:
        chart_type: 'bar', 'horizontal_bar', 'line', 'pie', or 'simulation_histogram'.
        title: Title of the chart.
        labels: List of categories or x-axis tick labels.
        values: Numerical values corresponding to labels.
        x_label: Optional X-axis label.
        y_label: Optional Y-axis label.
        secondary_values: Optional secondary data series.
        secondary_label: Legend label for secondary series.

    Returns:
        Public HTTPS URL of the uploaded chart PNG.
    """
    plt.figure(figsize=(7, 4.2), dpi=150)
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    colors = ['#1a73e8', '#34a853', '#fbbc04', '#ea4335', '#9c27b0', '#00bcd4', '#ff9800', '#795548']

    if chart_type == "bar":
        bars = plt.bar(labels, values, color=colors[:len(values)], width=0.5)
        plt.title(title, fontsize=12, fontweight='bold', pad=12)
        if x_label:
            plt.xlabel(x_label, fontsize=10)
        if y_label:
            plt.ylabel(y_label, fontsize=10)
        plt.xticks(rotation=20, ha='right')
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval + (max(values)*0.01 if values else 0), f"${yval:,.0f}" if yval >= 10 else f"{yval:.1f}", ha='center', va='bottom', fontsize=8)

    elif chart_type == "horizontal_bar":
        y_pos = range(len(labels))
        plt.barh(y_pos, values, color=colors[:len(values)], height=0.5)
        plt.yticks(y_pos, labels)
        plt.title(title, fontsize=12, fontweight='bold', pad=12)
        if x_label:
            plt.xlabel(x_label, fontsize=10)

    elif chart_type == "pie":
        plt.pie(values, labels=labels, autopct='%1.1f%%', colors=colors[:len(values)], startangle=140)
        plt.title(title, fontsize=12, fontweight='bold', pad=12)

    elif chart_type == "simulation_histogram":
        n, bins, patches = plt.hist(values, bins=25, color='#1a73e8', edgecolor='white', alpha=0.85)
        plt.axvline(sum(values)/len(values), color='#ea4335', linestyle='dashed', linewidth=2, label=f'Mean (${sum(values)/len(values):,.0f})')
        plt.title(title, fontsize=12, fontweight='bold', pad=12)
        plt.xlabel(x_label or "Net Worth at Age 65 ($)", fontsize=10)
        plt.ylabel(y_label or "Frequency (Outcomes)", fontsize=10)
        plt.legend()

    else:
        # Default line chart
        plt.plot(labels, values, marker='o', color='#1a73e8', linewidth=2, label='Primary')
        if secondary_values:
            plt.plot(labels, secondary_values, marker='s', color='#34a853', linewidth=2, label=secondary_label or 'Comparison')
            plt.legend()
        plt.title(title, fontsize=12, fontweight='bold', pad=12)
        if x_label:
            plt.xlabel(x_label, fontsize=10)
        if y_label:
            plt.ylabel(y_label, fontsize=10)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    image_bytes = buf.getvalue()

    filename = f"chart_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}.png"
    storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = storage_client.bucket(GCS_ASSETS_BUCKET)
    blob_name = f"charts/{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(image_bytes, content_type="image/png")

    return f"https://storage.googleapis.com/{GCS_ASSETS_BUCKET}/{blob_name}"
