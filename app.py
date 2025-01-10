from flask import Flask, jsonify, request
from flask_caching import Cache
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
import os
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

# Initialize query loader
query_loader = QueryLoader()

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

@app.route('/api/metrics', methods=['GET'])
@cache.cached(timeout=300)
def get_metrics():
    logger.info(f"Received metrics request from {request.remote_addr}")
    try:
        with get_db_cursor() as cur:
            query = query_loader.get_query('get_last_hour_metrics')
            logger.debug("Executing metrics query")
            cur.execute(query)
            results = cur.fetchall()
            logger.debug(f"Query returned {len(results)} results")
            
        return jsonify({
            "status": "success",
            "data": results
        })
    
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in get_metrics: {str(e)}\n{error_details}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/metrics/daily', methods=['GET'])
@cache.cached(timeout=300)
def get_daily_metrics():
    logger.info(f"Received daily metrics request from {request.remote_addr}")
    try:
        with get_db_cursor() as cur:
            query = query_loader.get_query('get_daily_average')
            cur.execute(query)
            results = cur.fetchall()
            
        return jsonify({
            "status": "success",
            "data": results
        })
    
    except Exception as e:
        logger.error(f"Error in get_daily_metrics: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/metrics/<metric_name>', methods=['GET'])
@cache.cached(timeout=300)
def get_metric_by_name(metric_name):
    logger.info(f"Received metric request for {metric_name} from {request.remote_addr}")
    try:
        with get_db_cursor() as cur:
            query = query_loader.get_query('get_metric_by_name')
            cur.execute(query, (metric_name,))
            results = cur.fetchall()
            
        return jsonify({
            "status": "success",
            "data": results
        })
    
    except Exception as e:
        logger.error(f"Error in get_metric_by_name: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response: {response.status}")
    return response

@app.teardown_appcontext
def close_pool(exception):
    if exception:
        logger.error(f"Error during request: {str(exception)}")
    pool.closeall()
    logger.debug("Connection pool closed")

if __name__ == '__main__':
    logger.info("Starting Dynatrace API service")
    app.run(debug=True) 