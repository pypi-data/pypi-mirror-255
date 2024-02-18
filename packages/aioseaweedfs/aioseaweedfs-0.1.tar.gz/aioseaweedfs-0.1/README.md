# aioseaweedfs

This is an asyncio client for [seaweedfs](https://github.com/seaweedfs/seaweedfs).

## Installation

`pip install aioseaweedfs`

## Basic Usage

```python
import aioseaweedfs

async def main():
    master = aioseaweedfs.Master()

    volume, file_ids = await master.get_assign_key()

    await volume.post(file_ids[0], "File Content")

    content = await volume.get(file_ids[0])
```

## Filer Usage

```python
filer = aioseaweedfs.Filer()

await filer.post("/some/path/to/file.txt", "file contents", content_type="text/plain")

contents = await filer.get("/some/path/to/file.txt")
# contents will always be bytes
```

