from enum import Enum

class ProvidersEnum(Enum):
    OPENAI = "openai"
    CHAT_OPENAI = "chat_openai"
    ANTHROPIC = "anthropic"
    AZURE_CHAT_OPENAI = "azure_chat_openai"
    COHERE = "cohere"
    DALLE = "dall-e"
    STABLE_DIFFUSION = "stable-diffusion-v1-6"

class ModelsEnum(Enum):
    OPENAI_GPT_35_TURBO_16K = "gpt-3.5-turbo-16k"
    AZURE_GPT_35_TURBO_16K = "gpt-35-turbo-16k"

    OPENAI_GPT_35_TURBO_1106 = "gpt-3.5-turbo-1106"

    OPENAI_GPT_35_TURBO_0613 = "gpt-3.5-turbo-0613"

    AZURE_GPT_35_TURBO = "gpt-35-turbo"

    OPENAI_GPT_4 = "gpt-4"
    AZURE_GPT_4 = "gpt-4"

    OPENAI_GPT_4_0613 = "gpt-4-0613"

    OPENAI_GPT_4_32K = "gpt-4-32k"
    AZURE_GPT_4_32K = "gpt-4-32k"

    OPENAI_GPT_35_TURBO_INSTRUCT = "gpt-3.5-turbo-instruct"

    CLAUDE_INSTANT_12 = "claude-instant-1.2"

    DALLE_3 = "dall-e-3"
    
    STABLE_DIFFUSION_XL = "stable-diffusion-xl-1024-v1-0"
    STABLE_DIFFUSION_V6 = "stable-diffusion-v1-6"

class StreamingEventType(Enum):
    UPDATE = "update"
    META = "meta"
    ERROR = "error"
    GENERATION_SOURCE = "generation_source"
    END = "end"
