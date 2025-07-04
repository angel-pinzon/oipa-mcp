"""
Configuration management for OIPA MCP Server

Handles environment variables, connection settings, and feature flags.
Supports both development and production configurations.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """Oracle Database connection configuration"""
    host: str = field(default_factory=lambda: os.getenv("OIPA_DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("OIPA_DB_PORT", "1521")))
    service_name: str = field(default_factory=lambda: os.getenv("OIPA_DB_SERVICE_NAME", "OIPA"))
    username: str = field(default_factory=lambda: os.getenv("OIPA_DB_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("OIPA_DB_PASSWORD", ""))
    
    # Connection pool settings
    pool_min_size: int = field(default_factory=lambda: int(os.getenv("DB_POOL_MIN_SIZE", "1")))
    pool_max_size: int = field(default_factory=lambda: int(os.getenv("DB_POOL_MAX_SIZE", "10")))
    pool_timeout: int = field(default_factory=lambda: int(os.getenv("DB_POOL_TIMEOUT", "30")))
    
    @property
    def dsn(self) -> str:
        """Build Oracle DSN string"""
        return f"{self.host}:{self.port}/{self.service_name}"
    
    @property
    def connection_string(self) -> str:
        """Build full connection string"""
        return f"{self.username}/{self.password}@{self.dsn}"


@dataclass  
class WebServiceConfig:
    """OIPA Web Service configuration"""
    endpoint: str = field(default_factory=lambda: os.getenv("OIPA_WS_ENDPOINT", ""))
    username: str = field(default_factory=lambda: os.getenv("OIPA_WS_USERNAME", ""))
    password: str = field(default_factory=lambda: os.getenv("OIPA_WS_PASSWORD", ""))
    
    # HTTP/SOAP settings
    http_timeout: int = field(default_factory=lambda: int(os.getenv("HTTP_TIMEOUT", "30")))
    soap_timeout: int = field(default_factory=lambda: int(os.getenv("SOAP_TIMEOUT", "60")))
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "3")))
    
    # SSL settings
    enable_ssl: bool = field(default_factory=lambda: os.getenv("ENABLE_SSL", "false").lower() == "true")
    ssl_cert_path: Optional[str] = field(default_factory=lambda: os.getenv("SSL_CERT_PATH") or None)
    ssl_key_path: Optional[str] = field(default_factory=lambda: os.getenv("SSL_KEY_PATH") or None)


@dataclass
class MCPServerConfig:
    """MCP Server configuration"""
    name: str = field(default_factory=lambda: os.getenv("MCP_SERVER_NAME", "oipa-mcp"))
    version: str = field(default_factory=lambda: os.getenv("MCP_SERVER_VERSION", "1.0.0"))
    description: str = field(default_factory=lambda: os.getenv("MCP_SERVER_DESCRIPTION", "MCP Server for Oracle OIPA"))


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "json"))
    file: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE") or None)


@dataclass
class PerformanceConfig:
    """Performance and caching configuration"""
    cache_ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL", "300")))
    max_query_results: int = field(default_factory=lambda: int(os.getenv("MAX_QUERY_RESULTS", "1000")))
    query_timeout: int = field(default_factory=lambda: int(os.getenv("QUERY_TIMEOUT", "30")))


@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling functionality"""
    enable_push_framework: bool = field(default_factory=lambda: os.getenv("ENABLE_PUSH_FRAMEWORK", "true").lower() == "true")
    enable_analytics: bool = field(default_factory=lambda: os.getenv("ENABLE_ANALYTICS", "true").lower() == "true")
    enable_caching: bool = field(default_factory=lambda: os.getenv("ENABLE_CACHING", "true").lower() == "true")
    enable_monitoring: bool = field(default_factory=lambda: os.getenv("ENABLE_MONITORING", "true").lower() == "true")


@dataclass
class Config:
    """Main configuration class combining all settings"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    webservice: WebServiceConfig = field(default_factory=WebServiceConfig)
    mcp_server: MCPServerConfig = field(default_factory=MCPServerConfig) 
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    
    def validate(self) -> None:
        """Validate configuration settings"""
        errors = []
        
        # Check required database settings
        if not self.database.username:
            errors.append("OIPA_DB_USERNAME is required")
        if not self.database.password:
            errors.append("OIPA_DB_PASSWORD is required")
            
        # Check required web service settings
        if not self.webservice.endpoint:
            errors.append("OIPA_WS_ENDPOINT is required")
        if not self.webservice.username:
            errors.append("OIPA_WS_USERNAME is required")
        if not self.webservice.password:
            errors.append("OIPA_WS_PASSWORD is required")
            
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (useful for logging/debugging)"""
        return {
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "service_name": self.database.service_name,
                "username": self.database.username,
                "password": "***" if self.database.password else None,
                "dsn": self.database.dsn
            },
            "webservice": {
                "endpoint": self.webservice.endpoint,
                "username": self.webservice.username,
                "password": "***" if self.webservice.password else None,
                "enable_ssl": self.webservice.enable_ssl
            },
            "mcp_server": {
                "name": self.mcp_server.name,
                "version": self.mcp_server.version,
                "description": self.mcp_server.description
            },
            "features": {
                "push_framework": self.features.enable_push_framework,
                "analytics": self.features.enable_analytics,
                "caching": self.features.enable_caching,
                "monitoring": self.features.enable_monitoring
            }
        }


# Global configuration instance
config = Config()
