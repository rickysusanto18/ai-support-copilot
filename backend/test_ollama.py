from app.llm.ollama_client import ollama_client


response = ollama_client.generate(
    "bisakah kamu mengerti saya jika saya menggunakan bahasa indonesia?"
)

print(response)