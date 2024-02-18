from flask import Blueprint
from flask import render_template, request

from shared_code import session_helper, datalake_helper, config_file_helper

datasets_config_page = Blueprint('datasets_config', __name__,
                                 template_folder='templates')


@datasets_config_page.route('/datasets', methods=["GET"])
def datasets():
    session_helper.set_session_variables()
    data_source = request.args.get('data_source')
    config_json = ""
    datasets = config_file_helper.get_all_configured_dataasets()
    if data_source is not None and len(data_source) > 0:
        config_json = datalake_helper.get_json_file(file_system="metadata/datahub/configs",
                                                    file_name=f"{data_source}_datahub_config.json")

    return render_template('datasets/config.html', config_json=config_json, datasets= datasets, selected_dataset=data_source)
