import pytest
import uuid

from aioseaweedfs import Master, Volume, Filer

COLLECTION = "test-%s" % uuid.uuid1().hex


@pytest.fixture(scope="session", autouse=True)
async def clear_collection():
    yield
    async with Master("http://127.0.0.1:9333") as m:
        await m.delete_collection(COLLECTION)
    async with Filer("http://127.0.0.1:8888") as f:
        await f.delete("/test/", recursive=True, ignore_errors=True)


@pytest.fixture
async def filer():
    async with Filer("http://127.0.0.1:8888") as f:
        yield f


@pytest.fixture(scope="function")
async def master():
    async with Master("http://127.0.0.1:9333") as m:
        yield m


async def test_filer_post(filer):
    fname = f"/test/{uuid.uuid1()}"
    response = await filer.post(
        fname, "hello world", collection=COLLECTION, ttl="5m", replication="000"
    )
    assert response["size"] == 11


async def test_filer_get_head(filer):
    fname = f"/test/{uuid.uuid1()}"
    response = await filer.post(
        fname, "test_filer_get", collection=COLLECTION, ttl="5m"
    )
    assert response
    retrieved = await filer.get(fname)
    assert retrieved == b"test_filer_get"

    retrieved = await filer.head(fname)
    assert retrieved == True

    missing = await filer.head(fname + "missing")
    assert missing == False

    missing = await filer.get(fname + "missing")
    print(missing)
    assert missing == False


async def test_filer_list(filer):
    fnames = set(
        [
            f"/test/{uuid.uuid1()}",
            f"/test/{uuid.uuid1()}",
            f"/test/{uuid.uuid1()}",
        ]
    )
    for fname in fnames:
        response = await filer.post(
            fname, "hello world", collection=COLLECTION, ttl="5m"
        )
        assert response

    contents = await filer.ls("/test/")
    for entry in contents["Entries"]:
        if entry["FullPath"] in fnames:
            fnames.remove(entry["FullPath"])
    assert fnames == set()

    contents = await filer.ls("/test/", raw=False)
    assert all(isinstance(c, str) for c in contents)

    contents = await filer.ls("/test/empty")
    assert not contents
    contents = await filer.ls("/test/empty/", raw=False)
    assert not contents


async def test_filer_delete(filer):
    path = f"/test/{uuid.uuid1()}"
    await filer.post(path, "stuff", collection=COLLECTION, ttl="5m", save_inside=True)
    response = await filer.delete(path)
    assert response == True
    response = await filer.delete(path)
    assert response == False


async def test_filer_move(filer):
    path = f"/test/{uuid.uuid1()}"
    await filer.post(path, "stuff", collection=COLLECTION, ttl="5m")
    target = f"/test/moved/{uuid.uuid1()}"
    moved = await filer.mv(path, target)
    assert moved
    content = await filer.get(target)
    assert content == b"stuff"


async def test_filer_tagging(filer):
    path = f"/test/{uuid.uuid1()}"
    await filer.post(path, "tagged", collection=COLLECTION, ttl="5m")

    tags = {"tag1": "This is Tag 1", "tag 2": "This is Tag 2"}
    tagged = await filer.set_tags(path, tags)
    assert tagged

    stored_tags = await filer.get_tags(path)
    assert stored_tags == tags

    deleted = await filer.set_tags(path, {})
    assert deleted

    stored_tags = await filer.get_tags(path)
    assert stored_tags == {}


async def test_filer_append(filer):
    path = f"/test/{uuid.uuid1()}"
    await filer.post(
        path, "hello", collection=COLLECTION, ttl="5m", tags={"appending": "now"}
    )
    response = await filer.post(
        path, " world!", collection=COLLECTION, ttl="5m", append=True
    )
    assert response

    content = await filer.get(path)
    assert content == b"hello world!"


async def test_master_basic(master):
    volume, fids = await master.get_assign_key(count=2)
    assert len(fids) == 2
    print(fids)


async def test_post_file(master):
    volume, fids = await master.get_assign_key(
        count=1, replication="000", collection=COLLECTION, ttl="5m"
    )
    content = uuid.uuid1().hex
    response = await volume.post(fids[0], content)
    assert response == len(content)
    assert repr(volume) == "Volume(http://127.0.0.1:8080)"


async def test_post_multiple(master):
    volume, fids = await master.get_assign_key(
        count=8, replication="000", collection=COLLECTION, ttl="5m"
    )
    content = uuid.uuid1().hex

    assert len(fids) == 8
    for fid in fids:
        response = await volume.post(fid, content)
        assert response == 32


async def test_post_ttl(master):
    volume, fids = await master.get_assign_key(
        count=8, replication="000", collection=COLLECTION, ttl="5m"
    )
    content = uuid.uuid1().hex

    assert len(fids) == 8
    for fid in fids:
        response = await volume.post(fid, content)
        assert response == 32


async def test_get_file(master):
    volume, fids = await master.get_assign_key(
        count=1, replication="000", collection=COLLECTION, ttl="5m"
    )
    content = uuid.uuid1().hex.encode()
    response = await volume.post(fids[0], content)

    assert response

    volume = await master.get_volume(fids[0])
    response = await volume.get(fids[0])
    assert response == content


async def test_delete_file(master):
    volume, fids = await master.get_assign_key(
        count=1, replication="000", collection=COLLECTION, ttl="5m"
    )
    content = uuid.uuid1().hex.encode()
    response = await volume.post(fids[0], content)

    assert response

    response = await volume.delete(fids[0])
    assert response == True

    response = await volume.delete("missing")
    assert response == False
