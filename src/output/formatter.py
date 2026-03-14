"""Format query results for Slack messages."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _unwrap_pandasai_response(result: Any) -> Any:
    """Unwrap a pandasai v3 response object to its inner value."""
    try:
        from pandasai.core.response import BaseResponse
        if isinstance(result, BaseResponse):
            return result.value
    except ImportError:
        pass
    return result


def format_result_for_slack(result: Any) -> str:
    """
    Convert a query result into a Slack-friendly message.
    
    Handles DataFrames, strings, lists, and other types. Returns text summary
    with markdown table blocks for tabular data. Automatically unwraps
    pandasai v3 response objects.
    
    Parameters
    ----------
    result : Any
        The result from PandasAI query (typically a DataFrame or string)
        
    Returns
    -------
    str
        Formatted message ready for Slack
    """
    try:
        result = _unwrap_pandasai_response(result)

        if isinstance(result, str):
            return _truncate_message(result)
        
        if isinstance(result, (int, float)):
            return _truncate_message(str(result))

        try:
            import pandas as pd
            if isinstance(result, pd.DataFrame):
                return _format_dataframe(result)
        except ImportError:
            logger.warning("pandas not available for dataframe formatting")
        
        if isinstance(result, (list, dict)):
            return _format_data_structure(result)
        
        return _truncate_message(str(result))
        
    except Exception as e:
        logger.error(f"Error formatting result: {e}")
        return "Unable to format the query result. Please try again."


def _format_dataframe(df: Any) -> str:
    """
    Format a pandas DataFrame for Slack using code blocks and text.
    
    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to format
        
    Returns
    -------
    str
        Slack-formatted message with summary and table
    """
    try:
        # Get summary stats
        num_rows = len(df)
        num_cols = len(df.columns)
        
        # Build message header
        message = f"📊 Query Results: {num_rows} rows × {num_cols} columns\n\n"
        
        # Truncate to max 20 rows for readability in Slack
        display_df = df.head(20)
        
        # Format as markdown table
        try:
            table_str = display_df.to_markdown(index=False)
            if table_str:
                message += f"```\n{table_str}\n```"
                
                if num_rows > 20:
                    message += f"\n\n_Showing first 20 of {num_rows} rows_"
        except Exception:
            # Fallback to simple string representation
            message += f"```\n{display_df.to_string()}\n```"
        
        return _truncate_message(message)
        
    except Exception as e:
        logger.error(f"Error formatting dataframe: {e}")
        return _truncate_message(f"Query returned {len(df)} rows. (Unable to format as table)")


def _format_data_structure(data: Any) -> str:
    """Format lists and dicts for Slack."""
    try:
        if isinstance(data, dict):
            lines = [f"• {k}: {v}" for k, v in data.items()]
            return _truncate_message("\n".join(lines))
        
        if isinstance(data, list):
            if not data:
                return "No results found."
            
            lines = [f"• {item}" for item in data[:20]]
            message = "\n".join(lines)
            
            if len(data) > 20:
                message += f"\n\n_Showing first 20 of {len(data)} items_"
            
            return _truncate_message(message)
        
        return _truncate_message(str(data))
        
    except Exception as e:
        logger.error(f"Error formatting data structure: {e}")
        return "Unable to format the results."


def _truncate_message(message: str, max_length: int = 3000) -> str:
    """
    Truncate message to Slack's character limit.
    
    Parameters
    ----------
    message : str
        The message to truncate
    max_length : int
        Maximum message length (Slack limit is 4000, use 3000 to be safe)
        
    Returns
    -------
    str
        Truncated message with ellipsis if needed
    """
    if len(message) <= max_length:
        return message
    
    truncated = message[:max_length-50]
    return truncated + "\n\n_Message truncated (too long for Slack)_"


def format_error_message(error: Exception | str) -> str:
    """
    Format an error for display to users in Slack.
    
    Parameters
    ----------
    error : Exception or str
        The error to format
        
    Returns
    -------
    str
        User-friendly error message
    """
    if isinstance(error, str):
        return f"❌ {error}"
    
    error_msg = str(error)
    
    # Generic error messages for common issues
    if "database" in error_msg.lower() or "connection" in error_msg.lower():
        return "❌ Unable to connect to the database. Please try again later."
    
    if "timeout" in error_msg.lower():
        return "❌ Query timed out. Try a simpler question."
    
    if "permission" in error_msg.lower() or "access" in error_msg.lower():
        return "❌ You don't have permission to access this data."
    
    # Default: be vague to users, log the real error
    logger.error(f"Unhandled error in query: {error}")
    return "❌ Something went wrong processing your query. Please try again."
