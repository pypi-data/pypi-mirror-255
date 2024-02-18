from .. import NamedModel, MissingDependencyError

try:
    from openai import OpenAI
except ImportError as err:
    raise MissingDependencyError("Please install openai library") from err


class OpenAIModel(NamedModel):
    """
    Model that calls OpenAI Completion API.

    - **model** (`str`): Name of the OpenAI model. Default is `"gpt-3.5-turbo"`.
    - **api_key** (`str`): OpenAI API key
    - **max_retries** (`int`): How many times to retry a failed request. Default is `2`.
    """

    def __init__(self, model="gpt-3.5-turbo", api_key=None, max_retries=2):
        self.model = model
        self.client = OpenAI(api_key=api_key, max_retries=max_retries)

        super().__init__(f"openai-{model}", self.__chat)

    def __chat(self, messages: list) -> str:
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        return chat_completion.choices[0].message.content
