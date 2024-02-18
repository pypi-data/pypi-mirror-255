from llama_cpp import Llama
from dataclasses import dataclass
from typing import Optional, Union, List, Iterable, Literal
from ._setting import download_model_gguf


@dataclass
class InferencePredictions:
    text: str
    index: int
    logprobs: Optional[float]
    finish_reason: Optional[bool]


@dataclass
class InferenceOutput:
    id: str
    object: str
    created: str
    model: str
    predictions: InferencePredictions


class GGMLModel:
    def __init__(
            self,
            model: Llama,
            max_position_embedding: int = 2048
    ):
        """
        The __init__ function is the constructor for a class. It's called when an object of that class is created.

        :param self: Represent the instance of the class
        :param model: Llama: Pass the model object to the class
        :param max_position_embedding: int: Set the maximum number of tokens that can be used in a single query
        """
        self.model = model
        self.max_position_embedding = max_position_embedding

    @classmethod
    def from_pretrained(
            cls,
            pretrained_model_name_or_path: str,
            filename: str,
            max_position_embedding: int = 2048

    ):
        ref = download_model_gguf(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            filename=filename
        )

        model = Llama(model_path=ref, n_ctx=max_position_embedding, verbose=False)
        return cls(
            model,
            max_position_embedding
        )

    def __call__(
            self,
            string: str,
            suffix: Optional[str] = None,
            max_position_embedding: Optional[int] = None,
            temperature: float = 0.8,
            top_p: float = 0.95,
            min_p: float = 0.05,
            typical_p: float = 1.0,
            logprobs: Optional[int] = None,
            echo: bool = False,
            stop=None,
            frequency_penalty: float = 0.0,
            presence_penalty: float = 0.0,
            repeat_penalty: float = 1.1,
            top_k: int = 40,
            seed: Optional[int] = None,
            tfs_z: float = 1.0,
            mirostat_mode: int = 0,
            mirostat_tau: float = 5.0,
            mirostat_eta: float = 0.1,
    ) -> Iterable[InferenceOutput]:
        """
       The __call__ function is the main function of this class.
       It takes in a string, and returns an iterable of InferenceOutput objects.
       The InferenceOutput object contains the following attributes:

       :param self: Bind the method to an object
       :param string: str: Pass the text to be completed by the model
       :param suffix: Optional[str]: Add a suffix to the end of the string
       :param max_position_embedding: Optional[int]: Limit the number of tokens that can be generated
       :param temperature: float: Control the randomness of the output
       :param top_p: float: Filter out the top p% of tokens
       :param min_p: float: Filter out tokens that have a probability less than min_p
       :param typical_p: float: Set the probability of a token being generated
       :param logprobs: Optional[int]: Control the number of log probabilities that are returned
       :param echo: bool: Determine whether to echo the string back as a prediction
       :param stop: Stop the inference at a certain token
       :param frequency_penalty: float: Penalize the frequency of words in the text
       :param presence_penalty: float: Penalize the presence of certain words in the output
       :param repeat_penalty: float: Penalize the model for repeating words
       :param top_k: int: Control the number of tokens that are considered for each step
       :param seed: Optional[int]: Set the seed for the random number generator
       :param tfs_z: float: Control the amount of text that is generated
       :param mirostat_mode: int: Determine which type of mirostat to use
       :param mirostat_tau: float: Control the rate of change in the probability distribution
       :param mirostat_eta: float: Control the amount of randomness in the model
       :param : Set the maximum number of tokens to generate
       :return: An iterable of inference-output objects
       """

        if stop is None:
            stop = []
        for model_response in self.model(
                string,
                stream=True,
                seed=seed,
                max_tokens=max_position_embedding or self.max_position_embedding,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                repeat_penalty=repeat_penalty,
                mirostat_mode=mirostat_mode,
                mirostat_tau=mirostat_tau,
                mirostat_eta=mirostat_eta,
                top_k=top_k,
                top_p=top_p,
                suffix=suffix,
                min_p=min_p,
                temperature=temperature,
                echo=echo,
                stop=stop,
                typical_p=typical_p,
                logprobs=logprobs
        ):
            predictions = InferencePredictions(
                **model_response["choices"][0]
            )
            predictions.text = predictions.text.replace("<0x0A>", "\n")
            response = InferenceOutput(
                predictions=predictions,
                created=model_response["created"],
                model=model_response["model"],
                object=model_response["object"],
                id=model_response["id"]
            )
            yield response

    @staticmethod
    def chat_template(
            message: str,
            chat_history: Optional[List[str] | List[List[str]]] = None,
            system_prompt: str = None
    ):
        """
        The chat_template function takes in a message, chat_history and system prompt.
        It then formats the message into a template that can be used to train the model.
        The function returns a string of text formatted as follows:

        :param message: str: Pass in the user's message to be added to the chat history
        :param chat_history: Optional[List[str] | List[List[str]]]: Pass in a list of strings or a list of lists
        :param system_prompt: str: Set the prompt for the system
        :return: prompt string
        """
        if chat_history is None:
            chat_history = []
        do_strip = False
        texts = [
            f'<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n'
        ] if system_prompt is not None else [f'<s>[INST] ']
        for user_input, response in chat_history:
            user_input = user_input.strip() if do_strip else user_input
            do_strip = True
            texts.append(
                f'{user_input} [/INST] {response.strip()} </s><s>[INST] ')
        message = message.strip() if do_strip else message
        texts.append(f'{message} [/INST]')
        return ''.join(texts)

    @staticmethod
    def os_chat_template(
            message: str,
            chat_history: Optional[List[str] | List[List[str]]] = None,
            system_prompt: Optional[str] = None
    ):
        """
        The os_chat_template function takes in a message, chat history, and system prompt.
        It returns a string that is formatted to be used as the input for the OpenSubtitles dataset.
        The format of this string is:

        :param message: str: Pass in the user's message to the assistant
        :param chat_history: Optional[List[str] | List[List[str]]]: Specify the history of the conversation
        :param system_prompt: Optional[str]: Add a system prompt to the chat history
        :return: prompt string
        """
        if chat_history is None:
            chat_history = []
        system = f"<|system|>\n{system_prompt}</s>\n" if system_prompt is not None else ""
        ua = ""
        for user_input, response in chat_history:
            ua += f"<|user|>\n{user_input}</s>\n<|assistant|>\n{response}</s>\n"
        return system + ua + f"<|user|>\n{message}</s>\n<|assistant|>\n"

    def get_chat_template(self, template_name: Literal["Llama2", "OpenChat"] = "Llama2"):
        if template_name == "Llama2":
            return self.chat_template
        elif template_name == "OpenChat":
            return self.os_chat_template
        else:
            raise ValueError("UnKnown Chat Template requested")
