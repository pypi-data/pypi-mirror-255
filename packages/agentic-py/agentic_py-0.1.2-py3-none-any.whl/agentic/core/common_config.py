from agentic.core.config import Config

DEEPLAKE_ACCOUNT_NAME = Config(
    name="DEEPLAKE_ACCOUNT_NAME",
    description="The name of the DeepLake account to use for storing the embeddings.",
)

SERPAPI_API_KEY = Config(
    name="SERPAPI_API_KEY",
    description="API key for SerpAPI, used for searching the internet.",
)
