import heapq
from component.HashCount import HashCount

class CustomHeap:
    def __init__(self):
        self.heap = []
        self.seen = {}

    def push(self, val:HashCount):
        if val.hash not in self.seen:
            heapq.heappush(self.heap, val)
            self.seen[val.hash] = val
        else:
            # 当值已经存在时
            self.seen[val.hash] += val

    def pop(self):
        val = heapq.heappop(self.heap)
        self.seen.pop(val.hash)
        return val

    def __str__(self):
        return str(sorted(self.heap, key=lambda x : x.count))
    
    def __len__(self):
        return self.heap.__len__()
    
    def __iter__(self):
        return self.heap.__iter__()

if __name__=="__main__":
    from HashCount import HashCount as hc
    # 使用自定义堆
    custom_heap = CustomHeap()
    custom_heap.push(hc(0.1, 1))
    custom_heap.push(hc(0.1, 5))  # 不会插入第二个0.1
    custom_heap.push(hc(0.2, 1))
    custom_heap.push(hc(0.01, 1))
    custom_heap.push(hc(0.1, 5))  
    custom_heap.push(hc(0.02, 1))
    custom_heap.push(hc(0.31, 1))
    custom_heap.push(hc(0.51, 5)) 
    custom_heap.push(hc(0.12, 1))
    custom_heap.pop()
    

    print(custom_heap)  
