from ds_capability.components.controller import Controller
import os
import pyarrow as pa


def run_repo_pipeline(canonical: pa.Table, repo_path: str, run_book: [str, list, dict]=None,
                      repeat: int=None, sleep: int=None, run_time: int=None, source_check_uri: str=None,
                      run_cycle_report: str=None, **kwargs):
    """"""
    for key, value in kwargs.items():
        key = key.upper()
        if key.startswith('HADRON_'):
            os.environ[key] = value

    controller = Controller.from_env(uri_pm_repo=repo_path, has_contract=False)

    controller.set_source_uri('event://internal_repo_pipeline/')
    controller.save_canonical(connector_name=Controller.CONNECTOR_SOURCE, canonical=canonical)
    controller.set_persist_uri('event://internal_repo_pipeline/')

    controller.run_controller(run_book=run_book, repeat=repeat, sleep=sleep, run_time=run_time,
                              source_check_uri=source_check_uri, run_cycle_report=run_cycle_report)
    # clean out environs
    for key in kwargs.keys():
        key = key.upper()
        if key in os.environ:
            del os.environ[key]

    return controller.load_canonical(connector_name=Controller.CONNECTOR_PERSIST, drop=True)

