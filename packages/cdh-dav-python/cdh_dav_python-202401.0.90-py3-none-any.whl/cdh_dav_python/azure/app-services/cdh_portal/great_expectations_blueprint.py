import os

from flask import Blueprint, render_template_string
from flask import render_template, request

from shared_code import session_helper, datalake_helper

great_expectations_page = Blueprint('great_expectations', __name__,
                                    template_folder='templates')


@great_expectations_page.route('/great-expectations-summary', methods=["GET"])
def great_expectations_summary():
    session_helper.set_session_variables()
    path = "work/great-expectations/"
    data_sources_full_path = datalake_helper.get_all_sub_directories_in_directory(path)
    data_sources = []
    for data_source in data_sources_full_path:
        data_sources.append(data_source.casefold().replace(path.casefold(),""))
    data_sources.sort()
    return render_template('great_expectations/summary.html',
                           data_sources=data_sources)

@great_expectations_page.route('/great-expectations/<data_source>/<path:text>', methods=["GET"])
def great_expectations(data_source: str, text: str):
    session_helper.set_session_variables()
    if text.casefold().startswith("validations") or text.casefold().startswith("expectations"):
        file_name = os.path.basename(text)
        dir_path = os.path.dirname(text)
        path = f"work/great-expectations/{data_source}/data_docs/local_site/" + dir_path
        raw_html = datalake_helper.get_raw_file(file_system=path, file_name=file_name)
    else:
        path = f"work/great-expectations/{data_source}/data_docs/local_site"
        raw_html = datalake_helper.get_raw_file(file_system=path, file_name=f"index.html")

    return render_template_string(raw_html)
