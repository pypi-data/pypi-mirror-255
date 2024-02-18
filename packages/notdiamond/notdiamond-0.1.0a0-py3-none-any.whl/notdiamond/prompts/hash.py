from datasketch import MinHash

import numpy as np
from typing import List

def nd_hash(s: str) -> List[int]:
    separate_words = s.split(" ")

    min_hash_set = set(separate_words)
    min_hash = MinHash(num_perm=128)

    for word in min_hash_set:
        min_hash.update(word.encode("utf8"))

    return [int(i) for i in min_hash.digest()]