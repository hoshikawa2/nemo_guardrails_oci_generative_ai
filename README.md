
# Tutorial Avançado: Integração do NeMo Guardrails com OCI Generative AI via Proxy OpenAI-Compatible

---

## Introdução

Este tutorial demonstra como utilizar o **OCI Generative AI** por meio de uma interface compatível com a API da OpenAI, permitindo integração com frameworks modernos como o NeMo Guardrails.

A ideia principal não é apenas “usar um proxy”, mas sim:

>**Nota:** **desacoplar o modelo de linguagem (LLM) da aplicação**, criando uma camada intermediária que permite:
- trocar modelos facilmente
- integrar diferentes provedores (OCI, OpenAI, modelos locais)
- padronizar consumo via API OpenAI

---

## Ideia Central

O proxy `oci_openai_proxy.py` atua como um **adaptador universal**:

- Recebe requisições no padrão OpenAI (`/v1/chat/completions`)
- Traduz para chamadas do OCI Generative AI
- Retorna resposta no mesmo formato OpenAI

>**Nota:** Isso permite que ferramentas como o NeMo Guardrails funcionem sem saber que estão usando OCI.

>**Mais importante:**
Esse modelo permite evoluir para:
- múltiplos LLMs
- fallback entre provedores
- balanceamento
- controle centralizado

---

## Conceitos Fundamentais (Explicação detalhada)

### 1. Proxy OpenAI-Compatible

Um proxy é uma aplicação intermediária que:

- recebe requisições padronizadas
- adapta para outro backend
- retorna no mesmo formato

Neste caso:

Entrada:
```
/v1/chat/completions
```

Saída:
```
OCI Generative AI → resposta OpenAI-like
```

>**Nota:** Benefício:
Você não precisa alterar aplicações ao trocar o modelo.

---

### 2. NeMo Guardrails

O **entity["software","NVIDIA NeMo Guardrails","framework"]** é um framework que permite:

- controlar comportamento do LLM
- aplicar regras de segurança
- garantir previsibilidade

Ele atua como uma camada entre:

```
Usuário ↔ Guardrails ↔ LLM
```

---

### 3. Guardrails (Rails)

Guardrails são regras que atuam em pontos específicos:

- antes da entrada (input)
- durante o processamento
- após a resposta (output)

>**Nota:** Eles permitem:
- bloquear conteúdo
- validar respostas
- controlar comportamento

---

### 4. Arquitetura Final

```
User
 ↓
NeMo Guardrails
 ↓
Proxy OpenAI (porta 8051)
 ↓
OCI Generative AI
 ↓
Resposta
```

---

## Pré-requisitos

- Python 3.10+
- OCI configurado (`~/.oci/config`)
- Dependências:

```bash
pip install nemoguardrails fastapi uvicorn
```

---

## Subindo o Proxy OCI

### Arquivo: oci_openai_proxy.py

Este arquivo é responsável por:

- expor endpoint OpenAI
- traduzir requisições para OCI
- formatar respostas

### Execução

```bash
uvicorn oci_openai_proxy:app --host 0.0.0.0 --port 8051
```

>**Nota:** Endpoint disponível:

```
http://localhost:8051/v1/chat/completions
```

---

## Configuração do NeMo Guardrails

### Estrutura de arquivos

```
config/
 ├── config.yml
 ├── rails.co
```

---

## Arquivo: config.yml (Explicação detalhada)

Este é o arquivo principal de configuração.

### models

Define qual modelo será usado.

```yaml
models:
  - type: main
    engine: openai
    model: gpt-4
```

>**Nota:** Importante:
Mesmo usando OCI, usamos `engine: openai` porque o proxy simula essa API.

---

### parameters

```yaml
parameters:
  base_url: http://localhost:8051/v1
  api_key: dummy
```

- `base_url`: aponta para o proxy
- `api_key`: não é usada, mas é exigida pela interface OpenAI

---

### rails

```yaml
rails:
  input:
    flows:
      - self check input
  output:
    flows:
      - self check output
```

>**Nota:** Define quais regras serão aplicadas.

---

## Arquivo: rails.co (Explicação detalhada)

Este arquivo define os **fluxos de comportamento**.

Ele usa a linguagem Colang.

### Exemplo:

```co
define flow self check input
  user input
  bot respond "Input validado"
```

>**Nota:** Isso significa:
Sempre que houver entrada do usuário, execute esse fluxo.

---

### Output flow

```co
define flow self check output
  bot output
  bot respond "Output validado"
```

>**Nota:** Intercepta a saída antes de retornar ao usuário.

---

## Executando o NeMo

```bash
nemoguardrails run --config config
```

>**Nota:** Isso inicia o servidor do guardrails.

---

## Testando

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Olá"}]
  }'
```

---

## Resultados Esperados

Você deverá observar:

- request passa pelo guardrails
- proxy é acionado
- OCI responde
- saída é filtrada

Fluxo real:

```
User
 ↓
Input Rails
 ↓
LLM (via Proxy)
 ↓
Output Rails
 ↓
Resposta final
```

---

## Observações Importantes

- O proxy deve estar ativo antes do NeMo
- Logs podem ser ativados para debug
- O sistema é extensível para:
  - múltiplos modelos
  - fallback automático
  - auditoria

---

## Conclusão

Este modelo permite:

- desacoplar LLM da aplicação
- trocar backend sem impacto
- aplicar governança com guardrails
- evoluir para arquitetura multi-modelo

---

## References

- [NeMo Guardrails Library Configuration Overview](https://docs.nvidia.com/nemo/guardrails/latest/configure-rails/overview.html)

Visão geral de como estruturar o sistema de controle do LLM



- [Tools Integration with the NeMo Guardrails Library](https://docs.nvidia.com/nemo/guardrails/latest/integration/tools-integration.html)

Como integrar ferramentas externas (tools/APIs) dentro de um fluxo com NVIDIA NeMo Guardrails.
- Executar ações externas
- Chamar APIs
- Usar funções ou serviços do sistema
- Integrar com agentes e workflows reais


### Observability:

- [Logging and Debugging Guardrails Generated Responses](https://docs.nvidia.com/nemo/guardrails/latest/observability/logging/index.html)

Como observar, entender e depurar o que acontece dentro do fluxo de guardrails durante a execução de um LLM.

- [Quick Start for Tracing Guardrails](https://docs.nvidia.com/nemo/guardrails/latest/observability/tracing/quick-start.html)

Exemplo de código para habilitar tracing (rastreamento detalhado) no NeMo Guardrails usando OpenTelemetry.



---


## Acknowledgments

- **Author** - Cristiano Hoshikawa (Oracle LAD A-Team Solution Engineer)
