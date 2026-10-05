import requests, json, re, hashlib, os

OLLAMA_URL = "http://localhost:11434/api/generate"
CACHE_FILE = "cache.json"

cache = {}
if os.path.exists(CACHE_FILE):
    cache = json.load(open(CACHE_FILE))


def extract_json(text):
    match = re.search(r"{[\s\S]*}", text)
    return match.group(0) if match else "{}"


def cache_key(prompt):
    return hashlib.md5(prompt.encode()).hexdigest()


def call_ollama(model, prompt):
    key = cache_key(prompt)

    if key in cache:
        return cache[key]

    try:
        res = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        output = res.json().get("response", "")
        clean = extract_json(output)
        result = json.loads(clean)
    except:
        result = {}

    cache[key] = result
    json.dump(cache, open(CACHE_FILE, "w"))

    return result