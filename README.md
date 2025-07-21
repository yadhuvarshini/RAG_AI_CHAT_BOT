Here's the \*\*all-in-one technical documentation\*\* with integrated diagrams, code samples, and deployment guides:

\---

\# 🚀 AI Document Chat - Complete Technical Documentation

!\[System Architecture\](https://i.imgur.com/EDxP5jm.png)

\*Figure 1: End-to-End Production Architecture\*

\## 📚 Table of Contents

1\. \[Architecture Overview\](#-architecture-overview)

2\. \[Core Components\](#-core-components)

3\. \[Installation\](#-installation)

4\. \[Configuration\](#-configuration)

5\. \[API Reference\](#-api-reference)

6\. \[WebSocket Protocol\](#-websocket-protocol)

7\. \[Database Schema\](#-database-schema)

8\. \[Deployment\](#-deployment)

9\. \[Monitoring\](#-monitoring)

10\. \[Security\](#-security)

11\. \[Appendix\](#-appendix)

\---

\## 🏗️ Architecture Overview

\### System Flow

\`\`\`mermaid

graph LR

A\[User\] --> B\[Streamlit UI\]

B --> C\[Node.js Proxy\]

C --> D\[FastAPI Microservice\]

D --> E\[(MongoDB)\]

D --> F\[(Redis)\]

C --> G\[WebSocket\]

D --> H\[LLM APIs\]

\`\`\`

\### Data Pipeline

\`\`\`mermaid

flowchart TD

A\[PDF Upload\] --> B\[Text Extraction\]

B --> C\[Chunking\\n(512 tokens)\]

C --> D\[Embedding Generation\]

D --> E\[Vector Storage\]

E --> F\[Semantic Search\]

F --> G\[Context Augmentation\]

G --> H\[LLM Response\]

\`\`\`

\---

\## ⚙️ Core Components

\### 1. \*\*Frontend Service\*\*

\`\`\`python

\# streamlit\_app.py

st.file\_uploader("Upload Document", type=\["pdf"\])

st.chat\_message("assistant").write(response)

\`\`\`

\### 2. \*\*API Gateway (Node.js)\*\*

\`\`\`javascript

// server.js

app.post('/api/upload',

authenticateJWT,

fileUpload.single('file'),

forwardToFastAPI

);

\`\`\`

\### 3. \*\*AI Service (FastAPI)\*\*

\`\`\`python

\# main.py

@app.post("/process")

async def process\_file(

file: UploadFile = File(...),

token: str = Depends(oauth2\_scheme)

):

chunks = split\_text(extract\_text(file))

embeddings = generate\_embeddings(chunks)

\`\`\`

\---

\## 📥 Installation

\### Prerequisites

\`\`\`bash

\# Hardware

\- Minimum: 4vCPU, 8GB RAM, 50GB storage

\- Recommended: 8vCPU, 16GB RAM + NVIDIA T4 GPU

\# Software

docker-compose >= 2.20

Python 3.10+

Node.js 18+

\`\`\`

\### Setup Commands

\`\`\`bash

\# Clone with submodules

git clone --recurse-submodules https://github.com/your-repo/ai-document-chat.git

\# Start infrastructure

docker-compose -f docker-compose.infrastructure.yml up -d

\# Install backend

cd ai-fastapi-rag && poetry install

\# Install frontend

cd ../streamlit-ui && pip install -r requirements.txt

\`\`\`

\---

\## ⚙️ Configuration

\### Key Environment Variables

| Variable | Example | Description |

|----------|---------|-------------|

| \`MONGO\_URI\` | \`mongodb://user:pwd@host:27017/ai?authSource=admin\` | MongoDB connection string |

| \`JWT\_SECRET\` | \`hex(32)\` | HS256 signing key |

| \`EMBEDDING\_MODEL\` | \`gemini-pro\` | LLM provider specification |

\### Config Files

\`\`\`yaml

\# configs/embedding.yaml

gemini-pro:

chunk\_size: 1024

overlap: 128

vector\_dim: 768

\`\`\`

\---

\## 📡 API Reference

\### REST Endpoints

| Endpoint | Method | Auth | Request | Response |

|----------|--------|------|---------|----------|

| \`/api/upload\` | POST | JWT | \`multipart/form-data\` | \`{document\_id, summary}\` |

| \`/api/chat\` | GET | JWT | - | \`Array\` |

\### WebSocket Events

\`\`\`json

{

"event": "question",

"data": {

"chat\_id": "65a1f2b3c4d5e",

"question": "Explain page 3"

}

}

\`\`\`

\---

\## 🗃️ Database Schema

\### MongoDB Collections

\`\`\`javascript

// documents collection

{

\_id: ObjectId,

owner: ObjectId,

chunks: \[

{

text: String,

embedding: \[Float\],

page: Number

}

\],

metadata: {

name: String,

size: Number,

uploaded\_at: ISODate

}

}

\`\`\`

\---

\## 🚢 Deployment

\### Kubernetes (Production)

\`\`\`yaml

\# fastapi-deployment.yaml

resources:

limits:

cpu: "2"

memory: "4Gi"

requests:

cpu: "1"

memory: "2Gi"

\`\`\`

\### AWS CDK

\`\`\`typescript

new ecs.FargateService(this, "Service", {

taskDefinition,

desiredCount: 3,

healthCheckGracePeriod: Duration.minutes(2)

});

\`\`\`

\---

\## 🔍 Monitoring

\### Prometheus Metrics

\`\`\`python

\# metrics.py

REQUEST\_DURATION = Histogram(

'http\_request\_duration\_seconds',

'HTTP response time',

\['method', 'endpoint'\]

)

\`\`\`

\### Grafana Dashboard

!\[Monitoring Dashboard\](https://i.imgur.com/8GkwVlg.png)

\---

\## 🔒 Security

\### Controls

1\. \*\*Encryption\*\*: TLS 1.3 + AES-256

2\. \*\*Authentication\*\*: JWT with 24h expiry

3\. \*\*Audit Logging\*\*:

\`\`\`python

logger.info(f"ACCESS|{user\_id}|{endpoint}")

\`\`\`

\---

\## 📎 Appendix

\### A. Postman Collection

\[!\[Run in Postman\](https://run.pstmn.io/button.svg)\](https://app.getpostman.com/run-collection/your-collection-id)

\### B. Load Testing

\`\`\`bash

k6 run --vus 100 --duration 30s script.js

\`\`\`

\### C. Troubleshooting

| Symptom | Solution |

|---------|----------|

| 401 Errors | Verify JWT\_SECRET matches across services |

| Slow Responses | Check Redis connection pool settings |
