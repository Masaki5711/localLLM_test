# Factory Knowledge GraphRAG System

生産工場向けローカル LLM ナレッジ検索・データ関連性分析システム。
完全オンプレミス環境で稼働し、RAG + ナレッジグラフを統合した GraphRAG アーキテクチャを採用。

## 目的

- **属人化の解消** — 熟練者の暗黙知をドキュメントから抽出し、誰でも検索可能に
- **データ間関連性分析** — ナレッジグラフによる設備・工程・不具合の関係可視化
- **セキュアな情報活用** — 閉域網で完結するローカル LLM による安全な社内情報検索

## アーキテクチャ

```
┌──────────────┐     ┌──────────────────┐     ┌───────────────┐
│   Frontend   │────▶│   API Gateway    │────▶│  ETL Service  │
│  React / TS  │     │   Rust / Axum    │     │ Python/FastAPI│
│   :3000      │     │   :8080          │     │   :8001       │
└──────────────┘     └──────────────────┘     └───────────────┘
                              │                        │
                              │                        ▼
                              │               ┌───────────────┐
                              └──────────────▶│  LLM Service  │
                                              │ Python/FastAPI│
                                              │   :8002       │
                                              └───────┬───────┘
                                                      │
                                                      ▼
                                              ┌───────────────┐
                                              │    Ollama      │
                                              │   :11434       │
                                              └───────────────┘
```

### インフラストラクチャ

| サービス | 技術 | ポート | 用途 |
|----------|------|--------|------|
| Frontend | React 18 + Vite + Tailwind CSS | 3000 | Web UI |
| API Gateway | Rust / Axum | 8080 | 認証・ルーティング・プロキシ |
| ETL Service | Python / FastAPI | 8001 | ドキュメント解析・ベクトル化 |
| LLM Service | Python / FastAPI | 8002 | LLM 推論・埋め込み生成 |
| Ollama | Ollama | 11434 | LLM ランタイム（開発環境） |
| PostgreSQL | PostgreSQL 16 | 5432 | ユーザー管理・メタデータ |
| Qdrant | Qdrant | 6333 | ベクトルデータベース |
| Redis | Redis 7 | 6379 | セッション・キャッシュ |
| MinIO | MinIO | 9000 / 9001 | オブジェクトストレージ |

## 技術スタック

| レイヤー | 技術 |
|----------|------|
| Frontend | TypeScript, React 18, Vite, Tailwind CSS, shadcn/ui, Zustand, TanStack Query |
| API Gateway | Rust, Axum 0.8, SQLx, JWT, bcrypt |
| ETL Pipeline | Python 3.11+, FastAPI, PyMuPDF, python-docx, SQLAlchemy |
| LLM Service | Python 3.11+, FastAPI, SSE, Ollama / vLLM |
| Vector DB | Qdrant |
| RDB | PostgreSQL 16 |
| Cache | Redis 7 |
| Storage | MinIO (S3 互換) |
| LLM Model | qwen2.5:7b (開発) / Qwen2.5-14B-GPTQ-Int4 (本番) |
| Embedding | nomic-embed-text |

## プロジェクト構成

```
├── frontend/           # React / TypeScript フロントエンド
│   ├── src/
│   │   ├── components/ # UI コンポーネント (chat, layout, ui)
│   │   ├── pages/      # ChatPage, DocumentsPage, LoginPage
│   │   ├── stores/     # Zustand ストア (認証状態)
│   │   ├── lib/        # API クライアント, ユーティリティ
│   │   └── types/      # TypeScript 型定義
│   └── Dockerfile
├── backend/            # Rust / Axum API Gateway
│   ├── src/
│   │   ├── auth/       # JWT ミドルウェア・トークン管理
│   │   ├── routes/     # API エンドポイント
│   │   ├── models/     # データモデル
│   │   ├── config.rs   # 環境変数設定
│   │   └── main.rs     # エントリーポイント
│   └── Dockerfile
├── etl/                # Python ETL サービス
│   ├── src/
│   │   ├── routes/     # API ルート
│   │   ├── services/   # ドキュメント解析・チャンク化
│   │   └── config.py   # 設定
│   └── Dockerfile
├── llm/                # Python LLM サービス
│   ├── src/
│   │   ├── routes/     # チャット・埋め込み API
│   │   └── config.py   # 設定
│   └── Dockerfile
├── docker/
│   └── postgres/init/  # DB 初期化スクリプト (8 テーブル)
├── docker-compose.yml  # 全サービスのオーケストレーション
├── .env.example        # 環境変数テンプレート
└── spesification.md    # 詳細仕様書 (日本語)
```

