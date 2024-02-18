import jax.lax
from EasyDel import JAXServer, AutoEasyDelModelForCausalLM
from fjformer import get_float_dtype_by_name
from transformers import AutoTokenizer
import logging
from typing import List
from ..utils import BaseClassAgent, DEFAULT_SYSTEM_PROMPT, prompt_model

logging.basicConfig(
    level=logging.INFO
)


class PixelyAIServeJax(JAXServer, BaseClassAgent):
    def __init__(self, config=None):
        super().__init__(config=config)
        self.gradio_app_custom = self.create_gradio_pixely_ai()

    @classmethod
    def load_from_torch(cls, pretrained_model_name_or_path, config=None):

        tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path)
        model, param = AutoEasyDelModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            dtype=get_float_dtype_by_name(config["dtype"] if config is not None else "fp16"),
            param_dtype=get_float_dtype_by_name(config["dtype"] if config is not None else "fp16"),
            precision=jax.lax.Precision("fastest"),
            device=jax.devices("cpu")[0]
        )
        return cls.load_from_params(
            config_model=model.config,
            model=model,
            config=config,
            params=param,
            tokenizer=tokenizer,
            add_params_field=True,
            do_memory_log=False
        )

    @classmethod
    def load_from_jax(cls, pretrained_model_name_or_path, checkpoint_path, config_repo=None, config=None):
        raise NotImplemented("Not Implemented Error!")

    def process_gradio_custom(self, prompt, user_id, data, system, max_new_tokens, greedy):
        history = data.split("<|END_OF_MESSAGE|>") if data != "" else []
        system = system if system != "" else DEFAULT_SYSTEM_PROMPT
        his = []
        for hs in history:
            if hs != "":
                his.append(hs.split("<|END_OF_MESSAGE_TURN_HUMAN|>"))
        history = his
        string = self.prompt_model(
            message=prompt,
            chat_history=history or [],
            system_prompt=system
        )
        response = "null"
        if not self.config.stream_tokens_for_gradio:

            for response, _ in self.process(
                    string=string,
                    greedy=greedy,
                    max_new_tokens=max_new_tokens,
            ):
                ...

        else:
            for response, _ in self.process(
                    string=string,
                    greedy=greedy,
                    max_new_tokens=max_new_tokens
            ):
                yield "", response
        return "", response

    @staticmethod
    def format_chat(history: List[List[str]], prompt: str, system: str = None) -> str:
        return prompt_model(message=prompt, system_prompt=system, chat_history=history)

    @staticmethod
    def prompt_model(message: str, chat_history, system_prompt: str):
        return prompt_model(message=message, chat_history=chat_history, system_prompt=system_prompt)
