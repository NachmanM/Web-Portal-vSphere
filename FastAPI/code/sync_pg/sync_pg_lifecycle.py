from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from .sync_pg_execution import sync_vcenter_to_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize and start the scheduler on application startup
    scheduler = AsyncIOScheduler()
    # Run the sync every 5 minutes
    scheduler.add_job(sync_vcenter_to_db, 'interval', minutes=5)
    scheduler.start()
    
    # Run an initial sync immediately on startup
    await sync_vcenter_to_db()
    
    yield
    # Shutdown scheduler on application exit
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)