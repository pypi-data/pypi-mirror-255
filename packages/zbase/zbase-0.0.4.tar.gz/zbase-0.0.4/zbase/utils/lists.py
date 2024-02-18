from typing import List, Any, Dict, Callable,Iterable

def paging(objs:Iterable,page_size:int)->List:
    if not objs:
        return objs
    buf = []
    count = 0
    for i in objs:
        buf.append(i)
        count += 1
        if count == page_size:
            yield buf
            buf = []
            count = 0
    if buf:
        yield buf


def calc_pages(total:int, page_size:int)->int:
    if page_size==0:
        return 0
    if total%page_size==0:
        return total//page_size
    else:
        return total//page_size+1
    
def groupby(arr:List, partition:Callable[[Any], Any] )->Dict[Any, List]:
    res = {}
    for v in arr:
        k = partition(v)
        if k not in res:
            res[k] = []
        res[k].append(v)
    return res
