""" process_config.py

Configuration proccessing "binary" file
Processes a "global" configuration file and, given a production date, infers
"version", "data", "mask" and "production" configurations
"""

from mfire.configuration.config_metronome_processor import ConfigMetronomeProcessor
from mfire.settings import Settings
from mfire.tasks.CLI import CLI

if __name__ == "__main__":
    # Arguments parsing
    args = CLI().parse_args()
    print(args)

    # Filenames
    settings = Settings()

    # Running the config processor
    config_processor = ConfigMetronomeProcessor(
        config_filename=settings.config_filename,
        rules=args.rules,
        drafting_datetime=args.draftdate,
        experiment=args.experiment,
    )
    # Retrieving processed configs
    config_processor.process_all(nproc=args.nproc)

    # Dumping configs
    config_processor.dump_configs(settings)
