""" collection of logging handlers sub-package """
# If DBUtils is not available, e.g., we're in kubernetes, simply ignore this import
try:
    from .splunk_databricks import get_splunk_handler_databricks
except ModuleNotFoundError as excp:
    assert "pyspark.dbutils" in str(excp)

from .splunk_handler import SplunkHandler
