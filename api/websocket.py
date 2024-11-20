from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Notification websocket")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)


ws_conn_manager = ConnectionManager()


@app.websocket("/notify")
async def websocket_endpoint(websocket: WebSocket):
    await ws_conn_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            print("Notification: ", data)
            await websocket.send_json(data)
    except WebSocketDisconnect as e:
        ws_conn_manager.disconnect(websocket)
