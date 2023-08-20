from preprocess import preprocess_docs, indexing_documents
from glob import glob 
import json
import pandas as pd
from tqdm import tqdm
from configs import *

all_pdf = glob(f"{FOLDER_PDF}/*")
cfg = {
    'y_min':0,
    'y_max':100000,
    'chunk_size':128,
    'chunk_stride':64
}
docs = []
for path in tqdm(all_pdf, 'preprocess'):
    doc = preprocess_docs(path,cfg)
    docs.append(doc)

chunks, meta_docs = indexing_documents(docs)

with open(PATH_METADATA,'w') as f:
    f.write(json.dumps(meta_docs, indent=4))

df = pd.DataFrame(chunks)
df.to_parquet(PATH_CHUNKS)