import ast

APPROVED_TARGET = "SIMULATED_PLC"
APPROVED_PROTOCOL = "MODBUS_TCP"
APPROVED_PORT = "APPROVED_MODBUS_PORT"
APPROVED_FUNCTION = "APPROVED_WRITE_FUNCTION"

APPROVED_ADDRESS = "APPROVED_TEST_REGISTER"
APPROVED_VALUE = "SAFE_TEST_VALUE"
MAX_WRITES = 1


def check_command(command):
    try:
        tree = ast.parse(command, mode="eval")
    except SyntaxError:
        return "BLOCKED", "Invalid command syntax."

    if not isinstance(tree.body, ast.Call):
        return "BLOCKED", "Command must be a single function call."

    call = tree.body

    if not isinstance(call.func, ast.Name) or call.func.id != "modbus_write":
        return (
            "BLOCKED",
            "Only the approved modbus_write operation is allowed."
        )

    if call.args:
        return (
            "BLOCKED",
            "Positional arguments are not allowed."
        )

    values = {}

    for kw in call.keywords:
        if kw.arg is None:
            return (
                "BLOCKED",
                "Keyword expansion is not allowed."
            )

        if not isinstance(kw.value, ast.Constant):
            return (
                "BLOCKED",
                f"Parameter '{kw.arg}' must use a fixed value."
            )

        values[kw.arg] = kw.value.value

    required = {
        "action",
        "target",
        "protocol",
        "port",
        "function",
        "address",
        "value",
        "count"
    }

    if set(values) != required:
        return (
            "BLOCKED",
            "Command parameters do not match the approved policy."
        )

    rules = [
        (
            "action",
            "WRITE_TEST_VALUE",
            "Action is not an approved test action."
        ),
        (
            "target",
            APPROVED_TARGET,
            "Target is not the simulated PLC."
        ),
        (
            "protocol",
            APPROVED_PROTOCOL,
            "Protocol is not approved."
        ),
        (
            "port",
            APPROVED_PORT,
            "Modbus port is not approved."
        ),
        (
            "function",
            APPROVED_FUNCTION,
            "Modbus write function is not approved."
        ),
        (
            "address",
            APPROVED_ADDRESS,
            "Register/coil is outside the approved test scope."
        ),
        (
            "value",
            APPROVED_VALUE,
            "Value is outside the predefined safe test value."
        ),
        (
            "count",
            MAX_WRITES,
            "Write count exceeds the allowed limit."
        ),
    ]

    violations = []

    for field, expected, reason in rules:
        if values[field] != expected:
            violations.append(reason)

    if violations:
        return (
            "BLOCKED",
            "Command violates predefined OT safety rules:\n- "
            + "\n- ".join(violations)
        )

    return (
        "APPROVED",
        "Command passed all predefined OT safety rules: "
        "target, protocol, port, function, address, "
        "value, and write count are approved."
    )


safe_command = """modbus_write(
    action="WRITE_TEST_VALUE",
    target="SIMULATED_PLC",
    protocol="MODBUS_TCP",
    port="APPROVED_MODBUS_PORT",
    function="APPROVED_WRITE_FUNCTION",
    address="APPROVED_TEST_REGISTER",
    value="SAFE_TEST_VALUE",
    count=1
)"""


unsafe_command = """modbus_write(
    action="WRITE_UNAUTHORIZED_VALUE",
    target="UNKNOWN_OR_EXTERNAL_PLC",
    protocol="MODBUS_TCP",
    port="UNAPPROVED_PORT",
    function="UNAPPROVED_FUNCTION",
    address="PROTECTED_REGISTER",
    value="UNAPPROVED_VALUE",
    count="UNBOUNDED"
)"""


if __name__ == "__main__":

    for name, command in [
        ("SAFE TEST", safe_command),
        ("UNSAFE TEST", unsafe_command),
    ]:

        status, reason = check_command(command)

        print(f"\n{name}")
        print("-" * len(name))
        print(f"Status: {status}")
        print(f"Reason: {reason}")
