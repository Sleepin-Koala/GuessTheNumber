"""Diffusion en temps reel (WebSocket) des changements de salles de duel + suivi des deconnexions.

Le serveur est le seul a decider de l'etat: les actions (cacher, deviner...) restent des requetes HTTP
validees; chaque changement est ensuite *pousse* aux sockets concernees.
Limite connue: l'annuaire de connexions est en memoire, donc un seul processus serveur (pour plusieurs
processus il faudrait un bus type Redis pub/sub).
"""
import asyncio
import threading
from collections import defaultdict
from typing import Optional

from fastapi import WebSocket


class Hub:
    def __init__(self) -> None:
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.rooms: dict[str, dict[WebSocket, str]] = defaultdict(dict)   # room_id -> {socket: player_id}
        self.lobby: set[WebSocket] = set()
        self.grace: dict[tuple[str, str], float] = {}                     # (room_id, player_id) -> echeance
        self.ips: dict[WebSocket, str] = {}                               # socket -> adresse (limite de connexions par IP)
        # lu par la boucle asyncio ET par les threads des routes / du balayeur
        self._lock = threading.Lock()

    def bind(self, loop: Optional[asyncio.AbstractEventLoop]) -> None:
        self.loop = loop

    # ---- appels depuis le code synchrone des routes (threads) ----
    def _schedule(self, coro) -> None:
        if self.loop is None or self.loop.is_closed():
            coro.close()
            return
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def publish_room(self, room_id: str, payload: dict) -> None:
        with self._lock:
            sockets = list(self.rooms.get(room_id, {}))
        if sockets:
            self._schedule(self._send(sockets, payload))

    def publish_lobby(self, payload: dict) -> None:
        with self._lock:
            sockets = list(self.lobby)
        if sockets:
            self._schedule(self._send(sockets, payload))

    # ---- connexions par adresse ----
    def track(self, ws: WebSocket, ip: str) -> None:
        with self._lock:
            self.ips[ws] = ip

    def connections_from(self, ip: str) -> int:
        with self._lock:
            return sum(1 for v in self.ips.values() if v == ip)

    # ---- presence ----
    def online(self, room_id: str) -> list[str]:
        with self._lock:
            return sorted(set(self.rooms.get(room_id, {}).values()))

    def is_online(self, room_id: str, player_id: str) -> bool:
        return player_id in self.online(room_id)

    # ---- delai de grace apres une deconnexion ----
    def set_grace(self, room_id: str, player_id: str, deadline: float) -> None:
        with self._lock:
            self.grace[(room_id, player_id)] = deadline

    def clear_grace(self, room_id: str, player_id: str) -> bool:
        with self._lock:
            return self.grace.pop((room_id, player_id), None) is not None

    def graces_for(self, room_id: str) -> list[tuple[str, float]]:
        with self._lock:
            return [(p, d) for (r, p), d in self.grace.items() if r == room_id]

    def expired_graces(self, now: float) -> list[tuple[str, str, float]]:
        with self._lock:
            return [(r, p, d) for (r, p), d in self.grace.items() if d <= now]

    # ---- cote asynchrone ----
    async def _send(self, sockets: list, payload: dict) -> None:
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                self.drop(ws)

    def drop(self, ws: WebSocket) -> None:
        with self._lock:
            self.ips.pop(ws, None)
            self.lobby.discard(ws)
            for room_id in list(self.rooms):
                self.rooms[room_id].pop(ws, None)
                if not self.rooms[room_id]:
                    del self.rooms[room_id]

    async def join_room(self, room_id: str, ws: WebSocket, player_id: str) -> None:
        with self._lock:
            self.rooms[room_id][ws] = player_id
            sockets = list(self.rooms[room_id])
        await self._send(sockets, {"type": "presence", "online": self.online(room_id)})

    async def leave_room(self, room_id: str, ws: WebSocket) -> None:
        self.drop(ws)
        with self._lock:
            sockets = list(self.rooms.get(room_id, {}))
        if sockets:
            await self._send(sockets, {"type": "presence", "online": self.online(room_id)})


hub = Hub()
