from __future__ import annotations

import asyncio
import datetime
import hashlib
import json
import os
import random
import re
import secrets
import sys
import time
import uuid
from dataclasses import dataclass
from functools import wraps
from subprocess import Popen, PIPE
from typing import Dict, List, Optional, Any

import aiofiles
import aiohttp
import execjs
import six
import yaml
from aiohttp.http_websocket import WS_CLOSED_MESSAGE, WS_CLOSING_MESSAGE
from aiohttp_socks import ProxyConnector
from execjs import ExternalRuntime
from loguru import logger

from PyPoeApi.exception import PoeException, ReachedLimitException
from PyPoeApi.query import QueryManager, QueryParam, query_fetch_list

__version__ = "0.1.6"


class _UTF8Context(ExternalRuntime.Context):

    def _exec_with_pipe(self, source):
        cmd = getattr(getattr(self, "_runtime"), "_binary")()

        try:
            p = Popen(cmd,
                      stdin=PIPE,
                      stdout=PIPE,
                      stderr=PIPE,
                      cwd=self._cwd,
                      encoding="utf-8",
                      universal_newlines=True)
            var_input = self._compile(source)
            if six.PY2:
                var_input = var_input.encode(sys.getfilesystemencoding())
            std_out_data, std_err_data = p.communicate(input=var_input)
            ret = p.wait()
        finally:
            del p

        self._fail_on_non_zero_status(ret, std_out_data, std_err_data)
        return std_out_data


