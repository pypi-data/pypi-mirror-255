# import requests
# import aiohttp
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# import json
# import sys
# import inspect
# from typing import Any, List, Optional
# from termcolor import colored


# import langchain
# from langchain.llms.base import LLM
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# from .callbacks import AsyncWebsocketHandler, AsyncWebSocksetCallbackManager

# def is_async_method(method):
#     return inspect.iscoroutinefunction(method)

# class VllmBase(LLM):
#     n = 1
#     use_beam_search = False
#     top_p:float =1.0
#     temperature:float = 0.0
#     max_tokens:int = 8096
#     history_len: int = 10
#     streaming: bool = True
#     verbose: bool = False
#     callbacks :Any  = [StreamingStdOutCallbackHandler()]
#     remote_host: str = None
#     hist = []
#     system = "You are a assistant."
    
        
#     def clear_history(self):
#         self.hist = []

#     def send(self, prompt,stop=[], **kwargs):
#         headers = {"User-Agent": "Test Client"}
#         basepload = {
#             "prompt": prompt,
#             "n": self.n,
#             "use_beam_search": self.use_beam_search,
#             "top_p": self.top_p,
#             "temperature": self.temperature,
#             "max_tokens": self.max_tokens,
#             "stream": True,

#         }
#         if stop and len(stop) > 0:
#             basepload["stop"] = stop
#         basepload.update(kwargs)
#         basepload = self.make_args(basepload)
#         if self.verbose:
#             print(prompt)
#             print(basepload)
#         api_url = f"https://{self.remote_host}:15443/generate"
#         response = requests.post(api_url, headers=headers, 
#                                  verify=False,
#                                  json=basepload, stream=True)
        
#         return response
    
#     def make_args(self, parameter):
#         raise NotImplementedError("must implement make_args(parameter)")
    
#     async def asend(self, prompt,stop=[], **kwargs):
#         """
#         async send use aiohttp
#         """
#         headers = {"User-Agent": "Test Client"}
#         basepload = {
#             "prompt": prompt,
#             "n": self.n,
#             "use_beam_search": self.use_beam_search,
#             "top_p": self.top_p,
#             "temperature": self.temperature,
#             "max_tokens": self.max_tokens,
            
#             "stream": True,
#         }
#         if stop and len(stop) > 0:
#             basepload["stop"] = stop
#         basepload.update(kwargs)
#         basepload = self.make_args(basepload)
#         api_url = f"https://{self.remote_host}:15443/generate"
#         async with aiohttp.ClientSession() as session:
#             async with session.post(api_url, headers=headers, 
#                                     verify_ssl=False,
#                                     json=basepload, 
#                                     timeout=aiohttp.ClientTimeout(total=60*60*24),
#                                     ) as response:
#                 one = ""
#                 old_data = b""
#                 async for chunk in response.content.iter_chunked(8192):
#                                     #  decode_unicode=False,
#                                     #  delimiter=b"\0"):
#                     if chunk:
#                         if old_data != b"":
#                             chunk = old_data + chunk
#                             old_data = b""

#                         if not chunk.endswith(b"\0"):
#                             old_data = chunk.rsplit(b"\0",1)[1]
#                             chunk = chunk.rsplit(b"\0",1)[0]

#                         for line in chunk.split(b"\0"):
#                             if line:
#                                 data = json.loads(line.decode("utf-8"))
#                                 output = data["text"]
#                                 for lineno, linetext in enumerate(output):
#                                     linetext = self.parse_output(linetext)
#                                     new_text = linetext[len(one):]
#                                     one = linetext
#                                     yield {
#                                         "new": new_text,
#                                         "history": self.hist,
#                                         "lineno": lineno,
#                                         "response": one,
#                                     }

#                 self.hist.append((prompt, one))

#     async def astream(self, prompt, history=[],stop=[],system="You are a assistent.", **kwargs):
#         if len(history) > 0:
#             query = self.make_context(prompt, history, system)
#             hist = history
#         else:
#             query = self.make_context(prompt, self.hist, system)
#             hist = self.hist
        
#         async for data in  self.asend(query,stop=stop, **kwargs):
#             yield data
        
        
#     @property
#     def _llm_type(self) -> str:
#         return self.__class__.__name__

#     async def _acall(self, prompt: str, stop: List[str] = None, run_manager: any = None,):
        
#         query = self.make_context(prompt, self.hist, self.system)
#         one = ""
#         try:
#             if hasattr(run_manager, "on_llm_start"):
#                 await run_manager.on_llm_start(
#                     None,
#                     prompt,
#                     verbose=self.verbose
#                 )
            
#             async for data in  self.asend(query,stop=stop):
#                 delta = data["new"]
#                 await run_manager.on_llm_new_token(
#                     delta, verbose=self.verbose, **data
#                 )
#                 one = data["response"]
#             await run_manager.on_llm_end(
#                 one, verbose=self.verbose
#             )
#             # self.hist.append((prompt, one))

#             return one
#         except Exception as e:
#             if hasattr(run_manager, "on_llm_error"):
#                 await run_manager.on_llm_error(e)
#             else:
#                 print(e)

