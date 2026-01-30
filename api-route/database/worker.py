from connect.BaseClass import BaseClass
import pandas as pd



class DatabaseWorker(BaseClass):
    def __init__(self):
        super().__init__()
    

    async def append_entrance(self, id_store:int, void:int, url:str = None, create_at:str = None):
        query = """
        INSERT INTO store_entrances (id_store, void, url, create_at)
        VALUES (%s, %s, %s, %s)
        """
        await self.db_km.ANALITIC_QUERY(query, (id_store, void, url, create_at))
