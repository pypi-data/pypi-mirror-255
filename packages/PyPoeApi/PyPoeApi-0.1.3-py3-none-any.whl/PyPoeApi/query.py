# @Time    : 2023/10/21 15:13
# @Author  : fyq
# @File    : query.py
# @Software: PyCharm

from __future__ import annotations

__author__ = 'fyq'

import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, MutableMapping, List, Tuple, Type

from aiohttp import ClientSession

from exception import PoeException

query_fetch_list: List[QueryFetch] = []


@dataclass
class QueryParam:
    file_id: str = ""

    key: str = ""

    id: str = ""

    metadata: dict = field(default_factory=lambda: dict())

    name: str = ""

    operationKind: str = ""

    text: str = ""


class QueryManager(MutableMapping[str, QueryParam]):

    def __init__(self):
        self.queries: Dict[str, QueryParam] = {}

    def __setitem__(self, key, value):
        self.queries[key] = value

    def __getitem__(self, item):
        if item not in self.queries:
            raise PoeException(f"查询名称[{item}]不存在")
        return self.queries[item]

    def __len__(self):
        return len(self.queries)

    def __iter__(self):
        return iter(self.queries)

    def __delitem__(self, key):
        del self.queries[key]


class QueryFetch(metaclass=ABCMeta):

    @abstractmethod
    async def fetch(self, asset_prefix: str, text: str, client: ClientSession) -> List[Tuple[str, str]]:
        pass

    def __init_subclass__(cls, **kwargs):
        query_fetch_list.append(cls())


class HomeQueryFetch(QueryFetch):

    async def fetch(self, asset_prefix: str, text: str, client: ClientSession) -> List[Tuple[str, str]]:
        chunks_prefix = f"{asset_prefix}/_next/static/chunks/"
        query_file_id_regex = ('<script src="'
                               + chunks_prefix
                               + r'([\d]{3,4})-([\w]{16}).js" defer(="")?></script>')
        query_file_urls = []
        for query_file_id_1, query_file_id_2, _ in re.findall(query_file_id_regex, text):
            query_file_urls.append(
                (query_file_id_1, f"{chunks_prefix}{query_file_id_1}-{query_file_id_2}.js")
            )
        return query_file_urls


class BuildManifestQueryFetch(QueryFetch):

    async def fetch(self, asset_prefix: str, text: str, client: ClientSession) -> List[Tuple[str, str]]:
        static_prefix = f"{asset_prefix}/_next/static/"
        build_manifest_id_regex = ('<script src="'
                                   + f"{static_prefix}"
                                   + r'([\w-]{20,22}/_buildManifest).js" defer(="")?></script>')
        build_manifest_id_text = re.search(build_manifest_id_regex, text).group(1)
        response = await client.get(f"{static_prefix}{build_manifest_id_text}.js")
        build_manifest_text = await response.text()
        chats_id_regex = (f"static/chunks/pages/"
                          + r'(chats-[\w]{16}).js"')
        chats_id_text = re.search(chats_id_regex, build_manifest_text).group(1)
        return [("chats", f"{static_prefix}chunks/pages/{chats_id_text}.js")]


class AppQueryFetch(QueryFetch):

    async def fetch(self, asset_prefix: str, text: str, client: ClientSession) -> List[Tuple[str, str]]:
        chunks_prefix = f"{asset_prefix}/_next/static/chunks/"
        app_id_regex = ('<script src="'
                        + f"{chunks_prefix}pages/"
                        + r'(_app-[\w]{16}).js" defer(="")?></script>')
        app_id = re.search(app_id_regex, text).group(1)
        return [("_app", f"{chunks_prefix}pages/{app_id}.js")]


class WebpackQueryFetch(QueryFetch):

    async def fetch(self, asset_prefix: str, text: str, client: ClientSession) -> List[Tuple[str, str]]:
        chunks_prefix = f"{asset_prefix}/_next/static/chunks/"
        webpack_id_regex = ('<script src="'
                            + chunks_prefix
                            + r'(webpack-[\w]{16}).js" defer(="")?></script>')
        webpack_id = re.search(webpack_id_regex, text).group(1)
        webpack_response = await client.get(f"{chunks_prefix}{webpack_id}.js")
        webpack_text = await webpack_response.text()
        webpack_require_u = re.search(r'__webpack_require__.u(.+?)".css"', webpack_text).group(1)
        query_file_urls = []
        for query_file_id_1, query_file_id_2 in re.findall(r'static/chunks/([\d]{1,4})-([\w]{16}).js',
                                                           webpack_require_u):
            query_file_urls.append(
                (query_file_id_1, f"{chunks_prefix}{query_file_id_1}-{query_file_id_2}.js")
            )

        for query_file_id_1, query_file_id_2 in re.findall(r'([\d]{1,4}):"([\w]{16})"', webpack_require_u):
            query_file_urls.append(
                (query_file_id_1, f"{chunks_prefix}{query_file_id_1}.{query_file_id_2}.js")
            )
        return query_file_urls


if __name__ == "__main__":
    qm = QueryManager()
    print(len(qm))
