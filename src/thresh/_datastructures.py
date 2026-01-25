from collections import deque

class RingBuffer():

    def __init__(self, size):
        self.size = size
        self.content = deque([0.] * self.size, maxlen=self.size)

    def write(self, item) -> None:
        self.content.append(item)

    def read(self) -> any:
        return self.content.popleft()
    


if __name__ == "__main__":

    rb = RingBuffer(10)

    for i in range(11):
        print(i)
        rb.write(i)

    for i in range(10):
        print(rb.read())