use axum::{extract::State, response::Json};
use serde_json::{json, Value};
use std::sync::Arc;

use crate::AppState;

pub async fn service_health(State(state): State<Arc<AppState>>) -> Json<Value> {
    let db_ok = sqlx::query("SELECT 1")
        .execute(&state.db)
        .await
        .is_ok();

    Json(json!({
        "success": true,
        "data": {
            "services": {
                "api_gateway": { "status": "healthy" },
                "postgres": { "status": if db_ok { "healthy" } else { "unhealthy" } }
            }
        }
    }))
}
