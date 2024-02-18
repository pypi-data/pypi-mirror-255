from typing import List, Literal, Optional, Union, Any,Dict
from pydantic import BaseModel, Field
import time
import os
import pathlib
import json
import numpy as np
from loguru import logger
try:
    from .utils import generate_stream_chatglm3, process_response
except Exception:
    pass
class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "owner"
    root: Optional[str] = None
    parent: Optional[str] = None
    path: Optional[str] = None
    permission: Optional[list] = None
    task: Optional[str] = ""


class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelCard] = []


class FunctionCallResponse(BaseModel):
    name: Optional[str] = None
    arguments: Optional[str] = None


class MessageRequest(BaseModel):
    messages: List[str]
    stream: Optional[bool] = False

class EmbedingResponse(BaseModel):
    len: Optional[int]
    id: str = "embeding_zh"
    data: Any
    used: float


class ModelCallRequest(BaseModel):
    id: str
    messages: List[str]
    stream: Optional[bool]
    

class ModelCallResponse(BaseModel):
    id: str
    data: Union[List[int],List[str], List[dict], List[List[dict]], dict]
    used: float
    error: Optional[str]



class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "function"]
    content: str = None
    name: Optional[str] = None
    function_call: Optional[FunctionCallResponse] = None


class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system"]] = None
    content: Optional[str] = None
    function_call: Optional[FunctionCallResponse] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.8
    top_p: Optional[float] = 0.8
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    functions: Optional[Union[dict, List[dict]]] = None
    # Additional parameters
    repetition_penalty: Optional[float] = 1.1


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length", "function_call"]


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length", "function_call"]]


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens: Optional[int] = 0

class MachineInfo(BaseModel):
    gpu: int = 0
    memory_use: Optional[float]
    gpu_usage: Optional[List[Dict]]
    loaded_models: Optional[ModelList]

class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    usage: Optional[UsageInfo] = None

class ClearRequest(BaseModel):
    ids: List[str]

async def predict(model, tokenizer, model_id: str, params: dict):
    

    choice_data = ChatCompletionResponseStreamChoice(
        index=0,
        delta=DeltaMessage(role="assistant"),
        finish_reason=None
    )
    chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
    
    yield "{}".format(chunk.json(exclude_unset=True))

    previous_text = ""
    for new_response in generate_stream_chatglm3(model, tokenizer, params):
        decoded_unicode = new_response["text"]
        delta_text = decoded_unicode[len(previous_text):]
        previous_text = decoded_unicode

        finish_reason = new_response["finish_reason"]
        if len(delta_text) == 0 and finish_reason != "function_call":
            continue

        function_call = None
        if finish_reason == "function_call":
            try:
                function_call = process_response(decoded_unicode, use_tool=True)
            except:
                logger.warning("Failed to parse tool call, maybe the response is not a tool call or have been answered.")

        if isinstance(function_call, dict):
            function_call = FunctionCallResponse(**function_call)

        delta = DeltaMessage(
            content=delta_text,
            role="assistant",
            function_call=function_call if isinstance(function_call, FunctionCallResponse) else None,
        )

        choice_data = ChatCompletionResponseStreamChoice(
            index=0,
            delta=delta,
            finish_reason=finish_reason
        )
        chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
        yield "{}".format(chunk.json(exclude_unset=True))

    choice_data = ChatCompletionResponseStreamChoice(
        index=0,
        delta=DeltaMessage(),
        finish_reason="stop"
    )
    chunk = ChatCompletionResponse(model=model_id, choices=[choice_data], object="chat.completion.chunk")
    yield "{}".format(chunk.json(exclude_unset=True))
    yield '[DONE]'





def ls_all_can_loaed_models():
    models = []
    # model_card = ModelCard(id="chatglm3-6b")
    e = pathlib.Path("~/.cache/").expanduser()
    for n in  os.listdir(e):
        if n.endswith("/"):
            n = n[:-1]
        repo =  e / n / "config.json"
        if repo.exists():
            task = ""
            with open(str(repo)) as fp:
                ee = json.loads(fp.read())
                if "architectures" in ee:
                    ars = ee["architectures"]
                    if len(ars) > 0:
                        task = ars[0]
                else:
                    if (e / n / "configuration.json").exists():
                        with open(str((e / n / "configuration.json"))) as fp:
                            ee = json.loads(fp.read())
                            if "task" in ee:
                                task = ee["task"]
    
            models.append(ModelCard(id=n, path=str(e/n), task=task))
        
    for n in os.listdir( e / "THUDM/" ):
        if n.endswith("/"):
            n = n[:-1]
        repo =  e / "THUDM"/ n / "config.json"
        if repo.exists():
            models.append(ModelCard(id=n, path=str(e/"THUDM"/n) ,task="llm" ))
    return ModelList(data=models)

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    