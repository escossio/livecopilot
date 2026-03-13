# Livecopilot

Livecopilot e um copiloto contextual em tempo real para conversas tecnicas, com base de conhecimento local, trilha de question bank e priorizacao de lacunas.

## Problema que resolve

Em cenarios de entrevista, troubleshooting e explicacao tecnica sob pressao, o projeto busca reduzir tempo de resposta com sugestoes curtas e contextualizadas, apoiadas por conhecimento pre-processado e sinais de gap.

## Visao tecnica (alto nivel)

O repositorio esta organizado em cinco blocos:

1. Realtime Copilot: captura/transcricao/contexto e resposta curta.
2. Knowledge Core: ingestao documental, chunking, busca e ranking semantico/local.
3. Question Bank + Gap Learning: ingestao de perguntas, cobertura e plano de acao.
4. Interview/Response Mode: framing de resposta curta por modo de uso.
5. Ops/Runbook Mode: automacao e CLI operacional para fluxos de incidente/runbook.

Referencias:
- `ARCHITECTURE.md`
- `docs/PROJECT_STAGE_INDEX.md`
- `docs/PROJECT_CONTRACT.md`

## Capacidades atuais

- API FastAPI com UI local em `http://localhost:8000`.
- Fluxo realtime com estado de conversa e respostas curtas.
- Ingestao de knowledge local (`txt`, `md`, `pdf`, `docx`, `html`) com manifestos e estado incremental.
- Ingestao separada de question bank com cobertura e action plan.
- Busca semantica/local com wrappers CLI.
- Gate local de testes unitarios via `scripts/unit_test_gate.sh`.

## Estrutura do projeto

Principais diretorios:

- `app/`: API, servicos de runtime realtime, ingestao e busca.
- `scripts/`: wrappers operacionais e gates locais.
- `tests/`: testes unitarios (`unittest`).
- `docs/`: contratos, handoffs, checkpoints e evidencias.
- `config/`: politicas e catalogos.
- `data/`: artefatos de ingestao e indices locais.
- `var/`: estado operacional e telemetria local.

## Como rodar localmente

### Requisitos

- Python 3.10+
- Ambiente Unix-like (scripts shell)

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Opcional:

```bash
cp .env.example .env
```

### Subir aplicacao

```bash
scripts/start.sh
```

Abrir:

- `http://localhost:8000`
- `http://localhost:8000/project-status`

### Testes locais

```bash
scripts/unit_test_gate.sh
```

Esse gate executa as suites:

- `tests/test_curated_sources_validation.py`
- `tests/test_knowledge_ingest_cli_modes.py`
- `tests/test_question_bank_items.py`
- `tests/test_question_bank_metadata.py`
- `tests/test_source_prefix_resolution.py`
- `tests/test_transcription_routing.py`

## Estado atual do projeto

- Projeto funcional em modo local-first.
- Etapas de base realtime, knowledge, question bank e trilha de gaps estao consolidadas.
- Etapa de busca externa com governanca ampliada segue parcial (contrato/documentacao definidos, expansao funcional em progresso).
- Precheck recente para GitHub registrou necessidade de curadoria local curta antes de remoto.

Referencias de estado:

- `STATUS.md`
- `docs/HANDOFF_GITHUB_PRECHECK_20260312T233115Z.md`
- `docs/PROJECT_STAGE_INDEX.md`

## Arquivos importantes

- `README.md`
- `ROADMAP.md`
- `ARCHITECTURE.md`
- `INGESTION_POLICY.md`
- `STATUS.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
