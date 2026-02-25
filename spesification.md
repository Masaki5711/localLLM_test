# 生産工場向け ローカルLLMナレッジ・データ関連性分析システム 詳細仕様書

> **バージョン**: 2.0
> **最終更新**: 2026-02-25
> **ステータス**: ドラフト（詳細設計フェーズ）

---

## 目次

1. [システム概要](#1-システム概要)
2. [アーキテクチャ詳細設計](#2-アーキテクチャ詳細設計)
3. [データベース詳細設計](#3-データベース詳細設計)
4. [API 設計](#4-api-設計)
5. [ETL パイプライン詳細設計](#5-etl-パイプライン詳細設計)
6. [LLM 統合詳細設計](#6-llm-統合詳細設計)
7. [フロントエンド詳細設計](#7-フロントエンド詳細設計)
8. [非機能要件](#8-非機能要件)
9. [開発フェーズ計画](#9-開発フェーズ計画)

---

## 1. システム概要

### 1.1 プロジェクトの目的と背景

生産工場内には、作業標準書、過去のトラブル報告書、品質データなど、多種多様な形式（PDF, Word, Excel, PowerPoint等）のファイルが膨大に存在している。現状、これらの情報はディレクトリに散在しており、必要な情報を迅速に引き出すことが困難である。

本プロジェクトは、完全閉域網（オンプレミス）環境で稼働するローカルLLMを活用し、以下の目的を達成するシステムを構築する。

**目的1：属人化の解消とナレッジの共有**
暗黙知となっているノウハウや過去の事例を容易に検索可能にし、経験の浅い作業者でも適切な情報にアクセスできる環境を構築する。

**目的2：データ間の関連性分析**
「設備」「工程」「不良要因」などのデータ間の繋がり（ナレッジグラフ）を可視化し、根本原因の分析やプロセス改善（ばらつきの排除）を支援する。

**目的3：セキュアな情報活用**
機密性の高い製造データを扱うため、外部のクラウドAPIに依存しない完全ローカル環境で推論とデータ保管を完結させる。

### 1.2 スコープ定義

#### MVP（Phase 1）で含むもの

- PDF / Word ドキュメントのインジェストと検索
- ベクトル検索による意味的類似検索
- チャットインターフェースでの質問応答
- 回答に対するソース引用表示
- 基本的なユーザー認証（ローカルアカウント）
- ドキュメントアップロード機能

#### MVP に含まないもの（Phase 2 以降）

- ナレッジグラフの構築・可視化
- Excel / PowerPoint 対応
- ハイブリッド検索（ベクトル + グラフ）
- Active Directory 連携 RBAC
- 管理者ダッシュボード
- バッチ処理スケジューリング
- 版管理（新旧管理）

### 1.3 前提条件・制約事項

| 項目 | 内容 |
|------|------|
| ドキュメント規模 | 1,000件以上（PDF, Word, Excel, PowerPoint） |
| 利用者 | 管理者・エンジニア中心（同時接続: 最大10名程度） |
| 開発環境 | Windows 11 PC（GPU なし、RAM 16GB以上推奨） |
| 本番環境 | Windows PC + NVIDIA RTX 4500 Ada（24GB VRAM）、**RAM 32GB以上必須** |
| デプロイ方式 | GitHub 経由で Docker Compose デプロイ |
| ネットワーク | 本番PC はインターネット接続あり（Docker pull / GitHub clone 可能） |
| 運用時セキュリティ | 閉域網想定、Active Directory 連携 RBAC |
| OS | Windows 11 Pro（Docker Desktop for Windows 使用） |

### 1.4 用語集

| 用語 | 説明 |
|------|------|
| GraphRAG | RAG（検索拡張生成）とナレッジグラフを統合したアーキテクチャ |
| チャンク (Chunk) | ドキュメントを意味単位で分割したテキスト断片 |
| エンベディング (Embedding) | テキストをベクトル空間上の数値表現に変換したもの |
| エンティティ (Entity) | テキストから抽出された固有表現（設備名、工程名、不良名等） |
| ナレッジグラフ | エンティティ間の関係をノードとエッジで表現したグラフ構造 |
| リランキング (Re-ranking) | 検索結果の関連度を再評価し、順序を最適化する処理 |
| ハイブリッド検索 | ベクトル検索（意味的類似性）とグラフ検索（構造的関連性）の併用 |
| ETL | Extract（抽出）・Transform（変換）・Load（格納）の処理パイプライン |
| RBAC | Role-Based Access Control（役割ベースのアクセス制御） |
| VRAM | GPU のビデオメモリ。LLM 推論に必要 |
| 量子化 (Quantization) | モデルの精度を下げてメモリ使用量を削減する手法（4bit, 8bit等） |
| チョコ停 | 設備の一時的な停止（製造業用語） |
| VLM | Vision Language Model（画像を理解できるLLM） |

---

## 2. アーキテクチャ詳細設計

### 2.1 技術スタック

| レイヤー | 技術 | バージョン（推奨） | 選定理由 |
|---------|------|------------------|---------|
| Frontend | TypeScript / React | React 18+ | SPA構築、豊富なエコシステム |
| UI Library | Tailwind CSS + shadcn/ui | 最新安定版 | 高速なUI開発、一貫したデザイン |
| Graph Visualization | Cytoscape.js | 3.x | React統合が良好、1000+ノード対応 |
| Backend (API Gateway) | Rust / Axum | Axum 0.7+ | 高パフォーマンス、型安全、低リソース消費 |
| ETL Pipeline | Python / FastAPI | Python 3.11+ | LlamaIndex/LangChain エコシステム活用 |
| LLM Engine (開発) | Ollama | 最新安定版 | CPU推論対応、セットアップ容易 |
| LLM Engine (本番) | vLLM | 最新安定版 | GPU最適化、高スループット、バッチ推論 |
| LLM Model | Qwen2.5-14B-Instruct-GPTQ-Int4 | — | 日本語高性能、24GB VRAMに収まる最大クラス |
| Embedding Model | BAAI/bge-m3 | — | 日本語対応、Dense+Sparse ハイブリッド対応 |
| Vector DB | Qdrant | 最新安定版 | 単一バイナリ、Windows Docker対応、1000件規模に最適 |
| Graph DB | Neo4j Community Edition | 5.x | ナレッジグラフの標準、Cypher クエリ言語 |
| RDB | PostgreSQL | 16+ | ユーザー管理、セッション、監査ログ等の構造化データ |
| Cache / Queue | Redis | 7+ | セッション管理、クエリキャッシュ、タスクキュー |
| File Storage | MinIO | 最新安定版 | S3互換オブジェクトストレージ、元ファイル保管 |
| Monitoring | Prometheus + Grafana | 最新安定版 | リソース監視、アラート、ダッシュボード |
| Container | Docker Compose | Docker Desktop for Windows | 全サービスのオーケストレーション |

### 2.2 VRAM 配分計画（RTX 4500 Ada 24GB）

| コンポーネント | VRAM 使用量 | 備考 |
|---------------|------------|------|
| LLM (Qwen2.5-14B-GPTQ-Int4) | ~8GB | 推論時。KVキャッシュ含む |
| Embedding (bge-m3) | ~2GB | バッチ処理時 |
| CUDA コンテキスト | ~0.5GB | ランタイムオーバーヘッド |
| 予備 / OS | ~13.5GB | 余裕あり。将来的なモデルサイズ拡大に対応可能 |

#### GPU 共有方式

LLM 推論（vLLM）とエンベディング生成（bge-m3）は **同一 GPU を共有** する。排他制御のため以下の設計とする。

- **エンベディング生成は `llm-service` に統合** する。etl-service は llm-service の API 経由でエンベディングを取得する。
- `llm-service` のみが GPU デバイスを予約（`count: 1`）し、**etl-service は GPU を直接使用しない**。
- vLLM の `--gpu-memory-utilization 0.35` で LLM 用 VRAM を制限し、残りを bge-m3 に使用。
- ETL バッチ処理とチャット推論が同時に走る場合は、**llm-service 内の排他セマフォ** で LLM 推論を優先し、エンベディング生成はキュー待ちとする。

#### RAM 要件（本番環境）

| サービス | 推定 RAM | 備考 |
|---------|---------|------|
| Frontend (Nginx) | ~50MB | 静的ファイル配信 |
| API Gateway (Rust/Axum) | ~100MB | 軽量 |
| ETL Service (Python) | ~1GB | PDF パース時にピーク |
| LLM Service (vLLM + bge-m3) | ~3GB | CPU 側メモリ |
| Qdrant | ~3GB | 15,000チャンク時 |
| Neo4j | ~2GB | JVM ヒープ |
| PostgreSQL | ~512MB | shared_buffers |
| Redis | ~256MB | キャッシュ |
| MinIO | ~256MB | |
| Prometheus + Grafana | ~512MB | |
| **合計** | **~11GB** | **32GB RAM 以上を推奨** |

> **注意**: 開発環境（GPU なし）では Ollama の CPU 推論モードを使用する。推論速度は遅いが、機能検証には十分。開発環境用モデルは `qwen2.5:7b`（GGUF 形式）を使用する。Ollama は GGUF 形式のみ対応のため、本番用 GPTQ モデルとは異なる点に注意。

### 2.3 マイクロサービス構成

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Network                          │
│                                                                │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │ Frontend │───▶│ API Gateway  │───▶│ ETL Service  │         │
│  │ (Nginx)  │    │ (Rust/Axum)  │    │ (Python)     │         │
│  │ :3000    │    │ :8080        │    │ :8001        │         │
│  └──────────┘    └──────┬───────┘    └──────┬───────┘         │
│                         │                    │                  │
│                    ┌────┴────┐          ┌────┴────┐            │
│                    ▼         ▼          ▼         ▼            │
│  ┌──────────┐  ┌───────┐ ┌──────┐ ┌────────┐ ┌───────┐       │
│  │ LLM Svc  │  │Qdrant │ │Neo4j │ │Postgres│ │ Redis │       │
│  │ (vLLM)   │  │:6333  │ │:7474 │ │:5432   │ │:6379  │       │
│  │ :8002    │  │       │ │:7687 │ │        │ │       │       │
│  └──────────┘  └───────┘ └──────┘ └────────┘ └───────┘       │
│                                                                │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐                    │
│  │  MinIO   │  │Prometheus │  │ Grafana  │                    │
│  │ :9000    │  │ :9090     │  │ :3001    │                    │
│  │ :9001    │  │           │  │          │                    │
│  └──────────┘  └───────────┘  └──────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 サービス一覧と役割

| サービス | ポート | 技術 | 役割 |
|---------|--------|------|------|
| frontend | 3000 | React/TS (Nginx配信) | Web UI 提供 |
| api-gateway | 8080 | Rust / Axum | 認証、ルーティング、レート制限、リクエスト検証 |
| etl-service | 8001 | Python / FastAPI | ドキュメント解析、チャンク化、エンベディング、エンティティ抽出 |
| llm-service | 8002 | Python / FastAPI + vLLM/Ollama | LLM 推論、ストリーミング応答、リランキング |
| qdrant | 6333 | Qdrant | ベクトル検索（意味的類似性） |
| neo4j | 7474 / 7687 | Neo4j Community | グラフ検索（構造的関連性）、Cypher クエリ |
| postgres | 5432 | PostgreSQL | ユーザー、セッション、フィードバック、監査ログ |
| redis | 6379 | Redis | セッション管理、クエリキャッシュ、ETL タスクキュー |
| minio | 9000 / 9001 | MinIO | 元ファイルのオブジェクトストレージ（S3互換） |
| prometheus | 9090 | Prometheus | メトリクス収集 |
| grafana | 3001 | Grafana | 監視ダッシュボード・アラート |

### 2.5 サービス間通信パターン

| 通信経路 | プロトコル | 方式 | 用途 |
|---------|-----------|------|------|
| Frontend → API Gateway | HTTP/HTTPS | REST + WebSocket | ユーザーリクエスト、ストリーミング応答 |
| API Gateway → ETL Service | HTTP | REST | ドキュメントアップロード、ETL ジョブ管理 |
| API Gateway → LLM Service | HTTP + SSE | REST + Server-Sent Events | 質問応答、ストリーミング生成 |
| API Gateway → Qdrant | HTTP | REST (gRPC も可) | ベクトル検索 |
| API Gateway → Neo4j | Bolt | Neo4j Bolt プロトコル | グラフ検索 |
| API Gateway → PostgreSQL | TCP | PostgreSQL プロトコル | ユーザー管理、メタデータ |
| API Gateway → Redis | TCP | Redis プロトコル | セッション、キャッシュ |
| ETL Service → Qdrant | HTTP | REST | ベクトル格納 |
| ETL Service → Neo4j | Bolt | Neo4j Bolt プロトコル | エンティティ・関係性格納 |
| ETL Service → MinIO | HTTP | S3 API | 元ファイル格納・取得 |
| ETL Service → LLM Service | HTTP | REST | エンベディング生成 + エンティティ抽出用 LLM 推論 |
| ETL Service → Redis | TCP | Redis プロトコル | タスクキュー（ETL ジョブ管理） |

### 2.6 Docker Compose 設計方針

```yaml
# docker-compose.yml 構成概要
version: "3.9"

services:
  frontend:
    build: ./frontend
    ports: ["3000:80"]
    depends_on: [api-gateway]

  api-gateway:
    build: ./backend
    ports: ["8080:8080"]
    depends_on: [postgres, redis, qdrant, neo4j]
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
      - NEO4J_URL=bolt://neo4j:7687

  etl-service:
    build: ./etl
    ports: ["8001:8001"]
    depends_on: [qdrant, neo4j, minio, redis, llm-service]
    volumes:
      - document-watch:/data/watch    # 監視対象ディレクトリ
    # GPU は使用しない（エンベディングは llm-service 経由）

  llm-service:
    build: ./llm
    ports: ["8002:8002"]
    # LLM 推論 + エンベディング生成の両方を担当（GPU 排他制御）
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: [qdrant-data:/qdrant/storage]

  neo4j:
    image: neo4j:5-community
    ports: ["7474:7474", "7687:7687"]
    volumes: [neo4j-data:/data]
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}

  postgres:
    image: postgres:16
    ports: ["5432:5432"]
    volumes: [postgres-data:/var/lib/postgresql/data]
    environment:
      - POSTGRES_DB=graphrag
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: [redis-data:/data]

  minio:
    image: minio/minio:latest
    ports: ["9000:9000", "9001:9001"]
    volumes: [minio-data:/data]
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes: [./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml]

  grafana:
    image: grafana/grafana:latest
    ports: ["3001:3000"]
    volumes: [grafana-data:/var/lib/grafana]

volumes:
  qdrant-data:
  neo4j-data:
  postgres-data:
  redis-data:
  minio-data:
  grafana-data:
  document-watch:
```

### 2.7 ネットワーク設計

全サービスは Docker の内部ネットワーク `graphrag-net` 上で通信する。外部公開ポートは最小限に制限。

| 外部公開 | ポート | 対象 |
|---------|--------|------|
| Yes | 3000 | Frontend（ユーザーアクセス） |
| Yes | 8080 | API Gateway（API アクセス） |
| Yes | 9001 | MinIO Console（管理者のみ） |
| Yes | 3001 | Grafana（管理者のみ） |
| No | その他全て | Docker 内部通信のみ |

---

## 3. データベース詳細設計

### 3.1 Qdrant（ベクトルデータベース）

#### 3.1.1 役割

ドキュメント内のテキストチャンクをベクトル化して保存し、ユーザーの自然言語クエリに対する意味的な類似検索を行う。

#### 3.1.2 コレクション設計

**コレクション名**: `document_chunks`

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | UUID | チャンクの一意識別子 |
| vector (dense) | Float[1024] | bge-m3 Dense ベクトル（1024次元） |
| vector (sparse) | SparseVector | bge-m3 Sparse ベクトル（BM25相当） |

**ペイロード（メタデータ）**:

```json
{
  "document_id": "uuid",
  "chunk_index": 0,
  "text": "チャンクのテキスト内容",
  "file_name": "トラブル報告書_2024Q3.pdf",
  "file_path": "/documents/reports/2024/",
  "file_type": "pdf",
  "document_type": "trouble_report",
  "created_at": "2024-07-15T10:30:00Z",
  "updated_at": "2024-07-15T10:30:00Z",
  "version": 1,
  "is_latest": true,
  "department": "manufacturing",
  "equipment_ids": ["EQ-001", "EQ-002"],
  "process_ids": ["PROC-SMT-01"],
  "heading": "3.2 原因分析",
  "page_number": 5,
  "chunk_size": 512,
  "language": "ja"
}
```

#### 3.1.3 インデックス設計

| インデックス種別 | 対象フィールド | 目的 |
|----------------|--------------|------|
| HNSW (Dense) | dense vector | 高速な近似最近傍検索 |
| Sparse Index | sparse vector | キーワードベースの精密検索 |
| Keyword Index | document_type | フィルタリング |
| Keyword Index | department | 部署別フィルタリング |
| Keyword Index | file_type | ファイル種別フィルタリング |
| Integer Index | version | 版管理フィルタリング |
| Boolean Index | is_latest | 最新版フィルタリング |

#### 3.1.4 検索方式

- **Dense 検索**: コサイン類似度による意味検索（主検索）
- **Sparse 検索**: BM25 相当のキーワード検索（補助検索）
- **ハイブリッド検索**: Dense + Sparse の RRF（Reciprocal Rank Fusion）統合
- **フィルタ付き検索**: メタデータ条件（部署、ファイル種別、最新版のみ等）と組み合わせ

### 3.2 Neo4j（グラフデータベース）

#### 3.2.1 役割

抽出されたエンティティ間の関係性をネットワーク状に保持し、複雑な因果関係や影響範囲の特定を行う。

#### 3.2.2 ノード設計

**Document ノード**

| プロパティ | 型 | 説明 | 制約 |
|-----------|-----|------|------|
| id | String | 一意識別子（UUID） | UNIQUE |
| title | String | ドキュメントタイトル | NOT NULL |
| file_name | String | ファイル名 | NOT NULL |
| file_path | String | ファイルパス | — |
| file_type | String | pdf / docx / xlsx / pptx | NOT NULL |
| document_type | String | trouble_report / standard / quality_data / manual | — |
| department | String | 所属部署 | — |
| version | Integer | 版番号 | DEFAULT 1 |
| is_latest | Boolean | 最新版フラグ | DEFAULT true |
| created_at | DateTime | 作成日時 | NOT NULL |
| updated_at | DateTime | 更新日時 | NOT NULL |
| chunk_count | Integer | チャンク数 | — |
| is_deleted | Boolean | 削除フラグ | DEFAULT false |
| minio_object_key | String | MinIO 上の元ファイルキー | — |

**Equipment ノード（設備）**

| プロパティ | 型 | 説明 | 制約 |
|-----------|-----|------|------|
| id | String | 設備ID（例: EQ-001） | UNIQUE |
| name | String | 設備名 | NOT NULL |
| type | String | 設備種別（リフロー炉、実装機等） | — |
| line | String | 所属ライン | — |
| location | String | 設置場所 | — |
| status | String | active / inactive / maintenance | DEFAULT "active" |

**Process ノード（工程）**

| プロパティ | 型 | 説明 | 制約 |
|-----------|-----|------|------|
| id | String | 工程ID（例: PROC-SMT-01） | UNIQUE |
| name | String | 工程名（例: はんだ印刷工程） | NOT NULL |
| category | String | 工程カテゴリ（SMT, THT, 検査等） | — |
| sequence | Integer | 工程順序 | — |

**Defect ノード（不良・異常）**

| プロパティ | 型 | 説明 | 制約 |
|-----------|-----|------|------|
| id | String | 不良ID（UUID） | UNIQUE |
| name | String | 不良名（はんだブリッジ、部品欠品等） | NOT NULL |
| category | String | 分類（外観不良、機能不良、設備異常等） | — |
| severity | String | critical / major / minor | — |

**Part ノード（部品）**

| プロパティ | 型 | 説明 | 制約 |
|-----------|-----|------|------|
| id | String | 部品番号 | UNIQUE |
| name | String | 部品名 | NOT NULL |
| type | String | 部品種別（IC, 抵抗, コンデンサ等） | — |
| manufacturer | String | メーカー名 | — |

#### 3.2.3 エッジ（リレーションシップ）設計

| エッジ | 始点 | 終点 | プロパティ | 説明 |
|--------|------|------|-----------|------|
| DESCRIBES | Document | Process | extracted_at, confidence | 文書が工程を記述 |
| MENTIONS | Document | Defect | extracted_at, confidence, context | 文書が不良を言及 |
| MENTIONS | Document | Equipment | extracted_at, confidence, context | 文書が設備を言及 |
| MENTIONS | Document | Part | extracted_at, confidence | 文書が部品を言及 |
| USES | Process | Equipment | — | 工程が設備を使用 |
| OCCURRED_IN | Defect | Equipment | date, frequency, resolved | 不良が設備で発生 |
| OCCURRED_IN | Defect | Process | date, frequency | 不良が工程で発生 |
| CAUSED_BY | Defect | Defect | — | 不良の因果関係 |
| REQUIRES | Process | Part | quantity | 工程が部品を必要とする |
| RELATED_TO | Document | Document | relation_type | 文書間の関連（参照、改訂等） |
| SUPERSEDES | Document | Document | — | 文書の改訂関係（新→旧） |

#### 3.2.4 インデックスと制約

```cypher
-- ユニーク制約
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT equipment_id IF NOT EXISTS FOR (e:Equipment) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT process_id IF NOT EXISTS FOR (p:Process) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT defect_id IF NOT EXISTS FOR (df:Defect) REQUIRE df.id IS UNIQUE;
CREATE CONSTRAINT part_id IF NOT EXISTS FOR (pt:Part) REQUIRE pt.id IS UNIQUE;

-- 全文検索インデックス（日本語対応）
CREATE FULLTEXT INDEX document_fulltext IF NOT EXISTS FOR (d:Document) ON EACH [d.title, d.file_name];
CREATE FULLTEXT INDEX equipment_fulltext IF NOT EXISTS FOR (e:Equipment) ON EACH [e.name, e.type];
CREATE FULLTEXT INDEX process_fulltext IF NOT EXISTS FOR (p:Process) ON EACH [p.name];
CREATE FULLTEXT INDEX defect_fulltext IF NOT EXISTS FOR (df:Defect) ON EACH [df.name, df.category];

-- 検索用インデックス
CREATE INDEX document_type_idx IF NOT EXISTS FOR (d:Document) ON (d.document_type);
CREATE INDEX document_latest_idx IF NOT EXISTS FOR (d:Document) ON (d.is_latest);
CREATE INDEX equipment_line_idx IF NOT EXISTS FOR (e:Equipment) ON (e.line);
CREATE INDEX defect_severity_idx IF NOT EXISTS FOR (df:Defect) ON (df.severity);
```

### 3.3 PostgreSQL（リレーショナルデータベース）

#### 3.3.1 役割

ユーザー管理、セッション管理、フィードバック、ドキュメントメタデータ、監査ログ等の構造化データを管理する。

#### 3.3.2 テーブル設計

**users テーブル**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- Phase 1: ローカル認証
    display_name VARCHAR(200),
    role VARCHAR(50) NOT NULL DEFAULT 'user',  -- admin, user, viewer
    department VARCHAR(100),
    ad_object_id VARCHAR(255),  -- Phase 3: AD連携用
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_department ON users(department);
```

**sessions テーブル**

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

**chat_sessions テーブル**

```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    is_archived BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
```

**chat_messages テーブル**

```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    sources JSONB,  -- 引用元情報 [{ document_id, chunk_id, text, score }]
    graph_data JSONB,  -- 関連グラフデータ
    token_count INTEGER,
    latency_ms INTEGER,  -- 応答生成時間
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(chat_session_id);
CREATE INDEX idx_chat_messages_created ON chat_messages(created_at);
```

**documents テーブル**

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000),
    file_type VARCHAR(20) NOT NULL,  -- pdf, docx, xlsx, pptx
    file_size BIGINT,  -- bytes
    document_type VARCHAR(50),  -- trouble_report, standard, quality_data, manual
    department VARCHAR(100),
    version INTEGER DEFAULT 1,
    is_latest BOOLEAN DEFAULT true,
    previous_version_id UUID REFERENCES documents(id),
    minio_object_key VARCHAR(500) NOT NULL,
    minio_bucket VARCHAR(100) DEFAULT 'documents',
    chunk_count INTEGER DEFAULT 0,
    etl_status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, partial, failed
    etl_error TEXT,
    uploaded_by UUID REFERENCES users(id),
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_department ON documents(department);
CREATE INDEX idx_documents_latest ON documents(is_latest);
CREATE INDEX idx_documents_etl_status ON documents(etl_status);
CREATE INDEX idx_documents_file_name ON documents(file_name);
```

**feedback テーブル**

```sql
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    rating VARCHAR(10) NOT NULL,  -- 'good' or 'bad'
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_feedback_message ON feedback(chat_message_id);
CREATE INDEX idx_feedback_rating ON feedback(rating);
```

**audit_log テーブル**

```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,  -- login, logout, search, upload, delete, admin_action
    resource_type VARCHAR(50),  -- document, user, chat_session
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);
```

**etl_jobs テーブル**

```sql
CREATE TABLE etl_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    job_type VARCHAR(50) NOT NULL,  -- ingest, re-index, delete
    status VARCHAR(20) DEFAULT 'queued',  -- queued, running, completed, failed
    progress REAL DEFAULT 0.0,  -- 0.0 ~ 1.0
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_etl_jobs_status ON etl_jobs(status);
CREATE INDEX idx_etl_jobs_document ON etl_jobs(document_id);
```

### 3.4 データストア間の整合性管理

#### 3.4.1 Single Source of Truth（信頼源）

**PostgreSQL を全ドキュメントメタデータの信頼源（SSoT）とする。**

| データストア | 保持するデータ | 役割 |
|-------------|-------------|------|
| PostgreSQL | 全メタデータ（SSoT） | マスターデータ管理、トランザクション保証 |
| Qdrant | `document_id`, `document_type`, `department`, `is_latest` + ベクトル | 検索フィルタに必要な最小限のメタデータ |
| Neo4j | `id`, `title`, `is_latest`, `is_deleted` | グラフ探索に必要な最小限のプロパティ |

詳細なメタデータ（`file_path`, `file_size`, `minio_object_key` 等）は PostgreSQL からのみ取得する。

#### 3.4.2 整合性維持方式

3 つのデータストアは異なるトランザクション管理機構を持つため、分散トランザクションは採用しない。代わりに **Saga パターン（補償トランザクション）** を使用する。

**データ格納の順序（ETL 完了時）**:
1. PostgreSQL にドキュメントメタデータを INSERT（`etl_status = 'processing'`）
2. Qdrant にチャンク + ベクトルを格納
3. Neo4j にエンティティ + 関係性を格納
4. PostgreSQL の `etl_status` を `'completed'` に更新

**失敗時の補償**:
- ステップ 2 で失敗: PostgreSQL の `etl_status` を `'failed'` に更新。MinIO のファイルは保持。
- ステップ 3 で失敗: Qdrant のチャンクを削除（補償）。PostgreSQL を `'failed'` に更新。
- ステップ 4 で失敗: 自動リトライ（3回）。それでも失敗時は管理者通知。

**非同期整合性チェック（日次バッチ）**:
- PostgreSQL の `completed` 状態のドキュメントが Qdrant と Neo4j に存在するか確認
- 不整合が検出された場合、管理者に通知し、再インデックスジョブを自動作成

### 3.5 バージョン管理（文書の新旧管理）方式

> **注意**: Phase 1 では版管理フィールド（`version`, `is_latest`, `previous_version_id`）はデータモデルに含むが、API/UI からの版管理操作は公開しない。Phase 3 で機能を有効化する。

1. **新版アップロード時**:
   - PostgreSQL: 既存文書の `is_latest = false` に更新 → 新文書を INSERT
   - Qdrant: 旧チャンクの `is_latest` を `false` に更新（バッチ更新）
   - Neo4j: Document ノードの `is_latest` を `false` に更新 → `SUPERSEDES` エッジを作成
   - **失敗時**: PostgreSQL のみ成功した場合は旧文書の `is_latest` をロールバック

2. **検索時のデフォルト動作**:
   - `is_latest = true` のチャンクのみを検索対象
   - ユーザーが明示的に「過去版も含む」を選択した場合のみ全版を検索

3. **削除時**:
   - PostgreSQL: 論理削除（`etl_status = 'deleted'`）
   - Qdrant: チャンクを物理削除
   - Neo4j: Document ノードに `is_deleted = true` を設定（エッジは保持、履歴追跡用）
   - グラフ検索クエリでは `WHERE d.is_deleted = false` を条件に含める

---

## 4. API 設計

### 4.1 共通仕様

#### ベース URL

```
http://{host}:8080/api/v1
```

#### 認証方式

- **Phase 1**: JWT Bearer Token（ローカルアカウント認証）
- **Phase 3**: JWT + Active Directory 連携（LDAP/SAML）

全てのエンドポイント（`/auth/*` を除く）は `Authorization: Bearer <token>` ヘッダーが必須。

#### 共通レスポンス形式

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "request_id": "uuid",
    "timestamp": "2024-07-15T10:30:00Z"
  }
}
```

**エラーレスポンス**:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力値が不正です",
    "details": [
      { "field": "query", "message": "検索クエリは必須です" }
    ]
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2024-07-15T10:30:00Z"
  }
}
```

#### エラーコード一覧

| HTTP Status | エラーコード | 説明 |
|------------|------------|------|
| 400 | VALIDATION_ERROR | 入力値不正 |
| 401 | UNAUTHORIZED | 未認証 |
| 403 | FORBIDDEN | 権限不足 |
| 404 | NOT_FOUND | リソースが見つからない |
| 409 | CONFLICT | リソース競合 |
| 413 | PAYLOAD_TOO_LARGE | ファイルサイズ超過 |
| 429 | RATE_LIMITED | レート制限 |
| 500 | INTERNAL_ERROR | サーバー内部エラー |
| 503 | SERVICE_UNAVAILABLE | LLM サービス等が利用不可 |

#### レート制限ポリシー

| エンドポイントグループ | 制限 | ウィンドウ |
|---------------------|------|----------|
| 認証系（/auth/*） | 10回 | 1分 |
| チャット系（/chat/*） | 30回 | 1分 |
| 検索系（/search/*） | 60回 | 1分 |
| ドキュメント管理（/documents/*） | 20回 | 1分 |
| 管理系（/admin/*） | 100回 | 1分 |

### 4.2 認証 API

#### POST /api/v1/auth/login

ユーザーログイン。

**リクエスト**:
```json
{
  "username": "tanaka",
  "password": "********"
}
```

**レスポンス（200）**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "username": "tanaka",
      "display_name": "田中太郎",
      "role": "user",
      "department": "製造部"
    }
  }
}
```

#### POST /api/v1/auth/refresh

トークンリフレッシュ。

**リクエスト**:
```json
{
  "refresh_token": "eyJ..."
}
```

#### POST /api/v1/auth/logout

ログアウト（セッション無効化）。

### 4.3 チャット API

#### POST /api/v1/chat

GraphRAG 検索 + 回答生成。

**リクエスト**:
```json
{
  "query": "昨年のAラインにおける実装工程のチョコ停の主な原因は？",
  "chat_session_id": "uuid | null",
  "options": {
    "include_graph": true,
    "search_mode": "hybrid",
    "max_sources": 5,
    "include_archived": false,
    "department_filter": null,
    "document_type_filter": null,
    "date_range": {
      "from": "2025-01-01",
      "to": "2025-12-31"
    }
  }
}
```

**レスポンス（200）**:
```json
{
  "success": true,
  "data": {
    "message_id": "uuid",
    "chat_session_id": "uuid",
    "answer": "Aラインにおける実装工程のチョコ停の主な原因は...",
    "sources": [
      {
        "document_id": "uuid",
        "document_title": "Aライン実装工程トラブル報告書 2025Q3",
        "file_name": "trouble_report_A_line_2025Q3.pdf",
        "chunk_text": "...該当テキスト...",
        "page_number": 5,
        "relevance_score": 0.92,
        "search_type": "vector"
      }
    ],
    "graph_data": {
      "nodes": [
        { "id": "EQ-001", "label": "実装機A", "type": "Equipment" },
        { "id": "PROC-SMT-01", "label": "実装工程", "type": "Process" },
        { "id": "DEF-001", "label": "チョコ停", "type": "Defect" }
      ],
      "edges": [
        { "source": "DEF-001", "target": "EQ-001", "label": "OCCURRED_IN" },
        { "source": "PROC-SMT-01", "target": "EQ-001", "label": "USES" }
      ]
    },
    "metadata": {
      "search_time_ms": 1200,
      "generation_time_ms": 3500,
      "total_chunks_searched": 1500,
      "chunks_retrieved": 10,
      "chunks_after_rerank": 5
    }
  }
}
```

#### POST /api/v1/chat/stream

ストリーミング回答生成（Server-Sent Events）。`POST /api/v1/chat` と同じリクエストボディを受け取り、レスポンスを SSE で返す。

> **設計メモ**: 質問送信（POST）とストリーミング受信を単一リクエストで行う。2 段階フロー（POST → GET）ではなく、POST 自体が SSE レスポンスを返す方式を採用。

**リクエスト**: `POST /api/v1/chat` と同一

**レスポンス**: `text/event-stream`

```
event: start
data: {"message_id": "uuid", "chat_session_id": "uuid"}

event: sources
data: {"sources": [...]}

event: graph
data: {"graph_data": {...}}

event: token
data: {"content": "A"}

event: token
data: {"content": "ライン"}

event: done
data: {"metadata": {"total_tokens": 256, "generation_time_ms": 3500}}
```

> ソース情報とグラフデータは検索完了後・回答生成開始前に送信し、フロントエンドで先行表示する。

#### GET /api/v1/chat/sessions

チャットセッション一覧取得。

**クエリパラメータ**: `page`, `limit`, `sort`

#### GET /api/v1/chat/sessions/:id/messages

セッション内メッセージ一覧取得。

#### DELETE /api/v1/chat/sessions/:id

チャットセッション削除。

### 4.4 検索 API

#### POST /api/v1/search

検索のみ（回答生成なし）。

**リクエスト**:
```json
{
  "query": "リフロー炉 温度プロファイル",
  "search_mode": "hybrid",
  "limit": 20,
  "offset": 0,
  "filters": {
    "document_type": ["trouble_report", "standard"],
    "department": "製造部",
    "date_range": { "from": "2024-01-01", "to": "2025-12-31" },
    "is_latest": true
  }
}
```

**search_mode 選択肢**:
- `vector`: ベクトル検索のみ（意味的類似性）
- `graph`: グラフ検索のみ（構造的関連性）
- `hybrid`: ベクトル + グラフ統合（デフォルト）
- `keyword`: Sparse ベクトルによるキーワード検索

### 4.5 ナレッジグラフ API

#### GET /api/v1/graph/explore

ナレッジグラフの探索。

**クエリパラメータ**:

| パラメータ | 型 | 説明 | デフォルト |
|-----------|-----|------|----------|
| node_id | String | 起点ノードのID | — |
| node_type | String | ノード種別フィルタ | — |
| depth | Integer | 探索深度 | 2 |
| limit | Integer | 最大ノード数 | 50 |
| relationship_types | String[] | エッジ種別フィルタ | 全て |

**レスポンス（200）**:
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "EQ-001",
        "label": "実装機A",
        "type": "Equipment",
        "properties": { "line": "Aライン", "status": "active" }
      }
    ],
    "edges": [
      {
        "id": "rel-001",
        "source": "PROC-SMT-01",
        "target": "EQ-001",
        "type": "USES",
        "properties": {}
      }
    ],
    "stats": {
      "total_nodes": 25,
      "total_edges": 40
    }
  }
}
```

#### GET /api/v1/graph/search

グラフ内のノード検索。

**クエリパラメータ**: `q` (検索文字列), `type` (ノード種別), `limit`

### 4.6 ドキュメント管理 API

#### POST /api/v1/documents/upload

ドキュメントアップロード。

**リクエスト**: `multipart/form-data`

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| file | File | Yes | アップロードファイル |
| document_type | String | No | ドキュメント種別 |
| department | String | No | 所属部署 |
| replace_document_id | UUID | No | 置換対象（版管理用） |

**ファイルサイズ上限**: 100MB

**対応形式**: `.pdf`, `.docx`, `.xlsx`, `.pptx`（Phase 1 では `.pdf`, `.docx` のみ）

**レスポンス（202 Accepted）**:
```json
{
  "success": true,
  "data": {
    "document_id": "uuid",
    "etl_job_id": "uuid",
    "status": "queued",
    "message": "ドキュメントがアップロードされ、処理キューに追加されました"
  }
}
```

#### GET /api/v1/documents

ドキュメント一覧取得。

**クエリパラメータ**: `page`, `limit`, `sort`, `document_type`, `department`, `etl_status`, `is_latest`

#### GET /api/v1/documents/:id

ドキュメント詳細取得。

#### DELETE /api/v1/documents/:id

ドキュメント削除（論理削除）。

#### GET /api/v1/documents/:id/download

元ファイルのダウンロード（MinIO から取得）。

#### GET /api/v1/documents/:id/chunks

ドキュメントのチャンク一覧取得。

### 4.7 ETL ジョブ管理 API

#### GET /api/v1/etl/jobs

ETL ジョブ一覧取得。

#### GET /api/v1/etl/jobs/:id

ETL ジョブ詳細・進捗取得。

#### POST /api/v1/etl/jobs/:id/retry

失敗したジョブのリトライ。

### 4.8 フィードバック API

#### POST /api/v1/feedback

回答に対するフィードバック送信。

**リクエスト**:
```json
{
  "chat_message_id": "uuid",
  "rating": "good",
  "comment": "正確な回答でした"
}
```

### 4.9 管理 API

#### GET /api/v1/admin/status

システム全体のステータス確認。

**レスポンス**:
```json
{
  "success": true,
  "data": {
    "services": {
      "api_gateway": { "status": "healthy", "uptime_seconds": 86400 },
      "llm_service": { "status": "healthy", "model": "Qwen2.5-14B-Instruct-GPTQ-Int4", "vram_usage_mb": 8192 },
      "etl_service": { "status": "healthy", "active_jobs": 2 },
      "qdrant": { "status": "healthy", "collections": 1, "total_points": 15000 },
      "neo4j": { "status": "healthy", "nodes": 5000, "relationships": 12000 },
      "postgres": { "status": "healthy", "connections": 5 },
      "redis": { "status": "healthy", "memory_used_mb": 128 },
      "minio": { "status": "healthy", "total_objects": 1000, "total_size_gb": 5.2 }
    },
    "stats": {
      "total_documents": 1000,
      "total_chunks": 15000,
      "total_users": 25,
      "total_chat_sessions": 500,
      "total_queries_today": 120
    }
  }
}
```

#### GET /api/v1/admin/users

ユーザー一覧取得（管理者のみ）。

#### POST /api/v1/admin/users

ユーザー作成（管理者のみ）。

#### PUT /api/v1/admin/users/:id

ユーザー更新（管理者のみ）。

#### DELETE /api/v1/admin/users/:id

ユーザー無効化（管理者のみ）。

#### GET /api/v1/admin/audit-log

監査ログ取得（管理者のみ）。

**クエリパラメータ**: `page`, `limit`, `user_id`, `action`, `date_from`, `date_to`

### 4.10 ユーザー設定 API

#### GET /api/v1/users/me

ログインユーザー自身の情報取得。

#### PUT /api/v1/users/me

ログインユーザー自身の設定更新（表示名、パスワード変更）。

**リクエスト**:
```json
{
  "display_name": "田中太郎",
  "current_password": "********",
  "new_password": "********"
}
```

### 4.11 辞書管理 API（Phase 2）

#### GET /api/v1/admin/dictionaries

辞書種別一覧取得（equipment, process, defect, part）。

#### GET /api/v1/admin/dictionaries/:type

指定種別の辞書エントリ一覧取得。

#### PUT /api/v1/admin/dictionaries/:type

辞書エントリの一括更新。

**リクエスト**:
```json
{
  "entries": [
    { "canonical": "実装機A", "aliases": ["マウンタA", "チップマウンタA"] }
  ]
}
```

#### POST /api/v1/admin/dictionaries/:type/entries

辞書エントリの追加。

#### DELETE /api/v1/admin/dictionaries/:type/entries/:id

辞書エントリの削除。

---

## 5. ETL パイプライン詳細設計

### 5.1 概要

指定されたディレクトリを監視し、多様なファイルを構造化してデータベースへ格納する非同期処理パイプライン。

### 5.2 処理フロー

```
ファイル検知/アップロード
    │
    ▼
┌──────────────┐
│ 1. ファイル収集 │  watchdog / API アップロード
└──────┬───────┘
       ▼
┌──────────────┐
│ 2. MinIO 格納 │  元ファイルをオブジェクトストレージに保存
└──────┬───────┘
       ▼
┌──────────────┐
│ 3. パース     │  形式別テキスト抽出
└──────┬───────┘
       ▼
┌──────────────────┐
│ 4. チャンク化     │  日本語対応セマンティック分割
└──────┬───────────┘
       ▼
┌──────────────────────────┐
│ 5. エンベディング生成      │  bge-m3 (Dense + Sparse)
└──────┬───────────────────┘
       ▼
┌──────────────────────────┐
│ 6. エンティティ抽出        │  LLM + ルールベース併用
└──────┬───────────────────┘
       ▼
┌──────────────────────────┐
│ 7. データ格納             │  Qdrant / Neo4j / PostgreSQL
└──────────────────────────┘
```

### 5.3 ファイル形式別パース戦略

#### PDF

| 項目 | 内容 |
|------|------|
| ライブラリ | PyMuPDF (fitz) |
| テキスト抽出 | ページ単位でテキスト抽出、レイアウト情報保持 |
| テーブル抽出 | PyMuPDF のテーブル検出 + Markdown 変換 |
| 画像内テキスト | 将来: ローカル VLM による OCR（Phase 3 検討） |
| メタデータ | タイトル、作成者、作成日、ページ数 |

#### Word (.docx)

| 項目 | 内容 |
|------|------|
| ライブラリ | python-docx |
| テキスト抽出 | 段落・見出し構造を維持して抽出 |
| テーブル抽出 | テーブルを Markdown 形式に変換 |
| 画像 | 将来対応（Phase 3） |
| メタデータ | タイトル、作成者、最終更新日 |

#### Excel (.xlsx)（Phase 2）

| 項目 | 内容 |
|------|------|
| ライブラリ | openpyxl |
| 変換方式 | シート単位で Markdown テーブルに変換 |
| セル結合 | 結合セルを展開して情報を補完 |
| 数式 | 計算結果の値を使用（数式自体は無視） |
| チャート | テキスト説明に変換（将来: VLM で画像解析） |
| メタデータ | シート名一覧、行数、列数 |

#### PowerPoint (.pptx)（Phase 2）

| 項目 | 内容 |
|------|------|
| ライブラリ | python-pptx |
| テキスト抽出 | スライド単位でテキスト抽出（タイトル + 本文） |
| テーブル | Markdown テーブルに変換 |
| 画像・図解 | 将来: ローカル VLM で解析（Phase 3） |
| ノート | スピーカーノートも抽出対象 |
| メタデータ | スライド数、タイトル |

### 5.4 日本語テキストのチャンク化戦略

#### チャンク化パラメータ

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| chunk_size | 512 トークン | bge-m3 の最大入力長 8192 だが、精度とのバランス |
| chunk_overlap | 64 トークン | チャンク間のオーバーラップ（文脈の連続性維持） |
| separator_priority | 見出し > 段落 > 文 | 分割の優先順位 |

#### チャンク化アルゴリズム

1. **見出し境界分割（最優先）**: Markdown の `#`, `##`, `###` 等の見出しで分割
2. **段落境界分割**: 空行（`\n\n`）で段落を識別して分割
3. **文境界分割**: 日本語の文末（`。`、`！`、`？`）で分割
4. **トークン数チェック**: 各チャンクが `chunk_size` を超える場合は再分割
5. **オーバーラップ追加**: 前チャンクの末尾 `chunk_overlap` トークンを次チャンクの先頭に付加

#### 日本語固有の処理

- トークナイザ: bge-m3 の tokenizer を使用（サブワード分割）
- 文境界検出: 正規表現 `[。！？\n]` + 括弧内の句点を除外
- 見出し検出: Markdown 見出し + Word の見出しスタイル情報を活用

### 5.5 エンティティ抽出

#### 二段構成: LLM + ルールベース併用

**Phase 1: ルールベース抽出**

| エンティティ種別 | 抽出方法 | パターン例 |
|----------------|---------|-----------|
| 設備名 | 正規表現 + カスタム辞書 | `[A-Z]ライン`, `実装機[A-Z0-9]+`, 辞書登録名 |
| 工程名 | カスタム辞書マッチング | `はんだ印刷工程`, `リフロー工程`, `検査工程` |
| 部品番号 | 正規表現 | `[A-Z]{2,3}-[0-9]{3,6}` パターン |
| 不良名 | カスタム辞書マッチング | `はんだブリッジ`, `部品欠品`, `チョコ停` |

**Phase 2: LLM ベース抽出**

```
システムプロンプト:
あなたは製造業の文書分析の専門家です。
以下のテキストから、次のカテゴリのエンティティを抽出してください。

カテゴリ:
- Equipment (設備): 設備名、機械名、ライン名
- Process (工程): 製造工程名
- Defect (不良・異常): 不良モード名、異常名
- Part (部品): 部品名、部品番号

出力は以下の JSON 形式で返してください:
{
  "entities": [
    { "text": "実装機A", "type": "Equipment", "confidence": 0.95 },
    { "text": "はんだ印刷工程", "type": "Process", "confidence": 0.90 }
  ],
  "relationships": [
    { "source": "チョコ停", "target": "実装機A", "type": "OCCURRED_IN", "confidence": 0.85 }
  ]
}
```

#### カスタム辞書

```json
{
  "equipment": [
    { "canonical": "実装機A", "aliases": ["マウンタA", "チップマウンタA"] },
    { "canonical": "リフロー炉1号", "aliases": ["リフロー1", "RF-01"] }
  ],
  "process": [
    { "canonical": "はんだ印刷工程", "aliases": ["印刷工程", "クリームはんだ印刷"] },
    { "canonical": "リフロー工程", "aliases": ["リフロー", "はんだ付け工程"] }
  ],
  "defect": [
    { "canonical": "はんだブリッジ", "aliases": ["ブリッジ", "半田ブリッジ"] },
    { "canonical": "チョコ停", "aliases": ["チョコ停止", "一時停止"] }
  ]
}
```

辞書ファイルは管理画面から編集可能（Phase 2）。

### 5.6 バッチ処理スケジューリング

| 処理種別 | トリガー | タイミング | 備考 |
|---------|---------|----------|------|
| オンデマンド処理 | API アップロード | 即時（キュー経由） | ユーザーがファイルをアップロードした場合 |
| ディレクトリ監視 | watchdog ファイル検知 | リアルタイム | 新規・更新ファイルの検知 |
| 夜間バッチ | スケジューラ (Redis Queue) | 毎日 22:00 | 大量ファイルの一括処理 |
| 再インデックス | 管理者手動実行 | 任意 | エンベディングモデル変更時等 |

### 5.7 ファイル監視（watchdog）

```python
# 監視設定
WATCH_DIRECTORY = "/data/watch"
SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".xlsx", ".pptx"]
DEBOUNCE_SECONDS = 5  # ファイル変更の安定待ち
```

| イベント | アクション |
|---------|----------|
| ファイル作成 | ETL ジョブ作成 → キューに投入 |
| ファイル更新 | 既存チャンク削除 → 再処理 |
| ファイル削除 | 論理削除 → Qdrant チャンク物理削除 |
| ディレクトリ作成 | サブディレクトリも再帰的に監視対象に追加 |

### 5.8 ETL エラーハンドリングと状態遷移

#### ジョブ状態遷移図

```
queued → running → completed
                 → failed → (retry) → running
```

#### ステップ別進捗率

| ステップ | 進捗率 (progress) | 説明 |
|---------|------------------|------|
| キュー待ち | 0.0 | ジョブ作成済み |
| MinIO 格納 | 0.1 | 元ファイルアップロード完了 |
| パース完了 | 0.3 | テキスト抽出完了 |
| チャンク化完了 | 0.5 | チャンク分割完了 |
| エンベディング完了 | 0.7 | ベクトル生成・Qdrant 格納完了 |
| エンティティ抽出完了 | 0.9 | Neo4j 格納完了 |
| 全完了 | 1.0 | PostgreSQL ステータス更新完了 |

#### 部分失敗時の方針

**原則: ベクトル検索のみでも機能させる（エンティティ抽出の失敗は許容）**

| 失敗ステップ | 挙動 | 補償アクション |
|------------|------|-------------|
| MinIO 格納失敗 | ジョブ全体を `failed` | リトライ対象 |
| パース失敗 | ジョブ全体を `failed` | リトライ対象。対応形式外はスキップ通知 |
| エンベディング失敗 | ジョブ全体を `failed` | Qdrant の部分格納分を削除して `failed` |
| エンティティ抽出失敗 | **部分成功を許容** | ベクトル検索は利用可能。`etl_status = 'partial'` |
| Neo4j 格納失敗 | **部分成功を許容** | ベクトル検索は利用可能。`etl_status = 'partial'` |

#### メモリ管理

- ETL Service の Docker メモリ制限: `mem_limit: 2g`
- 100MB の PDF 処理時のピーク: ~500MB-1GB
- 大容量ファイルはストリーミング処理（ページ単位で順次処理）

---

## 6. LLM 統合詳細設計

### 6.1 モデル選定

#### 推論モデル: Qwen2.5-14B-Instruct-GPTQ-Int4

| 項目 | 内容 |
|------|------|
| パラメータ数 | 14B（140億） |
| 量子化 | GPTQ 4bit |
| VRAM 使用量 | ~8GB（KV キャッシュ込み） |
| コンテキスト長 | 32,768 トークン（最大 131,072） |
| 日本語性能 | 高（Qwen シリーズは日中英に強い） |
| 選定理由 | 24GB VRAM 制約内で最大クラスの日本語対応モデル |

#### エンベディングモデル: BAAI/bge-m3

| 項目 | 内容 |
|------|------|
| ベクトル次元 | 1024（Dense） |
| Sparse 対応 | あり（BM25 相当のキーワード検索） |
| 最大入力長 | 8,192 トークン |
| VRAM 使用量 | ~2GB |
| 日本語性能 | 高（多言語モデル） |
| 選定理由 | Dense + Sparse ハイブリッド検索対応、日本語性能良好 |

### 6.2 LLM サービス構成

#### 開発環境（Ollama）

```yaml
# docker-compose.dev.yml
llm-service:
  image: ollama/ollama:latest
  # GPU なし: CPU 推論
  environment:
    - OLLAMA_MODELS=/models
  volumes:
    - ollama-models:/models
```

#### 本番環境（vLLM）

```yaml
# docker-compose.prod.yml
llm-service:
  image: vllm/vllm-openai:latest
  command: >
    --model Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4
    --quantization gptq
    --max-model-len 32768
    --gpu-memory-utilization 0.35
    --dtype half
    --trust-remote-code
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### 6.3 エンベディング API（llm-service 内）

llm-service は LLM 推論に加え、bge-m3 によるエンベディング生成 API を提供する。

#### POST /internal/embeddings

**リクエスト**:
```json
{
  "texts": ["テキスト1", "テキスト2"],
  "return_sparse": true
}
```

**レスポンス**:
```json
{
  "embeddings": [
    {
      "dense": [0.012, -0.034, ...],
      "sparse": {"indices": [1, 5, 23], "values": [0.8, 0.3, 0.5]}
    }
  ]
}
```

#### GPU 排他制御

```python
# llm-service 内の排他セマフォ
import asyncio

gpu_semaphore = asyncio.Semaphore(1)  # GPU は同時1アクセス

async def generate_embeddings(texts):
    async with gpu_semaphore:
        return model.encode(texts)

async def generate_response(prompt):
    async with gpu_semaphore:
        return llm.generate(prompt)
```

LLM 推論とエンベディング生成は同一セマフォで排他制御し、VRAM 競合を防止する。チャット推論リクエストは優先度を高く設定し、ETL のエンベディング生成は低優先度でキュー待ちさせる。

### 6.4 システムプロンプト設計

#### メインチャット用システムプロンプト

```
あなたは生産工場のナレッジベースアシスタントです。
工場内のドキュメント（トラブル報告書、作業標準書、品質データ等）に基づいて質問に回答します。

【重要なルール】
1. 回答は必ず「提供された情報源」のみに基づいてください。
2. 情報源にない内容は「該当する情報が見つかりませんでした」と回答してください。
3. 推測や一般知識での補完は絶対に行わないでください。
4. 回答には必ず情報源（ファイル名、ページ番号）を明記してください。
5. 複数の情報源がある場合は、それぞれの情報源を区別して提示してください。
6. 日本語で回答してください。

【回答フォーマット】
- 簡潔かつ正確に回答する
- 箇条書きを活用する
- 情報源を [出典: ファイル名, p.XX] の形式で記載する
- 不確かな場合は、その旨を明記する

【提供された情報源】
{context}

【ユーザーの質問】
{query}
```

#### エンティティ抽出用システムプロンプト

```
あなたは製造業の文書分析の専門家です。
以下のテキストから、製造業に関連するエンティティ（固有表現）とそれらの関係性を抽出してください。

【抽出対象エンティティ】
- Equipment (設備): 機械名、装置名、ライン名（例: 実装機A, リフロー炉1号, Aライン）
- Process (工程): 製造工程名（例: はんだ印刷工程, リフロー工程, 外観検査工程）
- Defect (不良・異常): 不良モード、異常現象（例: はんだブリッジ, チョコ停, 温度異常）
- Part (部品): 部品名、部品番号（例: コンデンサC101, IC-U201）

【抽出対象の関係性】
- OCCURRED_IN: 不良/異常が設備や工程で発生
- USES: 工程が設備を使用
- CAUSED_BY: 不良/異常の因果関係
- REQUIRES: 工程が部品を必要とする

【出力形式】
以下の JSON 形式で出力してください。該当なしの場合は空配列を返してください。
{
  "entities": [
    { "text": "エンティティ名", "type": "Equipment|Process|Defect|Part", "confidence": 0.0-1.0 }
  ],
  "relationships": [
    { "source": "ソースエンティティ名", "target": "ターゲットエンティティ名", "type": "関係性タイプ", "confidence": 0.0-1.0 }
  ]
}

【テキスト】
{text}
```

### 6.5 コンテキストウィンドウ管理

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| max_context_tokens | 4,096 | 情報源テキストの最大トークン数 |
| max_generation_tokens | 2,048 | 回答生成の最大トークン数 |
| system_prompt_tokens | ~500 | システムプロンプトのトークン数 |
| total_budget | ~6,644 | 合計（32,768 の約20%を使用） |
| top_k_chunks | 10 | ベクトル検索で取得するチャンク数 |
| rerank_top_n | 5 | リランキング後に使用するチャンク数 |

#### チャンク選択フロー

1. ベクトル検索: top_k_chunks（10件）を取得
2. グラフ検索: 関連ドキュメントのチャンクを追加取得（最大5件）
3. 重複排除: 同一チャンクを除外
4. リランキング: 全候補を関連度で再順位付け
5. トークン予算内選択: rerank_top_n（5件）をコンテキストに使用
6. トークン数確認: max_context_tokens（4,096）以内に収まるよう調整

### 6.6 ストリーミングレスポンス実装方式

#### Server-Sent Events (SSE) 方式

```
Client                    API Gateway              LLM Service
  │                          │                         │
  │── POST /chat ──────────▶│                         │
  │                          │── POST /generate ─────▶│
  │                          │                         │
  │◀── SSE: event:start ────│                         │
  │                          │◀── Stream token ───────│
  │◀── SSE: event:token ────│                         │
  │◀── SSE: event:token ────│◀── Stream token ───────│
  │◀── SSE: event:token ────│◀── Stream token ───────│
  │                          │                         │
  │◀── SSE: event:sources ──│  （検索結果）              │
  │◀── SSE: event:graph ────│  （グラフデータ）          │
  │◀── SSE: event:done ─────│◀── Stream end ─────────│
  │                          │                         │
```

- API Gateway は LLM Service からのストリーミングトークンをリアルタイムでフロントエンドに中継
- ソース情報とグラフデータは検索完了後に一括送信（回答生成開始前に送信可能）
- フロントエンドは `EventSource` API で SSE を受信

### 6.7 リランキング戦略

#### Phase 1: スコアベースリランキング

```python
def rerank_simple(query: str, chunks: list, weights: dict) -> list:
    """
    Dense/Sparse スコアの加重平均でリランキング
    weights = {"dense": 0.7, "sparse": 0.3}
    """
    for chunk in chunks:
        chunk.final_score = (
            weights["dense"] * chunk.dense_score +
            weights["sparse"] * chunk.sparse_score
        )
    return sorted(chunks, key=lambda c: c.final_score, reverse=True)
```

#### Phase 2: Cross-Encoder リランキング

```python
# bge-reranker-v2-m3 等の Cross-Encoder モデルを使用
# クエリとチャンクのペアを入力し、関連度スコアを算出
# Dense/Sparse 検索よりも高精度だが、計算コストが高い
```

| リランキング方式 | 精度 | 速度 | Phase |
|----------------|------|------|-------|
| スコア加重平均 | 中 | 高速 | Phase 1 |
| Cross-Encoder | 高 | 中速 | Phase 2 |

---

## 7. フロントエンド詳細設計

### 7.1 技術スタック

| 項目 | 技術 | 説明 |
|------|------|------|
| フレームワーク | React 18+ | SPA |
| 言語 | TypeScript | 型安全 |
| ビルドツール | Vite | 高速ビルド |
| UI ライブラリ | Tailwind CSS + shadcn/ui | ユーティリティファースト CSS |
| 状態管理 | Zustand | 軽量な状態管理 |
| データフェッチ | TanStack Query (React Query) | サーバー状態管理、キャッシュ |
| ルーティング | React Router v6 | SPA ルーティング |
| グラフ可視化 | Cytoscape.js + react-cytoscapejs | ナレッジグラフ描画 |
| アイコン | Lucide React | 一貫したアイコンセット |
| フォーム | React Hook Form + Zod | バリデーション付きフォーム |

### 7.2 ページ構成とルーティング

| パス | ページ | 説明 | 認証 |
|------|--------|------|------|
| `/login` | ログインページ | ユーザー認証 | 不要 |
| `/` | チャットページ | メインのチャット画面 | 必要 |
| `/chat/:id` | チャット（セッション指定） | 過去のチャット継続 | 必要 |
| `/search` | 検索ページ | 検索のみ（回答生成なし） | 必要 |
| `/graph` | グラフエクスプローラー | ナレッジグラフの対話的探索 | 必要 |
| `/documents` | ドキュメント管理 | アップロード、一覧、ステータス | 必要 |
| `/admin` | 管理ダッシュボード | システムステータス、ユーザー管理 | 管理者のみ |
| `/admin/users` | ユーザー管理 | ユーザーCRUD | 管理者のみ |
| `/admin/audit` | 監査ログ | 操作履歴 | 管理者のみ |
| `/settings` | 設定 | 個人設定 | 必要 |

### 7.3 コンポーネント設計

#### レイアウト構成

```
┌─────────────────────────────────────────────────┐
│ Header (ロゴ, ナビゲーション, ユーザーメニュー)    │
├──────────┬──────────────────────────────────────┤
│ Sidebar  │ Main Content                         │
│          │                                      │
│ - Chat   │  ┌──────────────────────────────┐    │
│ - Search │  │  Page-specific content       │    │
│ - Graph  │  │                              │    │
│ - Docs   │  │                              │    │
│ - Admin  │  │                              │    │
│          │  └──────────────────────────────┘    │
│          │                                      │
├──────────┴──────────────────────────────────────┤
│ (Status Bar - optional)                          │
└─────────────────────────────────────────────────┘
```

#### 主要コンポーネント一覧

**共通コンポーネント**

| コンポーネント | 責務 |
|-------------|------|
| `AppLayout` | 全体レイアウト（Header + Sidebar + Main） |
| `Header` | ロゴ、グローバルナビ、ユーザーメニュー |
| `Sidebar` | ページナビゲーション、チャット履歴 |
| `AuthGuard` | 認証状態チェック、未認証時リダイレクト |
| `ErrorBoundary` | エラーハンドリング、フォールバック UI |
| `LoadingSpinner` | ローディング表示 |

**チャット関連コンポーネント**

| コンポーネント | 責務 |
|-------------|------|
| `ChatPage` | チャットページ全体のコンテナ |
| `ChatInput` | メッセージ入力エリア（テキストエリア + 送信ボタン） |
| `ChatMessageList` | メッセージ一覧（スクロール、自動スクロール） |
| `ChatMessage` | 個別メッセージ表示（ユーザー / アシスタント） |
| `StreamingText` | ストリーミング応答のリアルタイム表示 |
| `SourceCitation` | 情報源の引用表示（ファイル名、ページ、テキスト抜粋） |
| `SourcePanel` | 引用元一覧のサイドパネル |
| `ChatGraphView` | チャット内のインラインナレッジグラフ |
| `FeedbackButtons` | Good/Bad フィードバックボタン |
| `ChatSessionList` | チャット履歴一覧（サイドバー内） |
| `SearchFilters` | 検索オプション（期間、部署、ドキュメント種別） |

**ナレッジグラフ関連コンポーネント**

| コンポーネント | 責務 |
|-------------|------|
| `GraphExplorer` | グラフエクスプローラーページ全体 |
| `GraphCanvas` | Cytoscape.js によるグラフ描画エリア |
| `GraphControls` | ズーム、リセット、レイアウト切替 |
| `GraphFilters` | ノード種別フィルタ、深度設定 |
| `NodeDetail` | ノード詳細パネル（クリック時） |
| `GraphLegend` | 凡例（ノード種別の色分け） |
| `GraphSearch` | グラフ内ノード検索 |

**ドキュメント管理関連コンポーネント**

| コンポーネント | 責務 |
|-------------|------|
| `DocumentList` | ドキュメント一覧テーブル |
| `DocumentUpload` | ファイルアップロード（ドラッグ&ドロップ対応） |
| `DocumentDetail` | ドキュメント詳細情報 |
| `ETLStatusBadge` | ETL 処理ステータス表示 |
| `DocumentPreview` | ドキュメントプレビュー |

**管理画面関連コンポーネント**

| コンポーネント | 責務 |
|-------------|------|
| `AdminDashboard` | システムステータス概要 |
| `ServiceStatusCard` | 各サービスのヘルスステータス |
| `StatsChart` | 利用統計グラフ |
| `UserManagement` | ユーザー CRUD テーブル |
| `AuditLogTable` | 監査ログ表示テーブル |

### 7.4 チャット UI 仕様

#### メッセージ表示

- **ユーザーメッセージ**: 右寄せ、背景色付き
- **アシスタントメッセージ**: 左寄せ、Markdown レンダリング対応
- **ストリーミング表示**: トークン単位でリアルタイム追記、タイピングインジケータ付き
- **ソース引用**: メッセージ下部にアコーディオン形式で折りたたみ表示
  - ファイル名（リンク付き）
  - ページ番号
  - 該当テキスト抜粋（ハイライト付き）
  - 関連度スコア

#### インラインナレッジグラフ

- 回答に関連するエンティティとその関係をコンパクトなグラフで表示
- クリックでグラフエクスプローラーに遷移可能
- ノード種別ごとに色分け:
  - Document: 青
  - Equipment: 緑
  - Process: オレンジ
  - Defect: 赤
  - Part: 紫

### 7.5 ナレッジグラフビューア仕様

#### 操作

| 操作 | 動作 |
|------|------|
| ノードクリック | 詳細パネル表示 |
| ノードダブルクリック | そのノードを起点に展開 |
| エッジクリック | 関係性の詳細表示 |
| ドラッグ | グラフのパン |
| ピンチ / マウスホイール | ズームイン / アウト |
| ノードドラッグ | ノードの位置移動 |

#### レイアウトアルゴリズム

| レイアウト | 用途 |
|-----------|------|
| CoSE (Compound Spring Embedder) | デフォルト。力学モデルベース |
| Breadthfirst | 階層構造の表示 |
| Circle | ノード数が少ない場合 |
| Grid | 一覧表示 |

#### パフォーマンス対策

- 1,000 ノード以上: 段階的読み込み（初期表示は近傍のみ）
- WebGL レンダリング（Cytoscape.js の canvas レンダラ）
- ノードの集約表示（同種ノードをグループ化）

### 7.6 レスポンシブ対応方針

| ブレークポイント | レイアウト |
|---------------|----------|
| < 768px（スマートフォン） | 非対応（デスクトップ前提） |
| 768px - 1024px（タブレット） | サイドバー折りたたみ、1カラム |
| > 1024px（デスクトップ） | フル表示（サイドバー + メインコンテンツ） |

> **注意**: 本システムは工場内の PC 端末での利用が主であるため、モバイル対応は優先度低。最低解像度は 1280x720 を想定。

---

## 8. 非機能要件

### 8.1 パフォーマンス目標値

| 項目 | 目標値 | 測定条件 |
|------|--------|---------|
| ETL 処理速度 | 100ファイル/時間 | PDF 平均 10ページ、バッチ処理 |
| ベクトル検索 | < 500ms | 15,000 チャンクの Qdrant 検索 |
| グラフ検索 | < 500ms | 5,000 ノードの Neo4j トラバース（深度2） |
| ハイブリッド検索 | < 3秒 | ベクトル検索 + グラフ検索 + リランキング |
| 回答生成（ストリーミング開始） | < 2秒 | 最初のトークン出力まで |
| 回答生成（完了） | < 10秒 | 平均 500 トークンの回答 |
| ページ読み込み | < 2秒 | 初回読み込み（Gzip圧縮後） |
| 同時接続数 | 10ユーザー | API Gateway のスレッドプール |

### 8.2 ストレージ見積もり（1,000ファイル想定）

| コンポーネント | 見積もりサイズ | 算出根拠 |
|-------------|-------------|---------|
| 元ファイル（MinIO） | ~5GB | 平均 5MB/ファイル x 1,000 |
| ベクトルデータ（Qdrant） | ~2GB | 15,000チャンク x 1024次元 x 4byte + メタデータ |
| グラフデータ（Neo4j） | ~500MB | 5,000ノード + 12,000エッジ |
| RDB（PostgreSQL） | ~200MB | ユーザー、セッション、監査ログ |
| Redis キャッシュ | ~256MB | セッション、クエリキャッシュ |
| Docker イメージ | ~15GB | 全サービスのイメージ合計 |
| LLM モデル | ~10GB | Qwen2.5-14B-GPTQ-Int4 + bge-m3 |
| **合計** | **~33GB** | SSD 100GB 以上を推奨 |

### 8.3 監視・ログ・アラート設計

#### メトリクス収集（Prometheus）

| メトリクス | 種別 | 説明 |
|-----------|------|------|
| `api_request_total` | Counter | API リクエスト総数（エンドポイント別） |
| `api_request_duration_seconds` | Histogram | API レスポンス時間 |
| `llm_inference_duration_seconds` | Histogram | LLM 推論時間 |
| `llm_tokens_generated_total` | Counter | 生成トークン数 |
| `etl_jobs_total` | Counter | ETL ジョブ数（ステータス別） |
| `etl_processing_duration_seconds` | Histogram | ETL 処理時間 |
| `qdrant_search_duration_seconds` | Histogram | Qdrant 検索時間 |
| `neo4j_query_duration_seconds` | Histogram | Neo4j クエリ時間 |
| `gpu_memory_usage_bytes` | Gauge | GPU メモリ使用量 |
| `gpu_utilization_percent` | Gauge | GPU 使用率 |
| `active_users` | Gauge | アクティブユーザー数 |

#### アラートルール（Grafana）

| アラート | 条件 | 重要度 |
|---------|------|--------|
| サービスダウン | サービスが 30 秒以上応答なし | Critical |
| 高レイテンシ | API 応答時間 > 10 秒（5 分平均） | Warning |
| GPU メモリ不足 | VRAM 使用率 > 90% | Warning |
| ETL ジョブ失敗 | 失敗率 > 10%（直近 1 時間） | Warning |
| ディスク容量 | 使用率 > 80% | Warning |
| ディスク容量 | 使用率 > 95% | Critical |

#### ログ設計

| サービス | ログ形式 | 出力先 | ログレベル |
|---------|---------|--------|----------|
| API Gateway (Rust) | JSON (tracing) | stdout → Docker logs | INFO (本番) / DEBUG (開発) |
| ETL Service (Python) | JSON (structlog) | stdout → Docker logs | INFO (本番) / DEBUG (開発) |
| LLM Service (Python) | JSON (structlog) | stdout → Docker logs | INFO (本番) / DEBUG (開発) |

**ログフォーマット例**:
```json
{
  "timestamp": "2024-07-15T10:30:00.123Z",
  "level": "INFO",
  "service": "api-gateway",
  "request_id": "uuid",
  "user_id": "uuid",
  "action": "search",
  "duration_ms": 1200,
  "message": "Search completed successfully"
}
```

### 8.4 バックアップ・リカバリ方針

| データ | バックアップ方式 | 頻度 | 保持期間 |
|--------|--------------|------|---------|
| PostgreSQL | pg_dump | 日次（夜間） | 30日 |
| Neo4j | neo4j-admin dump | 日次（夜間） | 30日 |
| Qdrant | スナップショット API | 週次 | 4世代 |
| MinIO | rsync / ミラーリング | 日次 | 全期間 |
| Redis | RDB スナップショット | 1時間ごと | 24時間 |

**リカバリ手順**:
1. Docker Compose で全サービスを停止
2. データボリュームをバックアップから復元
3. Docker Compose で全サービスを起動
4. ヘルスチェック API で各サービスの正常性確認

**RTO（目標復旧時間）**: 2時間以内
**RPO（目標復旧時点）**: 24時間以内（日次バックアップ分のデータ損失が最大）

### 8.5 セキュリティ要件詳細

#### 認証・認可

| 項目 | Phase 1 | Phase 3 |
|------|---------|---------|
| 認証方式 | JWT（ローカルアカウント） | JWT + Active Directory (LDAP) |
| トークン有効期限 | Access: 1時間 / Refresh: 7日 | 同左 |
| パスワードポリシー | 8文字以上、英数記号混合 | AD ポリシーに準拠 |
| アカウントロック | 5回失敗で 15分ロック | AD ポリシーに準拠 |
| ロール | admin, user, viewer | AD グループと連動 |

#### ロール別権限

| 機能 | admin | user | viewer |
|------|-------|------|--------|
| チャット（質問応答） | O | O | O |
| ドキュメント検索 | O | O | O |
| グラフ探索 | O | O | O |
| ドキュメントアップロード | O | O | X |
| ドキュメント削除 | O | X | X |
| ユーザー管理 | O | X | X |
| システムステータス閲覧 | O | X | X |
| 監査ログ閲覧 | O | X | X |
| 辞書管理 | O | X | X |

#### 通信セキュリティ

| 項目 | 内容 |
|------|------|
| フロントエンド → API | HTTPS（自己署名証明書 or 社内CA） |
| サービス間通信 | Docker 内部ネットワーク（暗号化なし、外部非公開） |
| データベース接続 | Docker 内部ネットワーク経由（外部ポート非公開） |
| ファイルアップロード | HTTPS + ファイル種別検証 + サイズ制限 |

#### CORS ポリシー

```
Access-Control-Allow-Origin: http://localhost:3000  (開発環境)
Access-Control-Allow-Origin: https://<internal-hostname>:3000  (本番環境)
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 3600
```

フロントエンド（`:3000`）から API Gateway（`:8080`）へのクロスオリジンリクエストを許可。許可するオリジンは環境変数で設定し、ワイルドカード（`*`）は禁止。

#### 入力値検証

| 入力 | 検証内容 |
|------|---------|
| 検索クエリ | 最大 1,000 文字、特殊文字エスケープ |
| ファイルアップロード | 拡張子検証、MIME タイプ検証、最大 100MB |
| ユーザー入力（全般） | XSS 防止（HTML サニタイズ）、SQL インジェクション防止 |
| Neo4j クエリ | **Cypher インジェクション防止: パラメータ化クエリ（`$param` 構文）を必須** とする。文字列連結によるクエリ構築は禁止。 |
| API パラメータ | Zod（フロントエンド）/ serde + validator（Rust）による型検証 |

#### SSRF 対策

- API Gateway はユーザー入力に基づく内部サービスへのリクエスト転送を制限
- 許可された内部サービス URL のホワイトリストを環境変数で管理
- URL パラメータによる内部サービスの指定は禁止（エンドポイント単位でルーティング）

#### 依存パッケージの脆弱性管理

| ツール | 対象 | タイミング |
|--------|------|----------|
| `cargo audit` | Rust (Cargo.lock) | CI/CD ビルド時 |
| `pip-audit` / `safety` | Python (requirements.txt) | CI/CD ビルド時 |
| `npm audit` | Node.js (package-lock.json) | CI/CD ビルド時 |
| Docker Scout / Trivy | Docker イメージ | イメージビルド時 |

初回デプロイ時（インターネット接続あり）にパッケージ取得と脆弱性スキャンを実施。CRITICAL/HIGH の脆弱性が検出された場合はデプロイをブロック。

#### JWT トークン保存方式

- **Access Token**: メモリ内保持（JavaScript 変数）。localStorage/sessionStorage には保存しない。
- **Refresh Token**: `httpOnly`, `Secure`, `SameSite=Strict` 属性付き Cookie で保存。XSS 攻撃によるトークン窃取を防止。

#### 機密データ保護

- パスワードは bcrypt でハッシュ化（コスト係数 12）
- JWT の署名鍵は環境変数で管理（ハードコード禁止）
- データベース接続文字列は環境変数で管理
- MinIO のアクセスキーは環境変数で管理
- 監査ログに機密データ（パスワード等）を含めない

---

## 9. 開発フェーズ計画

### Phase 1: MVP（基本チャット + 単純RAG）

**目標**: 最小限の動作するシステムを構築し、基本的な質問応答機能を実現する。

#### 機能スコープ

| カテゴリ | 機能 |
|---------|------|
| インジェスト | PDF / Word のパースとチャンク化 |
| エンベディング | bge-m3 による Dense + Sparse ベクトル生成（**Sparse も格納するが検索には未使用**） |
| 検索 | ベクトル検索（Qdrant Dense 検索のみ） |
| 回答生成 | Qwen2.5-14B によるストリーミング応答 |
| UI | チャットインターフェース（入力 + メッセージ一覧） |
| ソース引用 | 回答に対する情報源の表示 |
| 認証 | ローカルアカウント認証（JWT） |
| ドキュメント管理 | アップロード + 一覧表示 + ETL ステータス |

> **注意**: Phase 1 では Dense 検索のみ使用するが、bge-m3 は Dense + Sparse を同時に生成するため、Sparse ベクトルも Qdrant に格納しておく。これにより Phase 2 移行時の再エンベディングが不要になる。

#### Docker Compose 構成（Phase 1）

Phase 1 では Neo4j を起動しない。`docker-compose.yml` と `docker-compose.phase2.yml`（Neo4j 追加分）に分離する。

```yaml
# docker-compose.yml (Phase 1) — Neo4j なし
services: [frontend, api-gateway, etl-service, llm-service, qdrant, postgres, redis, minio]

# docker-compose.phase2.yml (Phase 2 追加分)
services: [neo4j, prometheus, grafana]
```

API Gateway は Neo4j が未起動でもエラーにならない設計とする（Neo4j 接続はオプショナル。未接続時はグラフ検索 API が `503 SERVICE_UNAVAILABLE` を返す）。

#### 開発タスク

1. Docker Compose 環境構築（Phase 1 サービスの起動確認）
2. PostgreSQL スキーマ作成（users, sessions, documents, chat_sessions, chat_messages, etl_jobs）
3. API Gateway 基本実装（認証、ルーティング、ヘルスチェック）
4. LLM Service 実装（vLLM/Ollama 統合、ストリーミング応答、エンベディング API）
5. ETL Service 基本実装（PDF/Word パース、チャンク化、llm-service 経由エンベディング）
6. Qdrant コレクション作成と Dense 検索機能
7. フロントエンド基本実装（ログイン、チャット、ドキュメント管理）
8. 結合テスト・パフォーマンス確認

### Phase 2: ナレッジグラフ + ハイブリッド検索

**目標**: ナレッジグラフを構築し、ベクトル検索とグラフ検索のハイブリッド検索を実現する。

#### 機能スコープ

| カテゴリ | 機能 |
|---------|------|
| インジェスト | Excel / PowerPoint 対応追加 |
| エンティティ抽出 | LLM ベース + ルールベース併用 |
| ナレッジグラフ | Neo4j へのエンティティ・関係性格納 |
| 検索 | ハイブリッド検索（ベクトル + グラフ + Sparse） |
| リランキング | Cross-Encoder リランキング |
| UI | ナレッジグラフビューア（Cytoscape.js） |
| UI | 検索フィルタ（期間、部署、ドキュメント種別） |
| フィードバック | Good/Bad 評価 + コメント機能 |
| 管理 | 管理者ダッシュボード（システムステータス） |
| 辞書 | カスタム辞書管理画面 |

#### 開発タスク

1. Neo4j スキーマ作成（ノード、エッジ、インデックス、制約）
2. エンティティ抽出パイプライン実装
3. Excel / PowerPoint パーサー実装
4. ハイブリッド検索エンジン実装
5. Cross-Encoder リランキング統合
6. ナレッジグラフビューア実装（Cytoscape.js）
7. フィードバック機能実装
8. 管理者ダッシュボード実装
9. カスタム辞書管理機能
10. 結合テスト・パフォーマンス最適化

### Phase 3a: 運用基盤

**目標**: 安定運用に必要な監視・バックアップ基盤を構築する。

#### 機能スコープ

| カテゴリ | 機能 |
|---------|------|
| 監視 | Prometheus + Grafana ダッシュボード |
| アラート | 異常検知アラート（サービスダウン、高レイテンシ、ディスク容量） |
| バックアップ | 自動バックアップスクリプト + リストア手順 |
| 監査 | 監査ログ閲覧画面 |
| パフォーマンス | キャッシュ最適化、クエリ最適化 |

#### 開発タスク

1. Prometheus メトリクスエクスポーター実装（各サービス）
2. Grafana ダッシュボード構築
3. アラートルール設定
4. バックアップスクリプト作成・自動化
5. 監査ログ閲覧画面実装
6. パフォーマンスチューニング・負荷テスト

### Phase 3b: エンタープライズ認証

**目標**: Active Directory 連携による本格的なアクセス制御を実現する。

#### 機能スコープ

| カテゴリ | 機能 |
|---------|------|
| 認証・認可 | Active Directory 連携（LDAP バインド） |
| RBAC | AD グループ → ロールマッピング |
| セキュリティ | セキュリティテスト、脆弱性スキャン |

#### 開発タスク

1. Active Directory 連携（LDAP バインド）実装
2. RBAC 実装（AD グループ → ロールマッピング）
3. 既存ローカル認証からの移行パス
4. セキュリティテスト・ペネトレーションテスト

### Phase 3c: 高度機能

**目標**: 運用効率化と高度な機能を追加する。

#### 機能スコープ

| カテゴリ | 機能 |
|---------|------|
| 版管理 | ドキュメントの新旧管理（自動検知 + 手動設定） |
| バッチ処理 | 夜間バッチスケジューリング |
| ファイル監視 | watchdog によるディレクトリ監視 |
| VLM | 画像・図面の OCR / 解析（検討） |

#### 開発タスク

1. ドキュメント版管理機能（API + UI）
2. watchdog ファイル監視サービス
3. バッチ処理スケジューラ（Redis Queue + cron）
4. VLM 統合の技術検証（ローカル VLM モデル評価）

---

## 付録

### A. 製造業特有の課題と対応方針

#### A.1 複雑な表・図面の取り扱い

- **Excel の複雑な表**: ETL フェーズで Markdown テーブルへ変換。結合セルは展開処理。
- **図面・画像**: Phase 3 でローカル VLM（視覚言語モデル）統合を検討。当面はテキスト情報のみ対象。
- **手書きメモ**: スコープ外（将来的な OCR 統合を検討）。

#### A.2 ドキュメントの新旧管理（版管理）

- メタデータに「最新版フラグ」「有効期間」「版番号」を付与。
- 新版アップロード時に旧版を自動的に非最新化。
- 検索時はデフォルトで最新版のみ、ユーザー選択で全版検索可能。
- Neo4j の `SUPERSEDES` エッジで改訂関係を追跡。

#### A.3 専門用語の辞書登録

- カスタム辞書（JSON 形式）で工場独自の略語・専門用語を管理。
- エンティティ抽出時に辞書を参照して正規化。
- 管理画面から辞書の追加・編集が可能（Phase 2）。
- 将来的にはエンベディングモデルのファインチューニングを検討。

### B. 環境変数一覧

```env
# PostgreSQL
POSTGRES_USER=graphrag
POSTGRES_PASSWORD=<secret>
POSTGRES_DB=graphrag

# Neo4j
NEO4J_PASSWORD=<secret>

# Redis
REDIS_URL=redis://redis:6379

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=<secret>
MINIO_BUCKET=documents

# JWT
JWT_SECRET=<secret>
JWT_ACCESS_TOKEN_EXPIRY=3600
JWT_REFRESH_TOKEN_EXPIRY=604800

# LLM
LLM_MODEL=Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4
LLM_SERVICE_URL=http://llm-service:8002
EMBEDDING_MODEL=BAAI/bge-m3

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=document_chunks

# Services
API_GATEWAY_PORT=8080
ETL_SERVICE_URL=http://etl-service:8001
```
