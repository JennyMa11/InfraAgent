import importlib.util
from pathlib import Path

from infra_rag.config import Settings
from infra_rag.grid_v2 import Arm
from infra_rag.models import Chunk
from infra_rag.service import RetrievalService


def test_config_rotation_keeps_each_index_sparse_and_exact_state(tmp_path, monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location("grid_v2_runner", scripts / "run_grid_v2.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    built = []

    def exact(chunks, vectors):
        result = object()
        built.append(result)
        return result

    monkeypatch.setattr(module, "ExactCollection", exact)
    g = module.Grid.__new__(module.Grid)
    g.service = RetrievalService(Settings(data_dir=tmp_path))
    g.lexical_by_index, g.exact_collections, g.ann_collections = {}, {}, {}
    data = {
        name: (
            [Chunk(name, name, "s", name, "infra")],
            [[1.0]],
            tmp_path,
            Settings(data_dir=tmp_path),
        )
        for name in ("I0", "I1")
    }
    g.index = lambda name: data[name]
    g.activate(Arm("I0"))
    sparse, collection = g.service.lexical_cache, g.service.text_collection
    sparse["warmed"] = object()
    g.activate(Arm("I1"))
    assert "warmed" not in g.service.lexical_cache
    g.activate(Arm("I0"))
    assert g.service.lexical_cache is sparse
    assert g.service.text_collection is collection and len(built) == 2
