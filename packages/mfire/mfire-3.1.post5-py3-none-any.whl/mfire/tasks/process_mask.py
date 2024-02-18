""" process_mask.py

Mask proccessing "binary" file
"""
# Built-in imports
from pathlib import Path

import mfire.mask.mask_processor as mpr

# to prevent numpy to use multithreading
# ATTENTION : must be before numpy
import mfire.tasks.monothread as monothread  # noqa: F401

# third parties imports
import mfire.utils.mfxarray as xr

# own package imports
from mfire.settings import Settings, get_logger
from mfire.tasks.CLI import CLI
from mfire.utils import MD5, JsonFile, Parallel

# Logging
LOGGER = get_logger(name="process_mask.mod", bind="process_mask")


def main(conf: dict):
    """main : main function

    Args:
        conf (dict): Single mask configuration
    """
    # Quelques checks à faire au prealable
    do_something = True
    #  Si la conf contient le fichier on l'utilise.
    #  Sinon on suppose qu'on cree le fichier quoiqu'il arrive
    if "file" in conf:
        LOGGER.info("File is in the conf")
        output_file = Path(conf.get("file"))
        LOGGER.info(output_file)
        if output_file.is_file():
            LOGGER.info("File already exist")
            if "mask_hash" in conf:
                current_hash = conf.get("mask_hash")
            else:
                handler = MD5(conf["geos"])
                current_hash = handler.hash
            LOGGER.info("Current conf hash is %s", current_hash)
            ds = xr.open_dataset(output_file)
            if ds.attrs.get("md5sum", "") == current_hash:
                do_something = False
            else:
                LOGGER.info("Current hash is different from the one in the file")
            ds.close()
    if do_something:
        LOGGER.info("Launching mask creation")
        mask_handler = mpr.MaskProcessor(conf)
        mask_handler.create_masks()
    else:
        LOGGER.info(
            "Mask already exist and have the same md5sum. Mask creation is skipped."
        )
    LOGGER.info(f"Mask {output_file} has been created")


if __name__ == "__main__":
    # Argument parsing
    args = CLI().parse_args()
    print(args)

    dict_config = JsonFile(Settings().mask_config_filename).load()
    dict_bigger = {
        key: val
        for key, val in sorted(
            dict_config.items(),
            key=lambda ele: len(ele[1]["geos"]["features"]),
            reverse=True,
        )
    }
    dict_config = dict_bigger
    parallel = Parallel(processes=args.nproc)
    for name, conf in dict_config.items():
        parallel.apply(main, task_name=name, args=(conf,))
    parallel.run(timeout=Settings().timeout)
