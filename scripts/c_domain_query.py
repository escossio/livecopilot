"""Consulta local do domínio C sem tocar no índice global.
"""
import argparse
import json
import math
import os
from pathlib import Path

from openai import OpenAI

DOMAIN_ROOT = Path('data/knowledge_domains/c_programming')
EMBEDDINGS_PATH = DOMAIN_ROOT / 'embeddings' / 'embeddings.jsonl'
CHUNK_META_PATH = DOMAIN_ROOT / 'metadata' / 'chunk_index.json'
MODEL = 'text-embedding-3-large'

if not EMBEDDINGS_PATH.exists():
    raise SystemExit(f'embeddings file missing: {EMBEDDINGS_PATH}')
if not CHUNK_META_PATH.exists():
    raise SystemExit(f'chunk metadata file missing: {CHUNK_META_PATH}')

records = []
with EMBEDDINGS_PATH.open('r', encoding='utf-8') as handle:
    for line in handle:
        record = json.loads(line)
        records.append(record)

chunk_meta_list = json.loads(CHUNK_META_PATH.read_text(encoding='utf-8'))
chunk_meta_map = {entry['chunk_id']: entry for entry in chunk_meta_list if 'chunk_id' in entry}

parser = argparse.ArgumentParser(description='Consulta o domínio C Programming usando vetores isolados.')
parser.add_argument('question', help='Pergunta a ser enviada ao embedding')
parser.add_argument('--top', type=int, default=5, help='Quantidade de resultados retornados')
parser.add_argument('--snippet-length', type=int, default=320, help='Tamanho máximo do snippet exibido')
args = parser.parse_args()

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise SystemExit('OPENAI_API_KEY não definido; rode `source codex-supervisor/.env.secrets` ou exporte a chave.')

client = OpenAI(api_key=api_key)
try:
    response = client.embeddings.create(model=MODEL, input=args.question)
    query_embedding = response.data[0].embedding
except Exception as exc:  # pragma: no cover - runtime dependency
    raise SystemExit(f'falha ao obter embedding da pergunta: {exc}')


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norma = math.sqrt(sum(x * x for x in a))
    normb = math.sqrt(sum(x * x for x in b))
    if norma == 0 or normb == 0:
        return 0.0
    return dot / (norma * normb)

scores = []
for record in records:
    score = cosine_similarity(query_embedding, record['embedding'])
    scores.append((score, record))

scores.sort(reverse=True, key=lambda pair: pair[0])
print(f'Top {args.top} resultados para: "{args.question}"')
for rank, (score, record) in enumerate(scores[: args.top], start=1):
    meta = chunk_meta_map.get(record['chunk_id'], {})
    snippet = record.get('text', '').replace('\n', ' ').strip()
    snippet = (snippet[: args.snippet_length] + '...') if len(snippet) > args.snippet_length else snippet

    print('---')
    print(f'[{rank}] chunk_id: {record.get("chunk_id")}')
    print(f'    source: {record.get("source_family")}/{record.get("source_file")} (score {score:.4f})')
    print(f'    title: {record.get("title")}')
    print(f'    section: {meta.get("section", "n/a")}')
    print(f'    chunk_path: {meta.get("domain_chunk_path", meta.get("chunk_path", "n/a"))}')
    print(f'    snippet: {snippet}')