## セットアップ

### 前提条件

- Docker Desktop (Docker Compose v2)
- Git

### 1. リポジトリをクローン

```bash
git clone https://github.com/Masaki5711/localLLM_test.git
cd localLLM_test
```

### 2. 環境変数を設定

```bash
cp .env.example .env
# 必要に応じて .env のパスワード・シークレットを変更
```

### 3. Docker Compose で起動

```bash
docker compose up -d --build
```

### 4. LLM モデルをダウンロード

```bash
# チャット用モデル
docker compose exec ollama ollama pull qwen2.5:7b

# 埋め込み用モデル
docker compose exec ollama ollama pull nomic-embed-text
```

### 5. アクセス

| URL | 説明 |
|-----|------|
| http://localhost:3000 | Web UI |
| http://localhost:8080 | API Gateway |
| http://localhost:9001 | MinIO コンソール |

**初期ログイン**: `admin` / `admin123`

## API エンドポイント

### 認証

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/api/v1/auth/login` | ログイン（JWT 発行） |
| POST | `/api/v1/auth/refresh` | トークンリフレッシュ |
| POST | `/api/v1/auth/logout` | ログアウト |

### チャット（認証必須）

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/api/v1/chat/stream` | RAG チャット（SSE ストリーミング） |

### ドキュメント（認証必須）

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/api/v1/documents/upload` | ドキュメントアップロード |
| GET | `/api/v1/documents` | ドキュメント一覧 |

### システム

| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/health` | ヘルスチェック |

## データベーススキーマ

PostgreSQL に 8 テーブル:

| テーブル | 説明 |
|----------|------|
| `users` | ユーザー管理（ロール・部門・AD 連携） |
| `sessions` | JWT セッション管理 |
| `documents` | ドキュメントメタデータ・ETL ステータス |
| `chat_sessions` | チャットセッション |
| `chat_messages` | チャットメッセージ（ソース・グラフデータ付き） |
| `feedback` | ユーザーフィードバック（評価・コメント） |
| `etl_jobs` | ETL ジョブ進捗管理 |
| `audit_log` | 操作監査ログ |

## 開発フェーズ

### Phase 1: MVP（現在）

- [x] プロジェクトスケルトン・Docker Compose 構成
- [x] JWT 認証（ログイン・リフレッシュ・ログアウト）
- [x] PDF / Word ドキュメントインジェスト
- [x] ベクトル検索（セマンティック検索）
- [x] SSE ストリーミングチャット
- [x] ソース引用表示
- [x] フロントエンド（チャット・ドキュメント管理・ログイン）

### Phase 2: ナレッジグラフ

- [ ] Neo4j 統合・ナレッジグラフ構築
- [ ] グラフ可視化（Cytoscape.js）
- [ ] ハイブリッド検索（ベクトル + グラフ）
- [ ] Excel / PowerPoint 対応
- [ ] フィードバック機能
- [ ] 管理者ダッシュボード

### Phase 3: エンタープライズ

- [ ] Active Directory 連携 RBAC
- [ ] バッチ処理スケジューリング
- [ ] ドキュメント版管理
- [ ] Prometheus + Grafana 監視
- [ ] パフォーマンス最適化

## 本番環境

| 項目 | スペック |
|------|---------|
| OS | Windows 11 |
| GPU | NVIDIA RTX 4500 Ada (24GB VRAM) |
| LLM | Qwen2.5-14B-GPTQ-Int4 (~8GB VRAM) |
| Embedding | BAAI/bge-m3 (~2GB VRAM) |
| デプロイ | Docker Compose |
| ネットワーク | 閉域網（オンプレミス） |

## ライセンス

Private - Internal Use Only
