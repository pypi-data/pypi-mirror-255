from fastapi.exceptions import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError


class MongoDB:
    def __init__(self, connection_url: str, db_name: str):
        self.client = None
        self.connection_url = connection_url
        self.db_name = db_name

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(self.connection_url)
        except ServerSelectionTimeoutError:
            raise HTTPException(
                status_code=500,
                detail="Failed to connect to the database. Check your connection settings.",
            )

    async def close(self):
        if self.client:
            self.client.close()

    def get_database(self):
        if not self.client:
            raise HTTPException(
                status_code=500,
                detail="Database connection not established. Call connect() method first.",
            )
        return self.client[self.db_name]
