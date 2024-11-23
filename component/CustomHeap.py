import heapq

class CustomHeap:
    def __init__(self):
        self.heap = []
        self.seen = []

    def push(self, val):
        if val not in self.seen:
            heapq.heappush(self.heap, val)
            self.seen.append(val)
        else:
            # 当值已经存在时进行某种操作（比如更新计数）
            for hc in self.seen:
                if hc == val:
                    hc += val
                    break

    def pop(self):
        val = heapq.heappop(self.heap)
        self.seen.remove(val)
        return val

    def __str__(self):
        return str(self.heap)
    
    def __len__(self):
        return self.heap.__len__()

if __name__=="__main__":
    from HashCount import HashCount as hc
    # 使用自定义堆
    custom_heap = CustomHeap()
    custom_heap.push(hc(0.1, 1))
    custom_heap.push(hc(0.1, 5))  # 不会插入第二个5
    custom_heap.push(hc(0.2, 1))
    custom_heap.push(hc(0.01, 1))
    custom_heap.push(hc(0.1, 5))  # 不会插入第二个5
    custom_heap.push(hc(0.02, 1))
    custom_heap.push(hc(0.31, 1))
    custom_heap.push(hc(0.51, 5))  # 不会插入第二个5
    custom_heap.push(hc(0.12, 1))
    custom_heap.pop()
    

    print(custom_heap)  # 输出：[5, 10]
