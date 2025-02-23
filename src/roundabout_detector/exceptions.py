from src.roundabout_detector.utils import global_logger


class TableUnavailableException(Exception):
    """Custom exception raised when a requested table is not found in the database."""
    def __init__(self, table_name, message="Table not found in the database"):
        global_logger.error(f"Missing table: {table_name}, aborting..")
        self.table_name = table_name
        self.message = f"{message}: {table_name}"
        super().__init__(self.message)
