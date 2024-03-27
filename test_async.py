import argparse
from application.functioncall_use_case import FunctionCallUseCase
import asyncio
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run recursive function calling loop")
    parser.add_argument("--query", type=str, default="I need the current stock price of Tesla (TSLA)")
    args = parser.parse_args()

    from preload import preloaded_model, preloaded_tokenizer
    use_case = FunctionCallUseCase(preloaded_model, preloaded_tokenizer)

    async_generator=use_case.achat(args.query)

    async def main():
        async for value in async_generator:
            print(f'\n\n[ts] response cache in client={value}\n\n')


    asyncio.run(main())