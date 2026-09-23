"""Create a serverless Vertex AI RAG corpus for Futurewise and index IRS/CFPB docs.
"""

from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr
import vertexai
import time

PROJECT_ID = "qwiklabs-gcp-04-7459370ad109"
LOCATION = "us-central1"
GCS_PATH = "gs://futurewise-assets-qwiklabs-gcp-04-7459370ad109/rag/"

PARSING_PROMPT = (
    "Extract clear financial guidance, definitions, rules, contribution limits, "
    "qualifications, and tax consequences from IRS Publication 590-A (IRAs), "
    "IRS Publication 969 (HSAs, FSAs, HRAs, MSAs), and CFPB Your Money Your Goals. "
    "Omit boilerplate and form instructions. Output clean, self-contained educational prose."
)

def create_and_index_corpus():
    print(f"Initializing Vertex AI for project={PROJECT_ID}, location={LOCATION}...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print("Step 1: Setting RAG engine managed DB config to serverless mode...")
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    try:
        rag.update_rag_engine_config(
            rag_engine_config=rag.RagEngineConfig(
                name=cfg,
                rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
            )
        )
        print("  ✓ Serverless mode enabled successfully.")
    except Exception as e:
        print(f"  Note during serverless config update: {e}")

    print("Step 2: Checking existing corpora or creating new corpus...")
    corpus_name = None
    try:
        existing = rag.list_corpora()
        for c in existing:
            if "futurewise" in c.display_name.lower():
                corpus_name = c.name
                print(f"  Found existing corpus: {corpus_name} ({c.display_name})")
                break
    except Exception as e:
        print(f"  Could not list corpora: {e}")

    if not corpus_name:
        print("  Creating new serverless corpus: futurewise-financial-docs...")
        corpus = rag.create_corpus(
            display_name="futurewise-financial-docs",
            embedding_model_config=rag.EmbeddingModelConfig(
                publisher_model="publishers/google/models/text-embedding-005"
            ),
        )
        corpus_name = corpus.name
        print(f"  ✓ Created corpus: {corpus_name}")

    print("Step 3: Importing documents into corpus...")
    txt_paths = [
        f"{GCS_PATH}cfpb_toolkit.txt",
        f"{GCS_PATH}p590a.txt",
        f"{GCS_PATH}p969.txt",
    ]
    try:
        resp = rag.import_files(
            corpus_name=corpus_name,
            paths=txt_paths,
            transformation_config=rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
            ),
            llm_parser=rag.LlmParserConfig(
                model_name="gemini-3.6-flash",
                custom_parsing_prompt=PARSING_PROMPT,
            ),
        )
        print(f"  ✓ Imported files response: {resp}")
    except Exception as e:
        print(f"  Warning on LLM parser import: {e}. Falling back to default parser...")
        resp = rag.import_files(
            corpus_name=corpus_name,
            paths=txt_paths,
            transformation_config=rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
            ),
        )
        print(f"  ✓ Fallback import response: {resp}")

    print("\nWaiting 10s for initial index propagation...")
    time.sleep(10)

    print("Step 4: Testing retrieval query...")
    test_query = "What is the difference between an HSA and an FSA?"
    resp = rag.retrieval_query(
        text=test_query,
        rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
        rag_retrieval_config=rag.RagRetrievalConfig(top_k=3),
    )
    contexts = getattr(resp.contexts, "contexts", [])
    print(f"  Retrieved {len(contexts)} contexts for '{test_query}':")
    for i, c in enumerate(contexts):
        score = getattr(c, "score", 0.0)
        text_snippet = getattr(c, "text", "")[:150].replace("\n", " ")
        print(f"  [{i+1}] (score={score:.3f}): {text_snippet}...")

    print(f"\nSUCCESS! Corpus resource name: {corpus_name}")
    return corpus_name

if __name__ == "__main__":
    create_and_index_corpus()
