import uvicorn
from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from langchain.embeddings import HuggingFaceEmbeddings
import os
import pathlib
import asyncio

import time
import json
from contextlib import asynccontextmanager
from concurrent.futures.thread import ThreadPoolExecutor
from chatglm_src.models.hf import HF
from chatglm_src.hf_server.models import ModelList, ModelCard, EmbedingResponse, MessageRequest, ls_all_can_loaed_models
from chatglm_src.hf_server.models import ModelCallRequest, ModelCallResponse
from chatglm_src.hf_server.models import NumpyEncoder
from chatglm_src.hf_server.models import ChatCompletionRequest,ChatCompletionResponseChoice,ChatCompletionResponse,ChatMessage
from chatglm_src.hf_server.utils import process_response, generate_chatglm3
from chatglm_src.hf_server.models import predict, UsageInfo, FunctionCallResponse
from chatglm_src.hf_server.models import MachineInfo,ClearRequest
from chatglm_src.extention.git import Git
try:
    import torch
    @asynccontextmanager
    async def lifespan(app: FastAPI):  # collects GPU memory
        yield
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    app = FastAPI(lifespan=lifespan)
except ImportError:
    app = FastAPI()


try:
    TEXT_EMB_PATH = pathlib.Path("~").expanduser() / ".cache"/ "bge-large-zh"
    # TEXT_EMB_EN_PATH = pathlib.Path("~").expanduser() / ".cache"/ "bge-large-en"
    
    embeding_zh = HuggingFaceEmbeddings(model_name=str(TEXT_EMB_PATH))
    # embeding_en = HuggingFaceEmbeddings(model_name=str(TEXT_EMB_EN_PATH))
    embeding_en = None
except  Exception as e:
    print("Load Embedings Failed!!",e)
ThreadingExecutor = ThreadPoolExecutor(5)
LoadedModels  = {}

LLMModel = None
LLModelTokenizer = None
LLMModelName = None

def load_llm(model_id) -> bool:
    global LLMModel, LLModelTokenizer
    MODEL_PATH = None
    for m in ls_all_can_loaed_models().data:
        if m.id == model_id:
            MODEL_PATH = m.path
            break
    if MODEL_PATH is not None:
        try:
            from transformers import AutoModel, AutoTokenizer
            from chatglm_src.hf_server.utils import load_model_on_gpus
            logger.info(f"Use GPU:{torch.cuda.device_count()}")
            LLMModel = load_model_on_gpus(MODEL_PATH, num_gpus=torch.cuda.device_count())
            LLModelTokenizer =  AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
            return True
        except Exception as e:
            print(e)
    return False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def loaded_models()-> ModelList:
    global LoadedModels
    res = []
    ss = ls_all_can_loaed_models()
    for i in LoadedModels:
        for s in ss.data:
            if s.id == i:
                res.append(s)
    return ModelList(data=res)


@app.get("/v1/models", response_model=ModelList)
async def list_models():
    return ls_all_can_loaed_models()



@app.post("/v1/models/load", response_model=ModelList)
async def load_model(request: ModelCard):
    global LoadedModels
    if request.id  not in LoadedModels:
        can = False
        for m in ls_all_can_loaed_models().data:
            if m.id == request.id:
                can = True
                break
        if can:
            HF.load_model(request.id)
            LoadedModels.update(HF.mos)
    return loaded_models()

async def call_model(model, docs):
    # global ThreadingExecutor
    loop = asyncio.get_running_loop()
    
    res = await loop.run_in_executor(None, model, docs)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    return res

