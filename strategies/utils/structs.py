class Queue(object):
    '''队列'''

    def __init__(self, size):
        self.__list = []
        self.__size = size

    def enqueue(self, item):
        '''往队列中添加元素'''
        if self.full():
            self.dequeue()
        self.__list.append(item)

    def dequeue(self):
        '''从队列头部删除元素'''
        return self.__list.pop(0)

    def is_empty(self):
        '''判断列表是否为空'''
        return self.__list == []

    def size(self):
        '''返回列表的大小'''
        return len(self.__list)

    def full(self):
        return self.size() == self.__size

    def tolist(self):
        return self.__list