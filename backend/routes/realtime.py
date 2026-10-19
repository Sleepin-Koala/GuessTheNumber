"""Diffusion en temps reel (WebSocket) des changements de salles de duel.

Le serveur est le seul a decider de l'etat: les actions (cacher, deviner...) restent des requetes HTTP
validees; chaque changement est ensuite *pousse* aux sockets concernees.
Limite connue: l'annuaire de connexions est en memoire, donc un seul processus serveur (pour plusieurs
processus il faudrait un bus type Redis pub/sub).
"""
import asyncio
from collections import defaultdict
from typing import Optional

from fastapi import WebSocket


class Hub:
    def __init__(self) -> None:
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.rooms: dict[str, dict[WebSocket, str]] = defaultdict(dict)   # room_id -> {socket: player_id}
        self.lobby: set[WebSocket] = set()

    def bind(self, loop: Optional[asyncio.AbstractEventLoop]) -> None:
        self.loop = loop

    # ---- appels depuis le code synchrone des routes (threads) ----
    def _schedule(self, coro) -> None:
        if self.loop is None or self.loop.is_closed():
            coro.close()
            return
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def publish_room(self, room_id: str, payload: dict) -> None:
        if room_id in self.rooms:
            self._schedule(self._send(list(self.rooms[room_id]), payload))

    def publish_lobby(self, payload: dict) -> None:
        if self.lobby:
            self._schedule(self._send(list(self.lobby), payload))

    # ---- cote asynchrone ----
    async def _send(self, sockets: list, payload: dict) -> None:
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                self.drop(ws)

    def drop(self, ws: WebSocket) -> None:
        self.lobby.discard(ws)
        for room_id in list(self.rooms):
            self.rooms[room_id].pop(ws, None)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    def online(self, room_id: str) -> list[str]:
        return sorted(set(self.rooms.get(room_id, {}).values()))

    async def join_room(self, room_id: str, ws: WebSocket, player_id: str) -> None:
        self.rooms[room_id][ws] = player_id
        await self._send(list(self.rooms[room_id]), {"type": "presence", "online": self.online(room_id)})

    async def leave_room(self, room_id: str, ws: WebSocket) -> None:
        self.drop(ws)
        if room_id in self.rooms:
            await self._send(list(self.rooms[room_id]), {"type": "presence", "online": self.online(room_id)})


hub = Hub()
