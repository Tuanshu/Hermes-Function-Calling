import asyncio
import functools
import inspect
import io
import logging
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Define multiple handlers
# https://stackoverflow.com/questions/46636206/python-3-6-logging-modul-error-unicodeencodeerror-charmap-codec-cant-encod
file_handler = logging.FileHandler("logs/timer.log", mode="a", encoding='utf-8')
stdout_handler = logging.StreamHandler(sys.stdout)

# Set the level and format for both handlers
handlers = [file_handler, stdout_handler]
for handler in handlers:
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Configure the root logger with these handlers
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", handlers=handlers, encoding="utf-8")
logger = logging.getLogger(__name__)


def timer(func):
    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get the class name if the function is a method of a class
            if args:
                # The first argument would be 'self' for an instance method,
                # or 'cls' for a class method.
                class_name = args[0].__class__.__name__
                logger.debug(f"{class_name}.{func.__name__} called.")
            else:
                logger.debug(f"{func.__name__} called.")

            start = time.time()
            result = await func(*args, **kwargs)
            end = time.time()
            log_msg = f"{func.__name__} took {end - start:.2f} seconds. [coroutine function]"
            logger.debug(log_msg)
            return result

        return async_wrapper
    elif inspect.isasyncgenfunction(func):  # 檢查是否為異步生成器

        @functools.wraps(func)
        async def async_gen_wrapper(*args, **kwargs):
            # Get the class name if the function is a method of a class
            if args:
                # The first argument would be 'self' for an instance method,
                # or 'cls' for a class method.
                class_name = args[0].__class__.__name__
                logger.debug(f"{class_name}.{func.__name__} called.")
            else:
                logger.debug(f"{func.__name__} called.")

            gen = func(*args, **kwargs)
            start = time.time()
            try:
                first_val = await gen.__anext__()
                end = time.time()
                log_msg = f"{func.__name__} to first value took {end - start:.2f} seconds. [async coroutine function]"
                print(log_msg)
                logger.debug(log_msg)
                yield first_val
                async for item in gen:
                    yield item
            except StopAsyncIteration:
                pass

        return async_gen_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get the class name if the function is a method of a class
            if args:
                # The first argument would be 'self' for an instance method,
                # or 'cls' for a class method.
                class_name = args[0].__class__.__name__
                logger.debug(f"{class_name}.{func.__name__} called.")
            else:
                logger.debug(f"{func.__name__} called.")

            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            log_msg = f"{func.__name__} took {end - start:.2f} seconds. [not coroutine function]"
            print(log_msg)
            logger.debug(log_msg)
            return result

        return sync_wrapper
