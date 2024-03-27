import asyncio

async def async_generator(max_depth):
    async def recursive_inner_generator(depth):
        if depth < max_depth:
            yield f"current depth={depth}"
            async for deeper_value in recursive_inner_generator(depth + 1):
                yield deeper_value

    async for value in recursive_inner_generator(0):
        yield value

async def main():
    async for value in async_generator(3):  # 假设最大深度为3
        print(value)

# 运行 main 函数
asyncio.run(main())