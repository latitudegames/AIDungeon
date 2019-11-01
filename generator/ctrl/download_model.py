import os
import sys
import requests
from tqdm import tqdm


for filename in ['checkpoint','model.ckpt-417400.data-00001-of-00002', 'model.ckpt-413000.index',
                 'model.ckpt-417400.meta', 'model.ckpt-417400.data-00001-of-00002']:

    subdir = "finetuned_model"
    r = requests.get("https://storage.googleapis.com/aidungeon2model/" + subdir + "/" + filename, stream=True)

    with open(os.path.join(subdir, filename), 'wb') as f:
        file_size = int(r.headers["content-length"])
        chunk_size = 1000
        with tqdm(ncols=100, desc="Fetching " + filename, total=file_size, unit_scale=True) as pbar:
            # 1k for chunk_size, since Ethernet packet size is around 1500 bytes
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                pbar.update(chunk_size)