#     def _call(self, prompt: str, stop: List[str] = None, run_manager:any = None,):
#         if stop is not None:
#             self.stop = stop
#         query = self.make_context(prompt, self.hist, self.system)
#         response = self.send(query)
#         one = ""
#         try:
#             if hasattr(run_manager, "on_llm_start"):
#                 run_manager.on_llm_start(
#                     None,
#                     prompt,
#                     verbose=self.verbose
#                 )

#             for chunk in response.iter_lines(chunk_size=8192,
#                                         decode_unicode=False,
#                                         delimiter=b"\0"):
#                 if chunk:
#                     data = json.loads(chunk.decode("utf-8"))
#                     output = data["text"]
#                     for lineno, linetext in enumerate(output):
#                         linetext = self.parse_output(linetext)
#                         new_text = linetext[len(one):]
#                         one = linetext
                        
#                         data = {
#                             "new": new_text,
#                             "lineno": lineno,
#                             "history": self.hist,
#                             "response": one,
#                         }

#                         delta = new_text
                    
#                         run_manager.on_llm_new_token(
#                             delta,
#                             **data
#                         )
                
#             self.hist.append((prompt, one))
#         except Exception as e:
#             if self.verbose:
#                 print(e)
#             run_manager.on_llm_error(e)
#         run_manager.on_llm_end(one, verbose=self.verbose)
#         return one

#     def stream(self, prompt, history=[],stop=[],system="You are a assistent.", **kwargs):
#         if len(history) > 0:
#             query = self.make_context(prompt, history, system)
#             hist = history
#         else:
#             query = self.make_context(prompt, self.hist, system)
#             hist = self.hist
#         response = self.send(query, stop=stop, **kwargs)
#         one = ""
        
#         for chunk in response.iter_lines(chunk_size=8192,
#                                      decode_unicode=False,
#                                      delimiter=b"\0"):
#             if chunk:
#                 data = json.loads(chunk.decode("utf-8"))
#                 output = data["text"]
#                 for lineno, linetext in enumerate(output):
#                     linetext = self.parse_output(linetext)
#                     new_text = linetext[len(one):]
#                     one = linetext
                    
#                     yield {
#                         "new": new_text,
#                         "lineno": lineno,
#                         "history": hist,
#                         "response": one,
#                     }
#         self.hist.append((prompt, one))
        
        
#     def stream_stdout(self, prompt, history=[], stop=[], system="You are a assistent.", **kwargs):
#         print(">>",colored(prompt, "green"), end="\nAssist:")
#         for data in self.stream(prompt,stop=stop,history=history,system=system, **kwargs):
#             sys.stdout.write(colored(data["new"], "blue"))
#             sys.stdout.flush()
#         print()

#     def make_context(prompt, system="", history=[]):
#         raise NotImplementedError("must implement make_context(prompt, history=[(q,h)])")

#     def parse_output(self, output):
#         raise NotImplementedError("must implement parse_output(output)")


# class NormalLLM(VllmBase):
#     start_token = ""
#     end_token = ""

#     def make_args(self, parameter):
#         # parameter["stop"] = ['<|im_end|>','<|endoftext|>']
#         # parameter["stop"] = '<|im_end>'
#         return parameter

#     def make_context(self, prompt, history=[],system="You are a assistant."):
#         def _token(role, content):
#             return f"{role}:\n{content}"

#         raw_text = _token("system", system) + "\n"
#         for q, h in history:
#             raw_text += _token("user", q)
#             raw_text += "\n"+_token("assistant", h) +"\n"
#         return raw_text + _token("user", prompt) + "\n" + self.start_token + "assistant\n"

#     def parse_output(self, output):
#         return output

# class QwenLLM(VllmBase):

#     start_token = "<|im_start|>"
#     end_token = "<|im_end|>"
    
#     def make_args(self, parameter):
#         parameter["stop"] = ['<|im_end|>','<|endoftext|>']
#         # parameter["stop"] = '<|im_end>'
#         return parameter

#     def make_context(self, prompt, history=[],system="You are a assistant."):
#         def _token(role, content):
#             return f"{self.start_token}{role}\n{content}{self.end_token}"

#         raw_text = _token("system", system) + "\n"
#         for q, h in history:
#             raw_text += _token("user", q)
#             raw_text += "\n"+_token("assistant", h) +"\n"
#         return raw_text + _token("user", prompt) + "\n" + self.start_token + "assistant\n"

#     def parse_output(self, output):
#         if self.start_token+"assistant" not in output:
#             if output.endswith(self.end_token):
#                 return output.rsplit(self.end_token,1)[0]
#             return output
#         else:
#             l = output.rsplit(self.start_token+"assistant",1)[1]
#             if l.endswith(self.end_token):
#                 return l.rsplit(self.end_token,1)[0]
#             return l


# # if __name__ == "__main__":
# #     import argparse

# #     parser = argparse.ArgumentParser()
# #     parser.add_argument("-H","--host", default="localhost")
# #     # loop
# #     parser.add_argument("--loop", action="store_true")
# #     #  query
# #     parser.add_argument("-q","--query",nargs="*", default="")
# #     args = parser.parse_args()
# #     if len(args.query) > 0 or args.loop:
# #         qwen = Qwen(args.host)

# #         if args.loop:
# #             while True:
# #                 q = input("You:")
# #                 qwen.stream_stdout(q)
# #         else:
# #             qwen.stream_stdout(" ".join(args.query))
