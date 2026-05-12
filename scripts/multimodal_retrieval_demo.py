"""Minimal image-text retrieval demo skeleton.

This script demonstrates the algorithmic flow:
1. encode images and texts into shared vector space,
2. normalize embeddings,
3. compute cosine similarity,
4. return top-k matches.

For a real run, install open_clip_torch or use a local CLIP-compatible model.
"""

import numpy as np


def normalize(x):
    norm = np.linalg.norm(x, axis=-1, keepdims=True) + 1e-9
    return x / norm


def topk_image_text_similarity(image_features, text_features, k=3):
    image_features = normalize(image_features)
    text_features = normalize(text_features)
    scores = image_features @ text_features.T
    return np.argsort(-scores, axis=1)[:, :k], scores


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    image_features = rng.normal(size=(4, 512))
    text_features = rng.normal(size=(8, 512))
    topk, scores = topk_image_text_similarity(image_features, text_features)
    print("topk text index for each image:", topk.tolist())
