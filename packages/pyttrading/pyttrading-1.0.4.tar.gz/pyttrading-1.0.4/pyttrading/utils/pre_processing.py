def remove_noise_trading(actions=None):
    
    action_open = 0
    action_list = []
    for i, action in enumerate(actions):
        action = int(action)
        action_filter = 0
        if action_open == 0:
            if action != 0:
                action_open = action
                action_filter = action
        elif action_open == 1:
            if action == 1 or action == 0:
                action_filter = 0
            elif action == 2:
                action_filter = action
                action_open = action
        elif action_open == 2:
            if action == 2 or action == 0:
                action_filter = 0
            elif action == 1:
                action_filter = action
                action_open = action
    
        action_list.append(action_filter)
    
    return action_list


def interval_to_minutes(interval):
    if interval.endswith('m'):
        return int(interval[:-1])
    elif interval.endswith('h'):
        return int(interval[:-1]) * 60
    else:
        return None


def interval_to_seconds(interval):
    if interval.endswith('m'):
        return int(interval[:-1]) * 60
    elif interval.endswith('h'):
        return int(interval[:-1]) * 60 * 60
    else:
        return None
