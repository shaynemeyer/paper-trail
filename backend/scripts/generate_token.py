# scripts/generate_token.py
import jwt
from datetime import datetime, timedelta, UTC
import os
import sys
from dotenv import load_dotenv

load_dotenv()
private_key = os.getenv("JWT_PRIVATE_KEY")
if private_key is None:
    raise ValueError("JWT_PRIVATE_KEY environment variable is not set")

private_key = private_key.replace("\\n", "\n")
# Read role from command line argument, default to "user"
role = sys.argv[1] if len(sys.argv) > 1 else "user"

payload = {
    "sub": "test_user",
    "role": role,
    "exp": datetime.now(UTC) + timedelta(hours=1),
}
token = jwt.encode(payload, private_key, algorithm="RS256")
print(token)
