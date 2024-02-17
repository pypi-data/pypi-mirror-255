from __future__ import annotations
import pandas as pd
import pyarrow as pa
from ds_capability.components.commons import Commons
from ds_capability.intent.feature_select_intent import FeatureSelectIntent
from ds_capability.managers.feature_select_property_manager import FeatureSelectPropertyManager
from ds_capability.components.abstract_common_component import AbstractCommonComponent

__author__ = 'Darryl Oatridge'


class FeatureSelect(AbstractCommonComponent):

    @classmethod
    def from_uri(cls, task_name: str, uri_pm_path: str, creator: str, uri_pm_repo: str=None, pm_file_type: str=None,
                 pm_module: str=None, pm_handler: str=None, pm_kwargs: dict=None, default_save=None,
                 reset_templates: bool=None, template_path: str=None, template_module: str=None,
                 template_source_handler: str=None, template_persist_handler: str=None, align_connectors: bool=None,
                 default_save_intent: bool=None, default_intent_level: bool=None, order_next_available: bool=None,
                 default_replace_intent: bool=None, has_contract: bool=None) -> FeatureSelect:
        """ Class Factory Method to instantiates the component's application. The Factory Method handles the
        instantiation of the Properties Manager, the Intent Model and the persistence of the uploaded properties.
        See class inline _docs for an example method

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
        pm_file_type = pm_file_type if isinstance(pm_file_type, str) else 'json'
        pm_module = pm_module if isinstance(pm_module, str) else cls.DEFAULT_MODULE
        pm_handler = pm_handler if isinstance(pm_handler, str) else cls.DEFAULT_PERSIST_HANDLER
        _pm = FeatureSelectPropertyManager(task_name=task_name, creator=creator)
        _intent_model = FeatureSelectIntent(property_manager=_pm, default_save_intent=default_save_intent,
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
    def pm(self) -> FeatureSelectPropertyManager:
        return self._component_pm

    @property
    def intent_model(self) -> FeatureSelectIntent:
        return self._intent_model

    @property
    def tools(self) -> FeatureSelectIntent:
        return self._intent_model

    def set_provenance(self, title: str=None, domain: str=None, description: str=None, license_type: str=None,
                       license_name: str=None, license_uri: str=None, cost_price: str = None, cost_code: str = None,
                       cost_type: str = None, provider_name: str=None, provider_uri: str=None, provider_note: str=None,
                       author_name: str=None, author_uri: str=None, author_contact: str=None, save: bool=None):
        """sets the provenance values. Only sets those passed

        :param title: (optional) the title of the provenance
        :param domain: (optional) the domain it sits within
        :param description: (optional) a description of the provenance
        :param license_type: (optional) The type of the license. Default 'ODC-By'
        :param license_name: (optional) The full name of the license. Default 'Open Data Commons Attribution License'
        :param license_uri: (optional) The license uri. Default https://opendatacommons.org/licenses/by/
        :param cost_price: (optional) a cost price associated with this provenance
        :param cost_code: (optional) a cost centre code or reference code
        :param cost_type: (optional) the cost type or description
        :param provider_name: (optional) the provider system or institution name or title
        :param provider_uri: (optional) a uri reference that helps identify the provider
        :param provider_note: (optional) any notes that might be useful
        :param author_name: (optional) the author of the data
        :param author_uri: (optional) the author uri
        :param author_contact: (optional)the the author contact information
        :param save: (optional) if True, save to file. Default is True
        """
        license_type = license_type if license_type else 'PDDL'
        license_name = license_name if license_name else 'Open Data Commons Attribution License'
        license_uri = license_uri if license_uri else 'https://opendatacommons.org/licenses/pddl/summary'

        self.pm.set_provenance(title=title, domain=domain, description=description, license_type=license_type,
                               license_name=license_name, license_uri=license_uri, cost_price=cost_price,
                               cost_code=cost_code, cost_type=cost_type, provider_name=provider_name,
                               provider_uri=provider_uri, provider_note=provider_note, author_name=author_name,
                               author_uri=author_uri, author_contact=author_contact)
        self.pm_persist(save=save)

    def reset_provenance(self, save: bool=None):
        """resets the provenance back to its default values"""
        self.pm.reset_provenance()
        self.pm_persist(save)

    def report_provenance(self, as_dict: bool=None, stylise: bool=None):
        """ a report on the provenance set as part of the domain contract

        :param as_dict: (optional) if the result should be a dictionary. Default is False
        :param stylise: (optional) if as_dict is False, if the return dataFrame should be stylised
        :return:
        """
        as_dict = as_dict if isinstance(as_dict, bool) else False
        stylise = stylise if isinstance(stylise, bool) else True
        report = self.pm.report_provenance()
        if as_dict:
            return report
        df = pd.DataFrame(report, index=['values'])
        df = df.transpose().reset_index()
        df.columns = ['provenance', 'values']
        if stylise:
            return Commons.report(df, index_header='provenance')
        return pa.Table.from_pandas(df)

