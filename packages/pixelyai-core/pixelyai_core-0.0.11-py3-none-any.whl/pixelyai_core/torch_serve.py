from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from EasyDel import PytorchServerConfig
from pixelyai_core import PixelyAIServeTorch
from absl.app import flags, run

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "pretrained_model_name_or_path",
    "LucidBrains/Pixely1B",
    help="huggingface repo_id for model for example pretrained_model_name_or_path"
)


def main(argv):
    pretrained_model_name_or_path = FLAGS.pretrained_model_name_or_path
    serve_config = PytorchServerConfig(
        max_length=2048,
        max_new_tokens=1024,
        max_gpu_perc_to_use=0.95
    )
    server = PixelyAIServeTorch(
        serve_config
    )
    load_kwargs = server.get_model_load_kwargs()
    config = AutoConfig.from_pretrained(
        pretrained_model_name_or_path
    )
    model = AutoModelForCausalLM.from_pretrained(
        pretrained_model_name_or_path,
        config=config,
        **load_kwargs
    )
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path
    )

    server.model = model
    server.tokenizer = tokenizer
    server.create_gradio_pixely_ai().launch(share=True)


if __name__ == "__main__":
    run(main)
