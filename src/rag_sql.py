import logging
from sentence_transformers import SentenceTransformer
import faiss
import json
from src.model import SQLCoderAgent
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from src.db_models import engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RAGSQL:
    def __init__(self,
                 schema_file: str = 'data/db.json',
                 embedding_model: str ="all-MiniLM-L6-v2"
                 ):
        # load schema
        with open(schema_file, 'r') as f:
            self.schema = json.load(f)

        self.descriptions = []
        for item in self.schema:
            desc = (
                f"Table: {item['table']}\n"
                f"{item['description']}\n"
                f"Columns: {', '.join(item['attributes'])}"
            )
            self.descriptions.append(desc)

        # initialize emedding model and FAISS idx
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embeddings = self.embedding_model.encode(self.descriptions)
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)  # type: ignore

        self.sql_agent = SQLCoderAgent()
        self.Session = sessionmaker(bind=engine)

    def _enrich_retrieved_tables(self, query_lower: str, retrieved: list) -> list:
        """
        Enrich FAISS-retrieved tables with forced tables based on query keywords.
        Returns list of additional tables to include.
        """
        forced_tables = []

        # Score aggregation queries
        if any(word in query_lower for word in ['average score', 'avg score', 'mean score', 'average rank', 'score per competition', 'score for each']):
            self._add_if_missing(forced_tables, retrieved, 'leaderboard_row')
            self._add_if_missing(forced_tables, retrieved, 'participation')

        # Winner/ranking queries
        if any(word in query_lower for word in ['winner', 'won', 'never won', 'not won', 'at least one', 'rank', 'leaderboard', 'top', 'best score']):
            self._add_if_missing(forced_tables, retrieved, 'leaderboard_row')
            self._add_if_missing(forced_tables, retrieved, 'participation')

        # Submission queries
        if any(word in query_lower for word in ['submit', 'submission', 'submitted']):
            self._add_if_missing(forced_tables, retrieved, 'submission', exclude_pattern='max_daily_submissions')
            self._add_if_missing(forced_tables, retrieved, 'participation')

        # Negative logic queries (no/never/without)
        if any(word in query_lower for word in ['no submission', 'no winner', 'never', 'without', 'have not', 'haven\'t']):
            if 'submission' in query_lower or 'submitted' in query_lower:
                self._add_if_missing(forced_tables, retrieved, 'submission', exclude_pattern='max_daily_submissions')
            if 'winner' in query_lower or 'won' in query_lower:
                self._add_if_missing(forced_tables, retrieved, 'leaderboard_row')

        # Entity mentions
        if any(word in query_lower for word in ['user', 'username', 'organizer', 'participant']):
            self._add_if_missing(forced_tables, retrieved, '"user"')

        if any(word in query_lower for word in ['competition', 'contest']):
            self._add_if_missing(forced_tables, retrieved, 'competition', exclude_pattern='competition_config')

        if any(word in query_lower for word in ['participate', 'participated', 'joined competition', 'registered']):
            self._add_if_missing(forced_tables, retrieved, 'participation')

        return forced_tables

    def _add_if_missing(self, forced_tables: list, retrieved: list, table_name: str, exclude_pattern: str = None):
        """Helper to add table if not already in retrieved."""
        table = next((d for d in self.descriptions
                     if table_name in d.lower() and (not exclude_pattern or exclude_pattern not in d.lower())),
                     None)
        if table and table not in retrieved and table not in forced_tables:
            forced_tables.append(table)

    def retrieve_schema(self, query, top_k: int=5):
        query_embeddings = self.embedding_model.encode([query])
        _, indices = self.index.search(query_embeddings, k=top_k)  # type: ignore
        retrieved = [self.descriptions[i] for i in indices[0]]

        # Enrich with keyword-based forced tables
        query_lower = query.lower()
        forced_tables = self._enrich_retrieved_tables(query_lower, retrieved)

        all_tables = retrieved + forced_tables
        return all_tables[:top_k + 2]

    def generate_sql(self, query: str, top_k: int=5):
        retrieved = self.retrieve_schema(query, top_k)
        logger.info(f"Retrieved {len(retrieved)} tables for query: {query}")

        retrieved_tables = [desc.split('\n')[0].replace('Table: ', '').strip() for desc in retrieved]
        logger.info(f"Tables: {', '.join(retrieved_tables)}")

        type_mapping = {
            'id': 'INTEGER PRIMARY KEY',
            'user_id': 'INTEGER',
            'competition_id': 'INTEGER',
            'participation_id': 'INTEGER',
            'task_type_id': 'INTEGER',
            'metric_id': 'INTEGER',
            'dataset_id': 'INTEGER',
            'submission_id': 'INTEGER',
            'evaluation_id': 'INTEGER',
            'organizer_id': 'INTEGER',
            'config_id': 'INTEGER',
            'prize_id': 'INTEGER',
            'file_id': 'INTEGER',
            'kernel_id': 'INTEGER',
            'row_id': 'INTEGER',
            'best_evaluation_id': 'INTEGER',
            'created_at': 'TIMESTAMP',
            'submitted_at': 'TIMESTAMP',
            'registered_at': 'TIMESTAMP',
            'computed_at': 'TIMESTAMP',
            'updated_at': 'TIMESTAMP',
            'start_at': 'TIMESTAMP',
            'end_at': 'TIMESTAMP',
            'amount': 'NUMERIC',
            'metric_value': 'NUMERIC',
            'score': 'NUMERIC',
            'size_bytes': 'BIGINT',
            'rank': 'INTEGER',
            'rank_position': 'INTEGER',
            'max_daily_submissions': 'INTEGER',
            'is_hidden': 'BOOLEAN',
            'is_valid': 'BOOLEAN'
        }

        create_statements = []
        for item in self.schema:
            if item['table'] in retrieved_tables:
                col_defs = []
                for col in item['attributes']:
                    col_type = type_mapping.get(col, 'TEXT')
                    col_defs.append(f"{col} {col_type}")

                cols_str = ', '.join(col_defs)
                create_statements.append(f"CREATE TABLE {item['table']} ({cols_str});")

        schema_context = "\n\n".join(retrieved) + "\n\n" + "\n".join(create_statements)

        prompt = (
            f"### Task:\n"
            f"Convert the question into a SQL query using the provided Postgres schema.\n\n"
            f"### Rules:\n"
            f"- Use table aliases to prevent ambiguity\n"
            f"- Use exact table names from schema (lowercase, singular form)\n"
            f"- Study the schema examples carefully for correct JOIN patterns\n\n"
            f"### Schema:\n"
            f"{schema_context}\n\n"
            f"### Question:\n"
            f"{query}\n\n"
            f"### SQL:\n"
            f"```sql\n"
        )

        logger.info(f"Prompt length: {len(prompt)} characters")
        logger.debug(f"Full prompt:\n{prompt}")

        return self.sql_agent.generate_response(prompt)

    def execute_sql(self, sql_query: str, limit: int = 3):
        """
        Execute SQL query with safety checks and result limiting.
        Only allows SELECT queries.
        """
        sql_query = sql_query.rstrip(';').strip()
        sql_upper = sql_query.upper()
        if not sql_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed for execution.")

        if "LIMIT" not in sql_upper:
            sql_query += f" LIMIT {limit}"

        try:
            session = self.Session()
            result = session.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
            session.close()
            return {"columns": list(columns), "rows": [list(row) for row in rows]}
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            raise ValueError(f"SQL execution error: {str(e)}")


if __name__ == "__main__":
    test_queries = [
        "Select all users who joined in 2023",
        "Get all competitions with their datasets",
        "Who is the winner of the competition with id 5?",
        "show me all users, who played at 2024"
    ]

    rag = RAGSQL()
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"User Query: {q}")
        result = rag.generate_sql(q)
        if isinstance(result, dict):
            print(f"Generated SQL: {result['processed']}")
        else:
            print(f"Generated SQL: {result}")
        print('='*60)

