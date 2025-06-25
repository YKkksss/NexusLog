# Project NexusLog: 新一代实时日志分析与异常告警平台

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0--M1-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Powered by](https://img.shields.io/badge/Architect-ArchitectPrime-_#651fff)

**Project NexusLog** 是一个高性能、高扩展性、支持多路接入的现代化实时日志分析与异常告警平台。它旨在成为工程团队的“中枢神经系统”，将分散的日志数据汇聚为可行动的洞察，实现从被动救火到主动预防的跨越。

---

## 目录 (Table of Contents)
1. [项目愿景与简介](#1--项目愿景与简介-vision--introduction)
2. [核心特性](#2--核心特性-core-features)
3. [架构总览](#3--架构总览-architectural-overview)
4. [技术栈](#4--技术栈-technology-stack)
5. [快速开始](#5--快速开始-quick-start)
6. [完整功能清单详解](#6--完整功能清单详解-complete-feature-checklist)
7. [部署模式与数据接入](#7--部署模式与数据接入-deployment-models--data-ingestion)
8. [项目演进路线图](#8--项目演进路线图-project-roadmap)
9. [贡献指南](#9--贡献指南-contributing)
10. [开源许可](#10--开源许可-license)

---

## 1. 📖 项目愿景与简介 (Vision & Introduction)

在复杂的分布式系统中，日志是洞察系统行为的唯一窗口。然而，海量、异构、分散的日志也带来了巨大的挑战。**NexusLog的愿景**是构建一个集中化、智能化、对开发者友好的统一可观测性平台，赋能每一位工程师，让他们能轻松、快速、自信地应对系统问题。

本项目旨在解决以下核心痛点：
* **日志孤岛:** 不同应用、不同环境的日志分散，难以关联分析。
* **问题排查效率低:** 依赖原始的`grep`和`SSH`，在海量数据中定位问题根源如同大海捞针。
* **告警滞后:** 当问题发生时，无法第一时间获得精准告警，导致故障影响扩大。
* **接入复杂:** 现有日志系统接入流程复杂，开发团队采纳意愿低。

## 2. ✨ 核心特性 (Core Features)

* **高性能接收:** 基于FastAPI异步IO模型，轻松应对高并发日志写入。
* **多路接入:** 原生支持`HTTP/S`, `Syslog (TCP/TLS)`以及通过官方Agent的日志接入。
* **实时分析:** 从数据接入到可供查询，延迟控制在秒级。
* **强大检索:** 基于OpenSearch，提供闪电般的全文搜索和结构化查询能力。
* **数据可视化:** 可定制的仪表盘，通过丰富的图表洞察数据趋势。
* **灵活告警:** 基于查询的阈值告警，通过Email、Webhook等多种渠道实时通知。
* **部署简单:** 提供一键式安装脚本、容器化部署方案，极大降低用户接入成本。
* **高可靠性:** 采用“父子节点”架构，通过子节点(Agent)的本地缓冲机制，确保数据在网络波动等异常情况下不丢失。

## 3. 🏗️ 架构总览 (Architectural Overview)

本平台采用典型的分层、解耦、异步处理的现代数据平台架构。核心思想是将数据采集、缓冲、处理、存储、查询等环节清晰分离，使每一层都可以独立扩展和优化。

```mermaid
graph TD
    subgraph 用户端 (Client-Side)
        A[应用A on VM/Server] --> C{Fluent Bit Agent};
        B[应用B in K8s Pod] --> C;
        D[网络设备/路由器] -- Syslog/TLS --> E;
        F[脚本/简单应用] -- Direct HTTPS --> G;
    end

    subgraph 平台后端 (NexusLog Platform Backend - Parent Node)
        subgraph Ingestion Layer
            G(HTTPS API Ingestion <br> FastAPI);
            E(Syslog Ingestion <br> Rsyslog);
        end

        subgraph Processing Pipeline
            G --> H[RabbitMQ <br> Message Queue];
            E --> H;
            H --> I{Celery Workers <br> Parse, Enrich, Alert};
        end
        
        subgraph Storage Layer
            I --> J[OpenSearch <br> Log & Analytics Storage];
            I -- 告警判断 --> K;
            K[Redis <br> Cache & State] --> I;
            L[PostgreSQL <br> Metadata Storage] <--> M;
        end

        subgraph API & UI Layer
            M[API & Web UI <br> FastAPI] --> J;
            M --> K;
            O[用户浏览器] --> M;
        end
    end

    C -- Batched HTTPS --> G;
````

## 4\. 🛠️ 技术栈 (Technology Stack)

| 领域 | 技术选型 | 核心职责 |
| :--- | :--- | :--- |
| **Web框架/API** | **FastAPI** | 高性能异步API，处理数据接收、查询请求。 |
| **消息中间件**| **RabbitMQ** | 系统解耦、流量削峰的中央缓冲池。 |
| **后台任务处理**| **Celery** | 分布式任务队列，执行日志解析、入库、告警等耗时操作。 |
| **日志/分析存储**| **OpenSearch** | 核心数据存储引擎，提供强大的搜索与聚合分析能力。 |
| **元数据存储** | **PostgreSQL** | 存储用户、项目、告警规则等关系型数据。 |
| **缓存/状态存储**| **Redis** | 高性能缓存、告警计数器、分布式锁等。 |
| **子节点/Agent** | **Fluent Bit** | 部署在用户端，轻量、高效的日志采集与转发代理。 |
| **容器化** | **Docker** | 标准化应用打包与环境隔离。 |
| **容器编排** | **Kubernetes** | 生产环境的应用部署、扩展与管理。 |
| **前端框架** | **Vue.js / React** | 构建用户交互界面。 |

## 5\. 🚀 快速开始 (Quick Start)

在本地启动完整的NexusLog开发环境。

**前提:** 已安装 `Git`, `Docker` 和 `Docker Compose`。

```bash
# 1. 克隆项目
git clone [https://github.com/your-org/nexuslog.git](https://github.com/your-org/nexuslog.git)
cd nexuslog

# 2. 配置环境变量
# 从模板复制环境变量文件，并根据需要进行修改
cp .env.example .env

# 3. 启动所有服务
# Docker Compose将根据docker-compose.yml文件，自动构建并启动所有容器
docker-compose up -d --build

# 4. 访问平台
# 稍等片刻，等待所有服务健康启动
# 然后在浏览器中打开 http://localhost:8000
```

## 6\. 🧩 完整功能清单详解 (Complete Feature Checklist)

以下是平台规划的完整功能清单，按核心职责划分为不同模块。清单中明确了**父节点 (平台后端)** 和 **子节点 (采集代理)** 的功能范畴。

  * **一、 核心数据管道 (Core Data Pipeline)**

      * **数据接入层 (Ingestion) - (由父节点提供)**
          * **多协议支持**
              * ✅ **HTTP/S API 接入:** 提供 `POST /v1/logs/bulk` 端点，用于接收子节点和其他客户端的数据。
              * ✅ **Syslog 接入:** 支持 `Syslog over TCP/TLS` 加密传输。
          * **安全与认证**
              * ✅ **API Key 认证:** 每个项目/数据源拥有独立的API Key。
      * **数据缓冲与解耦 (Buffering & Decoupling) - (父节点内部机制)**
          * ✅ **消息队列:** 使用 RabbitMQ作为核心缓冲池，应对流量高峰，隔离前后端。
      * **数据处理与扩充 (Processing & Enrichment) - (父节点内部机制)**
          * ✅ **异步处理:** 使用 Celery Worker 进行所有耗时的数据处理任务。
          * **日志解析**
              * ✅ **JSON 自动解析**
              * ✅ **Grok 模式解析** (V2)
          * ✅ **数据标准化:** 对时间戳、日志级别等关键字段进行统一格式化。

  * **二、 数据存储 (Data Storage) - (由父节点提供)**

      * **日志数据存储**
          * ✅ **搜索引擎:** 使用 OpenSearch 或 Elasticsearch。
      * **元数据存储**
          * ✅ **关系型数据库:** 使用 PostgreSQL 或 MySQL。
      * **缓存与状态存储**
          * ✅ **内存数据库:** 使用 Redis。
      * **数据生命周期管理 (ILM)**
          * ✅ **(V3) 自动归档与删除**

  * **三、 子节点核心功能 (Child Node Core Functions) - (由Agent实现)**

      * **日志采集 (Collection)**
          * ✅ **文件监听:** 通过`tail`模式持续读取日志文件。
      * **本地可靠性保障**
          * ✅ **持久化缓冲:** 必须支持在本地磁盘进行数据缓冲，防止网络或父节点故障时数据丢失。
          * ✅ **状态记录:** 记录文件读取位置，防止Agent重启后重复发送日志。
      * **可靠转发 (Forwarding)**
          * ✅ **HTTP输出:** 支持将日志通过HTTPS批量发送给父节点。
          * ✅ **失败自动重试:** 在发送失败时，采用指数退避策略进行重试。

  * **四、 用户核心功能 (User-Facing Core Features) - (由父节点提供)**

      * **日志检索与探索 (Search & Explore)**
          * ✅ **全文搜索**
          * ✅ **结构化查询**
          * ✅ **时间范围过滤**
          * ✅ **实时日志流 (Live Tail)**
          * ✅ **保存查询**
      * **数据可视化 (Visualization)**
          * ✅ **自定义仪表盘 (Dashboard)**
          * ✅ **可视化组件 (Widgets):** 折线图、柱状图、饼图、单值指标卡。
      * **告警系统 (Alerting System)**
          * ✅ **规则创建与管理**
          * ✅ **状态管理与历史记录**
          * ✅ **多渠道通知:** 邮件、Webhook。

  * **五、 平台管理与用户体验 (Platform Management & UX) - (由父节点提供)**

      * **用户与项目管理**
          * ✅ **用户认证与项目隔离**
          * ✅ **(V2/V3) 基于角色的访问控制 (RBAC)**
      * **数据源引导与自动化部署 (Onboarding & Automation for Child Nodes)**
          * ✅ **交互式接入向导**
          * **一键式部署支持**
              * ✅ **传统服务器:** 自动生成 `curl | bash` 安装脚本。
              * ✅ **Kubernetes环境:** 自动生成`DaemonSet` YAML文件。
              * ✅ **公有云集成 (AWS):** 支持通过IAM Role授权，从UI触发在EC2上远程安装。
          * ✅ **配置管理工具集成:** (V2/V3) 提供Ansible等工具的代码片段。

  * **六、 非功能性核心保障 (Non-Functional Requirements)**

      * ✅ **高可靠性:** 强调子节点的本地缓冲能力。
      * ✅ **高安全性:** 强调全程TLS加密和数据静态加密。
      * ✅ **平台自身的可观测性:** 使用Prometheus和Grafana进行自我监控。

## 7\. 🛰️ 部署模式与数据接入 (Deployment Models & Data Ingestion)

平台支持灵活的数据接入方式，核心是**父子节点 (Parent-Child) 架构**。

  * **父节点 (Parent Node):** 指的是集中部署的、功能完整的NexusLog后端平台。
  * **子节点 (Child Node):** 指的是部署在用户服务器上，专职采集与转发的轻量级Agent (官方推荐 **Fluent Bit**)。

用户可选择以下任一方式将日志发送至父节点：

1.  **Agent模式 (推荐):** 在用户服务器上部署子节点(Agent)，通过一键式脚本或Kubernetes YAML进行安装。这是最可靠、功能最全的方式，支持本地磁盘缓冲，确保数据不丢失。
2.  **HTTP/S模式:** 简单应用或脚本可以直接调用父节点的HTTP API来发送日志。
3.  **Syslog模式:** 网络设备或遗留系统可以通过`Syslog over TCP/TLS`协议发送日志。

## 8\. 🗺️ 项目演进路线图 (Project Roadmap)

我们采用分阶段的迭代开发模式，确保快速交付核心价值。

  * **Phase 0: 基础设施搭建 (已完成)**

      * **目标:** 建立稳固的开发与部署基础。
      * **交付:** CI/CD流水线, Docker化的本地开发环境。

  * **Phase 1: 核心数据管道与MVP (进行中)**

      * **目标:** 打通端到端的数据流，实现核心的日志查询与实时查看。
      * **交付:** Agent/HTTP数据接入, 日志搜索UI, Live Tail功能, 基础用户项目管理。

  * **Phase 2: 分析能力增强与用户赋能 (计划中)**

      * **目标:** 从日志查看器升级为分析平台。
      * **交付:** 可视化仪表盘, 阈值告警系统, Webhook/邮件通知。

  * **Phase 3: 企业级特性与智能化 (规划中)**

      * **目标:** 满足大型企业需求，引入AI能力。
      * **交付:** RBAC权限管理, 数据生命周期管理(ILM), AIOps智能异常检测。

## 9\. 项目结构 (Contributing)

```
nexuslog/
│
├── .github/                      # CI/CD 与项目模板
│   └── workflows/
│       └── main.yml              # GitHub Actions CI/CD 配置文件 (自动化测试、构建、部署)
│
├── .env.example                  # 环境变量模板文件，用于指导配置
├── .gitignore                    # Git忽略文件配置
├── docker-compose.yml            # Docker Compose编排文件，用于一键启动本地开发环境
├── Dockerfile                    # FastAPI应用主程序的Dockerfile
├── README.md                     # 项目总纲文档 (我们刚刚完成的版本)
├── requirements.txt              # Python项目依赖清单
│
└── src/                          # 核心源代码目录 (使用src布局以避免模块导入问题)
    └── nexuslog_api/             # 主应用包
        │
        ├── api/                  # API路由层，负责定义所有HTTP端点
        │   └── v1/               # API版本v1
        │       ├── endpoints/    # 各个功能模块的端点定义
        │       │   ├── alerts.py         # 告警规则的CRUD API
        │       │   ├── dashboards.py     # 仪表盘配置的CRUD API
        │       │   ├── ingestion.py      # 日志接收的核心端点 (/logs/bulk)
        │       │   ├── projects.py       # 项目和API Key管理API
        │       │   ├── search.py         # 日志查询API
        │       │   └── users.py          # 用户注册、登录、信息管理API
        │       │
        │       └── v1_router.py  # 聚合所有v1版本的路由，统一入口
        │
        ├── core/                 # 项目核心配置与通用组件
        │   ├── config.py         # 使用Pydantic读取和管理环境变量，提供全局配置
        │   ├── db.py             # 数据库连接与会话管理 (PostgreSQL连接池)
        │   └── security.py       # 安全相关：密码哈希、JWT Token生成与验证
        │
        ├── crud/                 # 数据库操作层 (Create, Read, Update, Delete)
        │   ├── base.py           # 基础CRUD操作的基类 (可选)
        │   ├── crud_alert.py     # 告警规则的数据库操作
        │   ├── crud_project.py   # 项目的数据库操作
        │   └── crud_user.py      # 用户的数据库操作
        │
        ├── models/               # 数据库模型层 (SQLAlchemy ORM Models)
        │   ├── alert_rule.py     # 告警规则的数据表模型
        │   ├── base.py           # SQLAlchemy的声明式基类
        │   ├── project.py        # 项目的数据表模型
        │   └── user.py           # 用户的数据表模型
        │
        ├── schemas/              # 数据校验层 (Pydantic Schemas)，定义API的输入输出格式
        │   ├── alert.py          # 告警规则相关的Pydantic模型
        │   ├── log.py            # 接收日志数据的Pydantic模型
        │   ├── project.py        # 项目相关的Pydantic模型
        │   ├── token.py          # JWT Token相关的Pydantic模型
        │   └── user.py           # 用户相关的Pydantic模型 (如UserCreate, UserRead)
        │
        ├── services/             # 业务逻辑服务层，处理复杂业务逻辑
        │   ├── alerting_service.py       # 执行告警规则检查的核心逻辑
        │   ├── notification_service.py   # 发送邮件、Webhook通知的服务
        │   └── onboarding_service.py     # 生成Agent安装脚本和配置文件的服务
        │
        ├── celery_app/           # Celery分布式任务相关模块
        │   ├── tasks/            # 具体的Celery任务定义
        │   │   ├── check_alerts.py     # 定时任务：周期性检查告警规则
        │   │   ├── process_log.py      # 核心任务：解析日志并存入OpenSearch
        │   │   └── send_notification.py# 异步任务：发送告警通知
        │   │
        │   └── worker.py         # Celery Worker的入口和配置
        │
        └── main.py               # FastAPI应用的主入口文件，创建App实例，挂载路由
```

### **结构说明**

1.  **顶级目录:**

      * `.github/`: 存放与GitHub平台相关的CI/CD配置。
      * `src/`: 将所有应用代码放在`src`目录下，是一种现代Python项目的最佳实践，可以有效避免潜在的路径和模块导入问题。

2.  **`src/nexuslog_api/` 核心应用包:**

      * **`api/`**: 严格分离API路由定义，并按版本（`v1`）组织，便于未来API的升级和维护。
      * **`core/`**: 存放与具体业务无关，但整个项目都依赖的核心组件，如配置加载、数据库连接。
      * **`models/`**: 定义了数据在**数据库中**的形态（表结构）。
      * **`schemas/`**: 定义了数据在**API接口**上的形态（请求体、响应体），使用Pydantic进行严格的数据校验。`models`和`schemas`的分离是FastAPI应用保持清晰边界的关键。
      * **`crud/`**: 封装了所有直接与数据库交互的原子操作（增删改查），使业务逻辑层不必关心SQL细节。
      * **`services/`**: 封装了更复杂的业务流程。例如，一个“创建用户”的服务可能会调用`crud.create_user`和`notification_service.send_welcome_email`。
      * **`celery_app/`**: 将所有与Celery相关的代码集中管理，结构清晰。
      * **`main.py`**: 保持主入口文件尽可能的简洁，只负责组装和启动。



## 10\. 🤝 贡献指南 (Contributing)

我们欢迎来自社区的任何贡献！如果您希望参与贡献，请参考 `CONTRIBUTING.md` 文件了解详细的流程和规范。

## 11\. 📄 开源许可 (License)

本项目采用 [Apache 2.0 License](https://www.google.com/search?q=LICENSE) 开源许可。