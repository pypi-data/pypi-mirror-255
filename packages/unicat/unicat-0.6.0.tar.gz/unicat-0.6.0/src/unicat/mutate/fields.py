from ..field import UnicatField
from ..error import UnicatError

typecheck = type  # I use 'type' as a keyword argument


def create_field(
    unicat,
    *,
    name=None,
    type=None,
    is_localized=None,
    is_required=None,
    label=None,
    unit=None,
    initial=None,
    options=None,
):
    properties = {}
    if name is not None:
        properties["name"] = name
    if type is not None:
        properties["type"] = type
    if is_localized is not None and typecheck(is_localized) is bool:
        properties["is_localized"] = is_localized
    if is_required is not None and typecheck(is_required) is bool:
        properties["is_required"] = is_required
    if label is not None and typecheck(label) is dict:
        properties["label"] = label
    if unit is not None:
        properties["unit"] = unit
    if initial is not None and typecheck(initial) is dict:
        properties["initial"] = initial
    if options is not None and typecheck(options) is dict:
        properties["options"] = options
    success, result = unicat.api.call("/fields/create", properties)
    if not success:
        raise UnicatError("create_field", result)
    return UnicatField(unicat, result["field"])


def modify_field(
    unicat,
    field,
    *,
    name=None,
    type=None,
    is_localized=None,
    is_required=None,
    label=None,
    unit=None,
    initial=None,
    options=None,
):
    properties = {}
    if name is not None:
        properties["name"] = name
    if type is not None:
        properties["type"] = type
    if is_localized is not None and typecheck(is_localized) is bool:
        properties["is_localized"] = is_localized
    if is_required is not None and typecheck(is_required) is bool:
        properties["is_required"] = is_required
    if label is not None and typecheck(label) is dict:
        properties["label"] = label
    if unit is not None:
        properties["unit"] = unit
    if initial is not None and typecheck(initial) is dict:
        properties["initial"] = initial
    if options is not None and typecheck(options) is dict:
        properties["options"] = options
    properties["field"] = field.gid
    success, result = unicat.api.call("/fields/modify", properties)
    if not success:
        raise UnicatError("modify_field", result)
    return UnicatField(unicat, result["field"])


def commit_field(unicat, new_or_working_copy):
    success, result = unicat.api.call(
        "/fields/commit", {"field": new_or_working_copy.gid}
    )
    if not success:
        raise UnicatError("commit_field", result)
    if (
        result["field"] != new_or_working_copy.gid
        and new_or_working_copy.gid in unicat.api.data["fields"]
    ):
        del unicat.api.data["fields"][new_or_working_copy.gid]
    return UnicatField(unicat, result["field"])


def save_as_new_field(unicat, working_copy):
    success, result = unicat.api.call(
        "/fields/save_as_new", {"field": working_copy.gid}
    )
    if not success:
        raise UnicatError("save_as_new_field", result)
    return UnicatField(unicat, result["field"])


def delete_field(unicat, field):
    success, result = unicat.api.call("/fields/delete", {"field": field.gid})
    if not success:
        raise UnicatError("delete_field", result)
    if field.gid in unicat.api.data["fields"]:
        del unicat.api.data["fields"][field.gid]
    return True
