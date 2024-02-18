from pixelyai_core.serving.ggml_serve import PixelyAIServeGGML
from absl.app import flags, run

FLAGS = flags.FLAGS

flags.DEFINE_string(
    "pretrained_model_name_or_path",
    "LucidBrains/Pixely1B-GGUF",
    help="huggingface repo_id for model for example pretrained_model_name_or_path"
)

flags.DEFINE_string(
    "filename",
    default="Pixely1B-GGUF.Q4_K_S.gguf",
    help="model filename in provided path or repo",
)

flags.DEFINE_bool(
    "share",
    True,
    "Share the gradio application"
)

flags.DEFINE_bool(
    "launch_chat",
    False,
    "Share the gradio Chat application"
)

flags.DEFINE_bool(
    "launch_custom",
    True,
    "Share the gradio PixelyAI application"
)


def main(argv):
    print(
        f"""
        \033[1;36m
        Running Options : 
            Pretrained Model Name Or Path : {FLAGS.pretrained_model_name_or_path}
            File Name                     : {FLAGS.filename}
            Share                         : {FLAGS.share}
            Launch Custom                 : {FLAGS.launch_custom}
            Launch Chat                   : {FLAGS.launch_chat}
        \033[1;0m
        """
    )
    server = PixelyAIServeGGML.from_pretrained(
        pretrained_model_name_or_path=FLAGS.pretrained_model_name_or_path,
        filename=FLAGS.filename
    )
    server.launch(
        launch_chat=FLAGS.launch_chat,
        launch_custom=FLAGS.launch_custom,
        share=FLAGS.share,
        server_name="0.0.0.0"
    )


if __name__ == "__main__":
    run(main)
