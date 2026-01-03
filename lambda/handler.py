import json
import os
import time
import boto3

ssm = boto3.client("ssm")

TARGET_INSTANCE_ID = os.getenv("TARGET_INSTANCE_ID", "")
SERVICE_NAME = os.getenv("SERVICE_NAME", "nginx")
PROJECT = os.getenv("PROJECT", "self-healing")
ENV = os.getenv("ENV", "dev")


def _safe_json_load(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None


def _extract_alarm_payload(event):
    records = event.get("Records", [])
    if not records:
        return None, "NoRecords"

    sns_msg = records[0].get("Sns", {}).get("Message", "")
    payload = _safe_json_load(sns_msg)
    return payload, sns_msg


def _send_ssm_command(instance_id: str, commands: list[str], comment: str):
    resp = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": commands},
        Comment=comment,
    )
    return resp["Command"]["CommandId"]


def _wait_for_command(instance_id: str, command_id: str, timeout_s=25):
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            inv = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
            status = inv.get("Status")
            if status in ["Success", "Failed", "Cancelled", "TimedOut"]:
                return inv
        except ssm.exceptions.InvocationDoesNotExist:
            pass
        time.sleep(2)

    return {
        "Status": "Unknown",
        "StandardOutputContent": "",
        "StandardErrorContent": "Timed out waiting"
    }


def lambda_handler(event, context):
    payload, raw_msg = _extract_alarm_payload(event)

    if not payload:
        return {"ok": False, "reason": "SNSMessageNotJSON", "raw": raw_msg[:500]}

    alarm_name = payload.get("AlarmName", "")
    new_state = payload.get("NewStateValue", "")
    reason = payload.get("NewStateReason", "")

    # Only heal when alarm is ALARM
    if new_state != "ALARM":
        return {"ok": True, "action": "NOOP", "alarm": alarm_name, "state": new_state}

    if not TARGET_INSTANCE_ID:
        return {"ok": False, "reason": "TARGET_INSTANCE_ID not set"}

    commands = [
        "set -e",
        "echo '=== Self-Heal: Restarting service ==='",
        f"sudo systemctl status {SERVICE_NAME} --no-pager || true",
        f"sudo systemctl restart {SERVICE_NAME}",
        f"sudo systemctl is-active {SERVICE_NAME}",
        "echo '=== Done ==='",
    ]

    cmd_id = _send_ssm_command(
        TARGET_INSTANCE_ID,
        commands,
        comment=f"{PROJECT}/{ENV} autoheal: restart {SERVICE_NAME}",
    )

    inv = _wait_for_command(TARGET_INSTANCE_ID, cmd_id)

    return {
        "ok": True,
        "alarm": alarm_name,
        "state": new_state,
        "reason": reason,
        "instance": TARGET_INSTANCE_ID,
        "ssm_command_id": cmd_id,
        "ssm_status": inv.get("Status"),
        "stdout": (inv.get("StandardOutputContent") or "")[:2000],
        "stderr": (inv.get("StandardErrorContent") or "")[:2000],
    }
