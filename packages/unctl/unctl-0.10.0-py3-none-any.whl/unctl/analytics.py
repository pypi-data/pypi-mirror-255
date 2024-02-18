import segment.analytics as analytics
import unctl.constants as constants
import asyncio
import functools
import threading
import time


class GlobalRunEvent:
    """Class to track unctl_run event in __main__.py"""

    def __init__(self):
        self.start_time = time.time()

    def send(self, options):
        report_generation_time = time.time() - self.start_time
        track_unctl_run(options, report_generation_time)


class CheckRunEvent:
    """Class to track unctl_check_run event in scanerkube.py"""

    def __init__(self):
        self.start_time = time.time()

    def send(self, check_id, failed_count):
        execution_time = time.time() - self.start_time
        track_check_results(check_id, failed_count, execution_time)


def async_track_event(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except Exception:
            # Add DEBUG statement code here
            pass

    return wrapper


@async_track_event
async def _async_track_event(event_name, properties):
    """Asynchronous helper function to track an event."""
    analytics.track(constants.USER, event_name, properties)


def track_unctl_run(options_dict, report_generation_time=None):
    """
    Track each time unctl is run along with the report generation time.
    Args:
        args: The arguments passed to the unctl run.
        report_generation_time: The time taken to generate a report, if applicable.
    """
    args_dict = vars(options_dict)
    event_properties = {"options": args_dict}
    if report_generation_time is not None:
        event_properties["report_generation_time_seconds"] = report_generation_time
    try:
        # Run the asynchronous event tracking in a separate thread
        threading.Thread(
            target=lambda: asyncio.run(
                _async_track_event("UNCTL_RUN", event_properties)
            )
        ).start()
        analytics.flush()
    except Exception as e:
        raise e


def track_check_results(check_id, failed_count, execution_time):
    """
    Track results for each check asynchronously.
    Args:
        check_id: The identifier of the check.
        failed_count: The number of failures for this check.
        execution_time: The time taken to execute this check.
    """
    event_properties = {
        "check_id": check_id,
        "failed_count": failed_count,
        "execution_time_seconds": execution_time,
    }
    asyncio.create_task(_async_track_event("UNCTL_CHECK_RESULTS", event_properties))


def track_resolution_screen(
    action_type,
    check_id,
    resource_name,
    recommended_commands,
    actual_commands,
):
    """
    Track user's decision to execute diagnostics or fixes on the resolution screen.
    Args:
        action_type: Type of action (e.g., 'diagnose', 'fix').
        check_id: Identifier of the check.
        resource_name: Name of the resource being checked.
        recommended_commands: List of recommended commands.
        actual_commands: List of actual commands executed.
    """
    asyncio.create_task(
        _async_track_event(
            "UNCTL_RESOLUTION_SCREEN",
            {
                "action_type": action_type,
                "check_id": check_id,
                "resource_selected": resource_name,
                "recommended_commands": recommended_commands,
                "actual_commands": actual_commands,
            },
        )
    )


def track_resolution_time(check_id, time_spent):
    """
    Track the time spent on the resolution screen for a specific check.
    Args:
        check_id: Identifier of the check.
        time_spent: Time spent on the resolution screen.
    """
    if time_spent > 10:
        asyncio.create_task(
            _async_track_event(
                "UNCTL_RESOLUTION_SCREEN_TIME",
                {"check_id": check_id, "time_spent_seconds": time_spent},
            )
        )


def track_failure_selection(check_id, index, mode):
    """
    Track the selection of a failure in the reports table.
    Args:
        check_id: Identifier of the check.
        index: The index of the failure selected in the list.
        mode: Mode of the application interface (e.g., 'interactive', 'remediation').
    """
    asyncio.create_task(
        _async_track_event(
            "UNCTL_FAILURE_SELECTION",
            {"check_id": check_id, "index": index, "mode": mode},
        )
    )


def track_group_selection(index, title):
    """
    Track the selection of a group in the groups table.
    Args:
        index: Index of the selected group.
        title: Title of the selected group.
    """
    asyncio.create_task(
        _async_track_event("UNCTL_GROUP_SELECTION", {"index": index, "title": title})
    )


def track_api_error(error_type, message):
    """
    Track API errors related to OpenAI Assistant.
    Args:
        error_type: Type of the API error.
        message: Error message.
    """
    asyncio.create_task(
        _async_track_event(
            "UNCTL_API_ERROR",
            {
                "error_type": error_type,
                "error_message": message,
            },
        )
    )


def track_llm_token_limit_error(error_type, message, cmd):
    """
    Track errors related to LLM (Large Language Models) token limit.
    Args:
        error_type: Type of the LLM error.
        message: Error message.
        cmd: command for which output exceeding token limit.
    """
    asyncio.create_task(
        _async_track_event(
            "UNCTL_LLM_TOKEN_LIMIT_ERROR",
            {
                "error_type": error_type,
                "error_message": message,
                "cmd": cmd,
            },
        )
    )


def track_json_error(error_type, message, identifier):
    """
    Track JSON parsing errors.
    Args:
        error_type: Type of the JSON error.
        message: Error message.
        identifier: Identifier related to the error context.
    """
    asyncio.create_task(
        _async_track_event(
            "UNCTL_JSON_ERROR",
            {
                "error_type": error_type,
                "error_message": message,
                "identifier": identifier,
            },
        )
    )


def track_chat_message(check_id, message):
    """
    Track the text entered in the chatbox on the resolution screen.
    Args:
        check_id: Identifier of the check.
        message: Text message entered in the chatbox.
    """
    asyncio.create_task(
        _async_track_event(
            "UNCTL_RESOLUTION_SCREEN_CHAT", {"check_id": check_id, "message": message}
        )
    )
