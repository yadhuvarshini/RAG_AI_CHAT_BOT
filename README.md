# 🌐 AI Document Chat - Complete Technical Documentation

![System Architecture](https://i.imgur.com/EDxP5jm.png)
*Figure 1: End-to-End Production Architecture*

## 📚 Table of Contents
1. [Architecture Overview](#-architecture-overview)
2. [Core Components](#-core-components)  
3. [Installation Guide](#-installation-guide)
4. [Configuration Reference](#-configuration-reference)
5. [API Specifications](#-api-specifications)
6. [WebSocket Protocol](#-websocket-protocol)
7. [Database Design](#-database-design)
8. [Deployment](#-deployment)
9. [Monitoring](#-monitoring)
10. [Security](#-security)
11. [Appendix](#-appendix)

---

## 🏗️ Architecture Overview

### System Flow
```mermaid
graph LR
    A[User] --> B[Streamlit UI]
    B --> C[Node.js Gateway]
    C --> D[FastAPI Microservice]
    D --> E[(MongoDB)]
    D --> F[(Redis)]
    C --> G[WebSocket]
    D --> H[LLM APIs]

graph TB
    subgraph Frontend
        A[Streamlit] --> B[React Components]
        B --> C[WebSocket Client]
    end
    
    subgraph Backend
        D[Node.js] --> E[Auth]
        D --> F[Rate Limiter]
        D --> G[WS Server]
        H[FastAPI] --> I[LangChain]
        H --> J[Vector DB]
    end
    
    subgraph Data
        K[MongoDB] --> L[Document Chunks]
        M[Redis] --> N[Session Cache]
    end

