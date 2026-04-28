from datetime import datetime
from typing import Optional

from config import CONFIG
from core.input import press_once
from modes.base import BaseMode, BattleEvent

_Ts = lambda: datetime.now().strftime("%H:%M:%S")


class BattleMode(BaseMode):
    @property
    def name(self) -> str:
        return "battle"

    @property
    def label(self) -> str:
        return "聚能模式"

    def on_action(self, event: BattleEvent, is_hit: bool, action_score: float) -> Optional[float]:
        if not is_hit:
            return None
        press_once(event.hwnd, CONFIG.press_key)
        print(f"[{_Ts()}] 已触发按键: {CONFIG.press_key}（连续模式）")
        return None
