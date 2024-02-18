from typing import List
from abc import abstractmethod
from langchain.prompts import PromptTemplate
from notdiamond.prompts.hash import nd_hash


class NDAbstractBase:
    def __init__(self, content):
        self.content = content

    @abstractmethod
    def optimize(self):
        pass
    
    @abstractmethod
    def get_module_type(self):
        pass

    @abstractmethod
    def hash_content(self):
        # TODO: future of this function: https://ekzhu.com/datasketch/lsh.html
        return nd_hash(self.content)


class NDPrompt(NDAbstractBase):
    def __init__(self, prompt: str):
        self.prompt = prompt
        super(NDPrompt, self).__init__(self.prompt)

    def __call__(self):
        return self.prompt

    def optimize(self):
        print("Not yet implemented!")
    
    def get_module_type(self):
        return "NDPrompt"


class NDContext(NDAbstractBase):
    def __init__(self, context: str):
        self.context = context
        super(NDContext, self).__init__(self.context)

    def __call__(self):
        return self.context

    def optimize(self):
        print("Not yet implemented!")

    def get_module_type(self):
        return "NDContext"

class NDQuery(NDAbstractBase):
    def __init__(self, query: str):
        self.query = query
        super(NDQuery, self).__init__(self.query)

    def __call__(self):
        return self.query

    def optimize(self):
        print("Not yet implemented!")
    
    def get_module_type(self):
        return "NDQuery"


class NDPromptTemplate(PromptTemplate):
    # prompt: NDPrompt, context: NDContext, query: NDQuery
    def __init__(self,
                 template: str,
                 input_variables: List[str],
                 input_values: List[NDAbstractBase]):
        # partial_variables could 0, 1, or N
        super(NDPromptTemplate, self).__init__(
            input_variables=[],
            template=template,
            partial_variables=dict(map(lambda input_variable, input_value: (input_variable, input_value), input_variables, input_values)))

    def from_template(self):
        # Future TODO: optimization will happen here

        # To get prompt/context/query do this:
        # self.partial_variables['prompt']() -> str

        return self.format_prompt()

    def optimize(self):
        print("Not yet implemented!")

    def prepare_for_request(self):
        return {
            k: { 'module_type': v.get_module_type(), 'content': v.hash_content() }
            for k, v in self.partial_variables.items()
        }
