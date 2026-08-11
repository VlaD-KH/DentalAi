"""
Главная точка входа бэкенда DentalAi и FastMCP сервера.
Предоставляет REST API, WebSocket для live-логов агентов и MCP эндпоинты.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api.orders_router import router as orders_router
from app.config import settings
import asyncio
import json

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Автономный бэкенд и MCP-сервер для Solo-лаборатории DentalAi",
)

# Подключение REST API роутера заказов
app.include_router(orders_router)


# Настройка CORS для фронтенд-дашборда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Менеджер активных WebSocket соединений логов агентов
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_log(self, log_data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(log_data))
            except Exception:
                pass


ws_manager = ConnectionManager()


async def broadcast_agent_log(agent: str, action: str, status: str = "SUCCESS"):
    """Вспомогательная функция для отправки логов агента во все активные WS соединения."""
    from datetime import datetime, timezone
    log_data = {
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
        "agent": agent,
        "action": action,
        "status": status,
    }
    await ws_manager.broadcast_log(log_data)


@app.on_event("startup")
async def startup_event():
    """Запуск фонового мониторинга Hot-Folder при старте бэкенда."""
    from pathlib import Path
    from app.services.ingestion.watcher import ingestion_service

    hot_folder = Path("./data/orders/hot_folder")
    hot_folder.mkdir(parents=True, exist_ok=True)

    async def watch_hot_folder_loop():
        processed_files = set()
        while True:
            try:
                for file_path in hot_folder.glob("*"):
                    if file_path.is_file() and file_path not in processed_files:
                        res = await ingestion_service.process_hot_folder_file(file_path)
                        if res:
                            processed_files.add(file_path)
                            await broadcast_agent_log(
                                agent="OrderIngestion",
                                action=f"New file ingested from HotFolder: {file_path.name} -> Order #{res['order_number']}",
                            )
            except Exception:
                pass
            await asyncio.sleep(3)

    asyncio.create_task(watch_hot_folder_loop())


@app.get("/health")
async def health_check():
    """Проверка работоспособности системы."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "gpu_enabled": settings.USE_GPU,
    }


@app.websocket("/ws/logs")
async def websocket_agent_logs(websocket: WebSocket):
    """WebSocket эндпоинт для живой трансляции логов роя MCP-агентов в дашборд."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Поддержание соединения
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
