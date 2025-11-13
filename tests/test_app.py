import sys
from pathlib import Path

import pytest
import pytest_asyncio
import httpx

sys.path.append(str(Path(__file__).resolve().parents[1]))
import main

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch):
    """Point the app at a temporary storage directory for every test."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir()
    monkeypatch.setattr(main, "STORAGE_DIR", storage_dir)
    main.files_stored_counter = 0
    yield


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


async def test_root_lists_available_endpoints(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "File Storage API"
    assert "GET /files" in " ".join(data["endpoints"])


async def test_health_check_reports_status(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "File Storage API"


async def test_list_files_initially_empty(client):
    response = await client.get("/files")
    assert response.status_code == 200
    data = response.json()
    assert data["files"] == []
    assert data["count"] == 0


async def test_store_and_retrieve_file(client):
    upload = await client.post(
        "/files",
        files={"file": ("greeting.txt", b"hello world", "text/plain")},
    )
    assert upload.status_code == 200
    upload_data = upload.json()
    assert upload_data["filename"] == "greeting.txt"
    assert upload_data["size"] == len(b"hello world")

    download = await client.get("/files/greeting.txt")
    assert download.status_code == 200
    assert download.content == b"hello world"
    assert download.headers["content-type"] == "application/octet-stream"


async def test_metrics_track_files_and_storage(client):
    await client.post("/files", files={"file": ("one.txt", b"1", "text/plain")})
    await client.post("/files", files={"file": ("two.txt", b"22", "text/plain")})

    metrics = await client.get("/metrics")
    assert metrics.status_code == 200
    data = metrics.json()
    assert data["files_stored_total"] == 2
    assert data["files_current"] == 2
    assert data["total_storage_bytes"] == 3
