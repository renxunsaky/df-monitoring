from flask import Flask, jsonify, request
from flask_caching import Cache
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
import os
import yaml
from dotenv import load_dotenv
from contextlib import contextmanager
from logging_config import setup_logger
import traceback
from utils.query_loader import QueryLoader

# Setup logger
logger = setup_logger()

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize query loader with configurable path
config_path = os.getenv('QUERIES_CONFIG_PATH', 'config/queries.yaml')  # Default to local path
query_loader = QueryLoader(config_path)

# Configure cache
cache_config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(cache_config)
cache = Cache(app)

# Create connection pool
try:
    pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=10,
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )
    logger.info("Database connection pool created successfully")
except Exception as e:
    logger.error(f"Failed to create connection pool: {str(e)}")
    raise

@contextmanager
def get_db_connection():
    conn = pool.getconn()
    try:
        logger.debug("Retrieved connection from pool")
        yield conn
    finally:
        pool.putconn(conn)
        logger.debug("Returned connection to pool")

@contextmanager
def get_db_cursor():
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
            logger.debug("Database transaction committed")
        except Exception as e:
            connection.rollback()
            logger.error(f"Database transaction rolled back: {str(e)}")
            raise
        finally:
            cursor.close()

@app.route('/api/query/<query_name>', methods=['GET'])
@cache.cached(timeout=300)
def execute_query(query_name):
    logger.info(f"Received query request for {query_name} from {request.remote_addr}")
    try:
        # Get query from configuration
        query = query_loader.get_query(query_name)
        if not query:
            return jsonify({
                "status": "error",
                "message": f"Query '{query_name}' not found"
            }), 404

        # Parse parameters from request args
        params = []
        if 'params' in request.args:
            params = request.args.getlist('params')

        with get_db_cursor() as cur:
            logger.debug(f"Executing query: {query_name}")
            cur.execute(query, params or None)
            results = cur.fetchall()
            logger.debug(f"Query returned {len(results)} results")

        return jsonify({
            "status": "success",
            "query_name": query_name,
            "description": query_loader.get_query_description(query_name),
            "data": results
        })

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in execute_query: {str(e)}\n{error_details}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "status": "success",
        "message": "DocFactory Monitoring API",
        "available_queries": [
            {
                "name": name,
                "description": query_loader.get_query_description(name),
                "endpoint": f"/api/query/{name}"
            }
            for name in query_loader.get_query_names()
        ]
    })

@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response: {response.status}")
    return response

@app.teardown_appcontext
def close_pool(exception):
    global pool
    if exception:
        logger.error(f"Error during request: {str(exception)}")
    try:
        if pool is not None:
            pool.closeall()
            pool = None
            logger.debug("Connection pool closed")
    except Exception as e:
        logger.warning(f"Error while closing pool: {str(e)}")

if __name__ == '__main__':
    logger.info("Starting Dynatrace API service")
    app.run(debug=True) 