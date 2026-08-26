from config import get_settings
from .client import get_openai_client
from .prompts import build_chat_prompt,build_rag_prompt,Message

settings = get_settings()

async def get_rag_completion(
    question:str,
    context_chunks: list[str],
) -> str:

 client = get_openai_client()
 messages = build_rag_prompt(question,context_chunks)

 response = await client.chat.completions.create(
    model = settings.azure_openai_chat_deployment,
    messages=messages,
    max_tokens= settings.azure_openai_max_tokens,
    temperature=0.2,
 )

 return response.choices[0].message.content or ""

async def get_chat_completion(
    question: str,
    context_chunks : list[str],
    history : list[Message]
) -> str:

  client = get_openai_client()
  messages = build_chat_prompt(question,context_chunks,history)

  response = await client.chat.completions.create(
    model=settings.azure_openai_chat_deployment,
    messages=messages,
    max_tokens=settings.azure_openai_max_tokens,
    temperature=0.2,
  )
  
  return response.choices[0].message.content or ""