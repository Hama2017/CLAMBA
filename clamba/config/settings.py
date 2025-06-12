"""
Configuration settings for CLAMBA
"""

import os
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class OllamaConfig(BaseModel):
    """Configuration for Ollama AI provider"""
    
    url: str = Field(default="http://localhost:11434", description="Ollama server URL")
    model: str = Field(default="nous-hermes2", description="Model name")
    max_tokens: int = Field(default=4000, description="Maximum tokens")
    temperature: float = Field(default=0.05, description="Temperature for randomness")
    timeout: int = Field(default=120, description="Request timeout in seconds")

    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI provider"""
    
    api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4", description="Model name")
    max_tokens: int = Field(default=4000, description="Maximum tokens")
    temperature: float = Field(default=0.05, description="Temperature for randomness")
    timeout: int = Field(default=120, description="Request timeout in seconds")
    organization: Optional[str] = Field(default=None, description="Organization ID")

    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v


class AnthropicConfig(BaseModel):
    """Configuration for Anthropic Claude provider"""
    
    api_key: str = Field(..., description="Anthropic API key")
    model: str = Field(
        default="claude-3-sonnet-20240229", 
        description="Model name"
    )
    max_tokens: int = Field(default=4000, description="Maximum tokens")
    temperature: float = Field(default=0.05, description="Temperature for randomness")
    timeout: int = Field(default=120, description="Request timeout in seconds")

    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class AIConfig(BaseModel):
    """AI provider configuration"""
    
    provider: Literal["ollama", "openai", "anthropic"] = Field(
        default="ollama", 
        description="AI provider to use"
    )
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    openai: Optional[OpenAIConfig] = Field(default=None)
    anthropic: Optional[AnthropicConfig] = Field(default=None)


class AnalysisConfig(BaseModel):
    """Analysis configuration"""
    
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    min_processes: int = Field(default=3, description="Minimum processes to detect")
    max_processes: int = Field(default=6, description="Maximum processes to detect")
    max_steps_per_process: int = Field(
        default=7, 
        description="Maximum steps per process"
    )
    cycle_detection: bool = Field(
        default=True, 
        description="Enable cycle detection in dependencies"
    )

    @validator("min_processes", "max_processes")
    def validate_process_counts(cls, v):
        if v < 1:
            raise ValueError("Process count must be at least 1")
        return v

    @validator("max_processes")
    def validate_max_processes(cls, v, values):
        if "min_processes" in values and v < values["min_processes"]:
            raise ValueError("max_processes must be >= min_processes")
        return v


class OutputConfig(BaseModel):
    """Output configuration"""
    
    include_metadata: bool = Field(
        default=True, 
        description="Include metadata in output"
    )
    sanitize_ids: bool = Field(
        default=True, 
        description="Sanitize IDs (remove accents, special chars)"
    )
    output_format: Literal["json", "yaml"] = Field(
        default="json", 
        description="Output format"
    )
    pretty_print: bool = Field(
        default=True, 
        description="Pretty print output"
    )


class CLAMBAConfig(BaseSettings):
    """Main CLAMBA configuration"""
    
    ai: AIConfig = Field(default_factory=AIConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    debug: bool = Field(default=False, description="Enable debug mode")

    class Config:
        env_prefix = "CLAMBA_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "CLAMBAConfig":
        """Load configuration from YAML file"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "CLAMBAConfig":
        """Load configuration from dictionary"""
        return cls(**config_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.dict()

    def to_yaml(self, file_path: Union[str, Path]) -> None:
        """Save configuration to YAML file"""
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(self.dict(), f, default_flow_style=False, indent=2)

    def get_ai_config(self) -> Union[OllamaConfig, OpenAIConfig, AnthropicConfig]:
        """Get the active AI provider configuration"""
        if self.ai.provider == "ollama":
            return self.ai.ollama
        elif self.ai.provider == "openai":
            if self.ai.openai is None:
                raise ValueError("OpenAI configuration is missing")
            return self.ai.openai
        elif self.ai.provider == "anthropic":
            if self.ai.anthropic is None:
                raise ValueError("Anthropic configuration is missing")
            return self.ai.anthropic
        else:
            raise ValueError(f"Unknown AI provider: {self.ai.provider}")

    def validate_ai_config(self) -> bool:
        """Validate AI configuration"""
        try:
            self.get_ai_config()
            return True
        except ValueError:
            return False

    @validator("ai")
    def validate_ai_provider_config(cls, v):
        """Validate that required AI provider config is present"""
        if v.provider == "openai" and v.openai is None:
            raise ValueError("OpenAI configuration is required when provider is 'openai'")
        elif v.provider == "anthropic" and v.anthropic is None:
            raise ValueError("Anthropic configuration is required when provider is 'anthropic'")
        return v


def get_default_config() -> CLAMBAConfig:
    """Get default configuration"""
    return CLAMBAConfig()


def load_config(config_path: Optional[Union[str, Path]] = None) -> CLAMBAConfig:
    """
    Load configuration from file or environment
    
    Priority:
    1. Provided config_path
    2. CLAMBA_CONFIG_PATH environment variable
    3. Default configuration
    """
    if config_path:
        return CLAMBAConfig.from_file(config_path)
    
    env_config_path = os.getenv("CLAMBA_CONFIG_PATH")
    if env_config_path and Path(env_config_path).exists():
        return CLAMBAConfig.from_file(env_config_path)
    
    # Try common config file names
    common_names = [
        "clamba_config.yaml",
        "clamba_config.yml",
        "clamba.yaml",
        "clamba.yml",
        ".clamba.yaml",
        ".clamba.yml"
    ]
    
    for name in common_names:
        if Path(name).exists():
            return CLAMBAConfig.from_file(name)
    
    # Return default configuration
    return CLAMBAConfig()


def create_sample_config(output_path: Union[str, Path] = "clamba_config.yaml") -> None:
    """Create a sample configuration file"""
    
    sample_config = """# Configuration CLAMBA - Smart Legal Contract Automaton Generator
# ================================================================

ai:
  # Fournisseur IA : "ollama", "openai", "anthropic"
  provider: "ollama"
  
  # Configuration Ollama (local)
  ollama:
    url: "http://localhost:11434"
    model: "nous-hermes2"
    max_tokens: 4000
    temperature: 0.05
    timeout: 120
    
  # Configuration OpenAI (décommenter si utilisé)
  # openai:
  #   api_key: "${OPENAI_API_KEY}"
  #   model: "gpt-4"
  #   max_tokens: 4000
  #   temperature: 0.05
  #   timeout: 120
  #   organization: null  # Optionnel
    
  # Configuration Anthropic Claude (décommenter si utilisé)
  # anthropic:
  #   api_key: "${ANTHROPIC_API_KEY}"
  #   model: "claude-3-sonnet-20240229"
  #   max_tokens: 4000
  #   temperature: 0.05
  #   timeout: 120

# Configuration de l'analyse
analysis:
  max_retries: 3
  min_processes: 3
  max_processes: 6
  max_steps_per_process: 7
  cycle_detection: true

# Configuration de sortie
output:
  include_metadata: true
  sanitize_ids: true
  output_format: "json"  # "json" ou "yaml"
  pretty_print: true

# Mode debug
debug: false
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sample_config)
    
    print(f"✅ Configuration d'exemple créée : {output_path}")