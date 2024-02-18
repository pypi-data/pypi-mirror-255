def openai_api_calculate_cost(usage,model="gpt-3.5-turbo-16k"):
    pricing = {
        'gpt-3.5-turbo-4k': {
            'prompt': 0.0015,
            'completion': 0.002,
        },
        'gpt-3.5-turbo-16k': {
            'prompt': 0.003,
            'completion': 0.004,
        },
        'gpt-4-8k': {
            'prompt': 0.03,
            'completion': 0.06,
        },
        'gpt-4-32k': {
            'prompt': 0.06,
            'completion': 0.12,
        },
        'text-embedding-ada-002-v2': {
            'prompt': 0.0001,
            'completion': 0.0001,
        }
    }

    try:
        model_pricing = pricing[model]
    except KeyError:
        raise ValueError("Invalid model specified")

    prompt_cost = usage['prompt_tokens'] * model_pricing['prompt'] / 1000
    completion_cost = usage['completion_tokens'] * model_pricing['completion'] / 1000

    total_cost = prompt_cost + completion_cost
    print(f"\nTokens used:  {usage['prompt_tokens']:,} prompt + {usage['completion_tokens']:,} completion = {usage['total_tokens']:,} tokens")
    print(f"Total cost for {model}: ${total_cost:.4f}\n")

    return total_cost