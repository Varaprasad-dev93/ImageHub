# Temporary in-memory store for token-to-session map
# In real usage, you'd use Redis or a DB
token_map = {}

def create_token(session_id):
    token = session_id
    token_map[token] = session_id
    return token

def validate_token(token):
    return token_map.get(token)

def invalidate_token(token):
    if token in token_map:
        del token_map[token]
