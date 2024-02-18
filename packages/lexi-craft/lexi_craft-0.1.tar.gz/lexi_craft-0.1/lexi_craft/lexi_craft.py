import openai
import os


#  TODO: Docs
#  TODO: Type checking


BASE_PROMPT = "\nПерепиши этот текст на русском языке со всеми грамматическими нормами русского языка. Избавься от лишних сслов паразитов, для этого можешь слегка перефразировать текст. Но не использую восклицательный знак."


def init(api_key: str | None = None) -> None:
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key is None:
            from dotenv import load_dotenv

            load_dotenv()

            api_key = os.getenv("OPENAI_API_KEY")
            
            if api_key is None:
                print("Please set your OpenAI API key as an environment variable or pass it as a parameter to the init function.")
                exit(1)

    openai.api_key = api_key
    

def decorate_text(text: str) -> str | None:
    prompt = f'"{text}"' + BASE_PROMPT

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

