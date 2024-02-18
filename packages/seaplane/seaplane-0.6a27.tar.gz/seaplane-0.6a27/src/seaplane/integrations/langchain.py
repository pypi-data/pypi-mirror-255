from typing import List

from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Qdrant
from pydantic import BaseModel
import requests

from seaplane.config import config
from seaplane.sdk_internal_utils.http import headers
from seaplane.sdk_internal_utils.token_auth import method_with_token
from seaplane.vector import vector_store


class SeaplaneEmbeddingFunction(BaseModel, Embeddings):
    @method_with_token
    def _embed(self, token: str, query: str) -> List[float]:
        url = config.substation_embed_endpoint

        resp = requests.post(
            url,
            headers=headers(token),
            json={"query": query},
        )
        resp.raise_for_status()
        result = resp.json()

        return [float(i) for i in result["embeddings"]]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = self._embed(f"Represent the document for Retrieval: {text}")
            embeddings.append(response)
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        response = self._embed(f"Represent the Science sentence: {query}")
        return response


seaplane_embeddings = SeaplaneEmbeddingFunction()


def langchain_vectorstore(index_name: str, embeddings: Embeddings = seaplane_embeddings) -> Qdrant:
    vectorstore = Qdrant(
        client=vector_store._get_client(),
        collection_name=index_name,
        embeddings=embeddings,
    )

    return vectorstore
