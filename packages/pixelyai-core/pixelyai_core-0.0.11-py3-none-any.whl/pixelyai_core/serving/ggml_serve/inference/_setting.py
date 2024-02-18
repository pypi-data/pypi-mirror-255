from huggingface_hub import hf_hub_download
from typing import Literal, List

AVAILABLE_FORMATS = [
    "Q2_K",
    "Q3_K_S",
    "Q3_K_M",
    "Q3_K_L",
    "Q4_K_S",
    "Q4_K_M",
    "Q5_K_S",
    "Q5_K_M",
    "Q6_K"
]

PROMPTING_STYLES: List[str] = [
    "Llama2",
    "OpenChat"
]


def prepare_model_to_load(
        model_name: str,
        quantize_format: str,
        provider: str = "erfanzar",
):
    """
    The prepare_model_to_load function is used to prepare the model name and format for loading.

    :param model_name: str: Specify the model name
    :param quantize_format: str: Specify the format of the model
    :param provider: str: Specify the provider of the model
    :return:  name and the file path of the quantized model
    """
    file_path = f"{model_name}.{quantize_format}.gguf"
    repo_id = f"{provider}/{model_name}"
    return repo_id, file_path


def download_model_gguf(
        pretrained_model_name_or_path: str | None = None,
        filename: str | None = None,
        quantize_type: str | Literal[
            "Q2_K",
            "Q3_K_S",
            "Q3_K_M",
            "Q3_K_L",
            "Q4_K_S",
            "Q4_K_M",
            "Q5_K_S",
            "Q5_K_M",
            "Q6_K"
        ] = "Q4_K_S",
        model_name: str | Literal["Pixely1B-GGUF", "Pixely7B-GGUF"] | None = None,
        provider: str | Literal["erfanzar", "LucidBrains"] | None = None,
        hf_token: str = None
):
    if pretrained_model_name_or_path is not None and (model_name is None or provider is None):
        provider, model_name = pretrained_model_name_or_path.split("/")
    if filename is None:
        pretrained_model_name_or_path, filename = prepare_model_to_load(
            model_name,
            quantize_type,
            provider
        )

    tkn = {}
    if hf_token is not None or hf_token != "":
        tkn = dict(token=hf_token)
    ref = hf_hub_download(
        repo_id=pretrained_model_name_or_path,
        filename=filename,
        **tkn
    )
    return ref
