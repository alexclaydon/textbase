def dedupe_sets(new_set: set, existing_set: set):
    return new_set.difference(existing_set)


def write_iterable_to_file(iterable, file):
    with open(file, 'w') as f:
        for item in iterable:
            f.write(f'{item}\n')
