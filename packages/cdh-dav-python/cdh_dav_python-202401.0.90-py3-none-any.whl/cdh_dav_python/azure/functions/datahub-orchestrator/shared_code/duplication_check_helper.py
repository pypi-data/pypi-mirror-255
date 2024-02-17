import json

from shared_code import datalake_helper, app_config, app_utils


def has_file_been_processed_already(file_name: str, md5_hash: str, data_source: str):
    journal_file_name = f"{data_source}{app_config.DUPLICATE_JOURNAL_FILE_SUFFIX}"
    config_json = datalake_helper.get_json_file(file_system=app_config.DATAHUB_JOURNALS_LOCATION,
                                                file_name=journal_file_name)
    if config_json is None:
        config_json = []

    # journals = config_json["journals"]
    for item in config_json:
        item_md5_hash = item["md5_hash"]
        item_file_name = item["file_name"]
        if item_md5_hash.casefold() == md5_hash.casefold():
            return True, item_file_name

    config_json.append({"md5_hash": md5_hash, "file_name": file_name, "picked_up_at": app_utils.utc_now_formatted()})
    datalake_helper.save_file(data=json.dumps(config_json), file_system=app_config.DATAHUB_JOURNALS_LOCATION,
                              file_name=journal_file_name)

    return False, file_name
