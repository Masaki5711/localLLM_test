use axum::{extract::State, response::Json};
use serde::Deserialize;
use serde_json::{json, Value};
use std::sync::Arc;

use crate::auth::jwt;
use crate::error::AppError;
use crate::models::user::UserResponse;
use crate::AppState;

#[derive(Debug, Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

#[derive(Debug, Deserialize)]
pub struct RefreshRequest {
    pub refresh_token: String,
}

pub async fn login(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<LoginRequest>,
) -> Result<Json<Value>, AppError> {
    let user = sqlx::query_as::<_, crate::models::user::User>(
        "SELECT * FROM users WHERE username = $1 AND is_active = true",
    )
    .bind(&payload.username)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::Unauthorized)?;

    let password_valid = bcrypt::verify(&payload.password, &user.password_hash)
        .map_err(|_| AppError::Internal("Password verification failed".to_string()))?;

    if !password_valid {
        return Err(AppError::Unauthorized);
    }

    // Update last_login_at
    sqlx::query("UPDATE users SET last_login_at = NOW() WHERE id = $1")
        .bind(user.id)
        .execute(&state.db)
        .await?;

    let access_token = jwt::create_access_token(
        user.id,
        &user.username,
        &user.role,
        &state.config.jwt_secret,
        3600,
    )
    .map_err(|e| AppError::Internal(format!("Token creation failed: {}", e)))?;

    let refresh_token = jwt::create_refresh_token(
        user.id,
        &user.username,
        &user.role,
        &state.config.jwt_secret,
    )
    .map_err(|e| AppError::Internal(format!("Token creation failed: {}", e)))?;

    let user_resp: UserResponse = user.into();

    Ok(Json(json!({
        "success": true,
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": user_resp
        }
    })))
}

pub async fn refresh(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<RefreshRequest>,
) -> Result<Json<Value>, AppError> {
    let claims = jwt::verify_token(&payload.refresh_token, &state.config.jwt_secret)
        .map_err(|_| AppError::Unauthorized)?;

    let user_id =
        uuid::Uuid::parse_str(&claims.sub).map_err(|_| AppError::Unauthorized)?;

    let user = sqlx::query_as::<_, crate::models::user::User>(
        "SELECT * FROM users WHERE id = $1 AND is_active = true",
    )
    .bind(user_id)
    .fetch_optional(&state.db)
    .await?
    .ok_or(AppError::Unauthorized)?;

    let access_token = jwt::create_access_token(
        user.id,
        &user.username,
        &user.role,
        &state.config.jwt_secret,
        3600,
    )
    .map_err(|e| AppError::Internal(format!("Token creation failed: {}", e)))?;

    let new_refresh_token = jwt::create_refresh_token(
        user.id,
        &user.username,
        &user.role,
        &state.config.jwt_secret,
    )
    .map_err(|e| AppError::Internal(format!("Token creation failed: {}", e)))?;

    Ok(Json(json!({
        "success": true,
        "data": {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600
        }
    })))
}

pub async fn logout() -> Json<Value> {
    Json(json!({
        "success": true,
        "data": { "message": "Logged out successfully" }
    }))
}
