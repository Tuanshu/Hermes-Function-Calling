import asyncio

async def async_generator():
    print ("between 0~1")

    yield  "first yield"

    print ("between 1~2")
    yield  "2nd yield"
    print ("between 2~3")

    yield  "3rd yield"

async def main():
    async for value in async_generator():
        print(value)

# 运行 main 函数
asyncio.run(main())