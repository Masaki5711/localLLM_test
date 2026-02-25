use axum::{
    extract::{Request, State},
    http::StatusCode,
    middleware::Next,
    response::{IntoResponse, Json, Response},
};
use serde_json::json;
use std::sync::Arc;

use crate::auth::jwt;
use crate::AppState;

#[derive(Debug, Clone)]
pub struct AuthUser {
    pub user_id: uuid::Uuid,
    pub username: String,
    pub role: String,
}

pub async fn auth_middleware(
    State(state): State<Arc<AppState>>,
    mut req: Request,
    next: Next,
) -> Response {
    let auth_header = req
        .headers()
        .get("Authorization")
        .and_then(|v| v.to_str().ok());

    let token = match auth_header {
        Some(h) if h.starts_with("Bearer ") => &h[7..],
        _ => {
            return (
                StatusCode::UNAUTHORIZED,
                Json(json!({
                    "success": false,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Missing or invalid authorization header"
                    }
                })),
            )
                .into_response();
        }
    };

    match jwt::verify_token(token, &state.config.jwt_secret) {
        Ok(claims) => {
            let user_id = match uuid::Uuid::parse_str(&claims.sub) {
                Ok(id) => id,
                Err(_) => {
                    return (
                        StatusCode::UNAUTHORIZED,
                        Json(json!({
                            "success": false,
                            "error": {
                                "code": "UNAUTHORIZED",
                                "message": "Invalid token"
                            }
                        })),
                    )
                        .into_response();
                }
            };

            let auth_user = AuthUser {
                user_id,
                username: claims.username,
                role: claims.role,
            };
            req.extensions_mut().insert(auth_user);
            next.run(req).await
        }
        Err(_) => (
            StatusCode::UNAUTHORIZED,
            Json(json!({
                "success": false,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid or expired token"
                }
            })),
        )
            .into_response(),
    }
}
