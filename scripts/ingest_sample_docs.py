from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.services.rag_service import RagService

if __name__ == "__main__":
    service = RagService()
    result = service.ingest_dir("examples/docs")
    print(result)
