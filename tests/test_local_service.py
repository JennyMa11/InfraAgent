import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from infra_rag.api import create_app
from infra_rag.config import Settings
from infra_rag.service import RetrievalService


@pytest.fixture
def launcher(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location("local_launcher", scripts / "serve_local.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_local_index_copies_snapshot_and_preserves_source_and_runtime(launcher, tmp_path):
    source = tmp_path / "frozen/index.json"
    source.parent.mkdir()
    original = json.dumps({"fingerprint": Settings(backend="bge").fingerprint()})
    source.write_text(original)
    (source.parent / "conversations.sqlite3").write_text("private conversation")
    runtime = tmp_path / "runtime"
    settings = launcher.runtime_settings(source, runtime)
    assert settings.fingerprint() == Settings(backend="bge").fingerprint()
    assert settings.rerank and settings.candidate_k == 30
    assert settings.query_language == "none"
    assert not (runtime / "conversations.sqlite3").exists()
    snapshot = runtime / "index.json"
    snapshot.write_text(json.dumps({"fingerprint": settings.fingerprint(), "sentinel": True}))
    launcher.runtime_settings(source, runtime)
    assert json.loads(snapshot.read_text())["sentinel"]
    assert source.read_text() == original
    with pytest.raises(ValueError, match="separate runtime"):
        launcher.runtime_settings(source, source.parent)


def test_optional_web_mount_preserves_api_and_cannot_serve_parent_files(tmp_path):
    web = tmp_path / "web"
    web.mkdir()
    (web / "index.html").write_text("<h1>InfraAgent UI</h1>")
    (web / "app.js").write_text("console.log('ready')")
    (tmp_path / "private.txt").write_text("must not be served")
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    assistant = SimpleNamespace(status=lambda: {"model": "fake", "provider": "test"})
    with TestClient(create_app(service, assistant, web_dir=web)) as client:
        assert "InfraAgent UI" in client.get("/").text
        assert client.get("/app.js").status_code == 200
        assert client.get("/health").json()["assistant"]["model"] == "fake"
        assert client.get("/sources").json() == {"sources": []}
        assert client.post("/chat", json={"message": ""}).status_code == 422
        assert client.get("/%2e%2e/private.txt").status_code == 404
    with TestClient(create_app(service, assistant)) as client:
        assert client.get("/").status_code == 404
