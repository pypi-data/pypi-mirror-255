import argparse
import logging
from visionai_data_format.utils.validator import save_as_json, validate_bdd

import json
import logging
import os
from collections import defaultdict
from copy import deepcopy

from visionai_data_format.schemas.bdd_schema import AtrributeSchema, FrameSchema
from visionai_data_format.schemas.visionai_schema import VisionAI

from utils.calculation import xywh2xyxy
from utils.validator import save_as_json, validate_vai

logger = logging.getLogger(__name__)
VERSION = "00"


def convert_vai_to_bdd(
    folder_name: str,
    company_code: int,
    storage_name: str,
    container_name: str,
    annotation_name: str = "groundtruth"
) -> dict:
    if not os.path.exists(folder_name) or len(os.listdir(folder_name)) == 0:
        logger.info("[convert_vai_to_bdd] Folder empty or doesn't exits")
    else:
        logger.info("[convert_vai_to_bdd] Convert started")
    frame_list = list()
    for sequence_name in sorted(os.listdir(folder_name)):
        annotation_folder =  os.path.join(folder_name, sequence_name,"annotations", annotation_name)
        vai_data = open(os.path.join(annotation_folder, "visionai.json")).read()
        json_format = json.loads(vai_data)
        vai_data = validate_vai(json_format).visionai
        cur_frame_list = convert_vai_to_bdd_single(
            vai_data, sequence_name, storage_name, container_name
        )
        frame_list += cur_frame_list

    data = {"frame_list": frame_list, "company_code": company_code}
    logger.info("[convert_vai_to_bdd] Convert finished")
    if not frame_list:
        logger.info("[convert_vai_to_bdd] frame_list is empty")
    return data


def convert_vai_to_bdd_single(
    vai_data: VisionAI, sequence_name: str, storage_name: str, container_name: str, img_extension:str=".jpg", include_sensors:list = ["camera"]
) -> list:
    frame_list = list()
    # only support sensor type is camera for now
    # TODO converter for lidar annotation
    sensor_names = [sensor_name for sensor_name, sensor_content in vai_data.streams.items() if sensor_content.type in include_sensors]
    for frame_key, frame_data in vai_data.frames.items():
        sensor_frame = {}
        for sensor in sensor_names:
            frame_temp = FrameSchema(storage=storage_name, dataset=container_name, sequence= '/'.join([sequence_name,"data", sensor]),name=frame_key + img_extension, labels=[])
            sensor_frame[sensor] = frame_temp.dict()
        
        idx = 0
        objects = getattr(frame_data, "objects", None) or {}
        for obj_id, obj_data in objects.items():
            classes = vai_data.objects.get(obj_id).type
            bboxes = obj_data.object_data.bbox or [] if obj_data.object_data else []
            for bbox in bboxes:
                geometry = bbox.val
                sensor = bbox.stream
                label = dict()
                label["category"] = classes
                label["meta_ds"] = {}
                label["meta_se"] = {}
                x1, y1, x2, y2 = xywh2xyxy(geometry)
                box2d = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                if bbox.confidence_score is not None:
                    label["meta_ds"]["score"] = bbox.confidence_score
                label["box2d"] = box2d

                object_id = {
                    "project": "General",
                    "function": "General",
                    "object": classes,
                    "version": VERSION,
                }
                label["objectId"] = object_id
                label["attributes"] = AtrributeSchema(INSTANCE_ID=idx).dict()
                sensor_frame[sensor]["labels"].append(label)
                idx += 1
        for _, frame in sensor_frame.items():
            frame_list.append(frame)
    return frame_list


logger = logging.getLogger(__name__)





def vai_to_bdd(
    vai_src_folder: str,
    bdd_dest_file: str,
    company_code: int,
    storage_name: str,
    container_name: str,
    annotation_name:str
) -> None:
    try:
        bdd_data = convert_vai_to_bdd(
            folder_name=vai_src_folder,
            company_code=company_code,
            storage_name=storage_name,
            container_name=container_name,
            annotation_name=annotation_name
        )
        bdd = validate_bdd(data=bdd_data)
        save_as_json(bdd.dict(), file_name=bdd_dest_file)
    except Exception as e:
        logger.error("Convert vai to bdd format failed : " + str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-vai_src_folder",
        type=str,
        required=True,
        help="VisionAI format source folder path",
    )
    parser.add_argument(
        "-bdd_dest_file",
        type=str,
        required=True,
        help="BDD+ format destination file name (i.e : bdd_dest.json)",
    )
    parser.add_argument(
        "-company_code",
        type=int,
        required=True,
        help="Company code information for BDD+",
    )
    parser.add_argument(
        "-storage_name",
        type=str,
        required=True,
        help="Storage name information for BDD+",
    )
    parser.add_argument(
        "-container_name",
        type=str,
        required=True,
        help="Container name information for BDD+",
    )

    parser.add_argument(
        "-annotation_name",
        type=str,
        required=True,
        default="groundtruth",
        help="annotation folder name in VAI",
    )

    FORMAT = "%(asctime)s[%(process)d][%(levelname)s] %(name)-16s : %(message)s"
    DATEFMT = "[%d-%m-%Y %H:%M:%S]"

    logging.basicConfig(
        format=FORMAT,
        level=logging.DEBUG,
        datefmt=DATEFMT,
    )

    args = parser.parse_args()

    vai_to_bdd(
        args.vai_src_folder,
        args.bdd_dest_file,
        args.company_code,
        args.storage_name,
        args.container_name,
        args.annotation_name,
    )
