from pymavlink.dialects.v20.ardupilotmega import (
    MAVLink_param_request_list_message,
    MAVLink_param_request_read_message,
    MAVLink_param_set_message,
)


def get_param_request_read_message(
    target_system: int,
    target_component: int,
    param_id: bytes,
    param_index: int,
) -> MAVLink_param_request_read_message:
    """
    MAVLink param request read message wrapper.

    :param target_system: message target system id
    :param target_component: message target component id
    :param param_id: name of the requested parameter
    :param param_index: parameter index. Send -1 to use the param ID field as identifier

    :returns: MAVLink_param_request_read_message: message object
    """
    return MAVLink_param_request_read_message(
        target_system,
        target_component,
        param_id,
        param_index,
    )


def get_param_request_list_message(
    target_system: int,
    target_component: int,
) -> MAVLink_param_request_list_message:
    """
    MAVLink param request list message wrapper.

    :param target_system: message target system id
    :param target_component: message target component id

    :returns: MAVLink_param_request_list_message: message object
    """
    return MAVLink_param_request_list_message(
        target_system,
        target_component,
    )


def get_param_set_message(
    target_system: int,
    target_component: int,
    param_id: bytes,
    param_value: float,
) -> MAVLink_param_set_message:
    """ "
    MAVLink param set message wrapper.

    :param target_system: message target system id
    :param target_component: message target component id
    :param param_id: name of the parameter that is changing value
    :param param_value: new onboard parameter value to be set

    :returns: MAVLink_param_set_message: message object
    """
    return MAVLink_param_set_message(
        target_system,
        target_component,
        param_id,
        param_value,
        # in ardupilot param_type in the message is ignored. The data type is obtained by checking stored type info (via name lookup).
        param_type=0,
    )