def _generate_nonce(length: int = 16):
    return secrets.token_hex(length // 2)


@dataclass
class Chat:
    # 会话标识
    chat_id: int = None


@dataclass
class _Message:
    # 会话标识
    chat_id: int
    # 消息标识
    message_id: int
    # 文本
    text: str
    # 是否完结
    finished: bool
    # 是否human
    human: bool

    def __str__(self):
        return self.text


def async_retry(tries: int = 3):
    """
    记录日志
    :param tries:
    :return:
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            begin_time = time.perf_counter()
            logger.info(f"{'*' * 10}<begin {func.__name__}>{'*' * 10}")
            try:
                for _ in range(tries + 1):
                    await asyncio.sleep(1)
                    try:
                        res = await func(*args, **kwargs)
                        logger.info(f"success to call {func.__name__}")
                        return res
                    except ReachedLimitException as e:
                        logger.warning(f"failed to call {func.__name__} : {str(e)}")
                        raise e
                    except Exception as e:
                        if _ < tries:
                            logger.warning(f"failed to call {func.__name__} : {str(e)}, try {_ + 1} again")
                        else:
                            logger.exception(e)
                            raise PoeException(e)
            finally:
                time.perf_counter() - begin_time
                logger.info(
                    f"{'*' * 10}<end {func.__name__} cost {round(time.perf_counter() - begin_time, 5)}s>{'*' * 10}")

        return wrapper

    return decorator


class PoeClient:
    # human标识
    _HUMAN = "human"
    # 辅助生产sdid
    _CONST_NAMESPACE = uuid.UUID("12345678123456781234567812345678")
    # 通用发送URL
    _GQL_URL = "https://poe.com/api/gql_POST"
    # 首页URL
    _HOME_URL = "https://poe.com"
    # 设置URL
    _SETTING_URL = "https://poe.com/api/settings"
    # 账户文件
    ACCOUNT_FILE: str = ""
    # 账户文件锁
    _ACCOUNT_FILE_LOCK: asyncio.Lock = asyncio.Lock()

    def __init__(self, p_b: str, formkey: str, proxy: Optional[str] = ""):
        # 通道数据
        self.tchannel_data: dict = {}
        # 机器人
        self.bots: Dict = {}
        # 会话
        self.chats: Dict = {}
        # 消息队列
        self.queues: Dict[int, asyncio.Queue] = {}
        # ws任务
        self.ws_task: Optional[asyncio.Task] = None
        # 会话锁
        self.chat_lock: Dict[int, asyncio.Lock] = {}
        # 消息头formkey
        self.formkey: str = formkey
        # cookie p_b
        self.p_b: str = p_b
        # 唯一标识
        self.sdid: str = ""
        # 用户ID
        self.user_id: str = ""
        # ws域名
        self.ws_domain = f"tch{random.randint(1, int(1e6))}"[:8]
        # 代理
        self.proxy = proxy
        # 盐值
        self.salt = "4LxgHM6KpFqokX0Ox"
        # 默认头信息
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 "
                          "Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "poe-formkey": self.formkey,
            "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="112"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Linux"',
            "Upgrade-Insecure-Requests": "1",
        }
        # 查询管理器
        self.query_manager = QueryManager()

    @property
    def channel_url(self):
        """
        ws频道url
        :return: ws频道url
        """
        return (
            f'wss://'
            f'{self.ws_domain}.tch.'
            f'{self.tchannel_data["baseHost"]}/up/'
            f'{self.tchannel_data["boxName"]}/'
            f'updates?min_seq={self.tchannel_data["minSeq"]}&'
            f'channel={self.tchannel_data["channel"]}&'
            f'hash={self.tchannel_data["channelHash"]}'
        )

    @property
    def session_args(self):
        """
        头信息
        :return:
        """
        args = {
            "headers": self.headers,
            "cookies": {"p-b": self.p_b},
        }
        if self.proxy:
            connector = ProxyConnector.from_url(self.proxy)
            args["connector"] = connector
        return args

    def _is_human(self, author: str) -> bool:
        """
        判断是否为人类
        :param author:
        :return:
        """
        return self._HUMAN == author

    async def refresh(self):
        """
        刷新基础信息和机器人
        :return:
        """
        await self._refresh_base_data()
        await self._refresh_bots()

    def bot_names(self) -> List[str]:
        """
        返回所有的机器人
        :return:
        """
        return list(self.bots.keys())

    async def ask(self, bot_name: str, question: str, chat: Chat = None) -> str:
        """
        发送问题
        :param bot_name: 机器人名称
        :param question: 问题
        :param chat: 会话
        :return:
        """
        messages = []
        async for message in self._ask_stream_raw(bot_name=bot_name,
                                                  question=question,
                                                  chat=chat):
            messages.append(message.text)
        return "".join(messages)

    @async_retry()
    async def delete_chat(self, chat_id: int, ignore_error: bool = False):
        """
        删除指定的会话
        :param ignore_error:
        :param chat_id:
        :return:
        """
        try:
            return await self._send_query("useDeleteChat_deleteChat_Mutation", {"chatId": chat_id})
        except Exception as e:
            logger.exception(e)
            if ignore_error:
                pass
            else:
                raise e

    async def delete_chats(self):
        """
        删除所有的会话
        :return:
        """
        await self._refresh_chats()
        for chat_id in list(self.chats.keys()):
            await asyncio.sleep(2)
            await self.delete_chat(chat_id, ignore_error=True)
            self.chats.pop(chat_id, {})

    @async_retry()
    async def _refresh_base_data(self) -> None:
        try:
            async with aiohttp.ClientSession(**self.session_args) as client:
                home_response = await client.get(self._HOME_URL, timeout=8)
                home_text = await home_response.text()

                """get next_data"""
                next_data_regex = (
                    r'<script id="__NEXT_DATA__" type="application\/json">(.+?)</script>'
                )
                next_data_text = re.search(next_data_regex, home_text).group(1)
                next_data = json.loads(next_data_text)

                """extract data from next_data"""
                viewer = next_data["props"]["initialData"]["data"]["pageQuery"][
                    "viewer"
                ]
                self.user_id = viewer["poeUser"]["id"]
                self.sdid = str(uuid.uuid5(self._CONST_NAMESPACE, self.user_id))

                try:
                    query_file_urls = []
                    asset_prefix_regex = (
                        r'"assetPrefix":"(.*?)"'
                    )
                    asset_prefix_text = re.search(asset_prefix_regex, home_text).group(1)
                    for query_fetch in query_fetch_list:
                        query_file_urls.extend(await query_fetch.fetch(asset_prefix=asset_prefix_text,
                                                                       text=home_text,
                                                                       client=client))

                    for query_file_id, query_file_url in query_file_urls:
                        response = await client.get(query_file_url, headers={"Purpose": "prefetch",
                                                                             "Referer": "https://poe.com/"})
                        query_hash_text = await response.text(encoding="utf-8")
                        if '(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).' in query_hash_text:
                            query_hash_text = query_hash_text.replace('"use strict";', '')
                            query_hash_text = query_hash_text.replace('(self.webpackChunk_N_E=self.webpackChunk_N_E'
                                                                      '||[]).',
                                                                      ('function ex() { '
                                                                       'n = (x)=> {};'
                                                                       'n.d = (a1, a2) => {};'
                                                                       'n.r = (x) => {};'
                                                                       'n.n = (x) => {};'
                                                                       'n._ = (x) => {};'
                                                                       'const webpackChunk_N_E = [];webpackChunk_N_E.'))
                            handle = ('const results = [];'
                                      'for (const [key, value] of Object.entries(webpackChunk_N_E[0][1]))'
                                      '{'
                                      'const result = {key: key, params: null, error: null};'
                                      'try'
                                      '{'
                                      'results.push(result);'
                                      'const a = {};'
                                      'const e = {};'
                                      'value(e, a, n);'
                                      'result.params = a?.default?.params || null'
                                      '}'
                                      'catch(e){result.error = e.message}'
                                      '};'
                                      'return results;}')
                            execjs.ExternalRuntime.Context = _UTF8Context
                            ctx = execjs.compile(query_hash_text + handle)
                            try:
                                results: List[Dict] = ctx.call('ex')
                                for result in results:
                                    if "params" in result and result["params"]:
                                        params: Dict = result.get("params", {})
                                        query_param = QueryParam()
                                        query_param.file_id = query_file_id
                                        query_param.key = result.get("key", None)
                                        query_param.text = params.get("text", "")
                                        query_param.name = params.get("name", "")
                                        query_param.id = params.get("id", "")
                                        query_param.metadata = params.get("metadata", {})
                                        query_param.operationKind = params.get("operationKind", "")
                                        self.query_manager[query_param.name] = query_param
                                    elif result["error"]:
                                        pass
                            except Exception as e:
                                logger.exception(str(e))
                finally:
                    pass
        except Exception as e:
            raise Exception("Failed to get hash from home.") from e

    @async_retry()
    async def _refresh_channel_data(self) -> None:
        """
        获取通道信息
        :return:
        """
        async with aiohttp.ClientSession(**self.session_args) as client:
            response = await client.get(self._SETTING_URL)
            data = await response.text()
            json_data = json.loads(data)
            self.tchannel_data = json_data["tchannelData"]
            self.headers["Poe-Tchannel"] = self.tchannel_data["channel"]

    @async_retry()
    async def _refresh_bot(self, bot_name: str):
        """
        刷新单个机器
        :param bot_name:
        :return:
        """
        response = await self._send_query("HandleBotLandingPageQuery", {"botHandle": bot_name})
        self.bots[bot_name] = response["data"]["bot"]

    @async_retry()
    async def _refresh_bots(self):
        """
        刷新机器人
        :return:
        """
        bots = []
        response = await self._send_query(query_name="BotSelectorModalQuery",
                                          variables={})
        while True:
            bots.extend([
                each["node"]
                for each in response["data"]["viewer"]["availableBotsConnection"]["edges"]
                if each["node"]["deletionState"] == "not_deleted"
            ])
            end_cursor, has_next_page = response["data"]["viewer"]["availableBotsConnection"]["pageInfo"].values()
            if has_next_page:
                response = await self._send_query(query_name="availableBotsSelectorModalPaginationQuery",
                                                  variables={
                                                      "cursor": end_cursor,
                                                      "limit": 10
                                                  })
            else:
                break
        self.bots.update(**{bot["handle"]: bot for bot in bots})

    @async_retry()
    async def _refresh_chats(self, bot_name: str = ""):
        """
        刷新会话
        :return:
        """
        response = await self._send_query(query_name="chatsHistoryPageQuery",
                                          variables={
                                              "handle": bot_name,
                                              "useBot": False
                                          })
        while True:
            edges: List = response["data"]["chats"]["edges"]
            end_cursor, has_next_page = response["data"]["chats"]["pageInfo"].values()
            for edge in edges:
                self.chats[edge["node"]["chatId"]] = edge["node"]
            if has_next_page:
                response = await self._send_query(query_name="ChatHistoryListPaginationQuery",
                                                  variables={
                                                      "count": 10,
                                                      "cursor": end_cursor
                                                  })
            else:
                break

    async def _ask_stream_raw(self, bot_name: str, question: str, chat: Chat):
        """
        流式
        :param bot_name: 机器人
        :param question: 问题
        :param chat: 会话id
        :return:
        """
        if chat is None:
            chat = Chat()

        await self._start_ws()
        first_message = await self._send_message_to_chat(bot_name=bot_name,
                                                         chat_id=chat.chat_id,
                                                         question=question)
        chat.chat_id = first_message.chat_id
        if not first_message.human:
            if first_message.text:
                yield first_message
            if first_message.finished:
                return

        if chat.chat_id not in self.chat_lock:
            self.chat_lock[chat.chat_id] = asyncio.Lock()

        async with self.chat_lock[chat.chat_id]:
            q = self._queue(chat_id=chat.chat_id)
            last_text = ""
            times = 0
            while True:
                if q.empty():
                    times += 1
                    if times == 100:
                        raise PoeException("get response time out")
                    await asyncio.sleep(1)
                    continue
                message: _Message = await q.get()
                q.task_done()
                times = 0
                if first_message.human:
                    if message.message_id <= first_message.message_id:
                        continue
                else:
                    if message.message_id != first_message.message_id:
                        continue

                if bot_name == "StableDiffusionXL" or bot_name == "Playground-v2":
                    if message.finished:
                        p = '\\[.+\\]: (.+)\n!\\[.+\\]\\[.+\\]'
                        message.text = re.search(p, message.text).group(1)
                    else:
                        continue

                yield _Message(
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    text=message.text[len(last_text):],
                    finished=message.finished,
                    human=False
                )
                last_text = message.text
                if message.finished:
                    break

    @async_retry()
    async def _send_message_to_chat(self, bot_name: str, chat_id: int, question: str) -> _Message:
        """
        发送问题到一个新的会话
        :param bot_name: 机器人
        :param question: 问题
        :return:
        """
        nickname = self.bots[bot_name]["nickname"]
        message_data = await self._send_query(
            "sendMessageMutation",
            {
                "attachments": [],
                "bot": nickname,
                "chatId": chat_id,
                "clientNonce": _generate_nonce(),
                "query": question,
                "sdid": self.sdid,
                "shouldFetchChat": True,
                "source": {
                    "sourceType": "chat_input",
                    "chatInputMetadata": {"useVoiceRecord": False},
                },

            },
        )

        status = message_data["data"]["messageEdgeCreate"]["status"]
        status_message = message_data["data"]["messageEdgeCreate"]["statusMessage"]
        if status != "success":
            if status == "reached_limit":
                await self._limit(self, bot_name)
                raise ReachedLimitException(f"{bot_name}: {status_message}")
            else:
                raise PoeException(status_message)

        logger.info(f"succeed to send message to {bot_name}")

        chat_data = message_data["data"]["messageEdgeCreate"]["chat"]
        last_edge_node = chat_data["messagesConnection"]["edges"][-1]["node"]

        return _Message(chat_id=chat_data["chatId"],
                        message_id=last_edge_node["messageId"],
                        text=last_edge_node["text"],
                        finished=last_edge_node["state"] == "complete",
                        human=self._is_human(last_edge_node["author"]))

    async def _send_query(self, query_name: str, variables: dict) -> Optional[dict]:
        """
        poe通用查询
        :param query_name: 查询名字
        :param variables: 查询参数
        :return: 查询结果，如果符合失败条件会抛出异常 PoeException
        """
        if query_name not in self.query_manager:
            raise PoeException(f"{query_name}在查询列表中未存在")
        query_param = self.query_manager[query_name]

        data = json.dumps({
            "queryName": query_name,
            "variables": variables,
            "extensions": {"hash": query_param.id},
        }, separators=(",", ":"))
        base_string = data + self.formkey + self.salt
        query_headers = {
            **self.headers,
            "content-type": "application/json",
            "poe-tag-id": hashlib.md5(base_string.encode()).hexdigest(),
        }

        async with aiohttp.ClientSession(**self.session_args) as client:
            logger.info(f"send message for query name: {query_name}")
            response = await client.post(self._GQL_URL, data=data, headers=query_headers)
            resp = await response.text()
            json_data = json.loads(resp)
            if (
                    "success" in json_data.keys()
                    and not json_data["success"]
                    or json_data["data"] is None
            ):
                raise PoeException(json_data["errors"][0]["message"])
            else:
                return json_data

    @async_retry()
    async def _subscribe(self):
        """
        订阅消息 用于在发送消息的时候接收指定类型的消息
        :return:
        """
        await self._send_query(
            "subscriptionsMutation",
            {
                "subscriptions": [
                    {
                        "subscriptionName": "messageAdded",
                        "query": None,
                        "queryHash": "6d5ff500e4390c7a4ee7eeed01cfa317f326c781decb8523223dd2e7f33d3698",
                    },
                    {
                        "subscriptionName": "messageCancelled",
                        "query": None,
                        "queryHash": "dfcedd9e0304629c22929725ff6544e1cb32c8f20b0c3fd54d966103ccbcf9d3",
                    },
                    {
                        "subscriptionName": "messageDeleted",
                        "query": None,
                        "queryHash": "91f1ea046d2f3e21dabb3131898ec3c597cb879aa270ad780e8fdd687cde02a3",
                    },
                    {
                        "subscriptionName": "viewerStateUpdated",
                        "query": None,
                        "queryHash": "ee640951b5670b559d00b6928e20e4ac29e33d225237f5bdfcb043155f16ef54",
                    },
                    {
                        "subscriptionName": "messageLimitUpdated",
                        "query": None,
                        "queryHash": "d862b8febb4c058d8ad513a7c118952ad9095c4ec0a5471540133fc0a9bd3797",
                    },
                    {
                        "subscriptionName": "chatTitleUpdated",
                        "query": None,
                        "queryHash": "740e2c7ab27297b7a8acde39a400b932c71beb7e9b525280fc99c1639f1be93a",
                    },
                ]
            },
        )

    async def _start_ws(self):
        """
        启动ws接收程序
        :return:
        """
        if not self.ws_task or self.ws_task.done():
            await self._refresh_channel_data()
            await self._subscribe()
            self.ws_task = asyncio.create_task(self._put_message())

    async def _put_message(self):
        """
        接收回答放到队列中
        :return:
        """
        async with aiohttp.ClientSession(**self.session_args) as client:
            ws = await client.ws_connect(self.channel_url)
            while True:
                if ws.closed:
                    return
                try:
                    ws_message = await ws.receive(timeout=0.5)
                    if ws_message == WS_CLOSED_MESSAGE or ws_message == WS_CLOSING_MESSAGE:
                        logger.warning(ws_message)
                        return
                    if ws_message.data:
                        data = ws_message.json()
                        if (
                                data.get("error") == "missed_messages"
                                or data.get("message_type") == "refetchChannel"
                        ):
                            await ws.close()
                            logger.warning(ws_message)
                            return
                        messages = [
                            json.loads(message)
                            for message in data.get("messages", "{}")
                            if message
                        ]
                        for message in messages:
                            payload = message.get("payload", {})
                            subscription_name = payload.get("subscription_name")
                            if subscription_name == "messageAdded":
                                chat_id = int(payload.get("unique_id").split(":")[-1])
                                message = (payload.get("data", {})).get(
                                    "messageAdded", {}
                                )
                                if message["author"] != self._HUMAN and len(message["suggestedReplies"]) == 0:
                                    q = self._queue(chat_id)
                                    finished = message.get("state") == "complete"
                                    if finished:
                                        logger.info(ws_message)
                                    await q.put(
                                        _Message(
                                            chat_id=chat_id,
                                            message_id=message.get("messageId"),
                                            text=message.get("text"),
                                            finished=finished,
                                            human=False
                                        )
                                    )
                except asyncio.exceptions.TimeoutError:
                    pass
                except json.decoder.JSONDecodeError:
                    pass
                except Exception as e:
                    logger.error(str(e))
                    return

    def _queue(self, chat_id: int) -> asyncio.Queue:
        if chat_id not in self.queues.keys():
            self.queues[chat_id] = asyncio.Queue(maxsize=1000)
        return self.queues[chat_id]

    @classmethod
    async def create(cls,
                     other: bool = True,
                     playground_v2: bool = False,
                     stable_diffusion_xl: bool = False,
                     claude_instant_100k: bool = False,
                     proxy: str = "http://127.0.0.1:7890") -> Optional[PoeClient]:
        """
        创建初始化
        :param other: 其他限制
        :param playground_v2: playground_v2限制 图片
        :param stable_diffusion_xl: stable_diffusion_xl限制 图片
        :param claude_instant_100k: claude_instant_100k 限制
        :param proxy: 代理
        :return: PoeClient实例
        """
        if account_data := await cls._read_yml_config(cls._ACCOUNT_FILE_LOCK, cls.ACCOUNT_FILE):
            now = datetime.datetime.now()
            now_hour = now.hour
            if now_hour >= int(account_data["hour"]) and now.date() > account_data["date"]:
                account_data["date"] = now.date()
                for account in account_data["accounts"]:
                    account["limit"] = False
                    account["Playground-v2"] = False
                    account["StableDiffusionXL"] = False
                    account["Claude-instant-100k"] = False
                await cls._write_yml_config(cls._ACCOUNT_FILE_LOCK, cls.ACCOUNT_FILE, account_data)
            no_limit_accounts = []
            for account in account_data["accounts"]:
                if other and account["limit"]:
                    continue
                if playground_v2 and account["Playground-v2"]:
                    continue
                if stable_diffusion_xl and account["StableDiffusionXL"]:
                    continue
                if claude_instant_100k and account["Claude-instant-100k"]:
                    continue
                no_limit_accounts.append(account)

            if no_limit_accounts:
                account = no_limit_accounts[0]
                poe_client = PoeClient(p_b=account["p_b"],
                                       formkey=account["formkey"],
                                       proxy=proxy)
                await poe_client.refresh()
                return poe_client
            else:
                raise PoeException("no poe account can use or all limit for this model")

    @classmethod
    async def _limit(cls, poe_client: PoeClient, bot_name: str):
        """
        限制
        :param poe_client:
        :param bot_name:
        :return:
        """
        if account_data := await cls._read_yml_config(cls._ACCOUNT_FILE_LOCK, cls.ACCOUNT_FILE):
            for account in account_data["accounts"]:
                if poe_client.p_b == account["p_b"] and poe_client.formkey == account["formkey"]:
                    if bot_name == "Playground-v2":
                        account["Playground-v2"] = True
                    elif bot_name == "StableDiffusionXL":
                        account["StableDiffusionXL"] = True
                    elif bot_name == "Claude-instant-100k":
                        account["Claude-instant-100k"] = True
                    else:
                        account["limit"] = True
                    break
            await cls._write_yml_config(cls._ACCOUNT_FILE_LOCK, cls.ACCOUNT_FILE, account_data)

    @staticmethod
    async def _read_yml_config(lock: asyncio.Lock, file_path: str) -> Any:
        """
        读取配置文件
        :param lock:
        :param file_path:
        :return:
        """
        if os.path.isfile(file_path):
            async with lock:
                async with aiofiles.open(file_path, "r") as f:
                    return yaml.safe_load(await f.read())
        else:
            raise PoeException("please set account_file")

    @staticmethod
    async def _write_yml_config(lock: asyncio.Lock, file_path: str, data: Any):
        """
        写入配置文件
        :param lock:
        :param file_path:
        :param data:
        :return:
        """
        async with lock:
            async with aiofiles.open(file_path, "w") as f:
                await f.write(yaml.safe_dump(data))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        for chat_id in list(self.queues.keys()):
            await asyncio.sleep(2)
            await self.delete_chat(chat_id, ignore_error=True)
