from transformers import AutoTokenizer

# Carrega o tokenizador do modelo Gemma 3B (ou outro da família)
tokenizer = AutoTokenizer.from_pretrained("google/gemma-3-4b-it")

# Seu texto de exemplo
texto = "Olá! Como posso contar os tokens neste modelo?"

# Tokenize e conte
tokens = tokenizer.tokenize(texto)
num_tokens = len(tokens)

print(f"Número de tokens: {num_tokens}")
