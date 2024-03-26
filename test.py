import argparse
from application.functioncall_use_case import FunctionCallUseCase
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run recursive function calling loop")
    parser.add_argument("--query", type=str, default="I need the current stock price of Tesla (TSLA)")
    args = parser.parse_args()

    from preload import preloaded_model, preloaded_tokenizer
    use_case = FunctionCallUseCase(preloaded_model, preloaded_tokenizer)
        
    # Run the model evaluator
    result=use_case.chat(args.query)

    print(f'[ts] results (should be all promts)={result}')