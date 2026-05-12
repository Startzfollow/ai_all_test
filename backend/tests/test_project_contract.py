from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app


ROOT = Path(__file__).resolve().parents[2]


def test_required_repository_files_exist():
    required = [
        "README.md",
        "QUICKSTART.md",
        "PROJECT_COVERAGE.md",
        "docs/architecture.md",
        "configs/default.yaml",
        "scripts/run_mini_demo.py",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert not missing, f"Missing required project files: {missing}"


def test_gitignore_excludes_large_artifacts():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required_patterns = ["*.pt", "*.onnx", "*.engine", "__pycache__/", "outputs/"]
    missing = [pattern for pattern in required_patterns if pattern not in gitignore]
    assert not missing, f".gitignore should exclude large/generated artifacts: {missing}"


def test_root_endpoint_declares_core_modules():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    modules = response.json().get("modules", [])
    for expected in ["RAG", "GUI Agent", "LLaVA/VLM", "YOLO acceleration"]:
        assert expected in modules
