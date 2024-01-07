from openai import AzureOpenAI
debug = False

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
            
        client = AzureOpenAI(
                api_version="2023-07-01-preview",
                azure_endpoint=openai_api_base,
                api_key=openai_api_key
        )
        openai_response = client.chat.completions.create(
            model=open_ai_model,
            messages=messages,
            temperature=model_temperature,
            max_tokens=max_prompt_tokens
        )
        return openai_response
    except Exception as e:
        print(f'error :{e}')
        return 'Failed'

def generate_res(messages,open_ai_model,model_temperature=0.7,max_prompt_tokens=None,connection_data=None):
    if debug:
        print(f'connection_data : {connection_data}')

    for url,key in connection_data.items():
        openai_api_base = url
        openai_api_key = key
        res = generic_azure_openai_client(openai_api_key,open_ai_model,messages,openai_api_base,model_temperature,max_prompt_tokens)   
        if res != 'Failed':
            return res  
            break   
    


