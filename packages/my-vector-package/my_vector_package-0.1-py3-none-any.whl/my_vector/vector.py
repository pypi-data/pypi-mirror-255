class Vector:
    def __init__(self):
        self.data = []

    def size(self):
        return len(self.data)

    def empty(self):
        return len(self.data) == 0

    def push_back(self, value):
        self.data.append(value)

    def pop_back(self):
        if not self.empty():
            self.data.pop()

    def at(self, index):
        if 0 <= index < len(self.data):
            return self.data[index]
        else:
            raise IndexError("Index out of range")

    def front(self):
        if not self.empty():
            return self.data[0]
        else:
            raise IndexError("Vector is empty")

    def back(self):
        if not self.empty():
            return self.data[-1]
        else:
            raise IndexError("Vector is empty")
