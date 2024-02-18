#!/usr/bin/env python
"""Annotate module

Take in items, convert to histograms, annotate,
visualise histo mask, save the exported annotation .parquet

N.B. Preprocess just converts to datastructure
It is annotate that converts to image etc.
i.e. preprocess doesn't assume histogram
Therefore, for scripts which use image info such as x pixel they need to
take in the annotate parquets
"""

import yaml
import os
from locpix.preprocessing import datastruc

# from locpix.visualise import vis_img
import argparse
from locpix.scripts.preprocessing import annotate_config
import json
import time
import numpy as np

# import numpy as np


def main():

    parser = argparse.ArgumentParser(
        description="Annotate the data."
        "If no args are supplied will be run in GUI mode"
    )
    parser.add_argument(
        "-i",
        "--project_directory",
        action="store",
        type=str,
        help="the location of the project directory",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        type=str,
        help="the location of the .yaml configuaration file\
                             for preprocessing",
    )
    parser.add_argument(
        "-m",
        "--project_metadata",
        action="store_true",
        help="check the metadata for the specified project and" "seek confirmation!",
    )
    parser.add_argument(
        "-r",
        "--relabel",
        action="store_true",
        default=False,
        help="If true will relabel and assume labels are present (default = False)",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="if true then will overwrite files"
    )

    args = parser.parse_args()

    # if want to run in headless mode specify all arguments
    if args.project_directory is None and args.config is None:
        config, project_folder = annotate_config.config_gui()

    if args.project_directory is not None and args.config is None:
        parser.error(
            "If want to run in headless mode please supply arguments to"
            "config as well"
        )

    if args.config is not None and args.project_directory is None:
        parser.error(
            "If want to run in headless mode please supply arguments to project"
            "directory as well"
        )

    # headless mode
    if args.project_directory is not None and args.config is not None:
        project_folder = args.project_directory
        # load config
        with open(args.config, "r") as ymlfile:
            config = yaml.safe_load(ymlfile)
            annotate_config.parse_config(config)

    metadata_path = os.path.join(project_folder, "metadata.json")
    with open(
        metadata_path,
    ) as file:
        metadata = json.load(file)
        # check metadata
        if args.project_metadata:
            print("".join([f"{key} : {value} \n" for key, value in metadata.items()]))
            check = input("Are you happy with this? (YES)")
            if check != "YES":
                exit()
        # add time ran this script to metadata
        file = os.path.basename(__file__)
        if file not in metadata:
            metadata[file] = time.asctime(time.gmtime(time.time()))
        else:
            print("Overwriting metadata...")
            metadata[file] = time.asctime(time.gmtime(time.time()))
        with open(metadata_path, "w") as outfile:
            json.dump(metadata, outfile)

    # list items
    if args.relabel:
        input_folder = os.path.join(project_folder, "annotate/annotated")
    else:
        input_folder = os.path.join(project_folder, "preprocess/no_gt_label")
    print(input_folder)
    try:
        files = os.listdir(input_folder)
    except FileNotFoundError:
        raise ValueError("There should be some preprocessed files to open")

    # if output directory not present create it
    output_folder = os.path.join(project_folder, "annotate/annotated")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # if output directory not present create it
    markers_folder = os.path.join(project_folder, "markers")
    if not os.path.exists(markers_folder):
        os.makedirs(markers_folder)

    # if output directory for seg imgs not present create it
    # output_seg_folder = os.path.join(project_folder, "annotate/seg_imgs")
    # if not os.path.exists(output_seg_folder):
    #     os.makedirs(output_seg_folder)

    if config["dim"] == 2:
        histo_size = (config["x_bins"], config["y_bins"])
    elif config["dim"] == 3:
        histo_size = (config["x_bins"], config["y_bins"], config["z_bins"])
    else:
        raise ValueError("Dim should be 2 or 3")

    for file in files:
        item = datastruc.item(None, None, None, None, None)

        item.load_from_parquet(os.path.join(input_folder, file))

        # check if file already present and annotated
        # note assumptions
        # 1. assumes name convention of save_to_parquet is
        # os.path.join(save_folder, self.name + '.parquet')
        parquet_save_loc = os.path.join(output_folder, item.name + ".parquet")
        # seg_save_loc = os.path.join(output_seg_folder, item.name + ".png")
        if args.force or args.relabel:
            go_ahead = True
        if os.path.exists(parquet_save_loc) and not go_ahead:
            print(f"Skipping file as already present: {parquet_save_loc}")
            continue
        # if os.path.exists(seg_save_loc) and not args.force:
        #    print(f"Skipping file as already present: {seg_save_loc}")
        #    continue

        # coord2histo
        item.coord_2_histo(histo_size, vis_interpolation=config["vis_interpolation"])

        # markers loc
        markers_loc = os.path.join(markers_folder, item.name + ".npy")

        # manual segment
        markers = item.manual_segment(relabel=args.relabel, markers_loc=markers_loc)

        # save markers
        np.save(markers_loc, markers)

        # save df to parquet with mapping metadata
        item.save_to_parquet(
            output_folder,
            drop_zero_label=config["drop_zero_label"],
            gt_label_map=config["gt_label_map"],
            overwrite=args.relabel,
        )

        # convert to histo
        # histo, channel_map, label_map = item.render_histo([config["channel"]])

        # img = np.transpose(histo, (0, 2, 1))

        # save images
        # if config["save_img"] is True:
        #     # only visualise one channel
        #     vis_img.visualise_seg(
        #         img,
        #         item.histo_mask.T,
        #         item.bin_sizes,
        #         axes=[0],
        #         label_map=label_map,
        #         threshold=config["save_threshold"],
        #         how=config["save_interpolate"],
        #         alphas=config["alphas"],
        #         blend_overlays=False,
        #         alpha_seg=config["alpha_seg"],
        #         cmap_img=None,
        #         cmap_seg=config["cmap_seg"],
        #         figsize=config["fig_size"],
        #         origin="upper",
        #         save=True,
        #         save_loc=seg_save_loc,
        #         four_colour=config["four_colour"],
        #         background_one_colour=config["background_one_colour"],
        #     )

    # save yaml file
    yaml_save_loc = os.path.join(project_folder, "annotate.yaml")
    with open(yaml_save_loc, "w") as outfile:
        yaml.dump(config, outfile)


if __name__ == "__main__":
    main()
