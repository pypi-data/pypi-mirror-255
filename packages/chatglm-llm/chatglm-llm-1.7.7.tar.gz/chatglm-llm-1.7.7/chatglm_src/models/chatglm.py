from langchain.llms.base import LLM
from typing import Iterable, List
import re
from typing import List, Dict, Any, Optional, Union
import pathlib
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import langchain
try:
    from langchain.cache import GPTCache
except:
    pass
import gptcache
from gptcache.processor.pre import get_prompt
from gptcache.manager.factory import get_data_manager

import json
import inspect
from loguru import logger
import asyncio
from ..hf_server.llm_agent import register_tool, dispatch_tool, unregister_tool, get_tools
from ..hf_server.models import ChatMessage, ModelList,ModelCard
from ..hf_server.cli_utils import create_chat_completion,ChatMessage, acreate_chat_completion,R
try:
    
    from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
    
    import torch, gc
    DEFAULT_CACHE_MAP_PATH = str(pathlib.Path.home() / ".cache" / "local_qa_cache_map")
    i = 0

    def init_gptcache_map(cache_obj: gptcache.Cache):
        global i
        cache_path = f'{DEFAULT_CACHE_MAP_PATH}_{i}.txt'
        cache_obj.init(
            pre_embedding_func=get_prompt,
            data_manager=get_data_manager(data_path=cache_path),
        )
        i += 1
    
    langchain.llm_cache = GPTCache(init_gptcache_map)
    # print(colored("init gptcache", "green"))
except Exception as e:
    # raise e
    print("use remote ignore this / load transformers failed, please install transformers and accelerate first and torch.")

def is_async_method(method):
    return inspect.iscoroutinefunction(method)

def load_model_on_gpus_old(checkpoint_path, num_gpus: int = 2,device_map = None, **kwargs):
    if num_gpus < 2 and device_map is None:
        model = AutoModel.from_pretrained(checkpoint_path, trust_remote_code=True, **kwargs).half().cuda()
    else:
        from accelerate import dispatch_model
        model = AutoModel.from_pretrained(checkpoint_path, trust_remote_code=True, **kwargs).half()
        if device_map is None:
            device_map = auto_configure_device_map(num_gpus)
        model = dispatch_model(model, device_map=device_map)

    return model
def auto_configure_device_map(num_gpus: int) -> Dict[str, int]:
    # transformer.word_embeddings 占用1层
    # transformer.final_layernorm 和 lm_head 占用1层
    # transformer.layers 占用 28 层
    # 总共30层分配到num_gpus张卡上
    num_trans_layers = 28
    per_gpu_layers = 30 / num_gpus

    # bugfix: 在linux中调用torch.embedding传入的weight,input不在同一device上,导致RuntimeError
    # windows下 model.device 会被设置成 transformer.word_embeddings.device
    # linux下 model.device 会被设置成 lm_head.device
    # 在调用chat或者stream_chat时,input_ids会被放到model.device上
    # 如果transformer.word_embeddings.device和model.device不同,则会导致RuntimeError
    # 因此这里将transformer.word_embeddings,transformer.final_layernorm,lm_head都放到第一张卡上
    device_map = {'transformer.word_embeddings': 0,
                  'transformer.final_layernorm': 0, 'lm_head': 0}

    used = 2
    gpu_target = 0
    for i in range(num_trans_layers):
        if used >= per_gpu_layers:
            gpu_target += 1
            used = 0
        assert gpu_target < num_gpus
        device_map[f'transformer.layers.{i}'] = gpu_target
        used += 1

    return device_map

def enforce_stop_tokens(text: str, stop: List[str]) -> str:
    """Cut off the text as soon as any stop words occur."""
    return re.split("|".join(stop), text)[0]


def auto_gc():
    if torch.cuda.is_available():
        # for all cuda device:
        for i in range(0,torch.cuda.device_count()):
            CUDA_DEVICE = f"cuda:{i}"
            with torch.cuda.device(CUDA_DEVICE):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
    else:
        gc.collect()

