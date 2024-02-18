"""An entrypoint for creating and running tool sessions."""

import argparse
import asyncio
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Type

from numerous.data_model import dump_data_model
from numerous.generated.graphql import Client
from numerous.session import Session, get_client_id
from numerous.utils import ToolT

log = logging.getLogger(__name__)


def read_tool_definition(tool_module: Path, tool_class: str) -> Any:  # noqa: ANN401
    scope: dict[str, Any] = {}
    module_text = tool_module.read_text()
    exec(module_text, scope)  # noqa: S102
    return scope[tool_class]


def print_tool(cls: Type[ToolT]) -> None:
    data_model = dump_data_model(cls)
    print(json.dumps(asdict(data_model)))  # noqa: T201


async def run_tool_session(
    graphql_url: str,
    graphql_ws_url: str,
    session_id: str,
    tool_module: Path,
    tool_class: str,
) -> None:
    gql = Client(graphql_url, ws_url=graphql_ws_url)
    tool_cls = read_tool_definition(tool_module, tool_class)
    client_id = get_client_id()
    session = await Session.initialize(session_id, client_id, gql, tool_cls)
    log.info("running %s:%s in session %s", tool_module, tool_class, session_id)
    await session.run()
    log.info("tool session stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    shared_parser = argparse.ArgumentParser()
    shared_parser.add_argument("module_path", type=Path)
    shared_parser.add_argument("class_name")

    cmd_parsers = parser.add_subparsers(title="Command", dest="cmd")
    read_parser = cmd_parsers.add_parser(
        "read",
        parents=[shared_parser],
        add_help=False,
    )
    run_parser = cmd_parsers.add_parser("run", parents=[shared_parser], add_help=False)
    run_parser.add_argument("--graphql-url", required=True)
    run_parser.add_argument("--graphql-ws-url", required=True)
    run_parser.add_argument("session_id")

    ns = parser.parse_args()

    if ns.cmd == "read":
        tool_cls = read_tool_definition(ns.module_path, ns.class_name)
        print_tool(tool_cls)
    elif ns.cmd == "run":
        asyncio.run(
            run_tool_session(
                ns.graphql_url,
                ns.graphql_ws_url,
                ns.session_id,
                ns.module_path,
                ns.class_name,
            ),
        )
    else:
        print(f"Unsupported command {ns.cmd!r}")  # noqa: T201
        sys.exit(1)
