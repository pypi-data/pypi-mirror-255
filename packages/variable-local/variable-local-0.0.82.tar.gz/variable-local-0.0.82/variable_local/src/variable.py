from database_mysql_local.generic_crud import GenericCRUD
from language_local.lang_code import LangCode
from logger_local.LoggerLocal import Logger
from user_context_remote.user_context import UserContext
import time

from .constants import variable_local_logger_init_object

logger = Logger.create_logger(object=variable_local_logger_init_object)
cache_with_timeout = {}

class VariablesLocal(GenericCRUD):
    def __init__(self):
        super().__init__(default_schema_name="field", default_table_name="field_table",
                         default_view_table_name="field_view", default_id_column_name="variable_id")
        self.name2id_dict = {}
        self.clean_name2id_dict = {}
        self.id2name_dict = {}
        self.next_variable_id = 1
        variable_names_dict = self.load_variable_names_dict_from_variable_table()
        for variable_id in variable_names_dict:
            self.add(variable_id=variable_id,
                     variable_name=variable_names_dict[variable_id])

    def add(self, variable_id: int, variable_name: str) -> None:
        logger.start(object={'variable_id': variable_id,
                             'variable_name': variable_name})
        try:
            if variable_id is not None and variable_name is not None:
                self.name2id_dict[variable_name] = variable_id
                clean_var = variable_name.lower().replace("_", "").replace(" ", "")
                self.clean_name2id_dict[clean_var] = variable_id
                self.id2name_dict[variable_id] = variable_name
            # TODO: just make bad performance, seems that can be removed
            # self.cursor.execute("""INSERT INTO variable_table(variable_id, name) VALUES (%s, %s)""", [
            #                     variable_id, variable_name])
            # GenericCRUD(schema_name=VARIABLE_LOCAL_SCHEMA_NAME).insert(
            #     table_name='variable_table', json_data={'variable_id': variable_id, 'name': variable_name})
            # self.connector.commit()

        except Exception as exception:
            message = 'error: Failed to add variable'
            logger.exception(message, object=exception)
            logger.end()
            raise
        logger.end()

    def get_variable_id_by_variable_name(self, variable_name: str) -> int:
        logger.start(object={'variable_name': variable_name})
        # TODO unified_variable_name
        clean_var = variable_name.lower().replace("_", "").replace(" ", "")
        if variable_name in self.name2id_dict:  # just in case it's not there already
            self.clean_name2id_dict[clean_var] = self.name2id_dict[variable_name]

        variable_id = self.clean_name2id_dict.get(clean_var)
        logger.end(object={'variable_id': variable_id})
        return variable_id

    def get_variable_name_by_variable_id(self, variable_id: int) -> str:
        logger.start(object={'variable_id': variable_id})
        variable_name = self.id2name_dict[variable_id]
        logger.end(object={'variable_name': variable_name})
        logger.end(object={'variable_name': variable_name})
        return variable_name

    def get_variable_value_by_variable_name_and_lang_code(self, variable_name: str, lang_code: LangCode) -> str:
        logger.start(object={'lang_code': lang_code,
                             'variable_name': variable_name})
        variable_id = self.get_variable_id_by_variable_name(
            variable_name=variable_name)
        variable_value = self.get_variable_value_by_variable_id(
            lang_code=lang_code, variable_id=variable_id)
        logger.end(object={'variable_value': variable_value})
        return variable_value

    def set_variable_value_by_variable_id(self, variable_id: int, variable_value: str, profile_id: str,
                                          state_id: int) -> None:
        logger.start(object={'variable_id': variable_id,
                             'variable_value': variable_value, 'profile_id': profile_id})
        # TODO I believe we should keep more fields
        self.set_schema(schema_name='logger')
        data_json = {'variable_id': variable_id, 'variable_value_new': variable_value, 'profile_id': profile_id,
                     'state_id': state_id}
        self.insert(table_name='logger_table', data_json=data_json)
        logger.end()

    def get_variable_value_by_variable_id(self, variable_id: int, lang_code: LangCode, profile_id: int = None) -> str:
        timeout = 60  # seconds
        if (variable_id, lang_code, profile_id) in cache_with_timeout:
            if cache_with_timeout[(variable_id, lang_code, profile_id)]["time"] > time.time() - timeout:
                return cache_with_timeout[(variable_id, lang_code, profile_id)]["result"]

        logger.start(object={'lang_code': lang_code,
                             'variable_id': variable_id})

        self.set_schema(schema_name='logger')
        where = ("variable_id= %s AND variable_value_new IS NOT NULL " +
                 (f"AND profile_id= %s " if profile_id is not None else ""))
        params = (variable_id, profile_id) if profile_id is not None else (variable_id,)
        result = self.select_one_dict_by_where(view_table_name="logger_dialog_workflow_state_history_view",
                                               select_clause_value="variable_value_new",
                                               where=where, params=params, order_by="timestamp DESC")
        if not result:
            if profile_id is not None:
                return self.get_variable_value_by_variable_id(variable_id=variable_id, lang_code=lang_code)
            else:
                logger.warn(f"No variable value found for "
                            f"variable_id {variable_id}, lang_code {lang_code}, profile_id {profile_id}")
        variable_value = result.get("variable_value_new")
        cache_with_timeout[(variable_id, lang_code, profile_id)] = {"result": variable_value, "time": time.time()}
        logger.end(object={'variable_value': variable_value})
        return variable_value

    def load_variable_names_dict_from_variable_table(self, profile_id: int = None, person_id: int = None) -> dict:
        logger.start()
        self.set_schema(schema_name='field')
        if profile_id is None:
            user_context = UserContext.login_using_user_identification_and_password()
            profile_id = user_context.get_real_profile_id()
        rows = self.select_multi_dict_by_where(view_table_name="variable_view",
                                               where="person_id = %s or profile_id=%s OR profile_id IS NULL" if person_id is not None else "profile_id=%s OR profile_id IS NULL",
                                               params=(person_id, profile_id) if person_id is not None else (
                                                   profile_id,),
                                               select_clause_value="variable_id, name")
        data = {}
        for row in rows:
            data[row['variable_id']] = row['name']
        logger.end(object={'data': data})
        return data
