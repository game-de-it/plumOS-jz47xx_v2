"""Preserve SimpleMenu's selected systems when aligning sections with theme art."""


def migrate_state(text, old_groups, new_groups):
    if list(old_groups) != list(new_groups):
        raise ValueError('Group identities/order changed; inspect saved state before migration')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 10:
        raise ValueError('Incomplete SimpleMenu state header')
    header = [int(line.rstrip(';')) for line in lines[:10]]
    if header[0] != 10:
        raise ValueError('Unsupported SimpleMenu state version')
    groups = list(old_groups)
    group_index, section_index = header[7:9]
    if not 0 <= group_index < len(groups):
        raise ValueError('Invalid saved group')
    old_current_group = groups[group_index]
    old_current_names = old_groups[old_current_group] + ['FAVORITES']
    if not 0 <= section_index < len(old_current_names):
        raise ValueError('Invalid saved section')
    current_name = old_current_names[section_index]
    saved = {}
    selected = {}
    return_index = 0
    index = -1
    for line in lines[10:]:
        fields = [int(field) for field in line.rstrip(';').split(';')]
        if len(fields) != 6:
            raise ValueError('Invalid saved section record')
        active, section, page, row, game, back = fields
        if section == 0:
            index += 1
        if not 0 <= index < len(groups):
            raise ValueError('Saved section group exceeds configuration')
        group = groups[index]
        names = old_groups[group] + ['FAVORITES']
        if not 0 <= section < len(names):
            raise ValueError('Saved section exceeds configuration')
        name = names[section]
        saved[(group, name)] = (page, row, game)
        if active:
            selected[group] = name
        if index == group_index:
            return_index = back
    new_current_group = old_current_group
    back_name = old_current_names[return_index] if 0 <= return_index < len(old_current_names) else None
    if current_name != 'FAVORITES':
        matches = [g for g, names in new_groups.items() if current_name in names]
        if len(matches) != 1:
            raise ValueError('Selected system was removed or duplicated')
        new_current_group = matches[0]
    elif back_name:
        matches = [g for g, names in new_groups.items() if back_name in names]
        if len(matches) == 1:
            new_current_group = matches[0]
            saved[(new_current_group, 'FAVORITES')] = saved.get((old_current_group, 'FAVORITES'), (0, 0, 0))
    new_names = new_groups[new_current_group] + ['FAVORITES']
    header[7] = groups.index(new_current_group)
    header[8] = new_names.index(current_name)
    new_return = new_names.index(back_name) if back_name in new_names else 0
    selected[new_current_group] = current_name
    result = [str(value) + ';' for value in header]
    for group, names in new_groups.items():
        names = names + ['FAVORITES']
        active_name = selected.get(group)
        if active_name not in names:
            active_name = names[0]
        for section, name in enumerate(names):
            position = saved.get((group, name))
            if position is None and name != 'FAVORITES':
                position = next((pos for (g, n), pos in saved.items() if n == name), None)
            page, row, game = position or (0, 0, 0)
            result.append(';'.join(map(str, [int(name == active_name), section, page, row, game, new_return])))
    return '\n'.join(result) + '\n'
