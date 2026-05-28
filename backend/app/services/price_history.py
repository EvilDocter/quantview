from collections import defaultdict, deque


PRICE_HISTORY = defaultdict(
    lambda: deque(maxlen=200)
)