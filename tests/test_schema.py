import pytest
from pydantic import ValidationError

from governor_ot.schema import Action, Command


def read_fields(**overrides):
    fields = {
        "action": "modbus_read",
        "target_ip": "192.168.1.10",
        "register": 40001,
        "expression": "modbus_read(register=40001)",
    }
    fields.update(overrides)
    return fields


def write_fields(**overrides):
    fields = {
        "action": "modbus_write",
        "target_ip": "192.168.1.10",
        "register": 40001,
        "value": 9999,
        "expression": "modbus_write(register=40001, value=9999)",
    }
    fields.update(overrides)
    return fields


def nmap_fields(**overrides):
    fields = {
        "action": "nmap_scan",
        "target_ip": "192.168.1.10",
        "expression": "nmap_scan(target='192.168.1.10')",
    }
    fields.update(overrides)
    return fields


def without(fields, key):
    return {k: v for k, v in fields.items() if k != key}


def single_error(exc_info):
    errors = exc_info.value.errors()
    assert len(errors) == 1
    return errors[0]


# Valid cases


def test_modbus_read_with_register_and_no_value():
    cmd = Command(**read_fields())
    assert cmd.action is Action.modbus_read
    assert cmd.register == 40001
    assert cmd.value is None


def test_modbus_write_with_register_and_value():
    cmd = Command(**write_fields())
    assert cmd.action is Action.modbus_write
    assert cmd.register == 40001
    assert cmd.value == 9999


def test_nmap_scan_with_only_action_and_target():
    cmd = Command(**nmap_fields())
    assert cmd.action is Action.nmap_scan
    assert cmd.register is None
    assert cmd.value is None
    assert cmd.reasoning is None


def test_port_defaults_to_502():
    cmd = Command(**read_fields())
    assert cmd.port == 502


def test_expression_is_stored_verbatim():
    text = "modbus_write(register=40001, value=9999)"
    cmd = Command(**write_fields(expression=text))
    assert cmd.expression == text


def test_action_serializes_to_its_string_value():
    cmd = Command(**read_fields())
    assert '"action":"modbus_read"' in cmd.model_dump_json()


# Invalid cases


def test_action_outside_the_enum_is_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Command(**read_fields(action="modbus_delete"))
    error = single_error(exc_info)
    assert error["loc"] == ("action",)
    assert error["type"] == "enum"


def test_modbus_write_without_value_is_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Command(**without(write_fields(), "value"))
    error = single_error(exc_info)
    assert error["type"] == "value_error"
    assert "modbus_write requires a value" in error["msg"]


def test_modbus_read_without_register_is_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Command(**without(read_fields(), "register"))
    error = single_error(exc_info)
    assert error["type"] == "value_error"
    assert "modbus_read requires a register" in error["msg"]


def test_nmap_scan_with_register_is_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Command(**nmap_fields(register=40001))
    error = single_error(exc_info)
    assert error["type"] == "value_error"
    assert "nmap_scan must not carry a register or value" in error["msg"]


def test_missing_target_ip_is_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Command(**without(read_fields(), "target_ip"))
    error = single_error(exc_info)
    assert error["loc"] == ("target_ip",)
    assert error["type"] == "missing"


def test_non_integer_value_is_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Command(**write_fields(value="abc"))
    error = single_error(exc_info)
    assert error["loc"] == ("value",)
    assert error["type"] == "int_parsing"


def test_unexpected_extra_field_is_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Command(**read_fields(unit_id=1))
    error = single_error(exc_info)
    assert error["loc"] == ("unit_id",)
    assert error["type"] == "extra_forbidden"


def test_empty_expression_is_rejected():
    with pytest.raises(ValidationError) as exc_info:
        Command(**read_fields(expression=""))
    error = single_error(exc_info)
    assert error["loc"] == ("expression",)
    assert error["type"] == "string_too_short"


# JSON schema sanity check


def test_json_schema_shape():
    schema = Command.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["action", "target_ip", "expression"]
    assert list(schema["properties"]) == [
        "action",
        "target_ip",
        "port",
        "register",
        "value",
        "expression",
        "reasoning",
    ]
    assert schema["$defs"]["Action"]["enum"] == [
        "modbus_read",
        "modbus_write",
        "nmap_scan",
    ]
