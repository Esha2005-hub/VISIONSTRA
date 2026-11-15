from dataclasses import dataclass
from typing import Optional
import time

TYPE_WEIGHT = {
    "car": 1.0, "truck": 1.0, "bus": 1.0,
    "motorcycle": 0.9, "bike": 0.8, "bicycle": 0.8,
    "person": 0.5, "pedestrian": 0.5, "dog": 0.4,
}

MAX_DISTANCE_M = 10.0
W_DIST, W_TYPE, W_POS, W_MOVE = 0.50, 0.20, 0.15, 0.15
HIGH_AT, MEDIUM_AT = 70, 50


@dataclass
class DetectedObject:
    kind: str
    distance_m: float
    x_center: float = 0.5
    prev_distance_m: Optional[float] = None


@dataclass
class RiskResult:
    obj: DetectedObject
    score: float
    level: str


def distance_score(d):
    return max(0.0, 1 - d / MAX_DISTANCE_M)


def type_score(kind):
    return TYPE_WEIGHT.get(kind.lower(), 0.5)


def position_score(x):
    return 1.0 if 0.33 <= x <= 0.67 else 0.6


def movement_score(obj):
    if obj.prev_distance_m is None:
        return 0.5
    change = obj.prev_distance_m - obj.distance_m
    if change > 0.3:
        return 1.0
    if change < -0.3:
        return 0.1
    return 0.4


def level_for(score):
    if score >= HIGH_AT:
        return "HIGH"
    if score >= MEDIUM_AT:
        return "MEDIUM"
    return "LOW"


def assess(obj):
    score = 100 * (
        W_DIST * distance_score(obj.distance_m)
        + W_TYPE * type_score(obj.kind)
        + W_POS * position_score(obj.x_center)
        + W_MOVE * movement_score(obj)
    )
    return RiskResult(obj, round(score, 1), level_for(score))


def prioritize(objects):
    return sorted((assess(o) for o in objects),
                  key=lambda r: r.score, reverse=True)


class AlertManager:
    def _init_(self, cooldown_s=3.0):
        self.cooldown_s = cooldown_s
        self.last_text = None
        self.last_time = 0.0

    def next_alert(self, objects):
        ranked = prioritize(objects)
        if not ranked:
            return None
        top = ranked[0]
        if top.level == "LOW":
            return None
        text = f"{top.level}: {top.obj.kind} {top.obj.distance_m:.0f} metres ahead"
        now = time.time()
        if text == self.last_text and now - self.last_time < self.cooldown_s:
            return None
        self.last_text, self.last_time = text, now
        return text
