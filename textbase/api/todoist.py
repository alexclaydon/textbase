from .legacy import local_logger
from todoist.api import TodoistAPI
from pathlib import Path


def export_link_list_from_todoist(
        todoist_token,
        target: Path,
        debug_mode: bool = True
):
    api = TodoistAPI(todoist_token)
    api.sync()
    tasks = export_task_data_by_project(
        api=api,
        project_id=2233683133
    )
    write_task_content_to_file(
        tasks=tasks,
        target=target
    )
    if not debug_mode:
        delete_tasks_in_max_chunks(
            api=api,
            tasks=tasks
        )


def export_task_data_by_project(
        api,
        project_id: int
):
    """
    Returns a list of dicts of all task data for the given project id.

    :param api: a Todoist API object
    :param project_id: an integer ...
    :return: a list of dicts, each dict containing task data
    """
    api.sync()
    tasks = [
        task.data for task in api.state['items']
        if task['project_id'] == project_id
    ]
    return tasks


def write_task_content_to_file(
        tasks: list,
        target: Path
):
    task_content = [item['content'] for item in tasks]
    if not Path.exists(target):
        local_logger.info(
            f'TEXTBASE: No export destination file exists; creating and appending new reading list items from Journal project.'
        )
        with open(target.as_posix(), mode="w") as outfile:
            for line in task_content:
                outfile.write(f"{line}\n\n")
    else:
        local_logger.info(
            f'TEXTBASE: Export destination file already exists; appending new reading list items from Journal project.'
        )
        with open(target.as_posix(), mode="a") as outfile:
            for line in task_content:
                outfile.write(f"{line}\n\n")
    local_logger.info('TEXTBASE: Export of Journal reading list items complete.')


def delete_tasks_by_id(
        api,
        task_ids: int or list,
):
    """

    :param task_ids: Either a single task id of type int, or a list of task ids of type int, with a maximum size of 100 items in order to play nice with the Todoist API.
    :param todoist_token: a string containing the Todoist API token; the default is to attempt to load it from envs
    """
    api.sync()
    if isinstance(task_ids, int):
        api.items.delete(item_id=task_ids)
    else:
        for task_id in task_ids:
            api.items.delete(item_id=task_id)
    api.commit()
    api.sync()
    local_logger.info(
        'TEXTBASE: Reading list items successfully deleted from Journal project.'
    )


def yield_list_of_exported_task_ids(
        tasks: list,
):
    """
    Yields lists of task ids extracted from a tasks object returned by export_task_data_by_project(), each list having a maximum size of 100 items in order to play nice with the Todoist API.

    :param tasks: A tasks object returned by export_task_data_by_project()
    :return: Yields a list of maximum 100 task ids
    """
    task_ids = [
        task['id'] for task in tasks
    ]

    def chunks(l: list, n: int):
        for i in range(0, len(l), n):
            yield l[i:i+n]

    task_ids_split = list(chunks(task_ids, 100))
    for split_list in task_ids_split:
        yield split_list


def delete_tasks_in_max_chunks(api, tasks):
    for split_list in yield_list_of_exported_task_ids(tasks=tasks):
        delete_tasks_by_id(
            api=api,
            task_ids=split_list,
        )
