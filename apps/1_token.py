import tiktoken

enc = tiktoken.get_encoding("cl100k_base")

text = "I love pizza"
ids = enc.encode(text)
print(ids)
print([enc.decode([i]) for i in ids])
print(len(ids))