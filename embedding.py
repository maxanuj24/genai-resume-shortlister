from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def compute_similarity(resume, jd):
    model = get_model()

    r = " ".join(resume.get("skills", []))
    j = " ".join(jd.get("required_skills", []))

    return similarity(model.encode(r), model.encode(j)) * 100