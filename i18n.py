"""Bilingual strings."""

STRINGS = {
    "zh": {
        "title": "孔明棋 / Peg Solitaire",
        "menu_play": "p) 开始游戏",
        "menu_help": "h) 帮助",
        "menu_scores": "l) 排行榜",
        "menu_settings": "s) 设置",
        "menu_quit": "q) 退出",
        "menu_choice": "请选择 > ",
        "bye": "再见!",
        "unknown": "未知选项: {choice}",
        "help_title": "帮助",
        "help_body": (
            "目标: 通过跳棋消除棋子, 最终只剩 1 颗 (理想情况下落在棋盘中心)。\n"
            "规则: 选一颗棋子, 跳过相邻的另一颗棋子, 落入空格。被跳过的棋子被移走。\n"
            "只能横/竖方向跳, 不能斜跳, 不能不跳。\n"
            "走子输入: 'r c d' (起点行,列 + 方向 u/d/l/r), 如 '3 1 r' 表示从(3,1)向右跳。\n"
            "也可以缩写为 '31r' 或 'r3c1 r'。\n"
            "命令: u=悔棋  h=提示  r=重置  q=放弃\n"
        ),
        "press_enter": "按回车继续...",
        "settings_title": "设置",
        "settings_lang": "1) 语言: {value}",
        "settings_sound": "2) 声音: {value}",
        "settings_volume": "3) 音量: {value}",
        "settings_variant": "4) 棋盘: {value}",
        "settings_back": "b) 返回",
        "scores_title": "排行榜 (Top 10)",
        "scores_empty": "暂无成绩",
        "scores_row": "{rank:>2}. {name:<12} {score:>5}  ({variant}, 剩 {pegs})",
        "name_prompt": "姓名(空= 不保存): ",
        "input_move": "走法 > ",
        "bad_format": "格式不正确, 例如 '3 1 r'",
        "illegal": "非法走法",
        "nothing_undo": "无可悔棋",
        "reset_done": "已重置",
        "hint_label": "提示: {move}",
        "no_hint": "无可走步",
        "pegs_left": "剩余棋子: {n}",
        "won": "胜利! 仅剩 1 颗棋子",
        "perfect": "完美! 棋子留在中心",
        "stuck": "无法继续, 还剩 {n} 颗棋子",
        "score_label": "得分: {score}",
        "result_perfect": "完美",
        "result_won": "胜利",
        "result_stuck": "卡住",
        "result_quit": "放弃",
        "variant_english": "英式 (33 孔)",
        "variant_european": "欧式 (37 孔)",
        "lang_zh": "中文",
        "lang_en": "英文",
        "on": "开",
        "off": "关",
        "dir_u": "上",
        "dir_d": "下",
        "dir_l": "左",
        "dir_r": "右",
    },
    "en": {
        "title": "Peg Solitaire (Hi-Q)",
        "menu_play": "p) Play",
        "menu_help": "h) Help",
        "menu_scores": "l) Leaderboard",
        "menu_settings": "s) Settings",
        "menu_quit": "q) Quit",
        "menu_choice": "Choose > ",
        "bye": "Bye!",
        "unknown": "Unknown option: {choice}",
        "help_title": "Help",
        "help_body": (
            "Goal: jump and remove pegs until only 1 remains (ideally in the centre).\n"
            "Rules: pick a peg, jump it over an orthogonally-adjacent peg into an empty hole.\n"
            "The jumped peg is removed. Diagonal jumps are not allowed.\n"
            "Move input: 'r c d' (source row,col + direction u/d/l/r),\n"
            "e.g. '3 1 r' jumps from (3,1) to the right. Compact form '31r' also works.\n"
            "Commands: u=undo  h=hint  r=reset  q=quit\n"
        ),
        "press_enter": "Press Enter to continue...",
        "settings_title": "Settings",
        "settings_lang": "1) Language: {value}",
        "settings_sound": "2) Sound: {value}",
        "settings_volume": "3) Volume: {value}",
        "settings_variant": "4) Board: {value}",
        "settings_back": "b) Back",
        "scores_title": "Leaderboard (Top 10)",
        "scores_empty": "No scores yet",
        "scores_row": "{rank:>2}. {name:<12} {score:>5}  ({variant}, {pegs} left)",
        "name_prompt": "Name (empty = skip save): ",
        "input_move": "Move > ",
        "bad_format": "Bad format, e.g. '3 1 r'",
        "illegal": "Illegal move",
        "nothing_undo": "Nothing to undo",
        "reset_done": "Reset",
        "hint_label": "Hint: {move}",
        "no_hint": "No moves available",
        "pegs_left": "Pegs left: {n}",
        "won": "You win! Only 1 peg left",
        "perfect": "Perfect! Last peg in the centre",
        "stuck": "No more moves — {n} pegs remain",
        "score_label": "Score: {score}",
        "result_perfect": "perfect",
        "result_won": "won",
        "result_stuck": "stuck",
        "result_quit": "quit",
        "variant_english": "English (33 holes)",
        "variant_european": "European (37 holes)",
        "lang_zh": "Chinese",
        "lang_en": "English",
        "on": "on",
        "off": "off",
        "dir_u": "up",
        "dir_d": "down",
        "dir_l": "left",
        "dir_r": "right",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    table = STRINGS.get(lang) or STRINGS["en"]
    s = table.get(key)
    if s is None:
        s = STRINGS["en"].get(key, key)
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s
