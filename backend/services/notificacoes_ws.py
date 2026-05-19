"""
AltaCLP — Notificações em tempo real (WebSocket) para técnicos e engenheiros.
"""

import json
import asyncio
from typing import Set, Dict, Any
from fastapi import WebSocket


class NotificationHub:
  def __init__(self):
    self._tecnicos: Dict[str, Set[WebSocket]] = {}
    self._engenheiros: Set[WebSocket] = set()
    self._lock = asyncio.Lock()

  async def connect_tecnico(self, tecnico_id: str, ws: WebSocket):
    await ws.accept()
    async with self._lock:
      self._tecnicos.setdefault(tecnico_id, set()).add(ws)

  async def connect_engenheiro(self, ws: WebSocket):
    await ws.accept()
    async with self._lock:
      self._engenheiros.add(ws)

  async def disconnect_tecnico(self, tecnico_id: str, ws: WebSocket):
    async with self._lock:
      if tecnico_id in self._tecnicos:
        self._tecnicos[tecnico_id].discard(ws)

  async def disconnect_engenheiro(self, ws: WebSocket):
    async with self._lock:
      self._engenheiros.discard(ws)

  async def _broadcast(self, sockets: Set[WebSocket], payload: dict):
    dead = []
    for ws in list(sockets):
      try:
        await ws.send_json(payload)
      except Exception:
        dead.append(ws)
    for ws in dead:
      sockets.discard(ws)

  async def notificar_novo_alarme(
    self,
    alerta: dict,
    tecnico_ids: list[str],
  ):
    payload = {
      "evento": "novo_alerta",
      "alerta": alerta,
      "mensagem": f"Novo alarme: {alerta.get('titulo', 'Alerta')}",
    }
    async with self._lock:
      for tid in tecnico_ids:
        if tid in self._tecnicos:
          await self._broadcast(self._tecnicos[tid], payload)
      await self._broadcast(self._engenheiros, payload)

  async def notificar_submissao_validacao(self, projeto_id: str, tecnico_nome: str):
    payload = {
      "evento": "submissao_validacao",
      "projeto_id": projeto_id,
      "mensagem": f"Técnico {tecnico_nome} submeteu projeto para validação",
    }
    async with self._lock:
      await self._broadcast(self._engenheiros, payload)


notification_hub = NotificationHub()
