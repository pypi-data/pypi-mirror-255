import gradio_client as gc
import json
import gradio as gr
import subprocess
import functools
from typing import Union, List, Tuple
import requests
import transformers

END_OF_MESSAGE_TURN_HUMAN = "<|END_OF_MESSAGE_TURN_HUMAN|>"
END_OF_MESSAGE = "<|END_OF_MESSAGE|>"

FOUND_SYSTEM_MESSAGE = (
    "you will get extra information to use in order to chat with users and answer the questions without"
    " mentioning the extra information if you been wanted to introduce yourself "
    "your Name is PixelyAI you are developed By a team of Researchers at LucidBrain Company Located in "
    "Dubai otherwise you dont have to introduce yourself just answer the question"
)

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, respectful and honest assistant and act as wanted, if you been wanted to introduce yourself "
    "your Name is PixelyAI you are developed By a team of Researchers at LucidBrain Company Located in "
    "Dubai otherwise you dont have to introduce yourself just answer the question"
)

try:
    from gradio.themes.base import Base
    from gradio.themes.utils import colors, fonts, sizes


    class Seafoam(Base):
        def __init__(
                self,
                *,
                primary_hue: Union[colors.Color, str] = colors.emerald,
                secondary_hue: Union[colors.Color, str] = colors.blue,
                neutral_hue: Union[colors.Color, str] = colors.gray,
                spacing_size: Union[sizes.Size, str] = sizes.spacing_md,
                radius_size: Union[sizes.Size, str] = sizes.radius_md,
                text_size: Union[sizes.Size, str] = sizes.text_lg,
                font: Union[fonts.Font, str]
                = (
                        fonts.GoogleFont("Quicksand"),
                        "ui-sans-serif",
                        "sans-serif",
                ),
                font_mono: Union[fonts.Font, str]
                = (
                        fonts.GoogleFont("IBM Plex Mono"),
                        "ui-monospace",
                        "monospace",
                ),
        ):
            super().__init__(
                primary_hue=primary_hue,
                secondary_hue=secondary_hue,
                neutral_hue=neutral_hue,
                spacing_size=spacing_size,
                radius_size=radius_size,
                text_size=text_size,
                font=font,
                font_mono=font_mono,

            )
            super().set(
                body_background_fill="linear-gradient(90deg, *secondary_800, *neutral_900)",
                body_background_fill_dark="linear-gradient(90deg, *secondary_800, *neutral_900)",
                button_primary_background_fill="linear-gradient(90deg, *primary_300, *secondary_400)",
                button_primary_background_fill_hover="linear-gradient(90deg, *primary_200, *secondary_300)",
                button_primary_text_color="white",
                button_primary_background_fill_dark="linear-gradient(90deg, *primary_600, *secondary_800)",
                slider_color="*secondary_300",
                slider_color_dark="*secondary_400",
                block_title_text_weight="600",
                block_border_width="0px",
                block_shadow="*shadow_drop_lg",
                button_shadow="*shadow_drop_lg",
                button_large_padding="4px",
            )


    seafoam = Seafoam()
except ModuleNotFoundError:
    seafoam = None


