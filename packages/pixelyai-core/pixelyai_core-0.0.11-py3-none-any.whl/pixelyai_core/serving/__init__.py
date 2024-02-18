try:
    from .jax_serve import PixelyAIServeJax
except ModuleNotFoundError:
    print("\033[1;32mCouldn't import JAXServe   [IGNORE THIS IF YOU ARE NOT ON AI SIDE]\033[1;0m")

try:
    from .torch_serve import PixelyAIServeTorch
except ModuleNotFoundError:
    print("\033[1;32mCouldn't import TorchServe [IGNORE THIS IF YOU ARE NOT ON AI SIDE]\033[1;0m")

try:
    from .ggml_serve import PixelyAIServeGGML
except ModuleNotFoundError:
    print("\033[1;32mCouldn't import GGMLServe  [IGNORE THIS IF YOU ARE NOT ON AI SIDE]\033[1;0m")
