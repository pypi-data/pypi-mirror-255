import random
import re
from datetime import datetime

from language_local.lang_code import LangCode
from logger_local.LoggerLocal import Logger
from smartlink_local.smartlink import SmartLinkLocal

from .constants import variable_local_logger_init_object
from .variable import VariablesLocal

logger = Logger.create_logger(object=variable_local_logger_init_object)

LEFT_BRACKETS = '{'
RIGHT_BRACKETS = '}'


class ReplaceFieldsWithValues:
    def __init__(self, message, language: LangCode, variable: VariablesLocal):
        self.message = message
        self.language = language
        self.variable = variable
        self.smartlink_local = None  # For performance reasons

    # TODO: Not used anymore. Remove?
    # Private method used by get_variable_names_and_chosen_option(self)
    # def choose_option(self, message_index: int, first_param: str) -> (str, int):
    #     """ Gets a message, an index of the first appearance of '|' , and the first parameter of the options
    #         Returns:
    #         1. One of the options randomly selected
    #         2. The index of one char after the next '}'"""
    #     logger.start(
    #         object={'message_index': message_index, 'first_param': first_param})
    #     list_of_params = [first_param]
    #     while self.message[message_index] != '}':
    #         next_param = ""
    #         while self.message[message_index] != '|' and self.message[message_index] != '}':
    #             next_param += self.message[message_index]
    #             message_index += 1
    #         list_of_params.append(next_param)
    #         if self.message[message_index] != '}':
    #             message_index += 1
    #     random_index = random.randint(0, len(list_of_params) - 1)
    #     random_option_selected, index = list_of_params[random_index], message_index + 1
    #     logger.end(object={'random_option_selected': random_option_selected, 'index': index})
    #     return random_option_selected, index

    @staticmethod
    def get_smartlink_url(smartlink_identifier: str) -> str:
        # TODO: move to url remote and improve
        return f"www.circ.zone?a={smartlink_identifier}"

    def get_smartlink(self, variable_name: str, **kwargs) -> str:
        self.smartlink_local = self.smartlink_local or SmartLinkLocal()
        smart_link_regex = r"smartLinkUrl\(smartLinkType=([0-9]+)\)"
        smartlink_type_id = re.search(smart_link_regex, variable_name).group(1)
        smartlink_details = self.smartlink_local.insert(smartlink_type_id=smartlink_type_id,
                                                        campaign_id=kwargs.get('campaign_id'),
                                                        from_recipient=kwargs.get('from_recipient'),
                                                        to_recipient=kwargs.get('to_recipient'))
        return self.get_smartlink_url(smartlink_details['smartlink_identifier'])

    def special_variable(self, variable_name: str, **kwargs) -> str:
        # TODO: use worker actions instead
        """Returns a special variable value by variable name"""
        logger.start(object={'variable_name': variable_name})
        smart_link_regex = r"smartLinkUrl\(smartLinkType=([0-9]+)\)"

        if variable_name == 'otp':
            variable_value = ReplaceFieldsWithValues.generate_otp()
        elif variable_name == 'date_sortable':
            variable_value = self.get_date_time()
        elif re.match(smart_link_regex, variable_name):
            variable_value = self.get_smartlink(variable_name, **kwargs)
        else:  # TODO: add more special variables
            logger.error("Error: unknown special variable name " + variable_name, object=kwargs)
            return ""
        logger.end(object={'variable_value': variable_value})
        return str(variable_value)

    @staticmethod
    def generate_otp():  # TODO: move to the appropriate place
        """Generates a 6-digit OTP"""
        logger.start()
        otp = random.randint(100000, 999999)
        logger.end(object={'otp': otp})
        return otp

    @staticmethod
    def get_date_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_variable_names_and_chosen_option(self, **kwargs) -> (list, str):
        """Returns:
            1. A list of all variable names that were inside curly braces of message
            2. A string that's a copy of the message but without the variable names inside curly braces,
            and a randomly chosen parameter out of each curly braces options:
            "Hello {First Name}, how are you {feeling|doing}?" --> "Hello {}, how are you doing?" 
        """
        logger.start(object={'kwargs': kwargs})
        kwargs_lower = {name.lower(): var_id for name, var_id in kwargs.get('kwargs', kwargs).items()}
        variable_names_list = []
        message_without_variable_names = kwargs.get("message", self.message)

        pattern = re.compile(r'\${{[^}]*}}')  # ${{vraiable}}
        matches = pattern.findall(message_without_variable_names)
        for exact_match in matches:
            match = exact_match[3:-2].strip()  # remove '${{' and '}}'
            clean_match = match.replace("_", "").replace(" ", "").lower()
            if '|' in match:  # # choose random option from {A|B|C}
                # pick random choice
                options = match.split('|')
                random_option = random.choice(options)
                message_without_variable_names = message_without_variable_names.replace(
                    exact_match, random_option, 1)

            elif match.lower() in kwargs_lower:
                message_without_variable_names = message_without_variable_names.replace(
                    exact_match, str(kwargs[match] if match in kwargs else kwargs_lower[match.lower()]), 1)

            elif clean_match in self.variable.clean_name2id_dict.keys():
                # replace variable name with '{}' and add variable names to list
                message_without_variable_names = message_without_variable_names.replace(exact_match, '{}', 1)
                variable_names_list.append(match)

            else:
                message_without_variable_names = message_without_variable_names.replace(
                    exact_match, self.special_variable(match, **kwargs), 1)

        return variable_names_list, message_without_variable_names

        # Old code:
        # For the following function to work the message must not have single '{' or '}'.
        # They should always come in pairs.
        #
        # message_without_variable_names = ""
        # message_index = 0
        # while message_index < len(self.message):
        #     index_after_choosing_option = None
        #     if self.message[message_index] == '{':
        #         message_index += 1
        #         next_variable_name = ""
        #         chosen_parameter = None
        #         while self.message[message_index] != '}':
        #             if self.message[message_index] == '|':
        #                 chosen_parameter, index_after_choosing_option = self.choose_option(
        #                     message_index + 1, next_variable_name)
        #                 break
        #             next_variable_name += self.message[message_index]
        #             message_index += 1
        #         if chosen_parameter is not None:
        #             message_without_variable_names += chosen_parameter
        #         elif next_variable_name:
        #             message_without_variable_names += "{}"
        #             variable_names_list.append(next_variable_name)
        #         else:  # error
        #             error = "Error: message has single '{' or '}' or empty variable name"
        #             logger.error(error)
        #             raise Exception(error)
        #
        #     else:
        #         message_without_variable_names += self.message[message_index]
        #     message_index = message_index + 1 if index_after_choosing_option is None \
        #         else index_after_choosing_option
        # logger.end(object={'variable_names_list': variable_names_list,
        #                    'message_without_variable_names': message_without_variable_names})
        # return variable_names_list, message_without_variable_names

    # Should be used both by Dialog workflow and message-local-python-package Message.py
    def get_variable_values_and_chosen_option(self, profile_id: int = None, **kwargs) -> str:
        """Returns:
            1. A list of all variable values by variable names that were inside curly braces of message 
            2. A string that's a copy of the message but without the variable names inside curly braces
            and a randomly chosen parameter out of each curly braces options:
            "Hello {First Name}, how are you {feeling|doing}?" --> "Hello {}, how are you doing?"
        """
        logger.start()
        variable_names_list, message_without_variable_names = self.get_variable_names_and_chosen_option(**kwargs)
        variable_value_list = []
        for variable_name in variable_names_list:
            variable_id = self.variable.get_variable_id_by_variable_name(variable_name)
            variable_value = self.variable.get_variable_value_by_variable_id(
                variable_id=variable_id, lang_code=self.language, profile_id=profile_id)
            variable_value_list.append(variable_value)

        formatted_message = message_without_variable_names.format(*variable_value_list)
        logger.end(object={'formatted_message': formatted_message})
        return formatted_message
