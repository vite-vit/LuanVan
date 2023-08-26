import pandas as pd
from configs import *
import json
import chromadb

client = chromadb.PersistentClient(path=PATH_VECTOR)
client.heartbeat() # returns a nanosecond heartbeat. Useful for making sure the client remains connected.
df = pd.read_parquet(PATH_CHUNKS)
documents = df['chunk_content'].tolist()
index = df['idx_chunk'].astype(str).tolist()
meta_image = json.loads(open(PATH_METADATA).read())

collection = client.create_collection(
                name="bksi",
                metadata={"hnsw:space": "cosine"} # l2 is the default
                )
collection.add(
        documents=documents,
        ids=index
        )