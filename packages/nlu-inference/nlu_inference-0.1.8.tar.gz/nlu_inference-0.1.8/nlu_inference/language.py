from pydantic import BaseModel
from .tokenizer import Tokenizer, CharTokenizer, WordTokenizer
from .inference import CLSInference, NERInference
from .io import ParserOutput, DomainOutput, CLSResult, NERResult, DomainResult, Event, ParserResult, Slot
from .config import registry
from .config import Config
from typing import Optional
from pathlib import Path


class NLU(BaseModel):
    
    domain: str
    tokenizer: Tokenizer
    domain_inference: CLSInference
    intention_inference: CLSInference
    ner_inference: NERInference
    config: Optional[Config] = None
    version: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    
    def predict_domain(self, text: str) -> DomainOutput:
        tokens = self.tokenizer(text)[0]
        result: CLSResult = self.domain_inference(tokens)
        data = DomainResult(domain=self.domain, probability=result.score)
        return DomainOutput(data=data, code=0, message="success")
    
    def predict_parser(self, text: str) -> ParserOutput:
        tokens = self.tokenizer(text)[0]
        intention_result: CLSResult = self.intention_inference(tokens=tokens)
        ner_result: NERResult = self.ner_inference(tokens=tokens)
        parser_result = ParserResult(domain=self.domain, intention=intention_result.label, ner=ner_result)
        slots = {}
        for label in ner_result.keys():
            ent = ner_result[label]
            slots[label] = Slot(raw_value=ent, value=ent)
        event = Event(eventId=f"model_intention_{intention_result.label}", raw=parser_result, slots=slots)
        return ParserOutput(data=[event], code=0, message="success")    
    
    @classmethod
    def from_checkpoint(cls, checkpoint_dir: str):
        config_path = Path(checkpoint_dir) / "config.cfg"
        if not config_path.exists():
            raise FileNotFoundError(f"config file {config_path} not found")
        config = Config().from_disk(config_path)
        nlu = registry.resolve(config=config)['nlu']
        nlu.config = config
        return nlu
    
    def save_config(self, save_path: str):
        config_path = Path(save_path)
        self.config.to_disk(config_path, interpolate=False)
    

@registry.languages.register("cmn")
def create_cmn(domain: str, 
               tokenizer: CharTokenizer, 
               domain_inference: CLSInference, 
               intention_inference: CLSInference, 
               ner_inference: NERInference,
               version: Optional[str] = None):
    return NLU(domain=domain, 
               tokenizer=tokenizer, 
               domain_inference=domain_inference, 
               intention_inference=intention_inference, 
               ner_inference=ner_inference,
               version=version)

@registry.languages.register("zho")
def create_zho(domain: str, 
               tokenizer: CharTokenizer, 
               domain_inference: CLSInference, 
               intention_inference: CLSInference, 
               ner_inference: NERInference,
               version: Optional[str] = None):
    return NLU(domain=domain, 
               tokenizer=tokenizer, 
               domain_inference=domain_inference, 
               intention_inference=intention_inference, 
               ner_inference=ner_inference,
               version=version)

@registry.languages.register("eng")
def create_eng(domain: str, 
               tokenizer: WordTokenizer, 
               domain_inference: CLSInference, 
               intention_inference: CLSInference, 
               ner_inference: NERInference,
               version: Optional[str] = None):
    return NLU(domain=domain, 
               tokenizer=tokenizer, 
               domain_inference=domain_inference, 
               intention_inference=intention_inference, 
               ner_inference=ner_inference,
               version=version)
        
    