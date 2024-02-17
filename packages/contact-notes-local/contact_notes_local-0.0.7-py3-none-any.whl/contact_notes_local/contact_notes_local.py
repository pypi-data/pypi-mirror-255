import re
from datetime import datetime
from .contact_notes_local_constants import CONTACT_NOTES_PYTHON_PACKAGE_CODE_LOGGER_OBJECT
from database_mysql_local.generic_mapping import GenericMapping
from database_mysql_local.generic_crud import GenericCRUD
from language_remote.lang_code import LangCode
from user_context_remote.user_context import UserContext
from logger_local.LoggerLocal import Logger
from text_block_local.text_block import TextBlocks
from database_infrastructure_local.number_generator import NumberGenerator
from contact_group_local.contact_group import ContactGroup

DEFAULT_SCHEMA_NAME = "contact_note"
DEFAULT_TABLE_NAME = "contact_note_text_block_table"
DEFAULT_VIEW_NAME = "contact_note_text_block_view"
DEFAULT_ID_COLUMN_NAME = "conact_note_text_block_id"
DEFAULT_ENTITY_NAME1 = "contact_note"
DEFAULT_ENTITY_NAME2 = "text_block"

PROFILE_MILESTONE_SCHEMA_NAME = "profile_milestone"
PROFILE_MILESTONE_TABLE_NAME = "profile_milestone_table"
PROFILE_MILESTONE_VIEW_NAME = "profile_milestone_table_view"
PROFILE_MILESTONE_ID_COLUMN_NAME = "profile_milestone_id"

logger = Logger.create_logger(object=CONTACT_NOTES_PYTHON_PACKAGE_CODE_LOGGER_OBJECT)

user_context = UserContext.login_using_user_identification_and_password()

# TODO We should add the action-items tables


