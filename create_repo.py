import urllib.request, json, sys, base64

token = sys.argv[1]
owner = "REWY432"
repo = "hey-freelancer-bot"
bot_token = "8620573998:AAEHS-I9oiHin56Eo8f5oI0bY54O4a9Eyng"

# Get repo public key for secret encryption
url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key"
req = urllib.request.Request(url, headers={
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
})
with urllib.request.urlopen(req, timeout=10) as r:
    key_data = json.loads(r.read())
    print(f"Key ID: {key_data['key_id']}")

# Encrypt secret using libsodium-style (XOR with PKCS1 for simplicity)
# Actually, we need libsodium for proper encryption. Let's use gh CLI instead.
# Or use the REST API with the public key...

# GitHub Actions secrets need to be encrypted with the public key using libsodium.
# Since we can't easily do that in pure Python without libsodium, let's try a different approach:
# Use the gh CLI which is now installed

import subprocess
# Set secret via gh CLI
result = subprocess.run([
    "gh", "secret", "set", "TELEGRAM_BOT_TOKEN",
    "--repo", f"{owner}/{repo}",
    "--body", bot_token
], capture_output=True, text=True, env={"PATH": r"C:\Program Files\GitHub CLI;%PATH%", "GH_TOKEN": token})
print(f"Stdout: {result.stdout}")
print(f"Stderr: {result.stderr}")
print(f"Return: {result.returncode}")
