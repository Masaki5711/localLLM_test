use axum::{
    middleware,
    routing::{get, post},
    Router,
};
use std::sync::Arc;

use crate::auth::middleware::auth_middleware;
use crate::AppState;

pub mod auth;
pub mod chat;
pub mod documents;
pub mod health;

pub fn api_routes(state: Arc<AppState>) -> Router<Arc<AppState>> {
    // Protected routes requiring authentication
    let protected = Router::new()
        .route("/chat/stream", post(chat::chat_stream))
        .route("/documents/upload", post(documents::upload_document))
        .route("/documents", get(documents::list_documents))
        .layer(middleware::from_fn_with_state(
            state,
            auth_middleware,
        ));

    // Public routes (no auth required)
    let public = Router::new()
        .route("/auth/login", post(auth::login))
        .route("/auth/refresh", post(auth::refresh))
        .route("/auth/logout", post(auth::logout))
        .route("/health", get(health::service_health));

    public.merge(protected)
}
