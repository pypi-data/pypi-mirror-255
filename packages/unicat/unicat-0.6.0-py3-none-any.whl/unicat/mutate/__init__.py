from .project import *
from .definitions import *
from .classes import *
from .fields import *
from .records import *
from .assets import *
from .queries import *


class UnicatMutate:
    def __init__(self, unicat):
        self._unicat = unicat

        self.add_language = self._wrap(add_language)
        self.remove_language = self._wrap(remove_language)
        self.create_channel = self._wrap(create_channel)
        self.delete_channel = self._wrap(delete_channel)
        self.create_ordering = self._wrap(create_ordering)
        self.delete_ordering = self._wrap(delete_ordering)
        self.create_fieldlist = self._wrap(create_fieldlist)
        self.delete_fieldlist = self._wrap(delete_fieldlist)

        self.create_definition = self._wrap(create_definition)
        self.modify_definition = self._wrap(modify_definition)
        self.modify_definition_modify_layout = self._wrap(
            modify_definition_modify_layout
        )
        self.modify_definition_add_class = self._wrap(modify_definition_add_class)
        self.modify_definition_remove_class = self._wrap(modify_definition_remove_class)
        self.modify_definition_add_field = self._wrap(modify_definition_add_field)
        self.modify_definition_remove_field = self._wrap(modify_definition_remove_field)
        self.modify_definition_fieldlist_add_field = self._wrap(
            modify_definition_fieldlist_add_field
        )
        self.modify_definition_fieldlist_remove_field = self._wrap(
            modify_definition_fieldlist_remove_field
        )
        self.modify_definition_add_childdefinition = self._wrap(
            modify_definition_add_childdefinition
        )
        self.modify_definition_remove_childdefinition = self._wrap(
            modify_definition_remove_childdefinition
        )
        self.commit_definition = self._wrap(commit_definition)
        self.save_as_new_definition = self._wrap(save_as_new_definition)
        self.delete_definition = self._wrap(delete_definition)

        self.create_class = self._wrap(create_class)
        self.modify_class = self._wrap(modify_class)
        self.modify_class_modify_layout = self._wrap(modify_class_modify_layout)
        self.modify_class_add_field = self._wrap(modify_class_add_field)
        self.modify_class_remove_field = self._wrap(modify_class_remove_field)
        self.commit_class = self._wrap(commit_class)
        self.save_as_new_class = self._wrap(save_as_new_class)
        self.delete_class = self._wrap(delete_class)

        self.create_field = self._wrap(create_field)
        self.modify_field = self._wrap(modify_field)
        self.commit_field = self._wrap(commit_field)
        self.save_as_new_field = self._wrap(save_as_new_field)
        self.delete_field = self._wrap(delete_field)

        self.create_record = self._wrap(create_record)
        self.set_record_definition = self._wrap(set_record_definition)
        self.extend_record_definition_add_class = self._wrap(
            extend_record_definition_add_class
        )
        self.extend_record_definition_add_field = self._wrap(
            extend_record_definition_add_field
        )
        self.extend_record_definition_add_fieldlist_field = self._wrap(
            extend_record_definition_add_fieldlist_field
        )
        self.update_record = self._wrap(update_record)
        self.set_record_channels = self._wrap(set_record_channels)
        self.copy_record_channels_from_parent = self._wrap(
            copy_record_channels_from_parent
        )
        self.copy_record_channels_down = self._wrap(copy_record_channels_down)
        self.copy_record_channels_up = self._wrap(copy_record_channels_up)
        self.set_record_orderings = self._wrap(set_record_orderings)
        self.link_record = self._wrap(link_record)
        self.delete_record = self._wrap(delete_record)
        self.undelete_record = self._wrap(undelete_record)
        self.permanent_delete_record = self._wrap(permanent_delete_record)

        self.upload_asset = self._wrap(upload_asset)
        self.upload_update_asset = self._wrap(upload_update_asset)
        self.create_asset = self._wrap(create_asset)
        self.update_asset = self._wrap(update_asset)
        self.delete_asset = self._wrap(delete_asset)
        self.undelete_asset = self._wrap(undelete_asset)
        self.permanent_delete_asset = self._wrap(permanent_delete_asset)

        self.create_query = self._wrap(create_query)
        self.update_query = self._wrap(update_query)
        self.delete_query = self._wrap(delete_query)

        self.create_backup = self._wrap(create_backup)
        self.update_backup = self._wrap(update_backup)
        self.restore_backup = self._wrap(restore_backup)
        self.delete_backup = self._wrap(delete_backup)
        self.delete_backups = self._wrap(delete_backups)

    def _wrap(self, function):
        def _inner_function(*args, **kwargs):
            return function(self._unicat, *args, **kwargs)

        return _inner_function
