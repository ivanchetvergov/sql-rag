from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from src.rag_sql import RAGSQL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    query: str

class SQLResponse(BaseModel):
    query: str
    generated_sql: str

class ExecuteRequest(BaseModel):
    query: str

class ExecuteResponse(BaseModel):
    query: str
    generated_sql: str
    result: dict

class SQLRAGService(APIRouter):
    def __init__(self):
        super().__init__()
        self.rag_agent = RAGSQL()

        self.add_api_route("/generate-sql", self.generate_sql_endpoint, methods=["POST"], response_model=SQLResponse)
        self.add_api_route("/execute-sql", self.execute_sql_endpoint, methods=["POST"], response_model=ExecuteResponse)
        self.add_api_route("/", self.root_endpoint, methods=["GET"])

    async def generate_sql_endpoint(self, request: QueryRequest):
        """
        Generate SQL query from natural language query using RAG.
        """
        try:
            logger.info(f"Received query: {request.query}")
            sql = self.generate_sql(request.query)
            logger.info(f"Generated SQL: {sql}")
            return SQLResponse(query=request.query, generated_sql=sql)
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating SQL: {str(e)}")

    async def execute_sql_endpoint(self, request: ExecuteRequest):
        """
        Generate SQL from query and execute it, returning results (limited to 3 rows for safety).
        Only SELECT queries are allowed.
        """
        try:
            logger.info(f"Received query for execution: {request.query}")

            sql = self.generate_sql(request.query)
            logger.info(f"Generated SQL: {sql}")

            result = self.execute_sql(sql, limit=3)
            logger.info(f"Execution result: {len(result.get('rows', []))} rows")

            return ExecuteResponse(query=request.query, generated_sql=sql, result=result)
        except Exception as e:
            logger.error(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    async def root_endpoint(self):
        """
        Health check endpoint.
        """
        return {"message": "SQL RAG API is running", "status": "healthy"}

    def generate_sql(self, query: str) -> str:
        result = self.rag_agent.generate_sql(query)
        if isinstance(result, dict):
            return result.get("processed", "")
        return result

    def execute_sql(self, sql: str, limit: int = 3):
        return self.rag_agent.execute_sql(sql, limit)

app = FastAPI(
    title="SQL RAG API",
    description="API for generating and executing SQL queries from natural language using RAG",
    version="1.0.0"
)

service = SQLRAGService()
app.include_router(service)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
