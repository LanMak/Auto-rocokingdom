import logging
from typing import Optional

from config import CONFIG
from core.input import press_once
from core.logger import log_audit
from modes.base import BaseMode, BattleEvent
from modes.escape import EscapeMode


class SmartMode(BaseMode):
    def __init__(self) -> None:
        self._escape_delegate = EscapeMode()
        self._current_action: Optional[str] = None

    @property
    def name(self) -> str:
        return "smart"

    @property
    def label(self) -> str:
        return "智能模式"

    def _classify(self, event: BattleEvent) -> str:
        if event.pollute_capture_score > event.capture_score:
            return "battle"
        return "escape"

    def _log_classify(self, event: BattleEvent, prefix: str = "智能模式判型") -> None:
        mode_label = "聚能" if self._current_action == "battle" else "逃跑"
        logging.info(
            "%s: 本场战斗=%s（capture=%.3f, pollute_capture=%.3f）",
            prefix, mode_label, event.capture_score, event.pollute_capture_score,
        )

    def on_battle_start(self, event: BattleEvent) -> None:
        self._current_action = self._classify(event)
        self._log_classify(event)
        log_audit(
            "智能模式判型",
            战斗次数=event.battle_count,
            本场动作=self._current_action,
            capture分数=round(event.capture_score, 4),
            pollute_capture分数=round(event.pollute_capture_score, 4),
        )

    def on_action(self, event: BattleEvent, is_hit: bool, action_score: float) -> Optional[float]:
        if not is_hit:
            return None

        # Fallback: if not yet classified, do it now
        if self._current_action is None:
            self._current_action = self._classify(event)
            self._log_classify(event, prefix="智能模式兜底判型")

        if self._current_action == "battle":
            press_once(event.hwnd, CONFIG.press_key)
            logging.info("智能模式动作: 已触发按键 %s（本场=聚能）", CONFIG.press_key)
            return None
        else:
            logging.info("智能模式动作: 已触发 ESC（本场=逃跑）")
            return self._escape_delegate.on_action(event, is_hit, action_score)

    def on_battle_end(self, event: BattleEvent) -> None:
        self._current_action = None

    def on_tick_display(self, event: BattleEvent, is_hit: bool, action_score: float, action_template: str) -> None:
        logging.info(
            "行动检测=%s 行动分数=%.3f 检测模板=%s 污染次数=%d",
            is_hit, action_score, action_template, event.pollute_count,
        )
