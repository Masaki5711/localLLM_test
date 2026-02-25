use axum::{
    extract::{Multipart, State},
    response::Json,
    Extension,
};
use serde_json::Value;
use std::sync::Arc;

use crate::auth::middleware::AuthUser;
use crate::error::AppError;
use crate::AppState;

/// POST /documents/upload - Forward multipart file upload to ETL service
///
/// Extracts the uploaded file from the multipart form data and
/// re-sends it to the ETL pipeline service for processing.
pub async fn upload_document(
    State(state): State<Arc<AppState>>,
    Extension(auth_user): Extension<AuthUser>,
    mut multipart: Multipart,
) -> Result<Json<Value>, AppError> {
    let mut file_part: Option<(String, Vec<u8>, Option<String>)> = None;

    while let Some(field) = multipart.next_field().await.map_err(|e| {
        tracing::error!("Failed to read multipart field: {}", e);
        AppError::Validation(format!("Invalid multipart data: {}", e))
    })? {
        let field_name = field.name().unwrap_or_default().to_string();
        if field_name == "file" {
            let file_name = field
                .file_name()
                .unwrap_or("unknown")
                .to_string();
            let content_type = field
                .content_type()
                .map(|ct| ct.to_string());
            let data = field.bytes().await.map_err(|e| {
                tracing::error!("Failed to read file bytes: {}", e);
                AppError::Internal("Failed to read uploaded file".to_string())
            })?;

            file_part = Some((file_name, data.to_vec(), content_type));
            break;
        }
    }

    let (file_name, file_data, content_type) = file_part
        .ok_or_else(|| AppError::Validation("No file field found in upload".to_string()))?;

    tracing::info!(
        user = %auth_user.username,
        file = %file_name,
        size = file_data.len(),
        "Uploading document to ETL service"
    );

    // Build multipart form for reqwest
    let mut part = reqwest::multipart::Part::bytes(file_data)
        .file_name(file_name.clone());

    if let Some(ct) = content_type {
        let mime = ct
            .parse::<reqwest::header::HeaderValue>()
            .map_err(|_| AppError::Internal("Invalid content type".to_string()))?;
        part = part.headers({
            let mut headers = reqwest::header::HeaderMap::new();
            headers.insert(reqwest::header::CONTENT_TYPE, mime);
            headers
        });
    }

    let form = reqwest::multipart::Form::new().part("file", part);

    let http_client = reqwest::Client::new();
    let etl_response = http_client
        .post(format!(
            "{}/api/v1/documents/upload",
            state.config.etl_service_url
        ))
        .multipart(form)
        .send()
        .await
        .map_err(|e| {
            tracing::error!("ETL upload request failed: {}", e);
            AppError::Internal("Document processing service unavailable".to_string())
        })?;

    let status = etl_response.status();
    let body: Value = etl_response.json().await.map_err(|e| {
        tracing::error!("Failed to parse ETL upload response: {}", e);
        AppError::Internal("Invalid response from document service".to_string())
    })?;

    if !status.is_success() {
        tracing::error!(
            status = %status,
            response = %body,
            "ETL service returned error for upload"
        );
        return Err(AppError::Internal(
            "Document processing failed".to_string(),
        ));
    }

    Ok(Json(body))
}

/// GET /documents - List documents from ETL service
///
/// Proxies the request to the ETL service and returns the document list.
pub async fn list_documents(
    State(state): State<Arc<AppState>>,
    Extension(_auth_user): Extension<AuthUser>,
) -> Result<Json<Value>, AppError> {
    let http_client = reqwest::Client::new();
    let etl_response = http_client
        .get(format!("{}/api/v1/documents", state.config.etl_service_url))
        .send()
        .await
        .map_err(|e| {
            tracing::error!("ETL documents list request failed: {}", e);
            AppError::Internal("Document service unavailable".to_string())
        })?;

    let body: Value = etl_response.json().await.map_err(|e| {
        tracing::error!("Failed to parse ETL documents response: {}", e);
        AppError::Internal("Invalid response from document service".to_string())
    })?;

    Ok(Json(body))
}
