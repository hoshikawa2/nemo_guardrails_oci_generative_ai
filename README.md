
# Integrating NeMo Guardrails with OCI Generative AI via an OpenAI-Compatible Proxy

---

## Introduction

This tutorial demonstrates how to use **OCI Generative AI** through an OpenAI-compatible API interface, enabling integration with modern frameworks such as NVIDIA NeMo Guardrails.

The main idea is not just to “use a proxy”, but rather:

> **Note:** **decouple the language model (LLM) from the application**, creating an intermediate layer that allows:
- easy model switching  
- integration with multiple providers (OCI, OpenAI, local models)  
- standardized consumption via the OpenAI API  

---

## Core Idea

The `oci_openai_proxy.py` acts as a **universal adapter**:

- Receives requests in OpenAI format (`/v1/chat/completions`)  
- Translates them into OCI Generative AI calls  
- Returns responses in the same OpenAI format  

> **Note:** This allows tools like NeMo Guardrails to operate without knowing they are using OCI.

**More importantly:** This model enables evolution toward:
- multiple LLMs  
- provider fallback  
- load balancing  
- centralized control  

---

## Fundamental Concepts (Detailed Explanation)

### 1. OpenAI-Compatible Proxy

A proxy is an intermediate application that:

- receives standardized requests  
- adapts them to another backend  
- returns responses in the same format  

In this case:

Input:
```
/v1/chat/completions
```

Output:
```
OCI Generative AI → OpenAI-like response
```

> **Note (Benefit):**  
You don’t need to modify applications when switching models.

---

### 2. NeMo Guardrails

NVIDIA NeMo Guardrails is a framework that enables:

- controlling LLM behavior  
- applying safety rules  
- ensuring predictability  

It operates as a layer between:

```
User ↔ Guardrails ↔ LLM
```

---

### 3. Guardrails (Rails)

Guardrails are rules applied at specific stages:

- before input (input)  
- during processing  
- after response (output)  

**Note:** They allow:
- blocking content  
- validating responses  
- controlling behavior  

---

### 4. Final Architecture

```
User
 ↓
NeMo Guardrails
 ↓
OpenAI Proxy (port 8051)
 ↓
OCI Generative AI
 ↓
Response
```

---
## Prerequisites

- Python 3.10+  
- OCI configured (`~/.oci/config`)  
- Dependencies:

```bash
pip install nemoguardrails fastapi uvicorn
```

---

## Running the OCI Proxy

To configure the proxy, you can read more here:

[Integrating OpenClaw with Oracle Cloud Generative AI (OCI)
](https://github.com/hoshikawa2/openclaw-oci)


### File: oci_openai_proxy.py

This file is responsible for:

- exposing an OpenAI-compatible endpoint  
- translating requests to OCI  
- formatting responses  

### Execution

```bash
uvicorn oci_openai_proxy:app --host 0.0.0.0 --port 8051
```

**Available endpoint:**

```
http://localhost:8051/v1/chat/completions
```

---

## Configuring NeMo Guardrails

### File structure

```
config/
 ├── config.yml
 ├── rails.co
```

---

## File: config.yml (Detailed Explanation)

This is the main configuration file.

### models

Defines which model will be used.

```yaml
models:
  - type: main
    engine: openai
    model: gpt-4
```

> **Note:** Even using OCI, we use `engine: openai` because the proxy simulates this API.

---

### parameters

```yaml
parameters:
  base_url: http://localhost:8051/v1
  api_key: dummy
```

- `base_url`: points to the proxy  
- `api_key`: not used, but required by OpenAI interface  

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

> **Note:** Defines which rules will be applied.

---

## File: rails.co (Detailed Explanation)

This file defines **behavior flows**.

It uses Colang language.

### Example:

```co
define flow self check input
  user input
  bot respond "Input validated"
```

> **Note:** This means:
Whenever user input occurs, this flow is executed.

---

### Output flow

```co
define flow self check output
  bot output
  bot respond "Output validated"
```

> **Note:** Intercepts output before returning to user.

---

## Running NeMo

```bash
nemoguardrails run --config config
```

> **Note:** This starts the guardrails server.

---

## Testing

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

---

## Expected Results

You should observe:

- request goes through guardrails  
- proxy is invoked  
- OCI responds  
- output is filtered  

Real flow:

```
User
 ↓
Input Rails
 ↓
LLM (via Proxy)
 ↓
Output Rails
 ↓
Final Response
```

---

## Important Notes

- Proxy must be running before NeMo  
- Logs can be enabled for debugging  
- System is extensible for:
  - multiple models  
  - automatic fallback  
  - auditing  

---

## Conclusion

This model allows:

- decoupling LLM from application  
- switching backend without impact  
- applying governance with guardrails  
- evolving to multi-model architecture  

---

## Disclaimer

>**IMPORTANT**: The source code must be used at your own risk. There is no support and/or link with any company. The source code is free to modify and was built solely for the purpose of helping the community

--- 

## References

- [Integrating OpenClaw with Oracle Cloud Generative AI (OCI)
  ](https://github.com/hoshikawa2/openclaw-oci)

- [NeMo Guardrails Library Configuration Overview](https://docs.nvidia.com/nemo/guardrails/latest/configure-rails/overview.html)

Overview of how to structure the LLM control system


- [Tools Integration with the NeMo Guardrails Library](https://docs.nvidia.com/nemo/guardrails/latest/integration/tools-integration.html)

How to integrate external tools (tools/APIs) into a workflow with NVIDIA NeMo Guardrails:
- Execute external actions
- Call APIs
- Use system functions or services
- Integrate with real agents and workflows


### Observability:

- [Logging and Debugging Guardrails Generated Responses](https://docs.nvidia.com/nemo/guardrails/latest/observability/logging/index.html)

How to observe, understand, and debug what happens within the guardrails flow during the execution of an LLM.

- [Quick Start for Tracing Guardrails](https://docs.nvidia.com/nemo/guardrails/latest/observability/tracing/quick-start.html)

Example code to enable tracing (detailed execution tracking) in NeMo Guardrails using OpenTelemetry.

---

## Acknowledgments

- Author: Cristiano Hoshikawa (Oracle LAD A-Team Solution Engineer)
