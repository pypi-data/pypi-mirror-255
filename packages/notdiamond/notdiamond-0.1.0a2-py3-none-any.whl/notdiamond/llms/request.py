import requests
from requests.models import Response

from notdiamond.prompts.prompt import NDPromptTemplate
from notdiamond.metrics.metric import NDMetric
from notdiamond.llms.provider import NDLLMProvider
from notdiamond.exceptions import ApiError

from typing import List
import json

BASE_URL = "https://not-diamond-server.onrender.com"


def model_select(prompt_template: NDPromptTemplate,
                 llm_providers: List[NDLLMProvider],
                 metric: NDMetric,
                 nd_api_key: str):
    """NotDiamond model select based on prompt
    """

    url = f"{BASE_URL}/v1/optimizer/modelSelect"


    payload = {
        "prompt_template": prompt_template.template,
        "components": prompt_template.prepare_for_request(),
        "llm_providers": [llm_provider.prepare_for_request() for llm_provider in llm_providers],
        "metric": metric.metric
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {nd_api_key}"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
    except Exception as e:
        raise ApiError(f"ND API error for modelSelect: {e}")

    if(response.status_code == 200):
        response_json = response.json()

        provider, model, pipeline_id = response_json['provider']['provider'], \
            response_json['provider']['model'], \
            response_json['pipeline_id']

        best_llm = list(filter(lambda x: (x.model == model) & (x.provider.value == provider), llm_providers))[0]
        return (best_llm, pipeline_id)
    
    raise ApiError(f"ND API error for modelSelect returning: {response.json()} with status {response.status_code}")


def report_latency(pipeline_id: str,
                   tokens_per_second: float,
                   nd_api_key: str):
    """NotDiamond API to report latency of LLM call
    """
    url = f"{BASE_URL}/v1/report/metrics/latency"


    payload = {
        "pipeline_id": pipeline_id,
        "latency": { "tokens_per_second": tokens_per_second }
    }

    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {nd_api_key}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        raise ApiError(f"ND API error for report metrics latency: {e}")

    return response.status_code
