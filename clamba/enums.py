from enum import Enum

class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    CLAUDE = "claude"
    HUGGINGFACE = "huggingface"
    FIREWORKS = "fireworks" 
