import requests
import openai 
import pandas as pd
from configs import *
import json
import numpy as np
import chromadb

#Init chromadb client database
client = chromadb.PersistentClient(path=PATH_VECTOR)
client.heartbeat() # returns a nanosecond heartbeat. Useful for making sure the client remains connected.
df = pd.read_parquet(PATH_CHUNKS)
documents = df['chunk_content'].tolist()
index = df['idx_chunk'].astype(str).tolist()
meta_image = json.loads(open(PATH_METADATA).read())
#Create Database
# client.delete_collection(name="bksi")
try:
    collection = client.get_collection(name="bksi")
    print("nhanh")
except:
    collection = client.create_collection(
                name="bksi",
                metadata={"hnsw:space": "cosine"} # l2 is the default
                )
    collection.add(
            documents=documents,
            ids=index
            )
    print("chậm ")
