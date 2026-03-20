# Semantic bad chunk before/after (20260315T080942Z)

- **Antes:** os top chunks das 10 perguntas parciais (descritos em `semantic_intent_chunk_trace_20260315T075619Z.json`) eram front matters ou definições desalinhadas que chegavam intactos até a síntese final.  
- **Depois:** o detector `_structural_noise_penalty()` aplica penalidades entre `0.28` e `0.6` sempre que há front matter, metadata, aliases ou caminhos (`STRUCTURAL_NOISE_PATTERNS`). O ranking continua apresentando os mesmos snippets, mas agora eles ficam abaixo de qualquer chunk com conteúdo útil verdadeiro graças à penalização forte.  
- **Impacto prático:** ainda não há COERENTE novo, pois os chunks úteis alternativos estão ausentes; o filtro prepara o terreno, garantindo que qualquer conteúdo limpo que surja na base seja preferido sem quebrar o que já estava bom.
