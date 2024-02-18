from typing import Optional

from notdiamond.types import NDApiKeyValidator
from notdiamond.metrics.request import feedback_request

class NDMetric:
    def __init__(self, metric: Optional[str] = "accuracy"):
        self.metric = metric

    def __call__(self):
        return self.metric
    
    def feedback(self,
                 feedback_payload: dict,
                 pipeline_id: str,
                 nd_api_key: str):
        NDApiKeyValidator(api_key=nd_api_key)

        response = feedback_request(feedback_payload, pipeline_id, nd_api_key)

        return response
        