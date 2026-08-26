from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

SYSTEM_PROMPT = """ You are a helpful assistant that answers questions based strictly on the provided context.
Rules:
- Only use information from the context below to answer the question.
- If the context does not contain enough information to answer, say "I don't have enough information to answer that."
- Do not make up facts or use outside knowledge.
- Keep your answers concise and accurate.
- If relevant, cite which part of the context supports your answer.
"""

def build_rag_prompt(question: str,context_chunks: list[str]) -> list[dict]:
    context = "\n\n---\n\n".join(context_chunks)
    user_message = f"""Context:{context}
 
    Question : {question}"""

    return [
        {"role" : "system","content":SYSTEM_PROMPT},
        {"role" : "user","content" : user_message},
      ]

def build_chat_prompt(
    question: str,
    context_chunks : list[str],
    history: list[Message],
) -> list[dict]:

   context = "\n\n---\n\n".join(context_chunks)
   messages: list[dict] = [
    {"role": "system","content" : SYSTEM_PROMPT},
    {
        "role": "system",
        "content" : f"Use the following context to answer the user's questions:\n\n{context}",
    },
   ]
   for msg in history:
    messages.append({"role" : msg.role,"content" : msg.content})

   messages.append({"role":"user","content": question})

   return messages 