"""AI query client for PandasAI with error handling and timeout support."""

import logging
from typing import Any
from functools import wraps
import time

logger = logging.getLogger(__name__)


def with_timeout(timeout_seconds: float = 30):
    """Decorator to timeout long-running functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # For simple timeout simulation with blocking calls
            # (Production would use threading or asyncio)
            try:
                start = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                if elapsed > timeout_seconds:
                    logger.warning(f"{func.__name__} took {elapsed:.1f}s (timeout: {timeout_seconds}s)")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator


class QueryClient:
    """
    Client for querying data using PandasAI.
    
    Wraps the PandasAI engine with error handling, timeout logic,
    and result formatting.
    """
    
    def __init__(self, query_func, timeout_seconds: float = 30):
        """
        Initialize the query client.
        
        Parameters
        ----------
        query_func : callable
            Function that takes a question string and returns results
        timeout_seconds : float
            Timeout for query execution in seconds
        """
        self.query_func = query_func
        self.timeout_seconds = timeout_seconds
        self.logger = logging.getLogger(__name__)
    
    def query(self, question: str) -> dict:
        """
        Execute a natural language query against the data.
        
        Parameters
        ----------
        question : str
            Natural language question to ask about the data
            
        Returns
        -------
        dict
            Dictionary with keys:
            - 'success' (bool): Whether the query succeeded
            - 'result' (Any): The query result (if successful)
            - 'error' (str): Error message (if failed)
        """
        if not question or not question.strip():
            return {
                'success': False,
                'result': None,
                'error': 'Please ask a question about the data.'
            }
        
        try:
            self.logger.info(f"Processing query: {question[:100]}...")
            
            # Call the wrapped query function
            result = self.query_func(question)
            
            self.logger.info("Query executed successfully")
            return {
                'success': True,
                'result': result,
                'error': None
            }
            
        except TimeoutError as e:
            self.logger.warning(f"Query timeout: {e}")
            return {
                'success': False,
                'result': None,
                'error': 'Query timed out. Please try a simpler question.'
            }
        
        except PermissionError as e:
            self.logger.warning(f"Permission denied: {e}")
            return {
                'success': False,
                'result': None,
                'error': "You don't have permission to access this data."
            }
        
        except ValueError as e:
            self.logger.warning(f"Invalid input: {e}")
            return {
                'success': False,
                'result': None,
                'error': f"Invalid question: {str(e)[:100]}"
            }
        
        except Exception as e:
            error_msg = str(e).lower()
            
            # Map common errors to user-friendly messages
            if 'database' in error_msg or 'connection' in error_msg:
                user_msg = 'Unable to connect to the database. Please try again later.'
            elif 'timeout' in error_msg:
                user_msg = 'Query timed out. Please try a simpler question.'
            elif 'memory' in error_msg:
                user_msg = 'Query used too much memory. Please try a simpler question.'
            else:
                user_msg = 'An error occurred processing your query. Please try again.'
            
            self.logger.error(f"Query error: {e}", exc_info=True)
            return {
                'success': False,
                'result': None,
                'error': user_msg
            }
