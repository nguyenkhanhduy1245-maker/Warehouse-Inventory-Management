class TransactionStack:
    def __init__(self):
        self.stack = []

    def push_transaction(self, transaction):
        self.stack.append(transaction)

    def undo_last(self):
        if self.stack:
            return self.stack.pop()
        return None