import requests
import aiohttp
import tqdm
from .models import *


def R(uri, object:BaseModel=None, method='post',use_stream=False, **datas):
    data = {}
    data.update(datas)
    o = None
    if object is not None:
        o = object.dict()
        if "stream" in o:
            # print("Set Stream:",use_stream)
            object.stream = use_stream
        o = object.dict()
        data.update(o)
        
    if method == "post":
        response = requests.post(uri, json=data, stream=use_stream)
    else:
        response = requests.get(uri, json=data, stream=use_stream)
    if response.status_code == 200:
        if use_stream:
            # 处理流式响应
            if "messages" in o:
                T = (len(object.messages) // 50) + 1
                if uri.endswith("embeddings"):
                    T = (len(object.messages) // 100) + 1
                bar = tqdm.tqdm(total=T,desc=" + deal data")
                bar.leave = False
                for line in response.iter_lines():
                    if line:
                        if line[:6] == b": ping" and line[6] != b"{":continue
                        decoded_line = line.decode('utf-8')[6:].strip()
                        if decoded_line:
                            try:
                                response_json = json.loads(decoded_line)
                                bar.update(1)
                                yield response_json
                            except Exception as e:
                                print("Special Token:", e, len(line), line)
                bar.clear()
                bar.close()
        else:
            # 处理非流式响应
            decoded_line = response.json()
            yield decoded_line
    else:
        print("Error:", response.status_code)
        return None



def create_chat_completion(url, messages:List[ChatMessage], functions=None, use_stream=True,model="chatglm3-6b-32k",temperature=0.8,top_p=0.8, max_tokens=8000):
    # data = {
    #     "function": functions,  # 函数定义
    #     "model": model,  # 模型名称
    #     "messages": messages,  # 会话历史
    #     "stream": use_stream,  # 是否流式响应
    #     "max_tokens": max_tokens,  # 最多生成字数
    #     "temperature": temperature,  # 温度
    #     "top_p": top_p,  # 采样概率
    # }
    req = ChatCompletionRequest(
        model=model, 
        functions=functions,
        messages=messages,
        top_p=top_p,
        temperature=temperature,
        stream=use_stream,
        max_tokens=max_tokens,
    )
    data = req.dict()
    response = requests.post(url, json=data, stream=use_stream)
    if response.status_code == 200:
        if use_stream:
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')[6:]
                    try:
                        if decoded_line.strip():
                            response_json = json.loads(decoded_line.strip())
                            # content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            c = ChatCompletionResponse.parse_obj(response_json)
                            if c.choices[-1].finish_reason == "stop":
                                yield c
                                break
                            elif c.choices[-1].finish_reason == "function_call":
                                yield c
                                break
                            
                            yield c
                            
                    except:
                        # print("Special Token:", decoded_line)
                        pass
        else:
            # 处理非流式响应
            decoded_line = response.json()
            # content = decoded_line.get("choices", [{}])[0].get("message", "").get("content", "")
            yield ChatCompletionResponse.parse_obj(decoded_line)
    else:
        print("Error:", response.status_code)
        return None

async def acreate_chat_completion(url, messages:List[ChatMessage], functions=None, use_stream=True,model="chatglm3-6b-32k",temperature=0.8,top_p=0.8, max_tokens=8000):
    req = ChatCompletionRequest(
        model=model, 
        functions=functions,
        messages=messages,
        top_p=top_p,
        temperature=temperature,
        stream=use_stream,
        max_tokens=max_tokens,
    )
    data = req.dict()
    # print()
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
    
            if response.status == 200:
                if use_stream:
                    # 处理流式响应
                    # import ipdb;ipdb.set_trace()
                    while 1:
                        try:
                            line = await response.content.readline()
                            if line:
                                decoded_line = line.decode('utf-8')[6:]
                                try:
                                    if decoded_line.strip():
                                        response_json = json.loads(decoded_line.strip())
                                        # content = response_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                        c = ChatCompletionResponse.parse_obj(response_json)
                                        
                                        if c.choices[-1].finish_reason == "stop":
                                            yield c
                                            break
                                        elif c.choices[-1].finish_reason == "function_call":
                                            yield c
                                            break
                                        yield c
                                        
                                        
                                except:
                                    print("Special Token:", decoded_line)
                        except EOFError:
                            break
                    
                        
                else:
                    # 处理非流式响应
                    decoded_line = response.json()
                    # content = decoded_line.get("choices", [{}])[0].get("message", "").get("content", "")
                    yield ChatCompletionResponse.parse_obj(decoded_line)
            else:
                print("Error:", response.status)
                

def simple_chat(url, messages,use_stream=True):
    functions = None
    chat_messages = [
        {
            "role": "system",
            "content": "You are ChatGLM3, a helpful assistant. Follow the user's instructions carefully. Respond using markdown.",
        },
        
    ]
    for message in messages:
        chat_messages.append(
            {
                "role": "user",
                "content": message
            }
        )
    return create_chat_completion( messages=chat_messages, functions=functions, use_stream=use_stream)
