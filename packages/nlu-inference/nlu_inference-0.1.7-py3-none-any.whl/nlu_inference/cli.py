from jsonargparse import CLI 
from logging import getLogger
from .io import ParserOutput, HealthCheckOutput, DomainOutput, NLUInput
from .config import Config, registry
from .language import NLU
from pathlib import Path
import uvicorn


logger = getLogger(__name__)


def serve(checkpoint_dir: str, port: int = 18000, host: str = "localhost"):
    
    nlu = NLU.from_checkpoint(checkpoint_dir)
    
    domain = nlu.domain
    
    
    logger.info(f"loading model {domain}")
    
    from fastapi import FastAPI
    app = FastAPI(description="NLU Inference API")
    
    @app.post("/parser", response_model=ParserOutput)
    def parse(inputs: NLUInput):
        
        return nlu.predict_parser(inputs.rawText)
    
    
    @app.post("/domain", response_model=DomainOutput)
    def domain(inputs: NLUInput):
        
        return nlu.predict_domain(inputs.rawText)
    
    
    @app.post("/health", response_model=HealthCheckOutput)
    def health(inputs: NLUInput):
        try:
            domain_results = nlu.predict_domain(inputs.rawText)
            parser_results = nlu.predict_parser(inputs.rawText)
            return HealthCheckOutput(code=0, message="success")
        except Exception as e:
            return HealthCheckOutput(code=1, message=str(e))
        
    uvicorn.run(app, host=host, port=port)


def run():
    CLI(serve, as_positional=False)