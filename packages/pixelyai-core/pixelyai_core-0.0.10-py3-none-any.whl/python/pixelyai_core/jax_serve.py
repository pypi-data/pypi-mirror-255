import os

os.environ["XLA_PYTHON_CLIENT_MEM_FRACTION"] = "0.1"  # don"t use all gpu mem
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # tell XLA to be quiet
from pixelyai_core import PixelyAIServeJax
from EasyDel import JAXServerConfig
from absl.app import flags, run

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "pretrained_model_name_or_path",
    "LucidBrains/Pixely1B",
    help="huggingface repo_id for model for example pretrained_model_name_or_path"
)


def main(argv):
    pretrained_model_name_or_path = FLAGS.pretrained_model_name_or_path
    config = JAXServerConfig(
        max_length=512,
        max_new_tokens=512,
        max_compile_tokens=32,
        pre_compile=False
    )
    server = PixelyAIServeJax.load_from_huggingface_torch(
        pretrained_model_name_or_path=pretrained_model_name_or_path,
        server_config=config
    )
    server.run()


if __name__ == "__main__":
    run(main)
