import argparse
from application.avaliable_functions import get_openai_tool_dicts,get_openai_tool_dicts_no_at_tool_dec
if __name__ == "__main__":


    print(f'[ts] get_openai_tool_dicts={get_openai_tool_dicts()}')

    print(f'[ts] get_openai_tool_dicts_no_at_tool_dec={get_openai_tool_dicts_no_at_tool_dec()}')