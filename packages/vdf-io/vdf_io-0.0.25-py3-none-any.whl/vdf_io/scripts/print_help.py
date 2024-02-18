import argparse
import subprocess
import sys

from vdf_io.export_vdf.vdb_export_cls import ExportVDB

# Define the commands and their subcommands
db_choices = [c.DB_NAME_SLUG for c in ExportVDB.__subclasses__()]
commands = {
    "export_vdf": db_choices,
    "import_vdf": db_choices,
}

# Create or clear the output file
output_file = "help_output.txt"
with open(output_file, "w") as f:
    pass

# Run the help command for each command and subcommand
for command, subcommands in commands.items():
    with open(output_file, "a") as f:
        f.write(f"Help for '{command}':\n")
        subprocess.run([sys.executable, command, "--help"], stdout=f)
        f.write("\n")

        for subcommand in subcommands:
            f.write(f"Help for '{command} {subcommand}':\n")
            subprocess.run([sys.executable, command, subcommand, "--help"], stdout=f)
            f.write("\n")

print(f"Help output has been written to {output_file}")