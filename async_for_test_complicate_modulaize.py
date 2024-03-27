import asyncio

async def async_generator(max_depth):
    async def yield_from_generator(generator, depth):
        if depth < max_depth:
            yield f"current depth={depth}"
            async for value in generator(depth + 1):
                yield value

    async def recursive_inner_generator(depth):
        return yield_from_generator(recursive_inner_generator, depth)

    # 现在只需直接迭代 recursive_inner_generator
    async for value in recursive_inner_generator(0):
        yield value

async def main():
    async for value in async_generator(3):
        print(value)

# 运行 main 函数
asyncio.run(main())
