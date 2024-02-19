from typing import Any, Optional, Union

import sys
from copy import copy

from .model import (
    GenConf,
    TextModel,
    Tokenizer
)

from .thread import (
    Thread
)

from .format import (
    apply_format,
    filter_out,
    get_format
)


try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False
    
try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        GenerationConfig,
        StoppingCriteria
    )    
    has_hf = True
except ImportError:
    has_hf = False



class HFModel(TextModel):

    def __init__(self,
                 pretrained_model_name_or_path: str,
                 format_type: Optional[str] = None,
                 *,

                 # common base model args
                 genconf: Optional[GenConf] = GenConf(),
                 tokenizer: Optional[Tokenizer] = None,
                 ctx_len: Optional[int] = 0,
                                  
                 # most important HF-specific args
                 device_map: str = "auto",
                 trust_remote_code: bool = False,
                 revision: Optional[str] = "main",

                 # other HF-specific args
                 **hf_kwargs
                ):
        
        if not has_torch:
            raise Exception("Please install PyTorch: https://pytorch.org/")
            
        if not has_hf:
            raise Exception("Please install Hugging Face Transformers by running: pip install transformers. You may also need to install other packages as requested")

        super().__init__(True,
                         genconf,
                         tokenizer, 
                         format_type, 
                         )
        
        self._hfmodel = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            device_map=device_map,
            trust_remote_code=trust_remote_code,
            revision=revision,
            **hf_kwargs
           )

        # correct super __init__ values
        if self.tokenizer is None:
            self.tokenizer = HFTokenizer(pretrained_model_name_or_path=pretrained_model_name_or_path)

        # find n_ctx_train:
        if self.tokenizer._tok.model_max_length < int(1e30): # https://github.com/huggingface/transformers/blob/main/src/transformers/tokenization_utils_base.py#L116
            n_ctx_train = tokenizer._tok.model_max_length
            
        elif hasattr(self._hfmodel.config, "sliding_window"):
            n_ctx_train = self._hfmodel.config.sliding_window
            
        elif hasattr(self._hfmodel.config, "max_length"):
            n_ctx_train = self._hfmodel.config.max_length
            
        else:
            raise ValueError('Unable to find n_ctx_train')

        if ctx_len == 0:
            self._ctx_len = n_ctx_train
        elif self._ctx_len > n_ctx_train:
            raise ValueError(f"ctx_len({self._ctx_len}) is greater than n_ctx_train ({n_ctx_train})")

        
        if False:
            # workaround GPTQ issue with exlamma: https://github.com/PanQiWei/AutoGPTQ/issues/253
            try:
                from auto_gptq import exllama_set_max_input_length
                model = exllama_set_max_input_length(model, self._ctx_len)
            except:
                pass
        
        self.stop_criteria = self.StrListStoppingCriteria(self)
    

    

    class StrListStoppingCriteria(StoppingCriteria):

        """
        This should be implemented in a lighter manner.
        """
        
        def __init__(self, 
                     model: TextModel):
            self._model = model

        def set(self, 
                stop_list: list[str]):
            self.stop_list = stop_list
            self.stop_max_len = max([len(l) for l in self.stop_list])
            #print(self.stop_max_len, self.stop_list)
        
        def __call__(self, 
                     input_ids: torch.LongTensor, 
                     _: torch.FloatTensor, 
                     **kwargs) -> bool:
            # stop_max_len is in chars which is a good upper bound for token_len
            last_ids = input_ids[0, -self.stop_max_len:].tolist()
            last_text = self._model.tokenizer.decode(last_ids)
            #print("last", last_ids, last_text)
            
            for text in self.stop_list:
                if text in last_text:
                    #print("TRUE: ", text)
                    return True

            return False


    
    
    def text_gen(self,
                 text: str,
                 genconf: Optional[GenConf] = None) -> str:

        token_ids = self.tokenizer.encode(text)

        if genconf is None: 
            genconf = self.genconf

        if genconf.max_tokens == 0:
            genconf = genconf(max_tokens = self.ctx_len - len(token_ids))

        elif len(token_ids) + genconf.max_tokens > self.ctx_len:
            logger.warn(f"Token length + genconf.max_tokens ({len(token_ids) + genconf.max_tokens}) is greater than model's context window length ({self.ctx_len})")

        if genconf.format != "text":
            raise ValueError("HFModel: only 'text' is currently supported for genconf.format")

        
        hf_genconfig = GenerationConfig(
            max_new_tokens = genconfig.max_tokens,
            pad_token_id = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.eos_token_id, # HF requires a pad token which is undefined in some models 
            do_sample = genconf.temperature != 0.
        )

        if hf_genconfig.do_sample:
            hf_genconfig.temperature = genconf.temperature
            hf_genconfig.top_p = genconf.top_p
        
        if genconf.stop:
            self.stop_criteria.set(genconf.stop)
            stop_crit = [self.stop_criteria]
        else:
            stop_crit = None

        
        inputs = torch.LongTensor(token_ids).unsqueeze(0).to(self._hfmodel.device)
        output_ids = self._hfmodel.generate(inputs = inputs,
                                            generation_config = hf_genconfig,
                                            stopping_criteria = stop_crit)

        new_output_ids = output_ids.squeeze(0)[len(token_ids):].tolist() # only new tokens
        
        text = self.tokenizer.decode(new_output_ids, skip_special=True)

        # remove the first stop text found
        if genconf.stop:
            for st in genconf.stop:
                index = text.find(st)
                if index >= 0:
                    text = text[:index]
                    break

        return text




    

    def thread_gen(self, 
                   thread: Thread,
                   genconf: Optional[GenConf] = None,
                  ) -> str:

        if genconf is None:
            genconf = self.genconf

        if self.format is not None:
            # stop sequences from REGISTRY must be used and merged with any GenConf stop sequences.
            if "stop" in self.format: # merge any stop text with model's registry stops
                genconf = copy(genconf)
                genconf.stop = list(set( genconf.stop + self.format["stop"] ))

        self.pre_thread_gen(thread, genconf)

        prompt = self.text_from_thread(thread)
        
        text = self.text_gen(prompt, genconf)
 
        text = filter_out(text, self.format)
            
        
        return text


    
    @property
    def desc(self) -> str:
        return f"HFModel: {self._hfmodel.name_or_path}"







class HFTokenizer(Tokenizer):

    def __init__(self, 
                 pretrained_model_name_or_path: str
                 ):

        self._tok = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=pretrained_model_name_or_path)

        self.vocab_size = self._tok.vocab_size
        
        self.bos_token_id = self._tok.bos_token_id
        self.bos_token = self._tok.bos_token

        self.eos_token_id = self._tok.eos_token_id
        self.eos_token = self._tok.eos_token

        self.pad_token_id = self._tok.pad_token_id
        self.pad_token = self._tok.pad_token

        self.unk_token_id = self._tok.unk_token_id
        self.unk_token = self._tok.unk_token
  

    
    def encode(self, 
               text: str) -> list[int]:
        """
        Also encodes special tokens.
        """

        return self._tok.encode(text, add_special_tokens=False)

        
    def decode(self, 
               token_ids: list[int],
               skip_special: bool = True) -> str:
        """
        skip_special: don't decode special tokens like bos and eos
        """

        return self._tok.decode(token_ids = token_ids,
                                skip_special_tokens = skip_special)

   




