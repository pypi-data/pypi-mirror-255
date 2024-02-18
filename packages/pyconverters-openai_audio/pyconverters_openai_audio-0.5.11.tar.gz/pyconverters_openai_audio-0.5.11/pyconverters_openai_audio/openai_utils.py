import os
from logging import Logger

import requests
from openai import OpenAI
from openai.lib.azure import AzureOpenAI
from strenum import StrEnum

logger = Logger("pymultirole")


def audio_list_models(prefix, **kwargs):
    def sort_by_created(x):
        if 'created' in x:
            return x['created']
        elif 'created_at' in x:
            return x['created_at']
        else:
            return x.id

    models = []
    client = set_openai(prefix)
    if prefix.startswith("DEEPINFRA"):
        deepinfra_url = client.base_url
        deploy_list_url = f"{deepinfra_url.scheme}://{deepinfra_url.host}/deploy/list/"
        response = requests.get(deploy_list_url,
                                headers={'Accept': "application/json", 'Authorization': f"Bearer {client.api_key}"})
        if response.ok:
            deploys = response.json()
            models = sorted(deploys, key=sort_by_created, reverse=True)
            models = list(
                {m['model_name'] for m in models if
                 m['task'] == 'automatic-speech-recognition' and m['status'] == 'running'})
    return models


def set_openai(prefix):
    if prefix.startswith("AZURE"):
        client = AzureOpenAI(
            # This is the default and can be omitted
            api_key=os.getenv(prefix + "OPENAI_API_KEY"),
            azure_endpoint=os.getenv(prefix + "OPENAI_API_BASE", None),
            api_version=os.getenv(prefix + "OPENAI_API_VERSION", None),
            azure_deployment=os.getenv(prefix + "OPENAI_DEPLOYMENT_ID", None)
        )
    else:
        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.getenv(prefix + "OPENAI_API_KEY"),
            base_url=os.getenv(prefix + "OPENAI_API_BASE", None)
        )
    return client


NO_DEPLOYED_MODELS = 'no deployed models - check API key'


def create_asr_model_enum(name, prefix="", key=lambda m: m):
    audio_models = []
    default_audio_model = None
    try:
        audio_models = [m for m in audio_list_models(prefix) if key(m)]
        if audio_models:
            default_audio_model = audio_models[0]
    except BaseException:
        logger.warning("Can't list models from endpoint", exc_info=True)

    if len(audio_models) == 0:
        audio_models = [NO_DEPLOYED_MODELS]
    models = [("".join([c if c.isalnum() else "_" for c in m]), m) for m in audio_models]
    model_enum = StrEnum(name, dict(models))
    default_audio_model = model_enum(default_audio_model) if default_audio_model is not None else None
    return model_enum, default_audio_model
