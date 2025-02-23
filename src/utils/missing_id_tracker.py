class MissingIDTracker:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MissingIDTracker, cls).__new__(cls)
            cls._instance._missing_ids = []
        return cls._instance

    def add_missing_id(self, id):
        """Adds an ID to the list if it's not already present."""
        if id not in self._missing_ids:
            self._missing_ids.append(id)

    def get_missing_ids(self):
        """Returns the list of missing IDs."""
        return self._missing_ids

    def clear_missing_ids(self):
        """Clears the list of missing IDs."""
        self._missing_ids = []
