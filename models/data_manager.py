class DataManager:
    def __init__(self, path: str):
        self.path = path
        self._incomes = []
        self._expenses = []
        self._budgets = []

    def load(self):
        # no real file I/O yet — placeholder
        return

    def save(self):
        # no real file I/O yet — placeholder
        return

    def get_incomes(self):
        return self._incomes

    def get_expenses(self):
        return self._expenses

    def get_budgets(self):
        return getattr(self, '_budgets', [])