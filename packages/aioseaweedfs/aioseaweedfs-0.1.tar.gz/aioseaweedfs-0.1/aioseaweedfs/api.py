"""
asyncio client for seaweedfs

Use `Master("http://master-url")` to interact with a seaweedfs master server
Use `Filer("http://filer-url")` to interact with the filer
"""
import aiohttp
import asyncio
import random
from urllib.parse import urljoin


__all__ = ("Filer", "Master", "Volume")


class Filer:
    def __init__(
        self,
        url: str = "http://localhost:8888",
        session: aiohttp.ClientSession = None,
        headers=None,
        basic_auth: aiohttp.BasicAuth = None,
    ):
        self.url = url
        self._session = session or aiohttp.ClientSession(
            headers=headers or {}, auth=basic_auth
        )

    async def get(self, path: str):
        async with self._session.get(urljoin(self.url, path)) as r:
            if r.status != 200:
                return False
            return await r.read()

    async def head(self, path: str):
        async with self._session.head(urljoin(self.url, path)) as r:
            return r.status == 200

    async def post(
        self,
        path: str,
        content,
        content_type: str = "application/octet-stream",
        collection: str = None,
        replication: str = None,
        data_center: str = None,
        rack: str = None,
        ttl: str = None,
        tags: dict = None,
        save_inside=False,
        append=False,
    ):
        """
        Post to a file

        content can be str/bytes/open file
        if append=True, append content to the file
        if save_inside=True, content will be saved in the filer metadata
        """
        form = aiohttp.FormData()
        form.add_field("file", content, content_type=content_type)
        headers = {}

        url = urljoin(self.url, path)

        params = {}
        if collection:
            params["collection"] = collection
        if replication:
            params["replication"] = replication
        if data_center:
            params["dataCenter"] = data_center
        if rack:
            params["rack"] = rack
        if ttl:
            params["ttl"] = ttl
        if append:
            params["op"] = "append"
        params["saveInside"] = str(save_inside).lower()
        if tags:
            headers.update(self._tags_to_headers(tags))
        async with self._session.post(
            url, data=form, headers=headers, params=params
        ) as r:
            data = await r.json()
            return data

    async def delete(self, path: str, recursive=False, ignore_errors=False):
        """
        Delete file at `path`
        """
        params = {}
        if recursive:
            params["recursive"] = "true"
            params["ignoreRecursiveError"] = str(ignore_errors).lower()
        async with self._session.delete(urljoin(self.url, path), params=params) as r:
            return r.status == 204

    async def mv(self, from_path: str, to_path: str):
        """
        Move file from `from_path` to `to_path`
        """
        params = {"mv.from": from_path}
        async with self._session.post(urljoin(self.url, to_path), params=params) as r:
            return r.status == 204

    async def ls(self, dirname: str, raw=True):
        """
        List a directory
        if raw=False, return only a list of names
        """
        if not dirname.endswith("/"):
            dirname += "/"
        headers = {"Accept": "application/json"}
        async with self._session.get(urljoin(self.url, dirname), headers=headers) as r:
            if r.status == 200:
                data = await r.json()
                if raw:
                    return data
                else:
                    return [
                        c["FullPath"].replace(dirname, "", 1) for c in data["Entries"]
                    ]
            else:
                return False

    def _tags_to_headers(self, tags: dict):
        headers = {}
        for tag, value in tags.items():
            headers["Seaweed-%s" % tag.capitalize().replace(" ", "_")] = value
        return headers

    def _headers_to_tags(self, headers: dict):
        tags = {}
        for header, value in headers.items():
            if header.startswith("Seaweed-"):
                tags[header.replace("Seaweed-", "").lower().replace("_", " ")] = value
        return tags

    async def set_tags(self, path: str, tags: dict):
        """
        Set tags on the file.
        if `tags` is empty, the tags will be deleted
        """
        headers = {}
        params = {"tagging": ""}
        if tags:
            method = "PUT"
            headers.update(self._tags_to_headers(tags))
        else:
            method = "DELETE"

        async with self._session.request(
            method, urljoin(self.url, path), headers=headers, params=params
        ) as r:
            content = await r.read()
            return r.status == 202

    async def get_tags(self, path: str):
        """
        Get tags for the file
        """
        async with self._session.head(urljoin(self.url, path)) as r:
            return self._headers_to_tags(r.headers)

    async def close(self):
        await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class Volume:
    def __init__(self, url: str, session: aiohttp.ClientSession = None):
        self.url = url
        self._session = session or aiohttp.ClientSession()

    def __repr__(self):
        return f"Volume({self.url})"

    async def get(self, file_id: str) -> bytes:
        """
        Return the contents of the given file_id
        """
        async with self._session.get(urljoin(self.url, file_id)) as r:
            return await r.read()

    async def post(
        self, file_id: str, content, content_type: str = "application/octet-stream"
    ) -> int:
        """
        Post content to file_id
        content can be str/bytes/open file

        Returns size of saved file
        """
        headers = {}
        form = aiohttp.FormData()
        form.add_field("file", content, content_type=content_type)
        async with self._session.post(
            urljoin(self.url, file_id), data=form, headers=headers
        ) as r:
            body = await r.json()
        return body["size"]

    async def delete(self, file_id: str):
        """
        Delete the given file_id
        """
        async with self._session.delete(urljoin(self.url, file_id)) as r:
            return r.status == 202

    async def close(self):
        await self._session.close()


class Master:
    def __init__(
        self,
        url="http://localhost:9333",
        headers=None,
        basic_auth: aiohttp.BasicAuth = None,
    ):
        self._scheme = url.split("://")[0] + "://"
        self.url = url

        self._assign_url = urljoin(self.url, "/dir/assign")
        self._lookup_url = urljoin(self.url, "/dir/lookup")
        self._session = aiohttp.ClientSession(auth=basic_auth, headers=headers or {})
        self._volume_cache = {}

    async def get_assign_key(
        self,
        count: int = 1,
        collection: str = None,
        replication: str = None,
        data_center: str = None,
        rack: str = None,
        ttl: str = None,
        use_public=False,
    ):
        params = {
            "count": count,
        }
        if collection:
            params["collection"] = collection
        if replication:
            params["replication"] = replication
        if data_center:
            params["dataCenter"] = data_center
        if rack:
            params["rack"] = rack
        if ttl:
            params["ttl"] = ttl
        async with self._session.get(self._assign_url, params=params) as r:
            body = await r.json()
            headers = r.headers

        if "authorization" in headers:
            self._session.headers["authorization"] = headers["authorization"]
        fid = body["fid"]
        fids = [fid]

        if count > 1:
            for c in range(1, count):
                fids.append(fid + "_%d" % c)
        volume_url = self._scheme + body["publicUrl" if use_public else "url"]
        return Volume(volume_url, session=self._session), fids

    async def get_volume(self, fid_or_volume: str, use_public=False) -> Volume:
        volume = fid_or_volume.split(",", 1)[0]
        volume_url = self._volume_cache.get(volume, None)
        if volume_url is None:
            params = {"volumeId": volume}
            async with self._session.get(self._lookup_url, params=params) as r:
                body = await r.json()
            self._volume_cache[volume] = volume_url = (
                self._scheme
                + random.choice(body["locations"])["publicUrl" if use_public else "url"]
            )
        return Volume(volume_url, session=self._session)

    async def delete_collection(self, collection):
        async with self._session.get(
            urljoin(self.url, "/col/delete"), params={"collection": collection}
        ) as r:
            return r.status == 200

    async def close(self):
        await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
