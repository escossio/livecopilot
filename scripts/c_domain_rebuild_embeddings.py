"""Regenera os embeddings do domínio C Programming isolado."""
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

DOMAIN_ROOT = Path('data/knowledge_domains/c_programming')
CHUNK_META = DOMAIN_ROOT / 'metadata' / 'chunk_index.json'
EMBEDDINGS_OUT = DOMAIN_ROOT / 'embeddings' / 'embeddings.jsonl'
METADATA_OUT = DOMAIN_ROOT / 'embeddings' / 'metadata.json'
MODEL = 'text-embedding-3-large'

if not CHUNK_META.exists():
    raise SystemExit(f'chunk metadata faltando: {CHUNK_META}')

chunk_entries = json.loads(CHUNK_META.read_text(encoding='utf-8'))
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise SystemExit('OPENAI_API_KEY não definido; exporte ou rode source codex-supervisor/.env.secrets')

client = OpenAI(api_key=api_key)
record_count = 0
length_sum = 0
embedding_dim = None

with EMBEDDINGS_OUT.open('w', encoding='utf-8') as out:
    for entry in chunk_entries:
        domain_path = Path(entry.get('domain_chunk_path', entry.get('chunk_path', '')))
        if not domain_path.is_file():
            raise SystemExit(f'chunk não encontrado: {domain_path}')
        text = domain_path.read_text(encoding='utf-8')
        response = client.embeddings.create(model=MODEL, input=text)
        vector = response.data[0].embedding
        if embedding_dim is None:
            embedding_dim = len(vector)
        record = {
            'chunk_id': entry['chunk_id'],
            'source_family': entry.get('source_family'),
            'source_file': entry.get('source_file'),
            'title': entry.get('title'),
            'text': text,
            'embedding': vector,
        }
        out.write(json.dumps(record, ensure_ascii=False) + '\n')
        record_count += 1
        length_sum += len(text.split())
print(f'{record_count} embeddings gerados com {embedding_dim} dimensões')

metadata = {
    'num_chunks': record_count,
    'avg_length_words': length_sum / record_count if record_count else 0,
    'embedding_dim': embedding_dim or 0,
    'model': MODEL,
    'generated_at': datetime.now(timezone.utc).isoformat(),
}
METADATA_OUT.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Metadata gravada em {METADATA_OUT}')
