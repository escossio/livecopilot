from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class TopicProfile:
    name: str
    keywords: List[str]
    short_answer: str
    long_answer: str
    time_gain: str
    counter_question: str
    experience_link: str


TOPIC_PROFILES: List[TopicProfile] = [
    TopicProfile(
        name="modelo OSI",
        keywords=["osi", "camadas", "camada", "l2", "l3", "l4", "l7", "modelo osi"],
        short_answer="O modelo OSI separa responsabilidades em camadas, do físico até a aplicação.",
        long_answer=(
            "Eu uso o OSI como guia: físico e enlace tratam transmissão, rede faz endereçamento,"
            " transporte garante confiabilidade, e aplicação entrega o serviço ao usuário."
        ),
        time_gain="Só um instante para organizar a explicação por camadas.",
        counter_question="Quer um exemplo prático de problema em L4 impactando a aplicação?",
        experience_link="Já usei essa divisão para acelerar troubleshooting e isolar falhas por camada.",
    ),
    TopicProfile(
        name="TCP/IP",
        keywords=["tcp/ip", "tcp", "ip", "udp", "icmp", "handshake", "conexão", "conexao"],
        short_answer="No TCP/IP, o foco é entender transporte (TCP/UDP) e endereçamento (IP).",
        long_answer=(
            "Eu costumo explicar pelo fluxo: IP cuida do roteamento, TCP garante entrega"
            " com handshake e controle de congestionamento, e UDP prioriza baixa latência."
        ),
        time_gain="Só um instante para organizar o fluxo TCP/IP.",
        counter_question="Você quer aprofundar em TCP (confiabilidade) ou UDP (latência)?",
        experience_link="Já otimizei serviços ajustando timeouts e janelas TCP conforme o tráfego real.",
    ),
    TopicProfile(
        name="redes de computadores",
        keywords=["redes de computadores", "rede", "redes", "lan", "wan", "switch", "roteador", "ip"],
        short_answer="Em redes de computadores, começo pelo escopo (LAN/WAN) e pelos requisitos.",
        long_answer=(
            "Eu mapeio topologia, protocolos e pontos de falha, garantindo segmentação"
            " adequada e observabilidade para manter desempenho e confiabilidade."
        ),
        time_gain="Deixa eu organizar o mapa da rede na resposta.",
        counter_question="Você está olhando mais para desenho de rede ou operação do dia a dia?",
        experience_link="Já participei de redesenho de topologia para reduzir latência e gargalos.",
    ),
    TopicProfile(
        name="troubleshooting",
        keywords=["troubleshooting", "diagnóstico", "diagnostico", "falha", "erro", "incidente"],
        short_answer="Em troubleshooting, sigo hipóteses e elimino camadas de forma sistemática.",
        long_answer=(
            "Eu inicio com sintomas e impacto, verifico camadas físicas e lógicas,"
            " e avanço com testes direcionados até isolar a causa raiz."
        ),
        time_gain="Só um instante para estruturar a linha de diagnóstico.",
        counter_question="Você já tem sintomas, logs ou métricas do incidente?",
        experience_link="Costumo reduzir MTTR usando checklists e métricas antes de fazer mudanças.",
    ),
    TopicProfile(
        name="Mikrotik",
        keywords=["mikrotik", "routeros", "winbox"],
        short_answer="No MikroTik, foco em regras claras de roteamento e firewall.",
        long_answer=(
            "Gosto de manter o RouterOS com regras documentadas, NAT e firewall explícitos,"
            " além de monitorar throughput e conexões para evitar gargalos."
        ),
        time_gain="Deixa eu organizar as regras principais na resposta.",
        counter_question="Você quer falar de roteamento, firewall ou QoS no MikroTik?",
        experience_link="Já implementei políticas de NAT e firewall em MikroTik com foco em segurança.",
    ),
    TopicProfile(
        name="roteamento",
        keywords=["roteamento", "routing", "rota", "rotas", "next-hop"],
        short_answer="Roteamento é escolher o melhor caminho com base em métricas e políticas.",
        long_answer=(
            "Eu defino rotas estáticas quando o cenário é simples, e uso roteamento dinâmico"
            " quando há crescimento, múltiplos links e necessidade de convergência."
        ),
        time_gain="Deixa eu organizar a lógica de roteamento.",
        counter_question="O ambiente é estático ou precisa de roteamento dinâmico?",
        experience_link="Já otimizei rotas para melhorar failover e reduzir perda de pacotes.",
    ),
    TopicProfile(
        name="BGP",
        keywords=["bgp", "asn", "peering", "roteamento externo", "route", "route-map"],
        short_answer="BGP é protocolo de roteamento externo baseado em políticas.",
        long_answer=(
            "Eu explico o BGP como escolha de caminhos usando atributos e políticas,"
            " garantindo redundância e controle de tráfego entre ASNs."
        ),
        time_gain="Só um instante para organizar o cenário de BGP.",
        counter_question="Estamos falando de peering público ou links privados entre ASNs?",
        experience_link="Já acompanhei ajustes de políticas para balancear tráfego entre links.",
    ),
    TopicProfile(
        name="VLAN",
        keywords=["vlan", "tag", "802.1q", "trunk", "access"],
        short_answer="VLAN segmenta a rede para segurança e organização.",
        long_answer=(
            "Eu uso VLANs para separar domínios de broadcast, reduzir ruído e aplicar"
            " políticas específicas por segmento."
        ),
        time_gain="Deixa eu organizar o desenho de VLAN.",
        counter_question="Você precisa de trunks entre switches ou VLANs isoladas?",
        experience_link="Já implementei segmentação por VLAN para separar ambientes e reduzir incidentes.",
    ),
    TopicProfile(
        name="NAT",
        keywords=["nat", "masquerade", "source nat", "dest nat", "snat", "dnat"],
        short_answer="NAT traduz endereços para permitir acesso entre redes.",
        long_answer=(
            "Eu vejo NAT como ferramenta de exposição controlada: SNAT para saída, DNAT para"
            " publicar serviços, sempre com regras claras e logs."
        ),
        time_gain="Só um instante para organizar as regras de NAT.",
        counter_question="Você quer SNAT para saída ou DNAT para publicar serviços?",
        experience_link="Já ajustei NAT para reduzir conflitos de IP e melhorar segurança.",
    ),
    TopicProfile(
        name="firewall",
        keywords=["firewall", "pf", "iptables", "nftables", "filter"],
        short_answer="Firewall é a política de quem pode falar com quem.",
        long_answer=(
            "Eu costumo definir regras explícitas por zona, manter defaults restritivos"
            " e registrar bloqueios críticos para análise."
        ),
        time_gain="Deixa eu organizar a política de regras.",
        counter_question="Você trabalha com zonas, serviços críticos ou listas de bloqueio?",
        experience_link="Já reduzi incidentes definindo regras mínimas e auditando logs de firewall.",
    ),
    TopicProfile(
        name="Linux",
        keywords=["linux", "systemd", "bash", "shell", "kernel", "iptables", "nftables"],
        short_answer="No Linux, foco em estabilidade, automação e observabilidade.",
        long_answer=(
            "Eu costumo administrar Linux com scripts seguros, serviços bem definidos"
            " no systemd e logs estruturados para diagnósticos rápidos."
        ),
        time_gain="Só um instante para organizar a resposta.",
        counter_question="Você quer foco em operação diária ou troubleshooting em Linux?",
        experience_link="Já automatizei rotinas de manutenção e deploy usando shell e systemd.",
    ),
    TopicProfile(
        name="observabilidade",
        keywords=["observabilidade", "tracing", "metrics", "metricas", "logs estruturados"],
        short_answer="Observabilidade é visibilidade de logs, métricas e traces.",
        long_answer=(
            "Eu defino SLIs/SLOs, centralizo logs e habilito traces para entender"
            " o comportamento de ponta a ponta."
        ),
        time_gain="Deixa eu estruturar a camada de observabilidade.",
        counter_question="Você já tem métricas e logs centralizados?",
        experience_link="Já implementei dashboards e alertas para reduzir tempo de detecção.",
    ),
    TopicProfile(
        name="logs",
        keywords=["log", "logs", "log estruturado", "loglevel", "rotacionar"],
        short_answer="Logs bons são claros, estruturados e fáceis de correlacionar.",
        long_answer=(
            "Eu padronizo logs com campos (request_id, usuário, latência) e"
            " defino rotação para evitar custo excessivo."
        ),
        time_gain="Só um segundo para organizar a estratégia de logs.",
        counter_question="Você já usa logs estruturados ou ainda texto simples?",
        experience_link="Já melhorei diagnóstico implementando correlação por request_id.",
    ),
    TopicProfile(
        name="monitoramento",
        keywords=["monitoramento", "alerta", "alertas", "dashboard", "prometheus", "grafana"],
        short_answer="Monitoramento é garantir saúde com métricas e alertas úteis.",
        long_answer=(
            "Eu defino métricas chave, thresholds realistas e alertas acionáveis,"
            " evitando ruído e mantendo foco no impacto ao usuário."
        ),
        time_gain="Deixa eu organizar as métricas principais.",
        counter_question="Você precisa mais de alertas de indisponibilidade ou de performance?",
        experience_link="Já reduzi alertas falsos ajustando thresholds e janelas de avaliação.",
    ),
    TopicProfile(
        name="Zabbix",
        keywords=["zabbix", "host", "trigger", "item", "template"],
        short_answer="No Zabbix, o foco é modelar hosts, itens e triggers com templates.",
        long_answer=(
            "Eu uso templates para padronizar coleta, e ajusto triggers para alertar"
            " o que realmente importa no ambiente."
        ),
        time_gain="Só um instante para organizar a estrutura no Zabbix.",
        counter_question="Você quer falar de templates, triggers ou agentes?",
        experience_link="Já implementei monitoramento com Zabbix em ambientes multi-site.",
    ),
    TopicProfile(
        name="APIs",
        keywords=["api", "rest", "endpoint", "swagger", "openapi"],
        short_answer="Em APIs, começo pelo contrato: recursos, métodos e erros.",
        long_answer=(
            "Eu desenho APIs pensando em recursos, idempotência, versionamento e"
            " documentação automática para facilitar integração."
        ),
        time_gain="Deixa eu organizar o contrato da API.",
        counter_question="Essa API é interna ou pública? Isso muda autenticação e versionamento.",
        experience_link="Já evoluí APIs mantendo compatibilidade por versionamento e contratos.",
    ),
    TopicProfile(
        name="FastAPI",
        keywords=["fastapi", "starlette", "pydantic", "uvicorn"],
        short_answer="FastAPI combina tipagem, validação automática e performance em Python.",
        long_answer=(
            "Eu destaco Pydantic para contratos claros e OpenAPI automático, com async"
            " para alto throughput quando há I/O."
        ),
        time_gain="Só um instante para estruturar a resposta.",
        counter_question="Quer foco em validação, performance ou organização dos endpoints?",
        experience_link="Já organizei APIs com FastAPI usando schemas e routers por domínio.",
    ),
    TopicProfile(
        name="Python",
        keywords=["python", "async", "asyncio", "typing", "pip", "venv"],
        short_answer="Em Python, priorizo legibilidade e tipagem leve.",
        long_answer=(
            "Eu organizo módulos pequenos, uso typing para contratos"
            " e async quando há I/O intensivo."
        ),
        time_gain="Só um instante para organizar a resposta.",
        counter_question="Você quer exemplo de organização de módulos ou de async?",
        experience_link="Já padronizei projetos Python para facilitar manutenção e testes.",
    ),
    TopicProfile(
        name="backend",
        keywords=["backend", "banco", "database", "fila", "cache", "microserviço", "microservico"],
        short_answer="No backend, o foco é consistência, performance e observabilidade.",
        long_answer=(
            "Eu penso em backend com dados, escalabilidade, filas e cache, além"
            " de métricas e logs para operação confiável."
        ),
        time_gain="Deixa eu organizar os pontos principais.",
        counter_question="Você está mais preocupado com performance, escala ou consistência?",
        experience_link="Já implementei cache e filas para reduzir latência e melhorar escala.",
    ),
    TopicProfile(
        name="arquitetura de sistemas",
        keywords=["arquitetura", "sistemas", "monolito", "microserviços", "eventos", "event-driven"],
        short_answer="Arquitetura é sobre trade-offs entre simplicidade, custo e evolução.",
        long_answer=(
            "Eu decido arquitetura avaliando domínio, equipe e requisitos, e"
            " prefiro começar simples antes de distribuir em serviços."
        ),
        time_gain="Só um instante para organizar os trade-offs.",
        counter_question="Há restrições de equipe ou escala que forçam uma arquitetura específica?",
        experience_link="Já conduzi migrações graduais para evitar ruptura e reduzir risco.",
    ),
    TopicProfile(
        name="automação de infraestrutura",
        keywords=["automação", "infraestrutura", "ansible", "terraform", "infra", "iac"],
        short_answer="Automação de infraestrutura reduz erro humano e acelera entregas.",
        long_answer=(
            "Eu aplico IaC para padronizar ambientes, com pipelines de validação"
            " e revisão para garantir segurança."
        ),
        time_gain="Deixa eu organizar a estratégia de automação.",
        counter_question="Você usa Ansible, Terraform ou outra ferramenta de IaC?",
        experience_link="Já automatizei provisionamento para reduzir tempo de setup.",
    ),
    TopicProfile(
        name="integração entre sistemas",
        keywords=["integração", "integracao", "sistemas", "webhook", "fila", "mensageria"],
        short_answer="Integração entre sistemas exige contratos claros e confiáveis.",
        long_answer=(
            "Eu gosto de definir contratos estáveis, lidar com idempotência e"
            " garantir observabilidade para detectar falhas."
        ),
        time_gain="Só um instante para organizar o desenho da integração.",
        counter_question="Essa integração é síncrona (API) ou assíncrona (fila)?",
        experience_link="Já implementei integrações com webhooks e filas garantindo rastreabilidade.",
    ),
]


def detect_topic(text: str) -> Optional[TopicProfile]:
    lowered = text.lower()
    scored = []
    for profile in TOPIC_PROFILES:
        hits = sum(1 for keyword in profile.keywords if keyword in lowered)
        if hits:
            scored.append((hits, profile))
    if not scored:
        return None
    scored.sort(key=lambda item: (-item[0], item[1].name))
    return scored[0][1]