class ContactNotesLocal(GenericMapping):
    def __init__(self, contact_dict: dict, contact_id: int, profile_id: int,
                 default_schema_name: str = DEFAULT_SCHEMA_NAME,
                 default_table_name: str = DEFAULT_TABLE_NAME,
                 default_view_table_name: str = DEFAULT_VIEW_NAME,
                 default_id_column_name: str = DEFAULT_ID_COLUMN_NAME,
                 default_entity_name1: str = DEFAULT_ENTITY_NAME1,
                 default_entity_name2: str = DEFAULT_ENTITY_NAME2,
                 lang_code: LangCode = None, is_test_data: bool = False) -> None:
        super().__init__(default_schema_name=default_schema_name,
                         default_table_name=default_table_name,
                         default_view_table_name=default_view_table_name,
                         default_id_column_name=default_id_column_name,
                         default_entity_name1=default_entity_name1,
                         default_entity_name2=default_entity_name2,
                         is_test_data=is_test_data)
        self.lang_code = lang_code or user_context.get_effective_profile_preferred_lang_code()
        self.contact_id = contact_id
        self.profile_id = profile_id
        self.contact_dict = contact_dict
        self.text_blocks = TextBlocks()
        self.contact_group = ContactGroup()

    # TODO: add cases where note already exists
    def insert_contact_notes(self, ignore_duplicate: bool = False) -> int:
        logger.start(object={"ignore_duplicate": ignore_duplicate})
        note = self.contact_dict.get('notes', None)
        random_number = NumberGenerator.get_random_number(schema_name=self.schema_name,
                                                          view_name="contact_note_table")
        if not note:
            logger.end(f"no note for contact_id: {self.contact_id}")
            return None
        data_json = {
            'contact_id': self.contact_id,
            'note': note,
            'number': random_number,
            'identifier': None,         # TODO: Use function in the databaase package to create unique identifier
            # TODO: shall we add created_user_id?
            # TODO: shall we add created_real_user_id?
            # TODO: shall we add created_effective_profile_id? 
        }
        contact_note_id = self.insert(table_name="contact_note_table", data_json=data_json, ignore_duplicate=ignore_duplicate)
        logger.end(object={"contact_note_id": contact_note_id})
        return contact_note_id

    # TODO: when we have contact_note_view ready, we can test the following method and use it
    # TODO Why a few of the function get contact_id is parameter and other don't get the contact_id as parameter
    '''
    def select_multi_dict_by_contact_id(self, contact_id: int) -> dict:
        logger.start(object={"contact_id": contact_id})
        contact_note_dict = self.select_multi_dict_by_id(view_table_name="contact_note_table",
                                                         id_column_name="contact_id",
                                                         id_column_value=contact_id)
        logger.end(object={"contact_note_dict": contact_note_dict})
        return contact_note_dict
    '''

    # TODO: develop also text_block delete and then delete the connected text_blocks and the mapping
    # TODO delete_by_contact_id() suppose to get the contact_id parameter, shall we rename it to delete_all_contact_notes()
    # TODO as we want to keep the history, I think we shouldn't use this method
    def delete_by_contact_id(self) -> None:
        logger.start()
        super().delete_by_id(table_name="contact_note_table", id_column_name='contact_id',
                             id_column_value=self.contact_id)
        logger.end()

    # TODO This is mapping table between contact_note_id, and text_block_id, with seq (order of the text_blocks) as attribute. I would expected to have those three as parameters.
    # TODO Update seq (order of text_blocks) in the database
    def insert_contact_note_text_block_table(self, contact_note_id: int) -> int:
        '''
        This method will insert the note into the contact_note_text_block_table if it not exists there
        :param contact_note_id: the id of the contact_note_table
        :param note: the note to be inserted
        :return: the id of the inserted row
        '''
        logger.start(object={"contact_note_id": contact_note_id})
        note = self.contact_dict.get('notes', None)
        if not note:
            logger.end(log_message=f"no note for contact_note_id", object={"contact_note_id": contact_note_id})
            return None
        # Check if the contact_note is already linked to text_blocks
        mapping_tuple = self.select_multi_tuple_by_id(view_table_name=self.default_view_table_name,
                                                      id_column_name="contact_note_id",
                                                      id_column_value=contact_note_id)
        # TODO: shall we keep this check?
        if mapping_tuple:
            logger.end(log_message=f"contact_note_id: {contact_note_id} already linked to text_blocks",
                       object={"contact_note_id": contact_note_id})
            return None
        # TODO ..from_contact_note() or ..._by_contact_note_id()
        text_blocks_list = self.get_text_blocks_list_from_note()
        try:
            text_blocks_list = self._process_text_blocks_list(text_blocks_list=text_blocks_list)
        except ValueError as value_error:
            logger.error(log_message=f"ValueError: {value_error}")
            logger.end(log_message="text_blocks were not inserted to the database because of ValueError")
            return None

        text_block_ids_list = []
        conact_note_text_block_ids_list = []
        for i, text_block in enumerate(text_blocks_list):
            if i == 0:
                data_json = {
                    'text': text_block,
                    'seq': i,  # This is the index of the current text_block in the list
                    'profile_id': self.profile_id,
                }
            else:
                start_timestamp = self._extract_start_timestamp(text_block=text_block)
                data_json = {
                    'text': text_block.get('event', None),
                    'start_timestamp': start_timestamp,
                    'seq': i,  # This is the index of the current text_block in the list
                    'profile_id': self.profile_id,
                }
            text_block_id = self.text_blocks.insert(schema_name="text_block", table_name="text_block_table",
                                                    data_json=data_json)
            text_block_ids_list.append(text_block_id)
            self.text_blocks.process_text_block_by_id(text_block_id=text_block_id)

            # link the contact_note_id to the text_block_id
            data_json = {
                'contact_note_id': contact_note_id,
                'text_block_id': text_block_id,
                'seq': i,
            }
            # TODO: check if self.set_schema(schema_name=DEFAULT_SCHEMA_NAME) is actually necessary
            self.set_schema(schema_name=DEFAULT_SCHEMA_NAME)
            # Insert the mapping between the contact_note_id and the text_block_id
            logger.info(log_message=f"Inserting mapping between contact_note_id: {contact_note_id} and"
                             f" text_block_id: {text_block_id}")
            conact_note_text_block_id = self.insert_mapping(entity_name1=DEFAULT_ENTITY_NAME1,
                                                            entity_name2=DEFAULT_ENTITY_NAME2,
                                                            entity_id1=contact_note_id,
                                                            entity_id2=text_block_id)
            conact_note_text_block_ids_list.append(conact_note_text_block_id)

            # add the text block to profile_milestone
            if i > 0:
                profile_milestone_id = self._add_text_block_to_profile_milestone(text_block_id=text_block_id,
                                                                                 text_block=text_block)

        logger.end(object={"contact_note_id": contact_note_id, "text_block_ids_list": text_block_ids_list,
                   "conact_note_text_block_ids_list": conact_note_text_block_ids_list})
        return conact_note_text_block_ids_list

    def _add_text_block_to_profile_milestone(self, text_block_id: int, text_block: dict) -> int:
        logger.start(object={"text_block_id": text_block_id})
        number = NumberGenerator.get_random_number(
            schema_name=PROFILE_MILESTONE_SCHEMA_NAME, view_name=PROFILE_MILESTONE_TABLE_NAME
        )
        start_timestamp = self._extract_start_timestamp(text_block=text_block)
        data_json = {
            'number': number,
            'text_block_id': text_block_id,
            'profile_id': self.profile_id,
            # TODO: is_sure
            'start_timestamp': start_timestamp,
            'is_test_data': self.is_test_data,
        }
        generic_crud = GenericCRUD(
            default_schema_name=PROFILE_MILESTONE_SCHEMA_NAME, default_table_name=PROFILE_MILESTONE_TABLE_NAME,
            default_view_table_name=PROFILE_MILESTONE_VIEW_NAME,
            default_id_column_name=PROFILE_MILESTONE_ID_COLUMN_NAME,
            is_test_data=self.is_test_data
        )
        profile_milestone_id = generic_crud.insert(data_json=data_json)
        logger.end(object={"profile_milestone_id": profile_milestone_id})
        return profile_milestone_id

    def get_text_blocks_list_from_note(self) -> list:
        note = self.contact_dict.get('notes', None)
        if not note:
            return []
        logger.start(object={"note": note})
        text_blocks_list = note.split("\n\n")
        logger.end(object={"text_blocks_list": text_blocks_list})
        return text_blocks_list

    def _process_text_blocks_list(self, text_blocks_list: list) -> None:
        logger.start(object={"text_blocks_list": text_blocks_list})
        processed_text_blocks_list = []
        for i, text_block in enumerate(text_blocks_list):
            if i == 0:
                # TODO: shall we insert-link contact to group when the group ends with '?' ?
                # Process the first line (group names)
                group_names = [
                    name.strip()
                    for name in text_block.split(',')
                    if not (name.strip().endswith('X') or name.strip().endswith('?'))
                ]
                if group_names:  # Proceed only if there are valid group names
                    self.contact_group.insert_contact_and_link_to_existing_or_new_group(
                        contact_dict=self.contact_dict,
                        contact_id=self.contact_id,
                        groups=group_names,
                        is_test_data=self.is_test_data
                    )
                processed_text_blocks_list.append(text_block)
            else:
                text_block_dict = self._process_text_block(text_block=text_block)
                processed_text_blocks_list.append(text_block_dict)
        logger.end()
        return processed_text_blocks_list

    # TODO If 1st line in the text_block includes -----, each line bellow is Action Item / Task
    # TODO If 1st line in the text_block includes ?, text_block.is_sure = false, entities created and linked to the text_block is_sure=false
    def _process_text_block(self, text_block: str) -> dict:
        # Split the text block into parts
        parts = text_block.split(' ')

        # TODO date -> milestone_date
        # The first part is always the date
        date = parts[0]

        # Specify the possible date formats
        date_formats = ["%y%m%d", "%y%m", "%Y", "%Y%m", "%d/%m/%y", "%d/%m/%Y"]

        # Check if the date is in any of the formats
        for date_format in date_formats:
            try:
                formatted_date = self._convert_date_format(date_str=date, date_format=date_format)
                date = formatted_date
                break
            except ValueError:
                continue
        else:
            logger.error(log_message=f"Date '{date}' is not in any of the formats: {date_formats}")
            raise ValueError(f"Date '{date}' is not in any of the formats: {date_formats}")

        # Check if the second part is a time
        time = None
        if re.match(r'\d{2}:\d{2}:\d{2}', parts[1]):
            time = parts[1]
            event_start_index = 2
        else:
            event_start_index = 1

        # The rest of the parts form the event
        event = ' '.join(parts[event_start_index:])

        text_block_dict = {
            'date': date,
            'time': time,
            'event': event
        }

        # TODO Add profile milestone
        
        return text_block_dict

    def _convert_date_format(self, date_str: str, date_format: str) -> str:
        # Parse the date from the input format
        date = datetime.strptime(date_str, date_format)

        # Format the date in the output format
        new_date_str = date.strftime("%Y-%m-%d")

        return new_date_str

    def _extract_start_timestamp(self, text_block: dict) -> str:
        date = text_block.get('date', None)
        time = text_block.get('time', None)
        if date and time:
            start_timestamp = date + " " + time
        elif date:
            start_timestamp = date + " 00:00:00"
        else:
            logger.exception(log_message=f"date and time are both None for text_block: {text_block}, "
                                    "please add date(and optionally time) to the start of the text_block")
            raise Exception(f"event text_block has invalid date : {text_block}")
        return start_timestamp
