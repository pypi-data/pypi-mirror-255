import yaml
from pydantic import BaseModel


class PageKeySite(BaseModel):
    project: str
    copyright: str
    author: str
    release: str
    package: str

def load_config(yaml_config: str):
    parsed_config = yaml.safe_load(yaml_config)
    site_config = PageKeySite(**parsed_config)
    return site_config
