import json
import subprocess
import re
import argparse

import jsonschema
from jsonschema import validate


def validate_data(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as err:
        print(f"Validation error: {err.message}")
        return False


def validate_files(inventory_file, rules_file) -> dict:
    # Load the schema files
    with open("src/schema/inventory.json", "r") as inv_schema_file, open(
        "src/schema/rules.json", "r"
    ) as rules_schema_file:
        inventory_schema = json.load(inv_schema_file)
        rules_schema = json.load(rules_schema_file)

    # Load and validate the inventory file
    with open(inventory_file, "r") as inv_file:
        inventory_data = json.load(inv_file)
        if not validate_data(inventory_data, inventory_schema):
            print(f"Validation of {inventory_file} failed.")
            return None

    # Load and validate the rules file
    with open(rules_file, "r") as rule_file:
        rules_data = json.load(rule_file)
        if not validate_data(rules_data, rules_schema):
            print(f"Validation of {rules_file} failed.")
            return None

    print("Validation successful.")
    return {"inventory": inventory_data, "rules": rules_data}


def run_command(command):
    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None
    return output


def process_inventory(inventory_cfg):
    output = run_command(inventory_cfg.get("command"))
    # Logic to extract items based on the output pattern (e.g., regex).
    # Assuming the command returns items line by line for simplicity:
    return [s for s in output.split(inventory_cfg.get("matchPattern")) if s.strip()]


def process_rule(rule_cfg, inventory):
    failed_items = []
    for item in inventory:
        cmd = rule_cfg.get("cmd")
        pattern = rule_cfg.get("pattern")
        formatted_command = cmd.replace(
            "{{" + rule_cfg.get("primary_input_name") + "}}", item
        )
        if rule_cfg.get("pattern_is_shell", False) is True:
            formatted_command = formatted_command + "|" + rule_cfg.get("pattern")
        print(f"Running command: {formatted_command}")
        output = run_command(formatted_command)

        if rule_cfg.get("pattern_is_shell", False) is False:
            if re.search(pattern, output):
                print(f"{pattern=} found in {output}")
                failed_items.append(item)
        elif len(output) > 0:
            failed_items.append(item)
    return failed_items


def main():
    parser = argparse.ArgumentParser(
        description="Process and evaluate rules against inventory."
    )
    parser.add_argument(
        "inventory_file", type=str, help="Path to the inventory JSON file"
    )
    parser.add_argument("rules_file", type=str, help="Path to the rules JSON file")
    args = parser.parse_args()

    data = validate_files(args.inventory_file, args.rules_file)

    # Cache inventories to avoid running the
    # same inventory command multiple times
    inventories = {}

    for rule in data.get("rules", []):
        if rule.get("skip", True):
            continue
        inventory_id = rule["inventoryId"]

        if inventory_id not in inventories:
            inventory_cfg = next(
                (ic for ic in data["inventory"] if ic["id"] == inventory_id), None
            )
            if not inventory_cfg:
                print(f"Inventory command for ID {inventory_id} not found.")
                continue
            inventories[inventory_id] = process_inventory(inventory_cfg)
            print(
                f"Inventory processed for {inventory_id} "
                f"using {inventory_cfg.get('command')} and "
                f"acquired {len(inventories[inventory_id])} items."
            )

        failed_items = process_rule(rule, inventories[inventory_id])
        print(f"Rule: {rule['name']}")
        print(f"Failed items: {failed_items}")
        print("----------------------")


if __name__ == "__main__":
    main()
