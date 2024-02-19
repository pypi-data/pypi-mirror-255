from pih import A, PIH, OutputStub
from pih.tools import n, nl, ne, nn, e, j, js, jnl
from typing import Any

output_stub: OutputStub = OutputStub()
    
class Stub(PIH):
    def arg(self) -> Any | None:
        return self.session.arg()


self: Stub = Stub()
b = output_stub.b
i = output_stub.i


def execute(file_search_request: str) -> None:
    with A.ER.detect_interruption():
        A.R_F.execute(
            file_search_request,
            parameters={"self": self},
            stdout_redirect=False,
            catch_exceptions=True,
        )
        
def execute_file(use_authentification: bool, title: str | None, file_search_request: str) -> None:
    A.O.init()
    if not use_authentification or A.SE.authenticate():
        A.O.clear_screen()
        A.O.pih_title()
        if ne(title):
            A.O.head1(title)
        execute(file_search_request)
    A.SE.exit(0, "Выход")
