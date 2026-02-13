from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.rag_sql import RAGSQL
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SQL RAG API",
    description="API for generating SQL queries from natural language using RAG",
    version="1.0.0"
)

rag_agent = RAGSQL()

class QueryRequest(BaseModel):
    query: str

class SQLResponse(BaseModel):
    query: str
    generated_sql: str

@app.post("/generate-sql", response_model=SQLResponse)
async def generate_sql(request: QueryRequest):
    """
    Generate SQL query from natural language query using RAG.
    """
    try:
        logger.info(f"Received query: {request.query}")
        result = rag_agent.generate_sql(request.query)
        
        # Handle both dict and string returns
        if isinstance(result, dict):
            sql = result.get("processed", "")
        else:
            sql = result
            
        logger.info(f"Generated SQL: {sql}")
        return SQLResponse(query=request.query, generated_sql=sql)
    except Exception as e:
        logger.error(f"Error generating SQL: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating SQL: {str(e)}")

@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {"message": "SQL RAG API is running", "status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