async def call_stream(id,model,docs) -> ModelCallResponse:
    batch = []
    
    for i,doc in enumerate(docs):
        batch.append(doc)
        if len(batch) % 50 == 0 and len(batch) > 0:
            st = time.time()
            # res = model(batch)
            logger.info(f"batch before {i}:")
            res = await call_model(model, batch)
            et = time.time() - st
            logger.info(f"batch after  {i}:{len(docs)}  ")
            
            try:
                e =  ModelCallResponse(id=id, data=res, used=et)
                # logger.info(f"result:{e}")
                reply = json.dumps(e.dict(exclude_unset=True), cls=NumpyEncoder) 
                yield "{}".format(reply)
                
                batch = []
            except Exception as e:
                print(type(res), type(res[0]),print(res[0]))
                logger.error(e)

    if len(batch) > 0:
        st = time.time()
        # res = model(batch)
        res = await call_model(model, batch)
        et = time.time() - st
        logger.info(f"batch:{len(docs)} : last")
        try:
            e =  ModelCallResponse(id=id, data=res, used=et)
            # logger.info(f"result:{e} | {res}")
            reply = json.dumps(e.dict(exclude_unset=True), cls=NumpyEncoder) 
            yield "{}".format(reply)

        except Exception as e:
            print(type(res), type(res[0]),print(res[0]))
            logger.error(e)


@app.post("/v1/models/call", response_model=ModelCallResponse)
async def call_smalle_models(request: ModelCallRequest):
    global LoadedModels
    if request.id  not in LoadedModels:
        can = False
        for m in ls_all_can_loaed_models().data:
            if m.id == request.id:
                can = True
                break
        if can:
            HF.load_model(request.id)
            LoadedModels.update(HF.mos)
    if request.id in LoadedModels:
        model = LoadedModels[request.id]
        if request.stream:
            logger.info(f"call : {request.id} streams")
            return EventSourceResponse(call_stream(request.id, model, request.messages))
        else:
            logger.info(f"call : {request.id} no streams")
            st = time.time()
            res = model(request.messages)
            rr = json.loads(json.dumps(res, cls=NumpyEncoder))
            return ModelCallResponse(id=request.id,data=rr, used=time.time()-st)
    else:
        return ModelCallResponse(id=request.id,data=[],error="no such model id:"+request.id, used=0.1)



async def embeding_stream(docs) -> EmbedingResponse:
    global LLMModelName, LLMModel, LLModelTokenizer
    batch = []
    for i, doc in enumerate(docs):
        batch.append(doc)
        if len(batch) % 100 == 0 and len(batch) > 0:
            res_batch = []
            st = time.time()
            res_batch = await embeding_zh.aembed_documents(batch)
            et =  time.time() - st
            logger.info(f"batch:{len(docs)} : {i}")
            e =  EmbedingResponse(data=res_batch, len=len(res_batch), used=et)
            reply = json.dumps(e.dict(exclude_unset=True), cls=NumpyEncoder) 
            yield "{}".format(reply)
            batch = []
    
        

    if len(batch) > 0:
        logger.info(f"batch:{len(docs)} : last")
        st = time.time()
        try:
            res_batch = await embeding_zh.aembed_documents(batch)
            et = time.time() - st
            e =  EmbedingResponse(data=res_batch, len=len(res_batch), used=et)
            reply = json.dumps(e.dict(exclude_unset=True), cls=NumpyEncoder) 
            yield "{}".format(reply)
        except RuntimeError:
            LLMModel = None
            LLModelTokenizer = None
            LLMModelName = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        
        
@app.get("/v1/device/info", response_model=MachineInfo)
async def machine_info():
    
    res = [i.split("|")[2].strip() for i in os.popen("nvidia-smi ").read().split("\n") if "Default " in i]
    g = []
    for i in res:
        if "/" in i:
            use, all = i.split("/",1)
            g.append({
                "used": int(use.strip()[:-3]),
                "all":  int(all.strip()[:-3]),
            })
    return MachineInfo(gpu=len(res), gpu_usage=g, loaded_models=loaded_models())

@app.post("/v1/models/clear", response_model=MachineInfo)
async def model_clear(request: ClearRequest):
    global LoadedModels
    for id in request.ids:
        if id in LoadedModels:
            m = LoadedModels[id]
            m.clean()
            del LoadedModels[id]

    res = [i.split("|")[2].strip() for i in os.popen("nvidia-smi ").read().split("\n") if "Default " in i]
    g = []
    for i in res:
        if "/" in i:
            use, all = i.split("/",1)
            g.append({
                "used": int(use.strip()[:-3]),
                "all":  int(all.strip()[:-3]),
            })
    return MachineInfo(gpu=len(res), gpu_usage=g, loaded_models=loaded_models())




