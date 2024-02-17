from blacksheep import FromJSON, FromText
from blacksheep.server.controllers import ApiController, get, post
from requests import Session
from typing import Any, Optional

from . import IExecutionService, executionhttpdocs
from ..model.function import FunctionProfile
from ..docs import docs


class ExecutionHttpServer(ApiController):
    def __init__(self, svr: IExecutionService) -> None:
        self._svr = svr
        super().__init__()

    @classmethod
    def route(cls) -> Optional[str]:
        return '/api/executions'

    @post("/runFn")
    @docs(executionhttpdocs.run_execution)
    async def run_execution(self, fn: FromJSON[FunctionProfile]) -> Any:
        function = FunctionProfile(body=fn.value.body,
                                   parameters=fn.value.parameters,
                                   result=fn.value.result)
        result = self._svr.execute_function(function)
        return result.to_dict_widget()

    @get("/tableData")
    @docs(executionhttpdocs.table_data)
    async def table_data(self, table: str, fromRow: int, n: int) -> Any:
        return self._svr.table_data(table, fromRow, n)

    @post("/createTable")
    @docs(executionhttpdocs.create_data)
    async def save_table(self, table_id: str, data: FromText):
        try:
            self._svr.save_table(table_id, data.value)
            return self.ok()
        except Exception as e:
            return self.bad_request(e)


class ExecutionHttpProxy(IExecutionService):
    def __init__(self, session: Session) -> None:
        self.session = session

    def execute_function(self, fn: FunctionProfile):
        return self.session.post('/api/executions/runFn/', params=[("fn", fn)])

    def table_data(self, table_id: str, from_row: int, n: int) -> str:
        params = [("table", table_id), ("fromRow", from_row), ("n", n)]
        return self.session.get('/api/executions/tableData/', params=params).content

    def save_table(self, table_id: str, data: str):
        params = [("table_id", table_id)]
        return self.session.post('/api/executions/createTable/', params=params, data=data)
