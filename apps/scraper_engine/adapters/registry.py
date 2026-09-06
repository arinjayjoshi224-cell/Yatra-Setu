# apps/scraper_engine/adapters/registry.py
from .yatra import YatraAdapter

ADAPTER_REGISTRY = {
    "yatra": YatraAdapter,
}