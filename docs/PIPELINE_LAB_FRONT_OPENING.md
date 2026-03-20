# Pipeline Lab — abertura formal da frente

## Contexto
A frente Pipeline Lab nasce do método validado nos domínios C, Python e Terraform, que já comprovou o pipeline padrão de ingestão e validação. Não substitui o LiveCopilot; ao contrário, é um projeto irmão e complementar que tem foco exclusivo em operacionalizar esse pipeline de domínios/assuntos antes que o conhecimento seja consumido pela aplicação principal.

## Problema que essa frente resolve
Hoje o processo está distribuído entre conversas, documentos soltos e execução manual; cada domínio precisa ser lembrado, rodado e monitorado com esforço humano repetitivo. Pipeline Lab consolida esse método em algo reproduzível, observável e auditável, reduzindo atrito, redundância e dependência de memória informal.

## O que é o Pipeline Lab
Pipeline Lab é uma frente separada, dedicada a ser o motor e orquestrador da execução de domínios usando o pipeline já validado. Inicialmente nasce como documentação e arquitetura de como o fluxo deve acontecer; futuramente pode evoluir para formas de execução assistida (runner, API e interface HTML).

## Utilidade prática
- organizar a ingestão de novos assuntos em filas controladas
- permitir execução em etapas delimitadas, com gates e checkpoints claros
- registrar artefatos, logs e divergências conforme cada domínio percorre o pipeline
- servir como cockpit operacional com visibilidade de status e próximos passos
- possibilitar ambientes descartáveis/sandbox e comparações de estratégias (A/B) quando chegar a fase de execução automatizada

## Encaixe no ecossistema do projeto
LiveCopilot permanece o projeto principal de conhecimento e operação; Pipeline Lab é a esteira de preparação e ingestão que alimenta o LiveCopilot. A ideia é: domínio novo → Pipeline Lab conduz o pipeline controlado → conhecimento pronto entregue ao LiveCopilot para consumo. Assim, um projeto alimenta o outro, sem que o pipeline tenha que ser refeito a cada domínio.

## Escopo inicial da frente
- acordos e contratos de execução entre domínios e supervisory operators
- definição de gates (source_policy, parsing, chunking etc.) e checkpoints obrigatórios
- catálogo básico de domínios pilotos para validar o fluxo
- runner mínimo para executar cada etapa manualmente, com logs
- sandbox simples para testar domínios em ambiente descartável
- API mínima para registrar status e divergências
- interface HTML mínima para visualização de etapas e autorizações de supervisão humana

## O que não será feito agora
- não construímos toda a ferramenta nesta rodada
- não lançamos o produto final Pipeline Lab
- não implementamos comparação A/B ativa ainda
- não integramos Pipeline Lab à produção do LiveCopilot agora
- não criamos automações cegas sem supervisão humana

## Ordem de execução prevista
1. abertura formal da frente (esta rodada)
2. documentação dos contratos e dos eyes-on gates
3. definição dos domínios de exemplo e registradores de fila
4. construção do runner mínimo e registro de artefatos
5. construção da API mínima para status/autorizações
6. construção da UI mínima (cockpit de supervisão)
7. prova de uso com domínios reais e registro de lições aprendidas

## Uso no dia a dia (visão)
- Escolher o domínio/assunto a ser ingerido
- Executar a etapa atual no runner mínimo, seguindo a ordem oficial
- Acompanhar logs e artefatos gerados por cada etapa
- Revisar divergências e registrar ações sugeridas
- Aceitar a passagem para a próxima etapa, retomar ou interromper o domínio
- Usar Pipeline Lab como estação de supervisão do pipeline que alimenta o LiveCopilot

## Estrutura inicial prevista
- `/lab/projects/pipeline-lab` (diretório raiz do projeto irmão)
- `docs/` (políticas, runbooks e handoffs específicos)
- `domains/` (catálogo de domínios e manifests)
- `app/` (runner/serviços operacionais)
- `web/` (UI mínima de cockpit)
- `runs/` (artefatos de execução, logs e checkpoints)
- `tests/` (validação de contratos e gates)

## Decisão desta rodada
A frente Pipeline Lab está oficialmente aberta. Esta rodada foi exclusivamente documental; nenhuma implementação foi feita e o foco foi registrar visão, escopo e plano de execução para conduzir etapas futuras.

## Próximos passos sugeridos
- detalhar documento de escopo e MVP do runner/API/UI
- estabelecer o protocolo de execução e os stage gates críticos
- definir o schema de domínio e checklist por etapa
- mapear o uso diário (daily usage) e os responsáveis por cada gate
- evoluir em seguida para runner/API/UI quando o protocolo estiver aprovado
