from typing import Any, List, Mapping, Optional

from notdiamond.llms.provider import NDLLMProvider, ProviderModel
from notdiamond.prompts.prompt import NDPromptTemplate
from notdiamond.metrics.metric import NDMetric
from notdiamond.llms.request import model_select, report_latency
from notdiamond.exceptions import MissingApiKey
from notdiamond.types import NDApiKeyValidator

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM

from langchain_community.chat_models import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from litellm import token_counter

import time


class NDLLM(LLM):
    """Custom implementation of NDLLM
    
    Starting reference is from here: https://python.langchain.com/docs/modules/model_io/llms/custom_llm
    
    """
    llm_providers: List[NDLLMProvider]
    api_key: str
    latency_tracking: bool = True

    def __init__(self, *args, **kwargs):
        NDApiKeyValidator(api_key=kwargs.get('api_key'))

        super(NDLLM, self).__init__(*args, **kwargs)

    @property
    def _llm_type(self) -> str:
        return "NotDiamond LLM"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        return "This function is deprecated for the latest LangChain version, use invoke instead"

    def invoke(self, prompt_template: Optional[NDPromptTemplate] = None, metric: NDMetric = NDMetric("accuracy")):
        best_llm, pipeline_id = model_select(prompt_template=prompt_template,
                                             llm_providers=self.llm_providers,
                                             metric=metric,
                                             nd_api_key=self.api_key)

        if(best_llm.provider == ProviderModel().openai):
            llm = ChatOpenAI(openai_api_key=best_llm.api_key, model_name=best_llm.model)
        elif(best_llm.provider == ProviderModel().anthropic):
            llm = ChatAnthropic(anthropic_api_key=best_llm.api_key, model=best_llm.model)
        elif(best_llm.provider == ProviderModel().google):
            llm = ChatGoogleGenerativeAI(google_api_key=best_llm.api_key, model=best_llm.model)
        
        if self.latency_tracking:
            result = self._invoke_with_latency_tracking(pipeline_id=pipeline_id, llm=llm, model=best_llm.model, prompt_template=prompt_template)
        else:
            result = llm.invoke(prompt_template.from_template())

        return pipeline_id, result
    

    def _invoke_with_latency_tracking(self, pipeline_id: str, llm, model: str, prompt_template: Optional[NDPromptTemplate] = None):
        start_time = time.time()
        result = llm.invoke(prompt_template.from_template())
        end_time = time.time()

        tokens_completed = token_counter(model=model, messages=[{"role": "assistant", "content": result.content}])
        tokens_per_second = tokens_completed / (end_time - start_time)

        report_latency(pipeline_id=pipeline_id, tokens_per_second=tokens_per_second, nd_api_key=self.api_key)
        
        return result
