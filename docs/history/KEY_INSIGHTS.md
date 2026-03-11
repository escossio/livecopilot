# Key Insights

## Princípios centrais
1. **Saber o que não sabe.**
   - insight fundador: perguntas revelam fronteiras reais de ignorância.

2. **Não uma base estática, mas uma máquina que aprende pela revelação da própria ignorância.**
   - insight de arquitetura: lacuna detectada deve virar ação de ingestão.

## Aprendizados técnicos relevantes
- Separar `question_bank` de `knowledge` é obrigatório para manter semântica limpa.
- "Mais documento" não implica "mais cobertura" sem boa metadata/inferência.
- Explainability (debug, why_matched, sinais de evidência) é requisito, não luxo.
- Higiene documental evita falsos positivos de cobertura (ex.: HTML salvo como PDF).
- Penalização por qualidade no ranking funciona melhor que exclusão agressiva.
- `partial` foi importante em rodadas intermediárias para evitar falso `covered`; o peso/uso desse estado é sensível a recalibração.
- Consolidação temática transforma ranking repetitivo em plano executável.

## Padrões de erro identificados
- Over-tagging em documentos amplos distorce recuperação.
- Heurística de metadata pode puxar domínio errado (ex.: Terraform puxando Python genérico) se não houver guarda por contexto explícito.
- Conteúdo duplicado ou fraco pode inflar suporte se não houver hygiene gating.

## Decisões de processo que funcionaram
- Evolução incremental em fases curtas com checkpoint em `STATUS.md`.
- Correção mínima e localizada, evitando refactor amplo desnecessário.
- Separar claramente decisão, hipótese e experimento antes de consolidar como regra.

## Hipóteses ainda abertas
- Ajustes futuros em inferência/score podem migrar parte de `partial` para `covered` com mais precisão.
- Expansão de trilhas além de Python/Terraform pode alterar prioridade global de ingestão.