class ChatGLMLLM(LLM):
    """
            Load a model from local or remote
        if want to use stream mode:
            'streaming=True'
        if want to use langchain's Callback:
            examples: 'callbacks=[StreamingStdOutCallbackHandler(), AsyncWebsocketHandler()]'

        if want use cpu: # default will try to use gpu
            'cpu=True'
        
        if want to use remote's model:
            'remote_host="xx.xxx.xx.xx"'  , if set this , will auto call by ws://xx.xxx.xxx.xx:15000"
            optional:
                remote_callback: a callback function, will call when receive a new token like  'callback(new_token, history, response)'
                if not set, will print to stdout

    """
    id: str = "chatglm3-6b-32k"
    max_tokens: int = 10000
    temperature: float = 0.01
    top_p = 0.9
    history :List[ChatMessage] = []
    history_id = "default"
    tokenizer: Any = None
    model: Any = None
    history_len: int = 10
    model: Any = None
    tokenizer: Any = None
    model_path: str = pathlib.Path.home() / ".cache" / "chatglm"
    cpu: bool = False
    streaming: bool = False
    system:str = "You are ChatGLM3, a helpful assistant. Follow the user's instructions carefully. Respond using markdown."
    verbose: bool = False
    callbacks :Any  = [StreamingStdOutCallbackHandler()]
    remote_host: Any = None
    functions: Optional[Dict]
    cache:Optional[bool] = True

    def set_history(self, hist:List[str]):
        self.history = hist
    
    def copy_llm(self):
        ee =  ChatGLMLLM(
            remote_host= self.remote_host
        )
        return ee

    def load_tools(self, name):
        fus = get_tools()
        if name in fus:
            if self.functions is None:
                self.functions = {
                    name: fus[name]
                }
            else:
                self.functions[name]= fus[name]
        
    

    def clean(self):
        uri = f"http://{self.remote_host}:15001/v1/chat/clean"
        return next(R(uri=uri, object=ModelList(data=[ModelCard(id=self.id)])))

    @classmethod
    def get_all_tools(cls):
        return get_tools()
    
    

    def unload_tools(self):
        self.functions = None

    @classmethod
    def clear_cache(cls):
        langchain.llm_cache.clear()

    @property
    def _llm_type(self) -> str:
        return "ChatGLM"
    
    def add_hist(self,prompt=None,content=None, role="user", name=None):
        if prompt:
            self.history.append(ChatMessage(role="user", content=prompt))
        
        if content:
            # print(role,content,name)
            # print(type(role),type(content), type(name))
            # ChatMessage(role=role, content=content, name=name)
            self.history.append(ChatMessage(role=role, content=content, name=name))

    async def _acall(self, prompt: str, stop: List[str] = None):
        
        if self.remote_host is not None :
            uri = f"http://{self.remote_host}:15001/v1/chat/completions"
            result = ''
            if self.functions is None or len(self.functions) == 0:
                msgs = [
                    ChatMessage(role="system", content=self.system)
                ]
            else:
                msgs = [
                    # ChatMessage(role="system", content="Answer the following questions as best as you can. You have access to the following tools:", )
                ]
            for h in self.history:
                if isinstance(h, ChatMessage):
                    msgs.append(h)
                else:
                    role,hist_prompt,response_msg = h
                    if role == "user":
                        msgs.append(ChatMessage(role="user", content=hist_prompt.strip()))
                        msgs.append(ChatMessage(role="assistant", content=response_msg.strip()))
                
            msgs.append(ChatMessage(role="user", content=prompt))
            for call in self.callbacks:
                if is_async_method(call.on_llm_start):
                    await call.on_llm_start(prompt, None, verbose=self.verbose)
            result = ""
            ss = ""
            role = ""
            name = ""
            function_call = None
            async for r in acreate_chat_completion(uri, msgs, temperature=self.temperature, max_tokens=self.max_tokens, top_p=self.top_p, functions=self.functions, model=self.id):
                for choice in r.choices:
                    
                    if choice.finish_reason == "stop":
                        self.add_hist(prompt=prompt, content=result, role=role)
                    elif choice.finish_reason == "function_call":
                        function_call = choice.delta.function_call
                        try:
                            function_args = json.loads(function_call.arguments)
                            function_res = await asyncio.get_event_loop().run_in_executor(None,dispatch_tool,function_call.name, function_args)
                            logger.info(f"Tool Call Response: {ss}")
                            # self.add_hist(prompt=prompt)
                            self.add_hist(content=function_res, role="function", name=function_call.name)
                        except Exception as e:
                            logger.error(f"[chatglm +192]call func err:{e}")
                        

                        
                    
                    else:
                        if choice.delta.content is not None:
                            msg = {}
                            role = choice.delta.role
                            # yield choice.delta
                            msg["new"] = choice.delta.content
                            ss += choice.delta.content
                            msg["response"] = ss
                            msg["verbose"] = self.verbose
                            result = ss
                            for call in self.callbacks:
                                if is_async_method(call.on_llm_new_token):
                                    data = {"response": ss, "history": self.history,"query": prompt}
                                    await call.on_llm_new_token(choice.delta.content, **data)
                    
                    
                        
                    
            if len(self.history) > 0 and isinstance(self.history[-1], ChatMessage):
                cl :ChatMessage = self.history[-1]
                if cl.role == "function":
                    msgs.append(cl)
                    # ss = ""
                    async for r in acreate_chat_completion(uri, msgs, temperature=self.temperature, max_tokens=self.max_tokens, top_p=self.top_p, functions=self.functions, model=self.id):
                        for choice in r.choices:
                            
                            if choice.finish_reason == "stop":
                                self.add_hist(prompt=prompt, content=result, role=role)
                            elif choice.finish_reason == "function_call":
                                function_call = choice.delta.function_call
                                try:
                                    function_args = json.loads(function_call.arguments)
                                    function_res = await asyncio.get_event_loop().run_in_executor(None,dispatch_tool,function_call.name, function_args)
                                    logger.info(f"Tool Call Response: {ss}")
                                    # self.add_hist(prompt=prompt)
                                    self.add_hist(content=function_res, role="function", name=function_call.name)
                                except Exception as e:
                                    logger.error(f"[chatglm +192]call func err:{e}")
                                

                                
                            
                            else:
                                if choice.delta.content is not None:
                                    msg = {}
                                    role = choice.delta.role
                                    # yield choice.delta
                                    msg["new"] = choice.delta.content
                                    ss += choice.delta.content
                                    msg["response"] = ss
                                    msg["verbose"] = self.verbose
                                    result = ss
                                    for call in self.callbacks:
                                        if is_async_method(call.on_llm_new_token):
                                            data = {"response": ss, "history": self.history,"query": prompt}
                                            await call.on_llm_new_token(choice.delta.content,  **data)
                            
                    

            # self.history = self.history+[[role, prompt, result]]
            for call in self.callbacks:
                if is_async_method(call.on_llm_start):
                    await call.on_llm_end(result, verbose=self.verbose)
            return result
        else:
            
            raise Exception(f"{self.remote_host} is not Set !!!!")

    def stream(self,prompt: str, stop: List[str] = None):
        uri = f"http://{self.remote_host}:15001/v1/chat/completions"
        result = ''
        if self.functions is None or len(self.functions) == 0:
            msgs = [
                ChatMessage(role="system", content=self.system)
            ]
        else:
            msgs = [
                # ChatMessage(role="system", content="Answer the following questions as best as you can. You have access to the following tools:", )
            ]
        for h in self.history:
            if isinstance(h, ChatMessage):
                msgs.append(h)
            else:
                role,hist_prompt,response_msg = h
                if role == "user":
                    msgs.append(ChatMessage(role="user", content=hist_prompt.strip()))
                    msgs.append(ChatMessage(role="assistant", content=response_msg.strip()))
        
        msgs.append(ChatMessage(role="user", content=prompt))

        gen = create_chat_completion(uri, msgs, temperature=self.temperature, max_tokens=self.max_tokens, top_p=self.top_p, functions=self.functions, model=self.id)
        ss = ""
        role = ""
        for r in gen:
            for choice in r.choices:
                if choice.finish_reason == "stop":
                    self.add_hist(prompt=prompt, content=result, role=role)
                    break
                elif choice.finish_reason == "function_call":
                    function_call = choice.delta.function_call
                    try:
                        function_args = json.loads(function_call.arguments)
                        function_res = dispatch_tool(function_call.name, function_args)
                        logger.info(f"Tool Call Response: {ss}")
                        self.add_hist(prompt=prompt)
                        self.add_hist(content=function_res, role="function", name=function_call.name)
                    except Exception as e:
                        logger.error(f"[chatglm +192]call func err:{e}")
                    break

                if choice.delta.content is not None:
                    msg = {}
                    # yield choice.delta
                    role = choice.delta.role
                    msg["new"] = choice.delta.content
                    ss += choice.delta.content
                    msg["response"] = ss
                    msg["verbose"] = self.verbose
                    result = ss
                    yield msg

        if len(self.history) > 0 and isinstance(self.history[-1], ChatMessage):
            cl :ChatMessage = self.history[-1]
            if cl.role == "function":
                # ss = ""
                msgs.append(cl)
                for r in create_chat_completion(uri, msgs, temperature=self.temperature, max_tokens=self.max_tokens, top_p=self.top_p, functions=self.functions, model=self.id):
                    for choice in r.choices:
                        if choice.finish_reason == "stop":
                            self.add_hist(content=result, role=role)
                            break
                        elif choice.finish_reason == "function_call":
                            function_call = choice.delta.function_call
                            try:
                                function_args = json.loads(function_call.arguments)
                                function_res = dispatch_tool(function_call.name, function_args)
                                logger.info(f"Tool Call Response: {ss}")
                                self.add_hist(prompt=prompt)
                                self.add_hist(content=function_res, role=choice.delta.role, name=function_call.name)
                            except Exception as e:
                                logger.error(f"[chatglm +192]call func err:{e}")
                            break

                        if choice.delta.content is not None:
                            msg = {}
                            # yield choice.delta
                            role = choice.delta.role
                            msg["new"] = choice.delta.content
                            ss += choice.delta.content
                            msg["response"] = ss
                            msg["verbose"] = self.verbose
                            result = ss
                            yield msg
        
        # self.history = self.history+[[prompt, result]]


    
    def _call(self, prompt: str, stop: Optional[List[str]] = None,run_manager: Optional[Any] = None) -> str:
        
        if self.remote_host is not None :
            uri = f"http://{self.remote_host}:15001/v1/chat/completions"
            result = ''
            if self.functions is None or len(self.functions) == 0:
                msgs = [
                    ChatMessage(role="system", content=self.system)
                ]
            else:
                msgs = [
                    # ChatMessage(role="system", content="Answer the following questions as best as you can. You have access to the following tools:", )
                ]

            for h in self.history:
                if isinstance(h, ChatMessage):
                    msgs.append(h)
                else:
                    role,hist_prompt,response_msg = h
                    if role == "user":
                        msgs.append(ChatMessage(role="user", content=hist_prompt.strip()))
                        msgs.append(ChatMessage(role="assistant", content=response_msg.strip()))
            
            msgs.append(ChatMessage(role="user", content=prompt))
            logger.info("start 1")
            gen = create_chat_completion(uri, msgs, temperature=self.temperature, max_tokens=self.max_tokens, top_p=self.top_p, functions=self.functions, model=self.id)
            ss = ""
            for callback in self.callbacks:
                if is_async_method(callback.on_llm_start):continue
                callback.on_llm_start(
                    None,
                    prompt,
                    run_id=0,
                    verbose=self.verbose
                )
            
            role = ""
            for r in gen:
                
                for choice in r.choices:
                    if choice.finish_reason == "stop":
                        self.add_hist(prompt=prompt, content=result, role=role)
                        break
                    elif choice.finish_reason == "function_call":
                        function_call = choice.delta.function_call
                        try:
                            function_args = json.loads(function_call.arguments)
                            function_res = dispatch_tool(function_call.name, function_args)
                            logger.info(f"Tool Call Response: {ss}")
                            self.add_hist(prompt=prompt)
                            self.add_hist(content=function_res, role="function", name=function_call.name)
                        except Exception as e:
                            logger.error(f"[chatglm +192]call func err:{e}")
                        break

                    if choice.delta.content is not None:
                        msg = {}
                        role = choice.delta.role
                        # yield choice.delta
                        msg["new"] = choice.delta.content
                        ss += choice.delta.content
                        new_token = choice.delta.content
                        msg["response"] = ss
                        msg["verbose"] = self.verbose
                        result = ss
                        for callback in self.callbacks:
                            if is_async_method(callback.on_llm_start):continue
                            callback.on_llm_new_token(
                                new_token,
                                **msg
                            )
                        # yield msg
                    
                    
            if len(self.history) > 0 and isinstance(self.history[-1], ChatMessage):
                cl :ChatMessage = self.history[-1]
                if cl.role == "function":
                    # ss = ""
                    msgs.append(cl)
                    for r in create_chat_completion(uri, msgs, temperature=self.temperature, max_tokens=self.max_tokens, top_p=self.top_p, functions=self.functions, model=self.id):
                        for choice in r.choices:
                            if choice.finish_reason == "stop":
                                self.add_hist(content=result, role=role)
                                break
                            elif choice.finish_reason == "function_call":
                                function_call = choice.delta.function_call
                                try:
                                    function_args = json.loads(function_call.arguments)
                                    function_res = dispatch_tool(function_call.name, function_args)
                                    logger.info(f"Tool Call Response: {ss}")
                                    self.add_hist(prompt=prompt)
                                    self.add_hist(content=function_res, role="function", name=function_call.name)
                                except Exception as e:
                                    logger.error(f"[chatglm +192]call func err:{e}")
                                break

                            if choice.delta.content is not None:
                                msg = {}
                                # yield choice.delta
                                role = choice.delta.role
                                msg["new"] = choice.delta.content
                                ss += choice.delta.content
                                new_token = choice.delta.content
                                msg["response"] = ss
                                msg["verbose"] = self.verbose
                                result = ss
                                for callback in self.callbacks:
                                    if is_async_method(callback.on_llm_start):continue
                                    callback.on_llm_new_token(
                                        new_token,
                                        **msg
                                    )
                                # yield msg  
            
            for callback in self.callbacks:
                if is_async_method(callback.on_llm_start):continue
                callback.on_llm_end(result, verbose=self.verbose)
            # self.history = self.history+[[prompt, result]]
            return result
        else:
            raise Exception(f"{self.remote_host} is not Set !!!!")