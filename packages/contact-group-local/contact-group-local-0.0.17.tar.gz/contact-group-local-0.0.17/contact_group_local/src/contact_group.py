from .contact_group_constans import CONTACT_GROUP_PYTHON_PACKAGE_CODE_LOGGER_OBJECT
from group_remote.group_remote import GroupsRemote
from logger_local.Logger import Logger
from database_mysql_local.generic_mapping import GenericMapping
from user_context_remote.user_context import UserContext
from dotenv import load_dotenv
load_dotenv()


logger = Logger.create_logger(
    object=CONTACT_GROUP_PYTHON_PACKAGE_CODE_LOGGER_OBJECT)


DEFAULT_SCHEMA_NAME = "contact_group"
DEFAULT_ENTITY_NAME1 = "contact"
DEFAULT_ENTITY_NAME2 = "group"
DEFAULT_ID_COLUMN_NAME = "contact_group_id"
DEFAULT_TABLE_NAME = "contact_group_table"
DEFAULT_VIEW_TABLE_NAME = "contact_group_view"


class ContactGroup(GenericMapping):
    def __init__(self, default_schema_name: str = DEFAULT_SCHEMA_NAME, default_entity_name1: str = DEFAULT_ENTITY_NAME1,
                 default_entity_name2: str = DEFAULT_ENTITY_NAME2, default_id_column_name: str = DEFAULT_ID_COLUMN_NAME,
                 default_table_name: str = DEFAULT_TABLE_NAME, default_view_table_name: str = DEFAULT_VIEW_TABLE_NAME) -> None:

        super().__init__(default_schema_name=default_schema_name, default_entity_name1=default_entity_name1,
                         default_entity_name2=default_entity_name2, default_id_column_name=default_id_column_name,
                         default_table_name=default_table_name, default_view_table_name=default_view_table_name)
        self.group_remote = GroupsRemote()

    def insert_contact_and_link_to_existing_or_new_group(self, contact_dict: dict, contact_id: int,
                                                         groups: list, mapping_data_json: dict = {},
                                                         is_test_data: bool = False) -> list[tuple]:
        logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id, "is_test_data": is_test_data})

        # TODO: Shall we also add the arguments is_interest, parent_group_id and title_lang_code?
        all_groups_linked = []
        for group in groups:
            groups_linked = self.add_update_group_and_link_to_contact(entity_name=group,
                                                                      contact_id=contact_id,
                                                                      title=group,
                                                                      mapping_data_json=mapping_data_json,
                                                                      is_test_data=self.is_test_data)
            all_groups_linked.append(groups_linked)

        logger.end(object={"all_groups_linked": all_groups_linked})
        return groups_linked

    def normalize_group_name(self, group_name: str) -> str:
        """
        Normalize group name
        Remove any special characters and spaces from group name and convert it to lowercase
        :param group_name: group name
        :return: normalized group name
        """
        normalized_name = ''.join(
            e for e in group_name if e.isalnum())  # Remove special characters and spaces
        normalized_name = normalized_name.lower()  # Convert to lowercase
        return normalized_name

    def get_group_names(self):
        response = self.group_remote.get_all_groups()
        groups = response.json()
        group_names = [group['title'] for group in groups['data']]
        return group_names

    def find_matching_groups(self, entity_name: str, group_names: list):
        groups_to_link = []
        for group in group_names:
            if group is None:
                continue
            group_normalized = self.normalize_group_name(group)
            entity_name_normalized = self.normalize_group_name(entity_name)
            if entity_name_normalized in group_normalized:
                groups_to_link.append(group)
        return groups_to_link

    def create_and_link_new_group(self, entity_name: str, contact_id: str, title_lang_code: str, is_interest: bool,
                                  mapping_data_json: dict = {}) -> list[tuple]:
        title = self.normalize_group_name(entity_name)
        group_id = self.group_remote.insert_update_group(title=title, title_lang_code=title_lang_code,
                                                         is_interest=is_interest).json()['data']['id']
        mapping_id = self.insert_mapping(entity_name1=self.default_entity_name1,
                                         entity_name2=self.default_entity_name2,
                                         entity_id1=contact_id, entity_id2=group_id,
                                         mapping_data_json=mapping_data_json)
        return [(group_id, title, mapping_id)]

    def link_existing_groups(self, groups_to_link: list, contact_id: str, title: str, title_lang_code: str,
                             parent_group_id: str, is_interest: bool, image: str,
                             mapping_data_json: dict = {}):
        groups_linked = []
        for group in groups_to_link:
            response = self.group_remote.get_group_response_by_group_name(group_name=group)
            if response.status_code != 200:
                logger.error(f"Failed to get group by group name: {group}")
                continue
            group_id = int(response.json()['data'][0]['id'])
            # TODO: if select_multi_mapping_tupel_by_id will be changed to return only a
            # mapping between entity_id1 and entity_id2, then the following code can be changed
            # to remove the for loop and just check if mapping_list is not None
            mapping_tuple = self.select_multi_mapping_tuple_by_id(entity_name1=self.default_entity_name1,
                                                                  entity_name2=self.default_entity_name2,
                                                                  entity_id1=contact_id, entity_id2=group_id)
            if mapping_tuple:
                logger.info(
                    f"Contact is already linked to group: {group}, contact_id: {contact_id}, group_id: {group_id}")
                # TODO: is this update_group call needed?
                self.group_remote.update_group(group_id=group_id, title=title, title_lang_code=title_lang_code,
                                               parent_group_id=parent_group_id, is_interest=is_interest, image=image)
                groups_linked.append((group_id, group))
            else:
                logger.info(log_message=f"Linking contact to group: {group}")
                self.insert_mapping(entity_name1=self.default_entity_name1, entity_name2=self.default_entity_name2,
                                    entity_id1=contact_id, entity_id2=group_id,
                                    mapping_data_json=mapping_data_json)
                logger.info(
                    f"Contact is linked to group: {group} , contact_id: {contact_id}, group_id: {group_id}")
                groups_linked.append((group_id, group))
        return groups_linked

    def add_update_group_and_link_to_contact(self, entity_name: str, contact_id: str,
                                             mapping_data_json: dict = {}, title: str = None,
                                             title_lang_code: str = None, parent_group_id: str = None,
                                             is_interest: bool = None, image: str = None,
                                             is_test_data: bool = False) -> list[tuple]:

        logger.start("Start add_update_group_and_link_to_contact group-remote")
        groups_to_link = []
        try:
            normalized_entity_name = self.normalize_group_name(entity_name)
            response = self.group_remote.get_group_response_by_group_name(group_name=normalized_entity_name)
            if response.status_code == 200:
                groups_to_link = [normalized_entity_name]

            groups_linked = None
            if len(groups_to_link) == 0:
                groups_linked = self.create_and_link_new_group(normalized_entity_name, contact_id, title_lang_code,
                                                               is_interest)
            else:
                groups_linked = self.link_existing_groups(groups_to_link, contact_id, title, title_lang_code, parent_group_id,
                                                          is_interest, image)

            if len(groups_linked) == 0:
                logger.end("No groups linked to contact")
                return None
            else:
                logger.end("Group linked to contact", object={
                    'groups_linked': groups_linked})
                return groups_linked

        except Exception as e:
            logger.exception("Failed to link group to contact", object={
                'groups_to_link': groups_to_link})
            logger.end("Failed to link group to contact")
            raise e
