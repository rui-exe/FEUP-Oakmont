import happybase
from app.core.config import settings
from collections.abc import Generator
from typing import Annotated
from fastapi import Depends

def get_hbase_connection() -> Generator[happybase.Connection, None, None]:
  """
    Get a HBase session
  """
  connection =  happybase.Connection(host=settings.HBASE_HOST, port=settings.HBASE_PORT)
  yield connection
  connection.close()

HBase = Annotated[happybase.Connection, Depends(get_hbase_connection)]
