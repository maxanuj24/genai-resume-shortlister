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

    # allow bypassing the cache for forced refreshes
    force_refresh = os.environ.get("FORCE_OLLAMA_REFRESH", "0") in ("1", "true", "True")
    if key in cache and not force_refresh:
        return cache[key]

    # allow temperature to be controlled via env var OLLAMA_TEMPERATURE (defaults to 0)
    try:
        temp_raw = os.environ.get("OLLAMA_TEMPERATURE", "0")
        try:
            temperature = float(temp_raw)
        except Exception:
            temperature = 0.0

        res = requests.post(
            OLLAMA_URL,
            # temperature can be adjusted; stream disabled for synchronous responses
            json={"model": model, "prompt": prompt, "stream": False, "temperature": temperature},
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