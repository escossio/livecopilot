# Docker Core Lexical Baseline Report

## Timestamp
- `20260319T020109Z`

## Método
- Busca lexical simples sobre os chunks já existentes em `data/knowledge_chunks/docker/`.
- Ranking básico por frequência e correspondência de termos normalizados.
- Sem embeddings, sem semantic baseline, sem expansão de corpus.

## Perguntas testadas
### 1. What is a container?
- chunk top: `docker-container-0001`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/core`
- classificação: `RESPONDIVEL`
- observação: Há correspondência direta de termos e definição operacional explícita no chunk top.
- trecho relevante: A container is an isolated process with the files and configuration it needs to run. Docker containers are self-contained, isolated, independent, and portable. Operationally, a container is the runtime unit you start with `docker run`, inspect with `docker ps`, and stop or remove without affecting other containers.

### 2. What is a Docker image?
- chunk top: `docker-image-layers-0002`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/storage`
- classificação: `RESPONDIVEL`
- observação: Há correspondência direta de termos e definição operacional explícita no chunk top.
- trecho relevante: Docker images are built from immutable filesystem layers. Each layer adds, removes, or modifies files, and layers can be reused across images to speed builds and reduce storage. Operationally, image layers explain why `docker image history` and Dockerfile-based builds are efficient.

### 3. What is a Dockerfile?
- chunk top: `docker-dockerfile-0003`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/core`
- classificação: `RESPONDIVEL`
- observação: Há correspondência direta de termos e definição operacional explícita no chunk top.
- trecho relevante: A Dockerfile is a text document used to build a container image. It declares instructions such as `FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD`, and `EXPOSE`. Operationally, it is the source of truth for `docker build` when you want to package an application into an image.

### 4. What does docker build do?
- chunk top: `docker-cli-build-0002`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/cli`
- classificação: `RESPONDIVEL`
- observação: Há correspondência direta de termos e definição operacional explícita no chunk top.
- trecho relevante: `docker build` reads a Dockerfile and produces an image from the instructions in that file. It is the core command for turning source plus build steps into a reusable image. A basic example is `docker build -t my-app .`, where the final dot points to the build context.

### 5. What does docker run do?
- chunk top: `docker-cli-run-0001`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/cli`
- classificação: `RESPONDIVEL`
- observação: Há correspondência direta de termos e definição operacional explícita no chunk top.
- trecho relevante: `docker run` creates and starts a container from an image. It is the main command for launching a workload with runtime settings like detached mode, port publishing, and container naming. A basic example is `docker run -d -p 8080:80 image-name`.

### 6. What does docker ps do?
- chunk top: `docker-cli-ps-0003`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/cli`
- classificação: `RESPONDIVEL`
- observação: Há correspondência direta de termos e definição operacional explícita no chunk top.
- trecho relevante: `docker ps` lists running containers and shows their IDs, images, commands, status, ports, and names. It is the quickest way to verify that a container is up. Use `docker ps -a` when you also need stopped containers.

### 7. What does docker logs do?
- chunk top: `docker-cli-logs-0004`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/cli`
- classificação: `RESPONDIVEL`
- observação: Há correspondência direta de termos e definição operacional explícita no chunk top.
- trecho relevante: `docker logs` prints a container's stdout and stderr so you can inspect application output after the container starts. It is the standard command for debugging runtime behavior without entering the container. A basic pattern is `docker logs <container-name>`.

### 8. What does docker exec do?
- chunk top: `docker-cli-exec-0005`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/cli`
- classificação: `RESPONDIVEL`
- observação: Há correspondência direta de termos e definição operacional explícita no chunk top.
- trecho relevante: `docker exec` runs a command inside an already running container. It is used for inspection and debugging when you need to interact with the container process namespace. A common example is `docker exec -it <container> sh`.

### 9. What are Docker volumes?
- chunk top: `docker-volumes-0001`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/storage`
- classificação: `RESPONDIVEL`
- observação: O chunk cobre persistência e montagem, suficiente para responder o conceito.
- trecho relevante: Volumes are Docker-managed persistent data stores for containers. They are the preferred mechanism for preserving data generated by or used by containers. Operationally, volumes let you keep data outside the container lifecycle and mount it with `docker run --mount` or `docker run --volume`.

### 10. What are Docker networks?
- chunk top: `docker-networks-0001`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/networking`
- classificação: `RESPONDIVEL`
- observação: O chunk cobre conectividade e port publishing, mas não define a rede Docker de forma canônica.
- trecho relevante: Docker networks provide connectivity between containers and between containers and the host. Core network use includes bridge-style networking, port publishing, and container-to-container communication. Operationally, networks are where you connect containers, expose ports, and control how traffic reaches a running workload.

### 11. What is a Docker registry?
- chunk top: `docker-registry-0002`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/networking`
- classificação: `RESPONDIVEL`
- observação: Há correspondência direta de termos e definição operacional explícita no chunk top.
- trecho relevante: A registry is a centralized location for storing and sharing container images. Docker Hub is the default public registry, and private registries are also common. Operationally, registries are where you pull images from and push tagged images to with `docker pull`, `docker tag`, and `docker push`.

### 12. What are image layers?
- chunk top: `docker-image-layers-0002`
- pasta: `/lab/projects/livecopilot/data/knowledge_chunks/docker/storage`
- classificação: `RESPONDIVEL`
- observação: O chunk explica layers imutáveis e reuso, cobrindo o núcleo da pergunta.
- trecho relevante: Docker images are built from immutable filesystem layers. Each layer adds, removes, or modifies files, and layers can be reused across images to speed builds and reduce storage. Operationally, image layers explain why `docker image history` and Dockerfile-based builds are efficient.

## Cobertura
- RESPONDIVEL: 12
- PARCIALMENTE_RESPONDIVEL: 0
- NAO_RESPONDIVEL: 0

## Conclusão
- O subset atual cobre os tópicos centrais do domínio docker_core com respostas lexicais diretas.
