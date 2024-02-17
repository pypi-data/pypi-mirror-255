import json
from typing import Optional

import rich
from rich.console import Console
from rich.panel import Panel

from airfold_common.utils import grouped, is_kind


def print_plan(plan: list[dict], verbose: bool = False, console: Optional[Console] = None) -> None:
    console = console or rich.get_console()
    console.print("Execution plan:")
    if not plan:
        console.print("\t[magenta]NO CHANGES[/magenta]")
        return
    for i, cmd in enumerate(plan):
        name = ""
        new_name = ""
        kind = ""
        command = ""
        id = ""
        if cmd.get("cmd") in ["CREATE", "DELETE"]:
            sources = [o for o in cmd["args"] if is_kind(o, "Source")]
            pipes = [o for o in cmd["args"] if is_kind(o, "PipeEntry")]
            command = f"[cyan]{cmd['cmd']}[/cyan]"
            if sources:
                source = sources[0]
                name = f'"{source.get("name")}"'
                kind = source.get("type")
                id = f'[grey]{source["id"]}[/grey]'
            elif pipes:
                name = f'"{pipes[0].get("name")}"'
                kind = "pipe"
                id = f'[grey]{pipes[0]["id"]}[/grey]'
        elif cmd.get("cmd") == "DELETE":
            obj = cmd["args"][0]
            name = f"{obj.get('name')}"
            if is_kind(cmd["args"][0], "Source"):
                kind = obj.get("type")
            elif is_kind(obj, "PipeEntry"):
                kind = "pipe"
            new_name = f"{cmd['args'][1].get('name')}"
            command = f"[magenta]{cmd['cmd']}[/magenta]"
        elif cmd.get("cmd") == "REPLACE":
            kind = "view"
            name = cmd["args"][-1]["id"]
            command = f"[magenta]{cmd['cmd']}[/magenta]"
        elif cmd.get("cmd") == "UPDATE":
            tables = [o for o in cmd["args"] if is_kind(o, "Table") or is_kind(o, "AITable")]
            if tables:
                kind = "table"
                name = f'"{tables[0].get("name")}"'
                command = f"[magenta]{cmd['cmd']}[/magenta]"
            sources = [o for o in cmd["args"] if is_kind(o, "Source")]
            if sources:
                kind = "source"
                name = f'"{sources[0].get("name")}"'
                command = f"[magenta]{cmd['cmd']}[/magenta]"

        if cmd.get("cmd") == "DELETE":
            command = f"[red]{cmd['cmd']}[/red]"

        extended = ""
        if cmd.get("cmd") == "RENAME":
            extended = f"[magenta]->[/magenta] [bold]{new_name}[/bold]"

        title = command
        if cmd.get("cmd") == "CREATE":
            title += f" new_id={id}"
        elif cmd.get("cmd") == "DELETE":
            title += f" old_id={id}"

        content = f"{i + 1}\t[yellow]{kind}[/yellow] [bold]{name}[/bold] {extended}"
        console.print(Panel(content, title=title, title_align="left"))

        if verbose:
            if cmd.get("cmd") == "RENAME":
                for j, (obj, obj_to) in enumerate(grouped(cmd["args"], 2)):
                    console.print(
                        f"\t[bold]{obj.get('name', obj['id'])}[/bold]"
                        f" [magenta]->[/magenta] [bold]{obj_to.get('name', obj_to['id'])}[/bold]:\n"
                        f"\t{json.dumps(obj_to)}"
                    )
                    console.print("")
            else:
                args = reversed(cmd["args"]) if cmd.get("cmd") == "DELETE" else cmd["args"]
                for j, obj in enumerate(args):
                    if is_kind(obj, "Node") or is_kind(obj, "Pipe"):
                        continue
                    console.print(f"\t{json.dumps(obj)}")
            console.print("")
