use axum::{
    extract::State,
    response::{
        sse::{Event, KeepAlive},
        Sse,
    },
    Extension, Json,
};
use futures_util::stream::Stream;
use futures_util::StreamExt;
use serde::Deserialize;
use serde_json::{json, Value};
use std::convert::Infallible;
use std::sync::Arc;

use crate::auth::middleware::AuthUser;
use crate::error::AppError;
use crate::AppState;

#[derive(Debug, Deserialize)]
pub struct ChatRequest {
    pub query: String,
}

#[derive(Debug, serde::Serialize)]
struct Source {
    document_id: String,
    file_name: String,
    heading: String,
    score: f64,
}

/// POST /chat/stream - GraphRAG chat with SSE streaming
///
/// 1. Receives query from authenticated user
/// 2. Searches ETL service for relevant context
/// 3. Streams LLM response back as SSE events
pub async fn chat_stream(
    State(state): State<Arc<AppState>>,
    Extension(_auth_user): Extension<AuthUser>,
    Json(payload): Json<ChatRequest>,
) -> Result<Sse<impl Stream<Item = Result<Event, Infallible>>>, AppError> {
    let query = payload.query.trim().to_string();
    if query.is_empty() {
        return Err(AppError::Validation("query must not be empty".to_string()));
    }

    // Step 1: Search ETL service for relevant documents (non-fatal on failure)
    let http_client = reqwest::Client::new();
    let (context_texts, sources) = match http_client
        .post(format!("{}/api/v1/search", state.config.etl_service_url))
        .json(&json!({ "query": query, "limit": 5 }))
        .send()
        .await
    {
        Ok(resp) => match resp.json::<Value>().await {
            Ok(search_body) => extract_search_results(&search_body),
            Err(e) => {
                tracing::warn!("Failed to parse ETL search response: {}", e);
                (Vec::new(), Vec::new())
            }
        },
        Err(e) => {
            tracing::warn!("ETL search request failed (proceeding without context): {}", e);
            (Vec::new(), Vec::new())
        }
    };

    tracing::info!(
        query = %query,
        context_count = context_texts.len(),
        "Starting chat stream with retrieved context"
    );

    // Step 3: Build the SSE stream
    let llm_url = format!("{}/api/v1/chat/stream", state.config.llm_service_url);
    let llm_body = json!({
        "query": query,
        "context": context_texts,
    });

    let stream = build_sse_stream(http_client, llm_url, llm_body, sources);

    Ok(Sse::new(stream).keep_alive(KeepAlive::default()))
}

/// Extract text content and source metadata from ETL search results.
fn extract_search_results(search_body: &Value) -> (Vec<String>, Vec<Source>) {
    let mut context_texts = Vec::new();
    let mut sources = Vec::new();

    let results = search_body
        .get("data")
        .and_then(|d| d.get("results"))
        .and_then(|r| r.as_array());

    if let Some(items) = results {
        for item in items {
            let payload = match item.get("payload") {
                Some(p) => p,
                None => continue,
            };

            let text = payload
                .get("text")
                .and_then(|t| t.as_str())
                .unwrap_or_default();
            if !text.is_empty() {
                context_texts.push(text.to_string());
            }

            let score = item
                .get("score")
                .and_then(|s| s.as_f64())
                .unwrap_or(0.0);

            sources.push(Source {
                document_id: payload
                    .get("document_id")
                    .and_then(|v| v.as_str())
                    .unwrap_or_default()
                    .to_string(),
                file_name: payload
                    .get("file_name")
                    .and_then(|v| v.as_str())
                    .unwrap_or_default()
                    .to_string(),
                heading: payload
                    .get("heading")
                    .and_then(|v| v.as_str())
                    .unwrap_or_default()
                    .to_string(),
                score,
            });
        }
    }

    (context_texts, sources)
}

/// Build the SSE stream that:
/// 1. Yields sources event
/// 2. Relays LLM streaming tokens
/// 3. Yields done event
fn build_sse_stream(
    http_client: reqwest::Client,
    llm_url: String,
    llm_body: Value,
    sources: Vec<Source>,
) -> impl Stream<Item = Result<Event, Infallible>> {
    async_stream::stream! {
        // First event: send search sources to frontend
        let sources_json = json!({ "sources": sources });
        yield Ok(Event::default().data(sources_json.to_string()));

        // Make streaming request to LLM service
        let llm_response = http_client
            .post(&llm_url)
            .json(&llm_body)
            .send()
            .await;

        let llm_response = match llm_response {
            Ok(resp) => resp,
            Err(e) => {
                tracing::error!("LLM service request failed: {}", e);
                let error_json = json!({ "error": "LLM service unavailable" });
                yield Ok(Event::default().data(error_json.to_string()));
                yield Ok(Event::default().data(json!({ "done": true }).to_string()));
                return;
            }
        };

        if !llm_response.status().is_success() {
            tracing::error!("LLM service returned status: {}", llm_response.status());
            let error_json = json!({ "error": "LLM service returned an error" });
            yield Ok(Event::default().data(error_json.to_string()));
            yield Ok(Event::default().data(json!({ "done": true }).to_string()));
            return;
        }

        // Stream the response bytes and parse SSE lines
        let mut byte_stream = llm_response.bytes_stream();
        let mut buffer = String::new();

        while let Some(chunk_result) = byte_stream.next().await {
            let chunk = match chunk_result {
                Ok(c) => c,
                Err(e) => {
                    tracing::error!("Error reading LLM stream chunk: {}", e);
                    break;
                }
            };

            let chunk_str = match std::str::from_utf8(&chunk) {
                Ok(s) => s,
                Err(e) => {
                    tracing::error!("Invalid UTF-8 in LLM stream: {}", e);
                    continue;
                }
            };

            buffer.push_str(chunk_str);

            // Process complete lines from the buffer
            while let Some(newline_pos) = buffer.find('\n') {
                let line = buffer[..newline_pos].trim_end_matches('\r').to_string();
                buffer = buffer[newline_pos + 1..].to_string();

                // Parse SSE data lines from the LLM service
                if let Some(data_str) = line.strip_prefix("data: ") {
                    if let Ok(data_value) = serde_json::from_str::<Value>(data_str) {
                        // Re-yield token content from LLM
                        if let Some(content) = data_value.get("content").and_then(|c| c.as_str()) {
                            let token_json = json!({ "content": content });
                            yield Ok(Event::default().data(token_json.to_string()));
                        }
                    }
                }
            }
        }

        // Final event: signal completion
        yield Ok(Event::default().data(json!({ "done": true }).to_string()));
    }
}
