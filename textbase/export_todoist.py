from liblogger.legacy import local_logger
from todoist.api import TodoistAPI
from pathlib import Path
from libnotify import notify_to_pushover

# I've elected not to use any of the various pre-baked Pushover packages on the Python Packages index and have gone instead for a zero-dependency approach using a function in my own library, libnotify.

# Pushover API documentation is here: https://todoist-python.readthedocs.io/en/latest/todoist.html


def export_link_list_from_todoist(
        todoist_token,
        target: Path
):
    api = TodoistAPI(todoist_token)
    api.sync()
    tasks = [
        task.data for task in api.state['items']
        if task['project_id'] == 2233683133
    ]
    if tasks:
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
        task_ids = [
            task['id'] for task in tasks
        ]
        # Create a function called "chunks" with two arguments, l and n:
        def chunks(l, n):
            # For item i in a range that is a length of l,
            for i in range(0, len(l), n):
                # Create an index range for l of n items:
                yield l[i:i+n]
        # Create a list that from the results of the function chunks:
        task_ids_split = list(chunks(task_ids, 100))
        for split_list in task_ids_split:
            for task_id in split_list:
                api.items.delete(item_id=task_id)
            api.commit()
            api.sync()
        local_logger.info(
            'TEXTBASE: Reading list items successfully deleted from Journal project.'
        )
        notify_to_pushover(
            message='TEXTBASE: Reading list items successfully exported to file and marked for deletion.',
        )
    else:
        msg = 'TEXTBASE: No new reading list items in Journal project; no action taken.'
        local_logger.info(msg)
        notify_to_pushover(
            message=msg,
        )
