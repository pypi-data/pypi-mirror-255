from __future__ import annotations

import os
import pickle
from typing import Any
import pyarrow as pa
from ds_core.handlers.abstract_handlers import ConnectorContract

from ds_capability.components.abstract_common_component import AbstractCommonComponent
from ds_capability.intent.automl_intent import AutoMLIntent
from ds_capability.managers.automl_property_manager import AutoMLPropertyManager


__author__ = 'Darryl Oatridge'


class AutoML(AbstractCommonComponent):

    @classmethod
    def from_uri(cls, task_name: str, uri_pm_path: str, creator: str, uri_pm_repo: str=None, pm_file_type: str=None,
                 pm_module: str=None, pm_handler: str=None, pm_kwargs: dict=None, default_save=None,
                 reset_templates: bool=None, template_path: str=None, template_module: str=None,
                 template_source_handler: str=None, template_persist_handler: str=None, align_connectors: bool=None,
                 default_save_intent: bool=None, default_intent_level: bool=None, order_next_available: bool=None,
                 default_replace_intent: bool=None, has_contract: bool=None) -> AutoML:
        """ Class Factory Method to instantiates the components application. The Factory Method handles the
        instantiation of the Properties Manager, the Intent Model and the persistence of the uploaded properties.
        See class inline docs for an example method

         :param task_name: The reference name that uniquely identifies a task or subset of the property manager
         :param uri_pm_path: A URI that identifies the resource path for the property manager.
         :param creator: A user name for this task activity.
         :param uri_pm_repo: (optional) A repository URI to initially load the property manager but not save to.
         :param pm_file_type: (optional) defines a specific file type for the property manager
         :param pm_module: (optional) the module or package name where the handler can be found
         :param pm_handler: (optional) the handler for retrieving the resource
         :param pm_kwargs: (optional) a dictionary of kwargs to pass to the property manager
         :param default_save: (optional) if the configuration should be persisted. default to 'True'
         :param reset_templates: (optional) reset connector templates from environ variables. Default True
                                (see `report_environ()`)
         :param template_path: (optional) a template path to use if the environment variable does not exist
         :param template_module: (optional) a template module to use if the environment variable does not exist
         :param template_source_handler: (optional) a template source handler to use if no environment variable
         :param template_persist_handler: (optional) a template persist handler to use if no environment variable
         :param align_connectors: (optional) resets aligned connectors to the template. default Default True
         :param default_save_intent: (optional) The default action for saving intent in the property manager
         :param default_intent_level: (optional) the default level intent should be saved at
         :param order_next_available: (optional) if the default behaviour for the order should be next available order
         :param default_replace_intent: (optional) the default replace existing intent behaviour
         :param has_contract: (optional) indicates the instance should have a property manager domain contract
         :return: the initialised class instance
         """
        pm_file_type = pm_file_type if isinstance(pm_file_type, str) else 'parquet'
        pm_module = pm_module if isinstance(pm_module, str) else 'ds_capability.handlers.pyarrow_handlers'
        pm_handler = pm_handler if isinstance(pm_handler, str) else 'PyarrowPersistHandler'
        creator = creator if isinstance(creator, str) else 'Unknown'
        _pm = AutoMLPropertyManager(task_name=task_name, creator=creator)
        _intent_model = AutoMLIntent(property_manager=_pm, default_save_intent=default_save_intent,
                                     default_intent_level=default_intent_level,
                                     order_next_available=order_next_available,
                                     default_replace_intent=default_replace_intent)
        super()._init_properties(property_manager=_pm, uri_pm_path=uri_pm_path, default_save=default_save,
                                 uri_pm_repo=uri_pm_repo, pm_file_type=pm_file_type, pm_module=pm_module,
                                 pm_handler=pm_handler, pm_kwargs=pm_kwargs, has_contract=has_contract)
        return cls(property_manager=_pm, intent_model=_intent_model, default_save=default_save,
                   reset_templates=reset_templates, template_path=template_path, template_module=template_module,
                   template_source_handler=template_source_handler, template_persist_handler=template_persist_handler,
                   align_connectors=align_connectors)

    @property
    def pm(self) -> AutoMLPropertyManager:
        return self._component_pm

    @property
    def intent_model(self) -> AutoMLIntent:
        return self._intent_model

    @property
    def tools(self) -> AutoMLIntent:
        return self._intent_model

    def add_trained_model(self, model_name: str, trained_model: Any,  uri: str=None, save: bool=None):
        """ A utility method to save the trained model ready for prediction.

        :param model_name: a unique name for the model.
        :param trained_model: model object that has been trained
        :param uri: a direct uri for the model persistence
        :param save: (optional) override of the default save action set at initialisation.
        """
        byte_model = result = pa.array([pickle.dumps(trained_model)], type=pa.binary())
        tbl = pa.table([byte_model], names=[model_name])
        if not isinstance(uri, str):
            uri_file =  self.pm.file_pattern(name=model_name, file_type='parquet', versioned=True)
            template = self.pm.get_connector_contract(connector_name=self.pm.TEMPLATE_PERSIST)
            uri = os.path.join(template.raw_uri, uri_file)
        self.add_connector_uri(connector_name=model_name, uri=uri, save=save)
        self.persist_canonical(connector_name=model_name, canonical=tbl)
        return

    def get_trained_model(self, model_name) -> Any:
        """ Retrieves a named trained model.

        :param model_name: The name of the model
        :return: The model class
        """
        if self.pm.has_connector(model_name):
            handler = self.pm.get_connector_handler(model_name)
            model = handler.load_canonical()
            model = model.column(model_name).combine_chunks()
            return pickle.loads(model[0].as_py())
        raise FileNotFoundError("The trained model cannot be found.")



