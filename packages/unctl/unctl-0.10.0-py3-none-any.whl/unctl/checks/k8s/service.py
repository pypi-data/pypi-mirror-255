import subprocess
from typing import List
from tempfile import NamedTemporaryFile
import asyncio


# FIXME; we need to implement dict based execution here
async def execute_k8s_cli(cmd: str) -> str:
    c = cmd.split()
    proc = await asyncio.create_subprocess_exec(
        *c, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    stdout, stderr = await proc.communicate()

    if stderr:
        print(f"Error(executing command({cmd}) stderr: {stderr}")
        return ""
    return stdout.decode("utf-8")


def find_enclosed_outputs(s: str) -> List[str]:
    return s.split("```")


async def execute_k8s_clis(cmds: List[str]) -> dict[str, str]:
    result = {}

    script = NamedTemporaryFile(mode="w+t", delete=False)
    script.write("#!/bin/bash\n")
    for cmd in cmds:
        if cmd.find("<") != -1 or cmd.find(">") != -1:
            print(f"Skipping command: {cmd}")
            continue
        script.write("echo {{" + cmd + "}}\n")
        script.write("echo '''\n")
        script.write(cmd + "\n")
        script.write("echo '''\n")

    script.close()
    diagnostics = "bash " + script.name
    cli_output = await execute_k8s_cli(diagnostics)
    outputs = find_enclosed_outputs(cli_output)

    for i in range(0, len(outputs) - 1, 2):
        cli = outputs[i].lstrip("{").rstrip("}")
        result[cli] = outputs[i + 1]

    return result
