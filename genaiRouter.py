from openai import AzureOpenAI

def generic_azure_openai_client(openai_api_key,open_ai_model,messages,openai_api_base,model_temperature=0.8,max_prompt_tokens=None):
    try:
        models_size = {
            "gpt-35-turbo-16k": 16000,
            "gpt-4-32k": 32000,
            "gpt-4": 4000,
            "gpt-4-1106-Preview": 50000,
        }
        if max_prompt_tokens is None:
            max_prompt_tokens = models_size[open_ai_model]
        open_ai_model = "gpt-35-turbo-16k"
        temperature = 0.8
        client = AzureOpenAI(
                api_version="2023-07-01-preview",
                azure_endpoint=openai_api_base,
                api_key=openai_api_key
        )
        res = client.chat.completions.create(
            model=open_ai_model,
            messages=messages,
            temperature=model_temperature
        )
        return res
    except Exception as e:
        print(f'error :{e}')
        return 'Failed'

def generate_res(messages,open_ai_model,model_temperature=0.7,max_prompt_tokens=None,connection_data=None):
    openai_api_key = connection_data["key"]
    openai_api_base = connection_data["base"] 
    return generic_azure_openai_client(openai_api_key,open_ai_model,messages,openai_api_base,model_temperature,max_prompt_tokens)   
    