class BaseClassAgent:
    tokenizer: transformers.PreTrainedTokenizerBase | None = None

    def gradio_app_custom(self):
        raise NotImplementedError("Not Implemented Yet!")

    def process_gradio_custom(
            self,
            prompt: str,
            user_id: str,
            data: str,
            system: str,
            max_new_tokens: int,
            greedy: bool
    ) -> Tuple[str, List[str]]:
        raise NotImplementedError("Not Implemented Yet!")

    def process(self, *args, **kwargs) -> Tuple[str, List[str]]:
        raise NotImplementedError("Not Implemented Yet!")

    def status(self) -> str:
        raise NotImplementedError("Not Implemented Yet!")

    def count_tokens(self, prompt, user_id, data, system, *_) -> int:
        if self.tokenizer is not None:
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
            return len(self.tokenizer.encode(string))
        return -1

    @staticmethod
    def get_available_backends(url="https://api.pixelyai.com/api/gradio/"):
        return get_available_backends(url=url)

    @staticmethod
    def set_available_backend(url_backend: str, url="https://api.pixelyai.com/api/gradio/", method="put"):
        set_available_backend(url_backend=url_backend, url=url, method=method)

    def launch(self,
               share_chat: bool = False,
               share_custom: bool = True
               ):
        share_kwargs = {}
        if share_chat:
            gradio_in = self.create_gradio_pixely_ai()
            gradio_in.launch(share=True)
            share_kwargs["chat"] = gradio_in.share_url
        if share_custom:
            gradio_in = self.gradio_app_custom()
            gradio_in.launch(share=True)
            share_kwargs["custom"] = gradio_in.share_url
        return share_kwargs

    def create_gradio_pixely_ai(self):
        with gr.Blocks(theme=seafoam) as block:
            gr.Markdown("# <h1> <center>Powered by [EasyDeL](https://github.com/erfanzar/EasyDel) </center> </h1>")

            with gr.Row():
                with gr.Column():
                    prompt = gr.Textbox(
                        show_label=True,
                        placeholder="Message Box",
                        container=True,
                        label="Message Box"
                    )
                    user_id = gr.Textbox(
                        show_label=True,
                        placeholder="UserId",
                        container=True,
                        value="",
                        label="UserId"
                    )
                    data = gr.Textbox(
                        show_label=True,
                        placeholder="Data",
                        container=True,
                        value="",
                        label="Data"
                    )
                    system = gr.Textbox(
                        show_label=True,
                        placeholder="System",
                        container=True,
                        value="",
                        label="System"
                    )
                    response = gr.TextArea(
                        show_label=True,
                        placeholder="Response",
                        container=True,
                        label="Response"
                    )
                    submit = gr.Button(variant="primary")
            with gr.Row():
                with gr.Accordion("Advanced Options", open=False):
                    max_new_tokens = gr.Slider(
                        value=2048,
                        maximum=10000,
                        minimum=1,
                        label="Max New Tokens",
                        step=1
                    )

                    greedy = gr.Checkbox(value=False, label="Greedy Search")
                    status = gr.Button(value="Status")
                    token_counter = gr.Button(value="Token Counter")
                    token_counter_prompt = gr.Button(value="Token Prompt Counter")
                    display = gr.TextArea(
                        show_label=True,
                        placeholder="Display",
                        container=True,
                        label="Display"
                    )

            inputs = [
                prompt,
                user_id,
                data,
                system,
                max_new_tokens,
                greedy
            ]
            _ = prompt.submit(
                fn=self.process_gradio_custom,
                inputs=inputs,
                outputs=[prompt, response]
            )
            _ = submit.click(
                fn=self.process_gradio_custom,
                inputs=inputs,
                outputs=[prompt, response]
            )
            _ = token_counter.click(
                fn=lambda p: len(self.tokenizer.encode(p)) if self.tokenizer is not None else -1,
                inputs=[prompt],
                outputs=[display]
            )
            _ = status.click(
                fn=lambda: str(self.status()), outputs=[display]
            )
            _ = token_counter_prompt.click(
                fn=self.count_tokens,
                inputs=inputs,
                outputs=display
            )
            block.queue()
        return block

    @staticmethod
    def format_chat(history: List[List[str]], prompt: str, system: str = None) -> str:
        return prompt_model(message=prompt, system_prompt=system, chat_history=history)

    @staticmethod
    def prompt_model(message: str, chat_history, system_prompt: str):
        return prompt_model(message=message, chat_history=chat_history, system_prompt=system_prompt)

    def prompt_agent(self, *args, **kwargs):
        return prompt_model(*args, **kwargs)

    def run(
            self,
            url="https://api.pixelyai.com/api/gradio/",
            share: bool = False,
            extra_options: dict | None = None
    ):

        extra_options = extra_options if extra_options is not None else {}
        app = self.create_gradio_pixely_ai()
        app.launch(share=share, **extra_options)
        set_available_backend(app.share_url, url=url, method="put")

        return app.share_url


def format_chat_for_ai_client(user: List[str], assistance: List[str]):
    history = ""
    for c1, c2 in zip(user, assistance):
        history += f"{c1}{END_OF_MESSAGE_TURN_HUMAN}{c2}{END_OF_MESSAGE}"
    return history


def in_check(
        response: str,
        question: str,
        non_legal_point: List[str] = None
):
    if non_legal_point is None:
        non_legal_point = [
            "the answer to the question is `no`",
            "The context does not provide",
            "the context provided does not provide any information that would allow "
            "you to determine the answer",
            "it is not possible to answer the question",
            "The given context does not provide any information about",
            "I can only respond with a `no` based on the provided context",
            "I can only respond with a no`",
            "Answer: No,",
            "it is not related to the provided contex",
            "is not mentioned anywhere in the provided context",
            "my answer would be `no`",
            "the context does not mention anything",
            "not related to the context provided",
            "not related to the provided contex",
            "i cannot answer your question",
            "The context mentions nothing about",
            "I cannot provide an answer to the question",
            "I cannot provide an answer",
            "not mentioned in the provided context",
            "not mentioned in the context",
            "Please go ahead and ask your question",
            "context provided does not mention"
        ]
    found = True
    _s = (f"'{question}' is not provided", f"{question} is not provided", f"The answer to '{question}?' is NO",
          f"The answer to '{question}' is NO")
    for s in _s:
        non_legal_point.append(s)
    for point in non_legal_point:
        if point.lower() in response.lower():
            found = False
    return found


