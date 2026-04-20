import logging
import time
from typing import Optional

from config import CONFIG
from core.capture import capture_window_bgr
from core.input import click_at, press_once
from core.logger import log_audit
from core.vision import best_yes_score_and_loc
from modes.base import BaseMode, BattleEvent


class EscapeMode(BaseMode):
    @property
    def name(self) -> str:
        return "escape"

    @property
    def label(self) -> str:
        return "逃跑模式"

    def on_action(self, event: BattleEvent, is_hit: bool, action_score: float) -> Optional[float]:
        if not is_hit:
            return None
        press_once(event.hwnd, "esc")
        logging.info("已触发 ESC")

        button_clicked = False
        yes_best_score = -1.0
        yes_best_loc = (0, 0)
        yes_threshold = CONFIG.match_threshold * 0.8

        for i in range(10):
            time.sleep(0.3)
            full_shot = capture_window_bgr(event.hwnd)
            best_score_this_round, best_loc_this_round = best_yes_score_and_loc(
                full_shot,
                event.templates,
                event.scale,
            )

            if best_score_this_round > yes_best_score:
                yes_best_score = best_score_this_round
                yes_best_loc = best_loc_this_round

            if best_score_this_round >= yes_threshold:
                cap_h, cap_w = full_shot.shape[:2]
                click_x = best_loc_this_round[0]
                click_y = best_loc_this_round[1]
                if cap_w > 0 and cap_h > 0 and (cap_w != event.window_width or cap_h != event.window_height):
                    click_x = int(round(best_loc_this_round[0] * event.window_width / cap_w))
                    click_y = int(round(best_loc_this_round[1] * event.window_height / cap_h))
                    click_x = max(0, min(event.window_width - 1, click_x))
                    click_y = max(0, min(event.window_height - 1, click_y))
                    logging.debug(
                        "点击坐标归一化: 截图=%sx%s 客户区=%sx%s 原始=(%s,%s) 映射=(%s,%s)",
                        cap_w, cap_h, event.window_width, event.window_height,
                        best_loc_this_round[0], best_loc_this_round[1],
                        click_x, click_y,
                    )

                click_ok = click_at(event.hwnd, click_x, click_y)
                button_clicked = click_ok
                if click_ok:
                    log_audit("逃跑确认点击成功", 模式=self.name)
                    break

        if not button_clicked:
            logging.warning("触发 ESC 后未找到确认按钮 yes.png")
            log_audit(
                "逃跑确认点击失败",
                模式=self.name,
                最佳是按钮分数=round(yes_best_score, 4),
            )

        # Extra cooldown to prevent ESC spam while dialog is closing
        return 2.0
