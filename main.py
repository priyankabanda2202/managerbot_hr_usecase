import openai
from fastapi import FastAPI, HTTPException
from concurrent.futures import ThreadPoolExecutor
import asyncio
# import uvicorn
import sys
import hypercorn
from hypercorn.config import Config
from src.data_processing.data_processing import GetManagerBotResponse

# from data_processing.qdrantdb import QdrantEmbedding




app = FastAPI()
# manager_response = GetManagerBotResponse("")
executor = ThreadPoolExecutor(max_workers=2)

@app.get("/")
async def home_page():
    return "Welcome to the ManagerBot Dashboard using LLM"


@app.post("/api/managerbot/")
async def response(query:dict):
     try:
         response = await asyncio.to_thread(lambda: GetManagerBotResponse("Manager_Handbook").get_completion_from_messages(query['query']))
         return response
     except Exception as e:
         raise HTTPException(status_code=500, details=str(e))
 
@app.post("/api/empbuddy/")
async def response(query:dict):
     try:
         response = await asyncio.to_thread(lambda: GetManagerBotResponse("Employee_Buddy").get_completion_from_messages(query['query']))
         return response
     except Exception as e:
         raise HTTPException(status_code=500, details=str(e))
     
if __name__ == "__main__":
    config = Config()
    config.from_pyfile("hypercorn_config.py")
    hypercorn.run(app,config)


#hypercorn -c hypercorn_config.py main:app --reload