def prompt_model(message: str, chat_history, system_prompt: str) -> str:
    texts = [f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n"]
    do_strip = False
    for user_input, response in chat_history:
        user_input = user_input.strip() if do_strip else user_input
        do_strip = True
        texts.append(f"{user_input} [/INST] {response.strip()} </s><s>[INST] ")
    message = message.strip() if do_strip else message
    texts.append(f"{message} [/INST]")
    return "".join(texts)


def get_available_backends(url="https://api.pixelyai.com/api/gradio/"):
    result = subprocess.run(
        ["curl", "-X", "GET", f"{url}", "-H", "accept: application/json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    ).stdout.decode("utf-8")
    return json.loads(result)


def set_available_backend(url_backend: str, url="https://api.pixelyai.com/api/gradio/", method="put"):
    assert method in ["put", "delete"]
    result = subprocess.run(
        ["curl", "-X", "POST", f"{url}", "-H", "accept: application/json", "-H", "Content-Type: application/json",
         "-d", "{"
               f"'url':'{url_backend}',"
               f"'method':'{method}'"
               '}'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    ).stdout.decode('utf-8')
    return json.loads(result)


def delete_all_of_the_backends(url="https://api.pixelyai.com/api/gradio/"):
    for I_A in get_available_backends(url=url)['available_backends']:
        i = I_A['url']
        _ = set_available_backend(i, method='delete')
        print(f"{i} Deleted Successfully")


def remove_deprecated_backends(url: str = "https://api.pixelyai.com/api/gradio/"):
    for url_backend in get_available_backends(url=url)['available_backends']:
        try:
            client = gc.Client(url_backend['url'], verbose=False)
        except (ValueError, requests.exceptions.HTTPError):
            print(f"URL : {url_backend['url']} is deprecated [REMOVING]")
            set_available_backend(url_backend=url_backend["url"], method="delete", url=url)
    return get_available_backends(url=url)


class PixelClient:
    def __init__(
            self,
            url_client: str = None,
            instruct_check: str = None,
            system_prompt: str = None,
            api_point: str = "https://api.pixelyai.com/api/gradio/"
    ):
        if url_client is None:
            url_client = get_available_backends(url=api_point)["available_backends"][-1]["url"]
        self.client = gc.Client(
            url_client,
            verbose=False,
            max_workers=128
        )

        self.instruct_check = (
            "Use the following pieces of context to answer the question at the end."
            " don't try to make up answers and just return answer nothing more."
            "\nContexts:\n{context}\nQuestion:\n{question}"
        ) if instruct_check is None else instruct_check
        self.DEFAULT_SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT if system_prompt is None else system_prompt

    def __call__(
            self,
            prompt: str,
            conversation_history: List[dict] = None,
            contexts: List[str] = None,
            debug: bool = False,
            max_new_tokens: int = 1024
    ):
        """

        :param prompt:string
        :param conversation_history:[{"user": ..., "assistance": ..., ...}]
        :param contexts: List of Contexts [str]
        :param debug: Bool
        :param max_new_tokens: int
        :return:
        """
        history = format_chat_for_ai_client(
            user=[f["user"] for f in conversation_history],
            assistance=[f["assistance"] for f in conversation_history]
        )

        is_found, generated_response = False, None
        if contexts is not None:
            gprs_func = functools.partial(
                self.client.predict,
                self.instruct_check.format(question=prompt, context="\n".join(context for context in contexts)),
                # str in "Message Box" Textbox component
                "",
                history,
                "you will be given a context and a question try to answer as good as possible and only use context"
                "provided information",
                max_new_tokens,
                False,
            )

            generated_response = gprs_func(fn_index=0)[-1]
        else:
            gr_func = functools.partial(
                self.client.predict,
                prompt,
                "",
                history,
                self.DEFAULT_SYSTEM_PROMPT,
                max_new_tokens,
                False,
            )
            generated_response = gr_func(fn_index=0)[-1]

            is_found = False
        return generated_response, is_found
