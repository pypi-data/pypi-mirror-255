
import json
import time
import datetime
import re

import tqdm
import pandas as pd

from hashlib import md5
from typing import Iterable
from functools import reduce
from typing import Any
from typing import List

# from websocket import create_connection
from termcolor import colored
from ..hf_server.cli_utils import R, ModelCard, ModelList, ModelCallResponse,ModelCallRequest,ClearRequest
from ..hf_server.cli_utils import MachineInfo
from loguru import logger

import requests
class SmallModel:
    remote_host_ :str = None
    def __init__(self,name, remote=None):
        if remote is None:
            remote = self.__class__.remote_host_
        assert remote is not None
        self.remote_host  = remote
        self.name = name
        self._ok = False
        self.purpose = "unKnow"
    
    
    def status(self):
        name = self.name
        if "/" in name:
            name = name.rsplit("/",1)[-1]
        for i in self.__class__.show_all_loaded_models():
            if i.id == name:
                return True
        return False
    
    @classmethod
    def from_remote(cls, name,remote=None):
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        model = cls(name, remote)
        model.try_load_in_remote()
        return model
    
    @classmethod
    def gpu_info_remote(cls, remote=None) ->MachineInfo:
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        url = f"http://{remote}:15001/v1/device/info"
        return MachineInfo.parse_obj(next(R(url, method="get")))
    
    @classmethod
    def clean_all(cls, remote=None):
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        all_models = cls.show_all_loaded_models(remote)
        url = f"http://{remote}:15001/v1/models/clear"
        o = ClearRequest(ids=[i.id for i in all_models])
        return next(R(url, object=o))
        
    
    @classmethod
    def show_all_loaded_models(cls, remote=None)->List[ModelCard]:
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        url = f"http://{remote}:15001/v1/device/info"
        return MachineInfo.parse_obj(next(R(url, method="get"))).loaded_models.data
        

    @classmethod
    def show_all_models(cls, remote=None) -> List[ModelCard]:
        if remote is None:
            remote = cls.remote_host_
        else:
            cls.remote_host_ = remote
        assert remote is not None
        url = f"http://{remote}:15001/v1/models"
        return ModelList.parse_obj(next(R(url, method="get"))).data
        
    def clean(self):
        try:
            # ws = create_connection(f"ws://{self.remote_host}:15000")
            # user_id = md5(time.asctime().encode()).hexdigest()
            # TODAY = datetime.datetime.now()
            # PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
            # ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
            # res = ws.recv()
            # if res != "ok":
            #     print(colored("[info]:","yellow") ,res)
            #     raise Exception("password error")
            # res = self.send_and_recv(json.dumps({"embed_documents":[self.name], "method":"clean"}),ws)
            # return res["embed"]
        
            name = self.name
            if "/" in name:
                name = name.rsplit("/",1)[-1]
            url = f"http://{self.remote_host}:15001//v1/models/clear"
            o = ClearRequest(ids=[name])
            m = MachineInfo.parse_obj(next(R(url, object=o)))
            self._ok = False
            for i in  m.loaded_models.data:
                if i.id == name:
                    self._ok = True
        except Exception as e:
            raise e
        finally:
            pass

    
    def down_remote(self):
        try:
            name = self.name
            if "/" in name:
                
                url = f"http://{self.remote_host}:15001/v1/models/download"
                o = ModelCallRequest(id=name, messages=[])
                for res in R(url, object=o, use_stream=True):
                    ri = ModelCallResponse.parse_obj(res)
                    yield ri.data[0]
            else:
                raise Exception(f"{name} must like xxx/model_name or /xxx/model_name or https://xxx.modelhub.cn/xxx/model_name")
            
        except Exception as e:
            raise e
        

    # @classmethod
    # def send_and_recv(cls, data, ws):
    #     try:
    #         T = len(data)// (1024*102)
    #         bart = tqdm.tqdm(total=T,desc=colored(" + sending data","cyan"))
    #         bart.leave = False
    #         for i in range(0, len(data), 1024*102):
    #             bart.update(1)
    #             ws.send(data[i:i+1024*102])
    #         bart.clear()
    #         bart.close()

    #         ws.send("[STOP]")
    #         message = ""
    #         total = int(ws.recv())
    #         bar = tqdm.tqdm(desc=colored(" + receiving data","cyan", attrs=["bold"]), total=total)
    #         bar.leave = False
    #         while 1:
    #             res = ws.recv()
    #             message += res
    #             bar.update(len(res))
    #             if message.endswith("[STOP]"):
    #                 message = message[:-6]
    #                 break
    #         bar.clear()
    #         bar.close()
    #         msg = json.loads(message)
    #         return msg
    #     except Exception as e:
    #         raise e
    
    # def msg(self):
    #     try:
    #         ws = create_connection(f"ws://{self.remote_host}:15000")
    #         user_id = md5(time.asctime().encode()).hexdigest()
    #         TODAY = datetime.datetime.now()
    #         PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
    #         ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
    #         res = ws.recv()
    #         if res != "ok":
    #             print(colored("[info]:","yellow") ,res)
    #             raise Exception("password error")
    #         res = self.send_and_recv(json.dumps({"embed_documents":[self.name], "method":"msg"}),ws)
    #         return res.get("embed","")
    #     except Exception as e:
    #         raise e
    #     finally:
    #         ws.close()
    
    # def change_remote_name(self, new_name):
    #     assert "/" not in new_name
    #     assert " " not in new_name
    #     ss = re.findall(r"[\w\-\_]+",new_name)
    #     assert len(ss) == 1 and ss[0] == new_name
    #     if self.name in self.show_all_models():
    #         try:
    #             ws = create_connection(f"ws://{self.remote_host}:15000")
    #             user_id = md5(time.asctime().encode()).hexdigest()
    #             TODAY = datetime.datetime.now()
    #             PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
    #             ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
    #             res = ws.recv()
    #             if res != "ok":
    #                 print(colored("[info]:","yellow") ,res)
    #                 raise Exception("password error")
    #             res = self.send_and_recv(json.dumps({"embed_documents":[self.name, new_name], "method":"change_name"}),ws)
    #             return res["embed"]
    #         except Exception as e:
    #             raise e
    #         finally:
    #             ws.close()
    #     else:
    #         raise Exception("model not exists")

    def check(self):
        self._ok = False
        name = self.name
        if "/" in name:
            name = name.rsplit("/",1)[-1]
        self.try_load_in_remote()
        return self._ok
    
    def try_load_in_remote(self):
        try:
            self._ok = False
            name = self.name
            if "/" in name:
                name = name.rsplit("/",1)[-1]
            url = f"http://{self.remote_host}:15001/v1/models/load"
            
            for i in ModelList.parse_obj(next(R(url, object=ModelCard(id=name)))).data:
                if i.id == name:
                    self._ok = True
                    self.purpose = i.task
                    return True
                
            return False
        except Exception as e:
            raise e
            return False

    def mt5_classifer(self, texts, labels=[]):
        if self.purpose != "MT5ForConditionalGeneration":
            return
        if len(labels) < 2:
            return
        ls = ",".join(labels)
        ts = [f"文本分类。\n候选标签：{ls}。\n文本内容："+i for i in texts]
        return self(ts)
        
    def mt5_keys(self, texts):
        if self.purpose != "MT5ForConditionalGeneration":
            return
        ts = [f"抽取关键词："+i for i in texts]
        return self(ts)
    
    def mt5_tr_zh(self, texts):
        if self.purpose != "MT5ForConditionalGeneration":
            return
        ts = [f"翻译成中文："+i for i in texts]
        return self(ts)
    
    def mt5_emotion(self, texts):
        if self.purpose != "MT5ForConditionalGeneration":
            return
        ts = [f"情感分析："+i for i in texts]
        return self(ts)
        
    # def show_remote_models(self):
    #     try:
    #         name = self.name
    #         if "/" in name:
    #             name = name.rsplit("/",1)[-1]
                
    #         ws = create_connection(f"ws://{self.remote_host}:15000")
    #         user_id = md5(time.asctime().encode()).hexdigest()
    #         TODAY = datetime.datetime.now()
    #         PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
    #         ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
    #         res = ws.recv()
    #         if res != "ok":
    #             print(colored("[info]:","yellow") ,res)
    #             raise Exception("password error")
    #         return self.send_and_recv(json.dumps({"embed_documents":[name], "method":"show"}), ws)["embed"]
    #     except Exception as e:
    #         raise e
    #     finally:
    #         ws.close()

    def __call__(self, args: List[str], pandas=False) -> Any:
        if isinstance(args, str):
            args = [args]
        assert isinstance(args, (list, tuple,Iterable,))
        if not self._ok:
            self.check()

        if not self._ok :
            raise Exception("remote's service no such model deployed"+self.name)
        name = self.name
        if "/" in name:
            name = name.rsplit("/",1)[-1]
        url = f"http://{self.remote_host}:15001/v1/models/call"
        nargs = []
        no_match = []
        if isinstance(args, (list,tuple,Iterable)):
            batch_size = 500
            for raw_no,l in enumerate(args):
                if len(l.encode()) > batch_size:
                    n_range = (len(l)//batch_size) +1
                    if len(l) % batch_size == 0:
                        n_range -= 1
                    for i in range(n_range):
                        sl = l[i*batch_size:i*batch_size+batch_size]
                        if len(sl.encode()) > batch_size:
                            nargs.append(sl.encode()[:batch_size].decode("utf-8","ignore"))
                        else:
                            nargs.append(sl)
                        no_match.append(raw_no)
                else:
                    nargs.append(l)
                    no_match.append(raw_no)
        else:
            nargs = args
        # print(len(nargs))
        # ml = len(max(nargs, key=lambda x: len(x)))
        # logger.info(f" max length:{ml}")
        try:
            o = ModelCallRequest(id=name, messages=nargs)

            no = 0
            oss = []
            for res in R(url, object=o, use_stream=True):
                ri = ModelCallResponse.parse_obj(res)
                # logger.info(ri)
                if isinstance(ri.data, List):
                    if  len(ri.data) > 0 and isinstance(ri.data[0], str):
                        oss += ri.data
                    elif isinstance(ri.data[0], dict):
                        for ii in ri.data:
                            ar = nargs[no]
                            ii["input"] = ar
                            no += 1
                            oss.append(ii)
                    else:
                        oss += ri.data
                else:
                    oss.append(ri.data)
            
            has_output_key = False
            if isinstance(args, (list,tuple,)):
                if len(oss) == len(nargs):
                    r_oss = []
                    for i,o in enumerate(oss):
                        if "output" in o and "input" in o:
                            has_output_key = True
                        r_i = no_match[i]
                        if len(r_oss) > r_i:
                            if isinstance(r_oss[r_i],dict) and "output" in r_oss[r_i]:
                                r_oss[r_i]["output"] += o["output"]
                            if isinstance(r_oss[r_i],dict) and "input" in r_oss[r_i]:
                                r_oss[r_i]["input"] += o["input"]

                        else:
                            r_oss.append(o)
                else:
                    logger.debug(f"len(oss):{len(oss)} vs len(nargs):{len(nargs)}")
                    r_oss = oss
            else:
                r_oss = oss

            if len(r_oss) > 0 and isinstance(r_oss[0], dict) and pandas:
                if has_output_key:
                    return pd.DataFrame([i["output"] for i in r_oss])
                return pd.DataFrame(r_oss)
            if has_output_key:
                return [i["output"] for i in r_oss]
            return r_oss
            
        except Exception as e:
            raise e
            # import ipdb;ipdb.set_trace()
    
    def _merged(self, res_list):
        res = []
        for one_obj in res_list:
            if isinstance(one_obj, list) :
                if len(one_obj) > 1:
                    if isinstance(one_obj[0], dict):
                        res.append({k:reduce(lambda x,y: x+y , map(lambda x: x[k] ,one_obj)) for k in one_obj[0]})
                    else:
                        res.append(one_obj)
                else:
                    res.append(one_obj[0])
            else:
                res.append(one_obj)
        return res




# class SmallModel_v2(SmallModel):

#     def status(self):
#         return super().status()

#     def try_load_in_remote(self):
#         def try_load_in_remote(self):
#         try:
#             self._ok = False
#             name = self.name
#             if "/" in name:
#                 name = name.rsplit("/",1)[-1]
            
            