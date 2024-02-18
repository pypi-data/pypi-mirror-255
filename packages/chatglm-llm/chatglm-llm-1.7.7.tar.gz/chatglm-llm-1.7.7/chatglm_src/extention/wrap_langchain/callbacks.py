

# class AsyncWebsocketHandler(AsyncCallbackHandler):
#     """Async callback handler that can be used to handle callbacks from langchain."""
    
#     async def on_llm_start(self, prompt: str,prompts: List[str], **kwargs: Any) -> Any:
#         """Run when chain starts running."""
#         if "verbose" in kwargs:
#             if kwargs["verbose"]:
#                 print(" load history from prompt.")
        
#         # await asyncio.sleep(0.3)
#         # if "(history_id:" in prompt:
#         #     history_id = self.extract_history_id_from_prompt(prompt)
#         #     if history_id != "":
#         #         prompt = prompt.replace("(history_id:"+history_id+")", "")
#         #         history = await self.load_history(history_id)
#         #         print("thinking....", end="", flush=True)
#         #         return prompt,history_id,history
        
#         # return prompt,None,None

#     async def on_llm_end(self, serialized:LLMResult, **kwargs: Any) -> None:
#         """Run when chain ends running."""
#         # print(".end query and save.")
#         # print("End",serialized, type(serialized))
#         if isinstance(serialized, Dict):
#             history_id = serialized["id"]
#             history = serialized["history"]
#             await asyncio.sleep(0.3)
#             await self.save_history(history_id, history)
    
#     async def on_llm_new_token(self, token: str, **kwargs: Any) -> Coroutine[Any, Any, None]:
#         # print("thinking....",kwargs)
#         if "verbose" in kwargs:
#             if kwargs["verbose"]:
#                 print(token, end="", flush=True)
    
#     async def save_history(self, history_id, history):
#         AsyncWebSocksetCallbackManager.online_histories[history_id] = history
    
#     async def load_history(self, history_id):
#         return AsyncWebSocksetCallbackManager.online_histories.get(history_id)
    

#     def extract_history_id_from_prompt(self, prompt):
#         """
#         extract history id 123 from '(history_id:123)'
#         """
#         try:
#             return re.findall(r'\(history_id:(\d+)\)', prompt)[0]
#         except:
#             return ""