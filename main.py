import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import userrouter, ticketrouter, adminrouter
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
def receive_signal(signalNumber, frame):
    print('Received:', signalNumber)
    sys.exit()
@app.on_event("startup")
async def startup_event():
    import signal
    signal.signal(signal.SIGINT, receive_signal)
    # startup tasks
# Include routers

@app.get('/')
def read_root():
    return {"Hello":"World"}
app.include_router(userrouter.router)
app.include_router(ticketrouter.router)
app.include_router(adminrouter.router)
