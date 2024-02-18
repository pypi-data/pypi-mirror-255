"""
DEV only. This module is used to request instance types from the inst-tagger service. We try to isolate the cod so it can be easily removed.
"""

import os
import requests
from ciocore import api_client

USE_INST_TAGGER = int(os.environ.get("CIO_FEATURE_USE_INST_TAGGER", 0))
SUPABASE_URL = os.environ.get("CIO_FEATURE_INST_TAGGER_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("CIO_FEATURE_INST_TAGGER_SUPABASE_KEY")

def request_supabase_data(table_name):
    HEADERS = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
    }

    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table_name}", headers=HEADERS, timeout=5
    )
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code, response.text)
        return None


def get_cloud(cio_inst_types):
    if not cio_inst_types:
        return None
    if cio_inst_types[0]["name"].startswith("cw-"):
        return "cw"
    elif "." in cio_inst_types[0]["name"]:
        return "aws"
    return "gcp"


def normalize_sb_inst_types(sb_inst_types):
    result = []
    for inst_type in sb_inst_types:
        el = inst_type["instance_type"].copy()
        el["id"] = inst_type["id"]
        result.append(el)
    return result


def to_id_dict(thelist):
    return {d["id"]: d for d in thelist}


def valid_inst_types():
    sb_inst_types = request_supabase_data("instance_types")
    sb_inst_types = normalize_sb_inst_types(sb_inst_types)

    cio_inst_types = api_client.request_instance_types()
    # print(json.dumps(cio_inst_types, indent=2))

    cloud = get_cloud(cio_inst_types)

    # filter out instance types that are not in the cloud

    sb_inst_types = [
        inst_type for inst_type in sb_inst_types if inst_type["cloud"] == cloud
    ]
    for it in sb_inst_types:
        it["cores"] = it["total_cpu"]
        it["memory"] = it["total_memory_gb"]

        cores = it["cores"]
        mem = it["memory_gb"]
        cpu_desc = f"{cores} cores, {mem} GB RAM"
        gpu_desc = ""
        if it["gpu"]:
            gpu_count = it["gpu"]["gpu_count"]
            gpu_model = it["gpu"]["gpu_model"]
            gpu_arch = it["gpu"]["gpu_architecture"]
            gpu_mem = it["gpu"]["total_gpu_memory"]
            gpu_desc = f" ({gpu_count}x {gpu_model} ({gpu_arch}) {gpu_mem} GB)"

        desc = f"{cpu_desc}{gpu_desc}"
        it["description"] = desc

    return sb_inst_types


def request_instance_types():
    """
    Request instance types from the inst-tagger service.

    Returns:
        list(dict): A list of instance types.
    """
    if not USE_INST_TAGGER:
        return None
    
    inst_types = valid_inst_types()

    tags = request_supabase_data("tags")
    tag_ids = [tag["id"] for tag in tags]
    tags_dict = to_id_dict(tags)

    assignments = request_supabase_data("assignments")
    assignments = [a for a in assignments if a["tag_id"] in tag_ids]


    # assign tags to instance types
    for inst_type in inst_types:
        inst_type["categories"] = []
        # find assignments relating to this instance type
        these_assignments = [
            a for a in assignments if a["instance_type_id"] == inst_type["id"]
        ]

        for assignment in these_assignments:
            tag = tags_dict[assignment["tag_id"]]
            inst_type["categories"].append({"label": tag["label"], "order": tag["order"]})

    return inst_types
