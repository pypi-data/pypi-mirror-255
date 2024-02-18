from afeng_tools.linux_tool import sh_tools


def run_cmd(cmd_str: str) -> list[tuple]:
    """运行命令"""
    result_list = []
    out_list = sh_tools.run(cmd_str)
    if out_list:
        out_list = list(filter(lambda x: True if x else False, out_list))
        for tmp_line in out_list:
            tmp_info_tuple = tuple(filter(lambda x: True if x else False, tmp_line.strip().split(' ')))
            result_list.append(tmp_info_tuple)
    return result_list


def run_task_list(task_name: str):
    result_list = []
    out_list = run_cmd(f'tasklist|findstr "{task_name}"')
    for tmp_info_tuple in out_list:
        result_list.append({
            'title': tmp_info_tuple[0],
            'pid': tmp_info_tuple[1],
            'name': tmp_info_tuple[2],
            'session_count': tmp_info_tuple[3],
            'memory_usage': tmp_info_tuple[4] + tmp_info_tuple[5],
        })
    return result_list


def run_task_kill(pid: int | str):
    run_cmd(f' taskkill /F /pid {pid}')


if __name__ == '__main__':
    for tmp_task in run_task_list('nginx'):
        run_task_kill(tmp_task.get('pid'))

