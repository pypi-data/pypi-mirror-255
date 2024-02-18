import pathlib
# from .llm import ChatGLMLLM,Vicuna13B
# from .models.qwen import QwenLLM

from .embeding import ChatGLMEmbeding as Embeddings
from .models.chatglm import ChatGLMLLM
from .hf_server.llm_agent import dispatch_tool, get_tools, register_tool
from .models.normal import SmallModel
from .models.hf import HF
# from .extention.cluster_and_smi import papers as QueryTexts
from .chains import KnowdageQA,QACallbacks, SQLiteChain
# from .models.baichuan import Baichuan2LLM

# _EMBEDDING_PATH = pathlib.Path.home() / ".cache" / "chatglm-embedding"

# if not _EMBEDDING_PATH.exists():
#     print("------ start founding embedding  ------:", _EMBEDDING_PATH)
#     import os
#     # unzip emb.zip to _EMBEDDING_PATH
#     import zipfile
    
#     os.makedirs(str(pathlib.Path.home() / ".cache"),exist_ok=True)
    
#     with zipfile.ZipFile(str(pathlib.Path(__file__).parent /"Res"/ "emb.zip"), 'r') as zip_ref:
#         zip_ref.extractall(str(_EMBEDDING_PATH))
#         print("------ init ---- embedding unziped ------:", _EMBEDDING_PATH)
