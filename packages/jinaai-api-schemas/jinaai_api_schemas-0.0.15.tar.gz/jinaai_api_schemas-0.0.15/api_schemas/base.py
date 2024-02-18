from pydantic import Field
from docarray.base_doc.doc import BaseDocWithoutId


class BaseInputModel(BaseDocWithoutId):
    model: str = Field(
        description='The identifier of the model.\n'
        '\nAvailable models and corresponding param size and dimension:\n'
        '- `jina-embedding-t-en-v1`,\t14m,\t312\n'
        '- `jina-embedding-s-en-v1`,\t35m,\t512 (default)\n'
        '- `jina-embedding-b-en-v1`,\t110m,\t768\n'
        '- `jina-embedding-l-en-v1`,\t330,\t1024\n'
        '\nFor more information, please checkout our [technical blog](https://arxiv.org/abs/2307.11224).\n',
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
