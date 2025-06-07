import asyncio
import threading
import concurrent.futures
from typing import Any, Coroutine, Optional

def run_coroutine_synchronously(
    coro: Coroutine[Any, Any, Any], 
    timeout_seconds: Optional[float] = None
) -> Any:
    """
    Runs an asyncio coroutine and blocks until it completes, returning the result.
    This function handles cases where an event loop may or may not be running
    in the current thread.

    Args:
        coro: The coroutine to run
        timeout_seconds: Maximum time to wait (None for no timeout)
        
    Returns:
        The result of the coroutine
        
    Raises:
        TimeoutError: If timeout_seconds is exceeded
        Exception: Any exception raised by the coroutine
    """
    try:
        # Check if an event loop is already running in the current thread.
        asyncio.get_running_loop()
        is_loop_running = True
    except RuntimeError:
        is_loop_running = False

    if not is_loop_running:
        # Safe to use asyncio.run() as it will create and manage a new event loop.
        if timeout_seconds is not None:
            return asyncio.run(asyncio.wait_for(coro, timeout=timeout_seconds))
        else:
            return asyncio.run(coro)
    else:
        # An event loop is already running.
        # Run the coroutine in a separate thread with its own event loop.
        result = None
        exception = None
        
        def target_thread_func():
            nonlocal result, exception
            try:
                if timeout_seconds is not None:
                    result = asyncio.run(asyncio.wait_for(coro, timeout=timeout_seconds))
                else:
                    result = asyncio.run(coro)
            except Exception as e:
                exception = e
        
        # Use ThreadPoolExecutor with timeout
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(target_thread_func)
            try:
                # Add buffer time to thread timeout
                thread_timeout = timeout_seconds + 5 if timeout_seconds else None
                future.result(timeout=thread_timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError(f"Coroutine execution timed out after {timeout_seconds} seconds")
        
        if exception:
            raise exception
        return result


def run_coroutine_with_timeout(
    coro: Coroutine[Any, Any, Any], 
    timeout_seconds: float,
    default_result: Any = None
) -> Any:
    """
    Runs a coroutine with timeout, returning default_result if timeout occurs.
    
    Args:
        coro: The coroutine to run
        timeout_seconds: Maximum time to wait
        default_result: Value to return if timeout occurs
        
    Returns:
        The result of the coroutine or default_result if timeout
    """
    try:
        return run_coroutine_synchronously(coro, timeout_seconds)
    except (TimeoutError, asyncio.TimeoutError):
        return default_result
