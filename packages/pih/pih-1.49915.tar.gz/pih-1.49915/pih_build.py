import ipih

from build_tools import build
from pih import A
from pih.tools import js

NAME: str = A.NAME

def build_main() -> None:
    build(NAME, js((NAME.upper(), "module")), A.V.value, ["consts"])


if __name__ == "__main__":
    build_main()