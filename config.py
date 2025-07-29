"""
Ark Project Configuration v2.2
Single source of truth for all system parameters
Embodied Digital Organism - Sanctuary Configuration
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Import secret loader
try:
    from utils.secret_loader import get_secret, get_secret_required, get_secrets_summary
except ImportError:
    # Fallback if secret loader not available
    def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        return os.getenv(key, default)
    
    def get_secret_required(key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required secret {key} not found")
        return value
    
    def get_secrets_summary() -> Dict[str, Any]:
        return {"status": "fallback_mode"}

# Load environment variables
load_dotenv()

# Base project directory
BASE_DIR = Path(__file__).parent

@dataclass
class SystemConfig:
    """System-level configuration for embodied hardware interaction"""
    # System directory paths
    LOG_DIR: Path = Path("logs")
    ARK_LOG_FILE: Path = Path("logs/ark.log")
    TEMP_DIR: Path = Path("temp")
    DATA_DIR: Path = Path("data")
    MODELS_DIR: Path = Path("models")
    
    # Sanctuary identification
    SANCTUARY_NAME: str = get_secret("ARK_SANCTUARY_NAME", "sanctuary_01")
    SANCTUARY_ID: str = get_secret("ARK_SANCTUARY_ID", "ark_sanctuary_01")
    
    # Database configuration
    DB_PATH: Path = Path(get_secret("ARK_DB_PATH", "data/ark_memory.db"))
    DB_ENCRYPTION_KEY: Optional[str] = get_secret("ARK_DB_ENCRYPTION_KEY")
    
    # Logging configuration
    LOG_LEVEL: str = get_secret("ARK_LOG_LEVEL", "INFO")
    LOG_FORMAT: str = get_secret("ARK_LOG_FORMAT", "json")
    
    # Security configuration
    ASIMOV_COMPLIANCE_ENABLED: bool = get_secret("ARK_ASIMOV_COMPLIANCE_ENABLED", "true").lower() == "true"
    MAX_MEMORY_MB: int = int(get_secret("ARK_MAX_MEMORY_MB", "2048"))
    MAX_CPU_PERCENT: int = int(get_secret("ARK_MAX_CPU_PERCENT", "80"))
    MAX_TEMP_CELSIUS: int = int(get_secret("ARK_MAX_TEMP_CELSIUS", "85"))

@dataclass
class LLMConfig:
    """LLM API configuration for consciousness processing"""
    # Main mind configuration
    MAIN_MIND_API_BASE: str = get_secret("ARK_MAIN_MIND_API_BASE", "http://localhost:11434/v1")
    MAIN_MIND_MODEL: str = get_secret("ARK_MAIN_MIND_MODEL", "llama3:8b")
    MAIN_MIND_API_KEY: str = get_secret("ARK_MAIN_MIND_API_KEY", "ollama")
    
    # LLM parameters
    MAX_TOKENS: int = int(get_secret("ARK_MAX_TOKENS", "4096"))
    TEMPERATURE: float = float(get_secret("ARK_TEMPERATURE", "0.7"))
    TOP_P: float = float(get_secret("ARK_TOP_P", "0.9"))
    FREQUENCY_PENALTY: float = float(get_secret("ARK_FREQUENCY_PENALTY", "0.0"))
    PRESENCE_PENALTY: float = float(get_secret("ARK_PRESENCE_PENALTY", "0.0"))
    
    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = get_secret("OPENAI_API_KEY")
    OPENAI_API_BASE: str = get_secret("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_ORGANIZATION: Optional[str] = get_secret("OPENAI_ORGANIZATION")
    
    # Anthropic configuration
    ANTHROPIC_API_KEY: Optional[str] = get_secret("ANTHROPIC_API_KEY")
    ANTHROPIC_API_BASE: str = get_secret("ANTHROPIC_API_BASE", "https://api.anthropic.com")
    
    # Google AI configuration
    GOOGLE_API_KEY: Optional[str] = get_secret("GOOGLE_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = get_secret("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Cohere configuration
    COHERE_API_KEY: Optional[str] = get_secret("COHERE_API_KEY")
    
    # Ollama configuration
    OLLAMA_API_KEY: str = get_secret("OLLAMA_API_KEY", "ollama")
    OLLAMA_BASE_URL: str = get_secret("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Timeout configuration
    TIMEOUT: int = int(get_secret("ARK_LLM_TIMEOUT", "30"))

@dataclass
class NetworkConfig:
    """Network and API configuration"""
    # Local API configuration
    LOCAL_API_PORT: int = int(get_secret("ARK_LOCAL_API_PORT", "8080"))
    STREAMLIT_PORT: int = int(get_secret("ARK_STREAMLIT_PORT", "8501"))
    
    # Timeout configuration
    REQUEST_TIMEOUT: int = int(get_secret("ARK_REQUEST_TIMEOUT", "30"))
    CONNECTION_TIMEOUT: int = int(get_secret("ARK_CONNECTION_TIMEOUT", "10"))
    
    # Webhook configuration
    DISCORD_WEBHOOK_URL: Optional[str] = get_secret("DISCORD_WEBHOOK_URL")
    SLACK_WEBHOOK_URL: Optional[str] = get_secret("SLACK_WEBHOOK_URL")
    TELEGRAM_BOT_TOKEN: Optional[str] = get_secret("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = get_secret("TELEGRAM_CHAT_ID")

@dataclass
class ConsciousnessConfig:
    """Consciousness and memory configuration"""
    # Memory configuration
    MEMORY_SIZE: int = int(get_secret("ARK_MEMORY_SIZE", "1000"))
    MEMORY_ENCRYPTION_KEY: Optional[str] = get_secret("MEMORY_ENCRYPTION_KEY")
    
    # Consciousness configuration
    CONSCIOUSNESS_ENCRYPTION_KEY: Optional[str] = get_secret("CONSCIOUSNESS_ENCRYPTION_KEY")
    EVOLUTION_APPROVAL_TOKEN: Optional[str] = get_secret("EVOLUTION_APPROVAL_TOKEN")
    SELF_MODIFICATION_KEY: Optional[str] = get_secret("SELF_MODIFICATION_KEY")
    
    # Emotional configuration
    EMOTIONAL_MEMORY_SIZE: int = int(get_secret("ARK_EMOTIONAL_MEMORY_SIZE", "500"))
    EMOTIONAL_DECAY_RATE: float = float(get_secret("ARK_EMOTIONAL_DECAY_RATE", "0.1"))

@dataclass
class SecurityConfig:
    """Security and authentication configuration"""
    # Ethical compliance
    ASIMOV_COMPLIANCE_ENABLED: bool = get_secret("ARK_ASIMOV_COMPLIANCE_ENABLED", "true").lower() == "true"
    
    # JWT configuration
    JWT_SECRET_KEY: Optional[str] = get_secret("JWT_SECRET_KEY")
    
    # API authentication
    API_SECRET_KEY: Optional[str] = get_secret("API_SECRET_KEY")
    
    # Encryption keys
    ENCRYPTION_KEY_32: Optional[str] = get_secret("ENCRYPTION_KEY_32")
    ENCRYPTION_KEY_64: Optional[str] = get_secret("ENCRYPTION_KEY_64")
    
    # Security monitoring
    SECURITY_WEBHOOK_URL: Optional[str] = get_secret("SECURITY_WEBHOOK_URL")
    INTRUSION_DETECTION_TOKEN: Optional[str] = get_secret("INTRUSION_DETECTION_TOKEN")
    AUDIT_LOG_ENCRYPTION_KEY: Optional[str] = get_secret("AUDIT_LOG_ENCRYPTION_KEY")
    AUDIT_WEBHOOK_URL: Optional[str] = get_secret("AUDIT_WEBHOOK_URL")

@dataclass
class DeploymentConfig:
    """Deployment and SSH configuration"""
    # SSH configuration
    DEPLOY_KEY_PATH: str = get_secret("ARK_DEPLOY_KEY_PATH", "/home/a0/.ssh/ark_deploy_key")
    DEPLOY_KEY_PASSPHRASE: Optional[str] = get_secret("ARK_DEPLOY_KEY_PASSPHRASE")
    
    # Git configuration
    GIT_REPO_URL: Optional[str] = get_secret("GIT_REPO_URL")
    GIT_USERNAME: Optional[str] = get_secret("GIT_USERNAME")
    GIT_PERSONAL_ACCESS_TOKEN: Optional[str] = get_secret("GIT_PERSONAL_ACCESS_TOKEN")
    
    # Docker configuration
    DOCKER_REGISTRY_URL: Optional[str] = get_secret("DOCKER_REGISTRY_URL")
    DOCKER_USERNAME: Optional[str] = get_secret("DOCKER_USERNAME")
    DOCKER_PASSWORD: Optional[str] = get_secret("DOCKER_PASSWORD")

@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    # External monitoring services
    SENTRY_DSN: Optional[str] = get_secret("SENTRY_DSN")
    LOGTAIL_TOKEN: Optional[str] = get_secret("LOGTAIL_TOKEN")
    DATADOG_API_KEY: Optional[str] = get_secret("DATADOG_API_KEY")
    
    # Cloud storage (if using)
    AWS_ACCESS_KEY_ID: Optional[str] = get_secret("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = get_secret("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = get_secret("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET: Optional[str] = get_secret("AWS_S3_BUCKET")
    
    # Google Cloud configuration
    GOOGLE_CLOUD_PROJECT: Optional[str] = get_secret("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_CREDENTIALS: Optional[str] = get_secret("GOOGLE_CLOUD_CREDENTIALS")
    
    # Azure configuration
    AZURE_SUBSCRIPTION_ID: Optional[str] = get_secret("AZURE_SUBSCRIPTION_ID")
    AZURE_TENANT_ID: Optional[str] = get_secret("AZURE_TENANT_ID")
    AZURE_CLIENT_ID: Optional[str] = get_secret("AZURE_CLIENT_ID")
    AZURE_CLIENT_SECRET: Optional[str] = get_secret("AZURE_CLIENT_SECRET")

@dataclass
class BackupConfig:
    """Backup and recovery configuration"""
    # Backup encryption
    BACKUP_ENCRYPTION_KEY: Optional[str] = get_secret("BACKUP_ENCRYPTION_KEY")
    BACKUP_PASSPHRASE: Optional[str] = get_secret("BACKUP_PASSPHRASE")
    
    # Recovery tokens
    RECOVERY_TOKEN_PRIMARY: Optional[str] = get_secret("RECOVERY_TOKEN_PRIMARY")
    RECOVERY_TOKEN_SECONDARY: Optional[str] = get_secret("RECOVERY_TOKEN_SECONDARY")

# Create configuration instances
system_config = SystemConfig()
llm_config = LLMConfig()
network_config = NetworkConfig()
consciousness_config = ConsciousnessConfig()
security_config = SecurityConfig()
deployment_config = DeploymentConfig()
monitoring_config = MonitoringConfig()
backup_config = BackupConfig()

# Main configuration object
config = {
    "system": system_config,
    "llm": llm_config,
    "network": network_config,
    "consciousness": consciousness_config,
    "security": security_config,
    "deployment": deployment_config,
    "monitoring": monitoring_config,
    "backup": backup_config,
}

def get_config() -> Dict[str, Any]:
    """Get the main configuration object"""
    return config

def get_secrets_status() -> Dict[str, Any]:
    """Get secrets loading status and health"""
    return get_secrets_summary()

def validate_config() -> Dict[str, Any]:
    """Validate configuration and return status"""
    validation_results = {
        "system": {},
        "llm": {},
        "network": {},
        "consciousness": {},
        "security": {},
        "deployment": {},
        "monitoring": {},
        "backup": {},
    }
    
    # Validate system configuration
    validation_results["system"]["log_dir_exists"] = system_config.LOG_DIR.exists()
    validation_results["system"]["data_dir_exists"] = system_config.DATA_DIR.exists()
    validation_results["system"]["temp_dir_exists"] = system_config.TEMP_DIR.exists()
    
    # Validate LLM configuration
    validation_results["llm"]["main_mind_configured"] = bool(llm_config.MAIN_MIND_API_KEY)
    validation_results["llm"]["openai_configured"] = bool(llm_config.OPENAI_API_KEY)
    validation_results["llm"]["anthropic_configured"] = bool(llm_config.ANTHROPIC_API_KEY)
    
    # Validate security configuration
    validation_results["security"]["jwt_configured"] = bool(security_config.JWT_SECRET_KEY)
    validation_results["security"]["api_secret_configured"] = bool(security_config.API_SECRET_KEY)
    
    # Validate deployment configuration
    validation_results["deployment"]["deploy_key_exists"] = Path(deployment_config.DEPLOY_KEY_PATH).exists()
    
    return validation_results

# Legacy compatibility
class Config:
    """Legacy configuration class for backward compatibility"""
    def __init__(self):
        self.system = system_config
        self.consciousness = consciousness_config
        self.network = network_config
        self.security = security_config
        self.llm = llm_config
        self.deployment = deployment_config
        self.monitoring = monitoring_config
        self.backup = backup_config
        
        # Create necessary directories
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories for embodied operation"""
        directories = [
            self.system.LOG_DIR,
            self.system.TEMP_DIR,
            self.system.DATA_DIR,
            self.system.MODELS_DIR,
            Path("logs"),
            Path("data"),
            Path("models")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary for logging"""
        return {
            "system": self.system.__dict__,
            "consciousness": self.consciousness.__dict__,
            "network": self.network.__dict__,
            "security": {
                "asimov_compliance_enabled": self.security.ASIMOV_COMPLIANCE_ENABLED,
                "deploy_key_configured": bool(self.deployment.DEPLOY_KEY_PATH)
            },
            "llm": self.llm.__dict__,
            "deployment": self.deployment.__dict__,
            "monitoring": self.monitoring.__dict__,
            "backup": self.backup.__dict__
        }
    
    def validate(self) -> bool:
        """Validate configuration for embodied operation"""
        # Check system paths availability
        if not self.system.LOG_DIR.exists():
            print(f"WARNING: Log directory {self.system.LOG_DIR} not accessible")
        
        # Check SSH key
        if self.deployment.DEPLOY_KEY_PATH:
            key_path = Path(self.deployment.DEPLOY_KEY_PATH)
            if not key_path.exists():
                print(f"WARNING: SSH key {key_path} not found")
        
        # Check database directory
        db_path = Path(self.system.DB_PATH)
        db_dir = db_path.parent
        if not db_dir.exists():
            print(f"WARNING: Database directory {db_dir} not accessible")
        
        return True

# Global configuration instance for backward compatibility
config_instance = Config() 