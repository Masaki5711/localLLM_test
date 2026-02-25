use std::env;

#[derive(Debug, Clone)]
pub struct Config {
    pub port: u16,
    pub database_url: String,
    pub redis_url: String,
    pub qdrant_url: String,
    pub llm_service_url: String,
    pub etl_service_url: String,
    pub jwt_secret: String,
    pub cors_allowed_origin: String,
}

impl Config {
    pub fn from_env() -> Result<Self, Box<dyn std::error::Error>> {
        Ok(Config {
            port: env::var("API_GATEWAY_PORT")
                .unwrap_or_else(|_| "8080".to_string())
                .parse()?,
            database_url: env::var("DATABASE_URL").unwrap_or_else(|_| {
                "postgresql://graphrag:changeme_postgres@localhost:5432/graphrag".to_string()
            }),
            redis_url: env::var("REDIS_URL")
                .unwrap_or_else(|_| "redis://localhost:6379".to_string()),
            qdrant_url: env::var("QDRANT_URL")
                .unwrap_or_else(|_| "http://localhost:6333".to_string()),
            llm_service_url: env::var("LLM_SERVICE_URL")
                .unwrap_or_else(|_| "http://localhost:8002".to_string()),
            etl_service_url: env::var("ETL_SERVICE_URL")
                .unwrap_or_else(|_| "http://localhost:8001".to_string()),
            jwt_secret: env::var("JWT_SECRET")
                .unwrap_or_else(|_| "dev_secret_change_in_production".to_string()),
            cors_allowed_origin: env::var("CORS_ALLOWED_ORIGIN")
                .unwrap_or_else(|_| "http://localhost:3000".to_string()),
        })
    }
}
