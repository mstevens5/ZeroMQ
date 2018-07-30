#!/usr/bin/env python3

import gzip
import shutil
with open('./config.ini', 'rb') as f_in:
    with gzip.open('./config.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

with open('./config.ini', 'rb') as fp:
    content = fp.read()

with gzip.open('./config.gzz', 'wb') as fd:
    fd.write(content)

out = gzip.compress(content)

with open('./config.gz2', 'wb') as fd2:
    fd2.write(out)
