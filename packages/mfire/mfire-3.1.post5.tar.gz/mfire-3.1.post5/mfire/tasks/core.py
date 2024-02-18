""" core.py

Core "binary" file
Compute risks and texts and exports them to JSON
"""

from mfire.production import ProductionManager
from mfire.settings import Settings, get_logger

# Own package imports
from mfire.tasks.CLI import CLI

LOGGER = get_logger(name="core.mod", bind="core")
# Logging

if __name__ == "__main__":
    # Arguments parsing
    args = CLI().parse_args()
    print(args)
    production_manager = ProductionManager.load(Settings().prod_config_filename)
    production_manager.compute(nproc=args.nproc)
