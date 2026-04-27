class MinHeap:

    # Constructors
    def __init__(self):
        self.heap = []

    def __len__(self):
        return len(self.heap)

    # Check if length is empty
    def is_empty(self):
        return len(self.heap) == 0

    # Insert item to the end, fixing the heap by moving it up
    def push(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    # Returns smallest element
    def pop(self):
        if not self.heap:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        minimum = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return minimum

    # Returns smallest element without removing it
    def peek(self):
        if not self.heap:
            return None
        return self.heap[0]
        
    # Restores the heap after inserting a new element
    def _heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self.heap[index] < self.heap[parent]:
                self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
                index = parent
            else:
                break

    # Restores heap after removing the root
    def _heapify_down(self, index):
        size = len(self.heap)

        while True:
            smallest = index
            left = 2 * index + 1
            right = 2 * index + 2

            if left < size and self.heap[left] < self.heap[smallest]:
                smallest = left

            if right < size and self.heap[right] < self.heap[smallest]:
                smallest = right

            if smallest == index:
                break

            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            index = smallest
