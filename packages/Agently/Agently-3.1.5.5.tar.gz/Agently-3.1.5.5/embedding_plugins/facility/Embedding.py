from .utils import FacilityABC
from Agently.utils import RuntimeCtx, RuntimeCtxNamespace

class Embedding(FacilityABC):
    def __init__(self, *, storage: object, plugin_manager: object, settings: object):
        self.plugin_manager = plugin_manager
        self.settings = settings

    def OpenAI(self, input: str, options: dict={}):
        from openai import OpenAI
        import httpx
        settings = RuntimeCtxNamespace("embedding.OpenAI", self.settings)
        # Prepare Client Params
        client_params = {}
        base_url = settings.get_trace_back("url")
        if base_url:
            client_params.update({ "base_url": base_url })
        proxy = self.settings.get_trace_back("proxy")
        if proxy:
            client_params.update({ "http_client": httpx.Client( proxies = proxy ) })
        api_key = settings.get_trace_back("auth.api_key")
        if api_key:
            client_params.update({ "api_key": api_key })
        else:
            raise Exception("[Embedding] OpenAI require api_key. use .set_settings('embedding.OpenAI.auth', { 'api_key': '<Your-API-Key>' }) to set it.")
        if "model" not in options:
            options["model"] = "text-embedding-ada-002"
        # Create Client
        client = OpenAI(**client_params)
        # Request
        result = client.embeddings.create(
            input = input,
            **options
        )
        if result.data:
            return result.data[0].embedding
        else:
            raise Exception(result)

def export():
    return ("embedding", Embedding)