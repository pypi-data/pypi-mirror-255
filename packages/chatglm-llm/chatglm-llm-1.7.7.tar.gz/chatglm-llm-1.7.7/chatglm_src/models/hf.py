from typing import Any, Dict, List, Optional, Tuple, Union
import pathlib
from termcolor import colored
try:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoModelForTokenClassification,pipeline, AutoConfig
    from transformers import AutoModelForSeq2SeqLM
    from langchain.embeddings import HuggingFaceEmbeddings
    BBBB = {
        "AutoModelForSequenceClassification": AutoModelForSequenceClassification,
        "AutoModelForTokenClassification": AutoModelForTokenClassification,
        "AutoModelForSeq2SeqLM": AutoModelForSeq2SeqLM,

    }
except:
    pass




class HF:
    mos = {}
    def __init__(self, model, token, purpose="cls"):
        self.purpose = purpose
        self.model = model
        self.token = token
        
        if self.purpose != "embed" and not self.purpose.startswith("pipe"):
            self.model = model.to("cuda")
        if self.purpose == "ner":
            self.pip = pipeline("ner", model=model, tokenizer=token, device=self.model.device.index)
        else:
            self.pip = None

        if self.purpose.startswith("pipe"):
            self.pip = model
        
        if self.purpose != "embed" and not self.purpose.startswith("pipe"):
            self.model.eval()
        

    def clean(self):
        
        if self.pip is not None:
            del self.pip
        del self.model
        del self.token
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        try:
            import gc
            gc.collect()
        except Exception as e:
            raise e

    def max_length(self, input: Any) -> int:
        if isinstance(input, list):
            l =  max([len(i) for i in input])
        else:
            l = len(input)
        if l > 512:
            return 512
        return l
    
    @classmethod
    def load_extend_models(cls):
        
        try:
            
            print("Load : ", "emotion_chinese_english")
            modelp = (pathlib.Path("~") / ".cache" / "emotion_chinese_english").expanduser()
            mos = AutoModelForSequenceClassification.from_pretrained(modelp)
            token = AutoTokenizer.from_pretrained(modelp)        
            cls.mos["emotion"] = cls(mos, token)
            modelp2 = pathlib.Path("~").expanduser() / ".cache" /'roberta-base-finetuned-cluener2020-chinese'
            print("Load : ", "ner")
            model2 = AutoModelForTokenClassification.from_pretrained(modelp2)
            token2 = AutoTokenizer.from_pretrained(modelp2)
            cls.mos["ner"] = cls(model2, token2, purpose="ner")
            return mos
        except Exception as e:
            return str(e)
    
    
    
    @classmethod
    def load_model(cls, name):
        try:
            print(colored("Loading : "+ name, "yellow"))
            if ":" in name:
                name, modetp = name.split(":",1)
                modelp = (pathlib.Path("~") / ".cache" / name).expanduser()
                M = BBBB[modetp]
                mos = M.from_pretrained(modelp)
                purpose = "seq2seq"
                token = AutoTokenizer.from_pretrained(modelp)        
                print(colored("Load : "+ name, "green"))
                cls.mos[name] = cls(mos, token, purpose)
                return cls.mos

            modelp = (pathlib.Path("~") / ".cache" / name).expanduser()
            
            conf = AutoConfig.from_pretrained(modelp)
            if conf.architectures is None:
                if conf.id2label is not None and len(conf.id2label) > 3:
                    try:
                        from modelscope.utils.constant import Tasks
                        from modelscope.pipelines import pipeline
                        mos = pipeline(Tasks.named_entity_recognition, str(modelp))
                        purpose = "pipe-ner"
                        token = AutoTokenizer.from_pretrained(modelp)        
                    
                        print(colored("Load : "+ name + " : "+purpose, "green"))
                        cls.mos[name] = cls(mos, token, purpose)
                        return cls.mos
                    except Exception as e:
                        raise e
                
                    
            
            purpose = "cls"
            if "ForTokenClassification" in conf.architectures[0]:
                mos = AutoModelForTokenClassification.from_pretrained(modelp)
                purpose = "ner"
            elif "SequenceClassification" in conf.architectures[0]:
                mos = AutoModelForSequenceClassification.from_pretrained(modelp)
                purpose = "cls"
            elif "MarianMTModel" in conf.architectures[0]:
                mos = AutoModelForSeq2SeqLM.from_pretrained(modelp)
                purpose = "seq2seq"
            elif "MT5ForConditionalGeneration" in conf.architectures[0]:
                mos = AutoModelForSeq2SeqLM.from_pretrained(modelp)
                purpose = "seq2seq"
            elif "BertModel" in conf.architectures[0]:
                mos = HuggingFaceEmbeddings(model_name=str(modelp))
                purpose = "embed"
            
            else:

                mos = AutoModelForSequenceClassification.from_pretrained(modelp)
            token = AutoTokenizer.from_pretrained(modelp)        
            print(colored("Load : "+ name + " : "+purpose, "green"))
            cls.mos[name] = cls(mos, token, purpose)
            return cls.mos
        except Exception as e:
            print(colored("Load Err : "+ name + " : "+str(e), "green"))
            return str(e)

    def __call__(self, _msgs) -> Any:
        msgs = [i for i in _msgs if i is not None and i.strip()!="" ]
        dos = []
        ix = [] 
        outputs = []
        for pos,m in enumerate(msgs):
            if len(m) > 512:
                for ii in range(0, len(m), 512):
                    dos.append(m[ii:ii+512])
                    ix.append(pos)    
            else:
                dos.append(m)
                ix.append(pos)
            if len(dos) > 20:
                outputs += self._call__(dos)
                dos = []
        if len(dos) > 0:
            outputs += self._call__(dos)
        outs = []
        last = -1
        used = 1
        for i,o in enumerate(outputs):
            ii = ix[i]
            if ii != last:
                if used > 1:
                    outs[-1] = [i/used for i in outs[-1] ]
                used = 1
                outs.append(o)
            else:
                if isinstance(o, list) and isinstance(o[0], float):
                    old = outs[-1]
                    onew = [old[i]  + o[i] for i in range(len(o))]
                    outs[-1] = onew
                    used += 1

                else:
                    outs[-1] += o
            last = ii

        return outs

    def _call__(self, _msgs) -> Any:
        msgs = [i for i in _msgs if i is not None and i.strip()!="" ]
        if len(msgs) > 0:
            max_length = self.max_length(msgs)
            # print(max_length)
            with torch.no_grad():
                if self.purpose == "cls":
                    inputs = self.token(msgs, 
                                        padding="max_length",
                                        max_length=max_length,
                                        return_tensors="pt", 
                                        truncation=True).to(self.model.device)
                    outputs = self.model(**inputs)
                    
                    ids = self.model.config.id2label
                    out =  outputs.logits.detach().cpu().numpy()
                    # print()
                    # return [ {msgs[i]: {ids[ix]:ii for ix,ii in enumerate(ii) }} for i,ii in enumerate(out)]
                    return [[{ids[ix]:ii for ix,ii in enumerate(ii) }] for i,ii in enumerate(out) ]
                elif self.purpose == "embed":
                    outputs = self.model.embed_documents(msgs)
                    return outputs
                elif self.purpose == "seq2seq":
                    inputs = self.token(msgs, 
                                        padding="max_length",
                                        max_length=max_length,
                                        return_tensors="pt", 
                                        truncation=True).to(self.model.device)
                    outputs = self.model.generate(**inputs)
                    out = self.token.batch_decode(outputs, skip_special_tokens=True)
                    # print(out)
                    return out
                elif self.purpose == "pipe-ner":
                    # print(msgs)
                    return self.pip(msgs, batch_size=128)
                elif self.purpose == "pipe-classifier":
                    return self.model(msgs)
                elif self.purpose == "ner":
                    res = self.pip(msgs)
                    out = []
                    for i in res:
                        if len(i) ==0:
                            out.append([])
                            continue
                        words_i = set()
                        words = []
                        word = {"entity":"", "text":""}
                        end = -1
                        l_end = -1
                        for j in i:
                            name = ""

                            if j['entity'][1] == "-":
                                name = j['entity'][2:].strip()
                            end = j['end']
                            last_name = word.get("entity", "  ").strip()
                            if last_name != name:
                                
                                if last_name != "":
                                    
                                    if end -1 == l_end and (last_name in ("company",  "organization") and name in ("company",  "organization")):
                                        word["text"] += j["word"]
                                        word["entity"] = name
                                        l_end = end
                                        continue

                                    if word["text"] not in words_i:
                                        words_i.add(word["text"])
                                        words.append(word)
                                    
                                    word = {"entity":"", "text":""}
                                word["entity"] = name
                                word["text"] = j["word"]
                                l_end = end
                            else:
                                if end -1 != l_end:
                                    if word["text"] not in words_i:
                                        words_i.add(word["text"])
                                        words.append(word)
                                    word["entity"] = name
                                    word["text"] = j["word"]
                                    l_end = end
                                    continue
                                word["text"] += j["word"]
                                l_end = end
                        if word["entity"] != "":
                            if word["text"] not in words_i:
                                words_i.add(word["text"])
                                words.append(word)
                        out.append(list(words))
                    return out
