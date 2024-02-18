from fastapi import FastAPI
import uvicorn

# Example FastAPI app definition
def create_app():
    app = FastAPI()

    @app.get("/")
    async def default():
        return "ok"

    return app

# Function to run a FastAPI app with uvicorn programmatically
def run_server(port=12741):
    app = create_app()
    config = uvicorn.Config(app=app, host="0.0.0.0", port=port, loop="asyncio",  log_level="warning")
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    run_server()
