import secrets

# 生成 32 字节（256位）的随机密钥（适用于 HS256）
secret_key = secrets.token_hex(32)
print(secret_key)