@app.post("/v1/embeddings", response_model=EmbedingResponse)
async def embeding(request: MessageRequest):
    global embeding_zh ,embeding_en
    request.messages
    if request.stream:
        return  EventSourceResponse(embeding_stream(request.messages))
    st = time.time()
    res = embeding_zh.embed_documents(request.messages)
    et = time.time() - st
    return EmbedingResponse(data=res,len=len(res), used=et)

@app.post("/v1/chat/clean", response_model=bool)
async def clear_llm_model(request: ModelList):
    global LLMModelName, LLMModel, LLModelTokenizer
    for d in request.data:
        if d.id == LLMModelName:
            LLMModel = None
            LLModelTokenizer = None
            LLMModelName = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
            return True
    return False

async def async_read_log(id):
    st = time.time()
    async for line in Git([id]).async_log():
        e = ModelCallResponse(id="system msg", data=[line], used=time.time()-st)
        reply = json.dumps(e.dict(exclude_unset=True), cls=NumpyEncoder) 
        yield "{}".format(reply)
        

@app.post("/v1/models/download", response_model=ModelCallResponse)
async def download_smallmodel(request: ModelCallRequest):
    if request.id.startswith("https://"):
        Git([request.id]).start()
    else:
        if request.id.startswith("/"):
            id = "https://modelscope.cn" + request.id
        else:
            id = "https://modelscope.cn/" + request.id
        Git([id]).start()
    return  EventSourceResponse(async_read_log(request.id))
    



@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    global LLMModel, LLModelTokenizer

    if LLMModel is None:
        if not load_llm(request.model):
            usage = UsageInfo()
            choice_data = ChatCompletionResponseChoice(
                index=0,
                message=ChatMessage(role="function", content=f"Err in Not found model {request.model} path"),
                finish_reason=finish_reason,
            )
            return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion", usage=usage)
    model, tokenizer = LLMModel, LLModelTokenizer

    if len(request.messages) < 1 or request.messages[-1].role == "assistant":
        raise HTTPException(status_code=400, detail="Invalid request")

    gen_params = dict(
        messages=request.messages,
        temperature=request.temperature,
        top_p=request.top_p,
        max_tokens=request.max_tokens or 1024,
        echo=False,
        stream=request.stream,
        repetition_penalty=request.repetition_penalty,
        functions=request.functions,
    )

    logger.debug(f"==== request ====\n{gen_params}")

    if request.stream:
        try:
            generate = predict(model,tokenizer,request.model, gen_params)
            return EventSourceResponse(generate, media_type="text/event-stream")
        except RuntimeError:
            LLMModel = None
            LLModelTokenizer = None
            LLMModelName = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
            return None
    response = None
    try:
        response = generate_chatglm3(model, tokenizer, gen_params)
    except RuntimeError:
        LLMModel = None
        LLModelTokenizer = None
        LLMModelName = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        
        return

    # Remove the first newline character
    if response["text"].startswith("\n"):
        response["text"] = response["text"][1:]
    response["text"] = response["text"].strip()
    usage = UsageInfo()
    function_call, finish_reason = None, "stop"
    if request.functions:
        try:
            function_call = process_response(response["text"], use_tool=True)
        except:
            logger.warning("Failed to parse tool call, maybe the response is not a tool call or have been answered.")

    if isinstance(function_call, dict):
        finish_reason = "function_call"
        function_call = FunctionCallResponse(**function_call)

    message = ChatMessage(
        role="assistant",
        content=response["text"],
        function_call=function_call if isinstance(function_call, FunctionCallResponse) else None,
    )

    logger.debug(f"==== message ====\n{message}")

    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=message,
        finish_reason=finish_reason,
    )
    task_usage = UsageInfo.model_validate(response["usage"])
    for usage_key, usage_value in task_usage.model_dump().items():
        setattr(usage, usage_key, getattr(usage, usage_key) + usage_value)
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion", usage=usage)


def run(port=15001, workers=1):
    uvicorn.run(app, host='0.0.0.0', port=port, workers=workers)

if __name__ == "__main__":
    run()
