"""Image generation tools for Futurewise using gemini-3.1-flash-lite-image."""

import base64
import datetime
import secrets
from typing import Optional
from google.adk.tools.tool_context import ToolContext
from google.cloud import storage
import google.genai
from google.genai import types

FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-7459370ad109"
GCS_ASSETS_BUCKET = "futurewise-assets-qwiklabs-gcp-04-7459370ad109"


def generate_futurewise_image(
    prompt: str,
    context_label: str = "concept",
    tool_context: Optional[ToolContext] = None,
) -> str:
    """Generates an image for life simulator chapters or lesson concepts.

    Uses gemini-3.1-flash-lite-image in the global region.
    Ensures no text or numbers appear in the generated image.
    Saves image via tool_context.save_artifact (if context available)
    and uploads the image bytes directly to the public Cloud Storage bucket.

    Args:
        prompt: Visual description of the image.
        context_label: Short descriptor e.g. 'chapter', 'lesson_hsa', 'brief'.
        tool_context: ADK ToolContext injected automatically by the runtime.

    Returns:
        Public HTTPS URL for the uploaded image.
    """
    clean_prompt = (
        f"{prompt.strip()}. "
        "Style: clean, modern minimalist vector illustration with vibrant friendly colors. "
        "Strict visual constraint: Absolutely NO text, NO numbers, NO letters, and NO symbols in the image."
    )

    client = google.genai.Client(
        vertexai=True,
        project=FIRESTORE_PROJECT_ID,
        location="global",
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=clean_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    candidate = response.candidates[0]
    image_bytes = None
    mime_type = "image/png"

    for part in candidate.content.parts:
        if part.inline_data:
            image_bytes = part.inline_data.data
            if part.inline_data.mime_type:
                mime_type = part.inline_data.mime_type
            break

    if not image_bytes:
        raise RuntimeError("No image data returned from gemini-3.1-flash-lite-image")

    # Save via tool_context if available
    filename = f"{context_label}_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4)}.png"
    if tool_context is not None:
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)
        except Exception:
            pass

    # Upload directly to public GCS bucket
    storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
    bucket = storage_client.bucket(GCS_ASSETS_BUCKET)
    blob_name = f"images/{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{GCS_ASSETS_BUCKET}/{blob_name}"
    return public_url
