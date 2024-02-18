import inspect
import pickle
from typing import Any
import numpy as np
import pandas as pd
import pyarrow as pa
from ds_capability.intent.common_intent import CommonsIntentModel
from ds_core.handlers.abstract_handlers import HandlerFactory
from ds_capability.intent.abstract_automl_intent import AbstractAutoMLIntentModel

__author__ = 'Darryl Oatridge'


class AutoMLIntent(AbstractAutoMLIntentModel, CommonsIntentModel):

    TRAIN_INTENT_LEVEL = 'train_level'
    PREDICT_INTENT_LEVEL = 'predict_level'

    def label_predict(self, canonical: pa.Table, model_name: str, *, id_header: str=None, save_intent: bool=None,
                      intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                      remove_duplicates: bool=None):
        """ Retrieves a trained model and applies it to the canonical, returning the canonical with prediction labels.
        This assumes a trained model with a predict function. if an ``id_header`` name is given, that column will be
        removed from the feature and reapplied with the predictions.

        :param canonical: the model canonical
        :param model_name: a unique name for the model
        :param id_header: (optional) the name of a header that is not a feature that uniquely identifies each row
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: the canonical with a prediction.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        if self._pm.has_connector(model_name):
            canonical = self._get_canonical(canonical)
            handler = self._pm.get_connector_handler(model_name)
            model = handler.load_canonical()
            model = model.column(model_name).combine_chunks()
            model = pickle.loads(model[0].as_py())
            _id = None
            if isinstance(id_header, str) and id_header in canonical.column_names:
                _id = canonical.column(id_header).combine_chunks()
                canonical = canonical.drop_columns(id_header)
            features = np.asarray(canonical)
            score = model.predict(features).ravel()
            if isinstance(_id, pa.Array):
                return pa.table([_id, score], names=[id_header, 'predict'])
            return pa.table([score], names=['predict'])
        raise FileNotFoundError("The trained model cannot be found. Ensure the trained model has been added.")

