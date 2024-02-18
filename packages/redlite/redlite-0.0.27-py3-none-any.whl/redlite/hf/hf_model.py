from .._core import NamedModel, Message, MissingDependencyError, log

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
    import torch
except ImportError as err:
    raise MissingDependencyError("Please install transformers and torch libraries") from err


class HFModel(NamedModel):
    """
    Model loaded from HuggingFace hub.

    - **hf_name** (`str`): name of the model on HuggingFace hub.
    - **device** (`str | None`): which device to use for inference. If left
            unset, will use CUDA if present, else CPU.
    - **token** (`str | None`): HuggingFace authorization token. May be needed
            for some models (e.g. Mistral).
    - **max_length** (`int`): Largest number of tokens that model can handle.
            If prompt is too big, model will output an empty string.
    """

    def __init__(self, hf_name: str, device: str | None = None, token=None, max_length=8192):
        self.name = "hf:" + hf_name
        if device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"

        config = AutoConfig.from_pretrained(hf_name, token=token)

        self.__model = (
            AutoModelForCausalLM.from_pretrained(
                hf_name,
                token=token,
                config=config,
                torch_dtype=torch.bfloat16,
            )
            .to(device)
            .eval()
        )

        self.__tokenizer = AutoTokenizer.from_pretrained(
            hf_name,
            model_max_length=max_length,
            use_fast=False,
            token=token,
            trust_remote_code=True,
        )
        self.max_length = max_length

        super().__init__("hf:" + hf_name, self.__predict)

    def __predict(self, messages: list[Message]) -> str:
        prompt = self.__tokenizer.apply_chat_template(messages, tokenize=False)
        inputs = self.__tokenizer(prompt, return_tensors="pt").to(self.__model.device)
        prompt_tokens = inputs["input_ids"].shape[1]
        if prompt_tokens >= self.max_length:
            log.warn(
                f"Prompt of size {prompt_tokens} does not fit into "
                + "model max_length of {self.max_length}. Returning empty string!"
            )
            return ""

        with torch.no_grad():
            outputs = self.__model.generate(
                **inputs,
                max_new_tokens=self.max_length - prompt_tokens,
                pad_token_id=self.__tokenizer.eos_token_id,
            )

        response = outputs[0][prompt_tokens:]
        return self.__tokenizer.decode(response, skip_special_tokens=True)
