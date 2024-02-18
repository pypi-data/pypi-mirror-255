import os
from types import MappingProxyType
from string import Template

from unctl.constants import CheckProviders


def load_provider_instructions(provider: str):
    file_path = os.path.join(
        os.path.dirname(__file__), f"instructions/{provider.lower()}.txt"
    )

    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            return "\n".join(line.strip() for line in lines)
    except FileNotFoundError:
        raise Exception(f"Instruction for {provider} has not been created")


def load_group_instructions(provider: str):
    file_path = os.path.join(os.path.dirname(__file__), "instructions/group.txt")
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            group_instruction = "\n".join(line.strip() for line in lines)
            group_instruction = Template(group_instruction).safe_substitute(
                provider=str(provider)
            )
            return group_instruction
    except FileNotFoundError:
        raise Exception(f"Instruction for {provider} has not been created")


ASSISTANT = "assistant"
GROUP = "group"
REMEDIATION = "remediation"

ASSISTANTS = {
    CheckProviders.K8S: "k8s expert (unctl)",
    CheckProviders.MySQL: "MySQL expert (unctl)",
}

INSTRUCTIONS = {
    CheckProviders.K8S: {
        ASSISTANT: load_provider_instructions(CheckProviders.K8S.value),
        GROUP: load_group_instructions(CheckProviders.K8S.value),
    },
    CheckProviders.MySQL: {
        ASSISTANT: load_provider_instructions(CheckProviders.MySQL.value),
        GROUP: load_group_instructions(CheckProviders.MySQL.value),
    },
}

INSTRUCTIONS = MappingProxyType(INSTRUCTIONS)
ASSISTANTS = MappingProxyType(ASSISTANTS)
