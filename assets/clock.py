import numpy as np
from collections import deque

class Clock:
    def __init__(self):
        self.current_time = 0
        self.max_time = 24*4
        self.time_list = deque(np.arange(0, 24*4), maxlen=self.max_time)
        self.time_list.append(self.current_time)

    def tick(self):
        self.current_time += 1
        # Reset to 0 after reaching 24 hours (1440 minutes)
        if self.current_time >= self.max_time:
            self.current_time = 0

        self.time_list.append(self.current_time)

    def get_time(self):
        return self.current_time
    
    def get_time_list(self):
        return np.array(self.time_list)/4  # Convert deque to list for display purposes


# # Example usage
# clock = Clock()
# for _ in range(24*5):  # 24 hours * 4 ticks per hour + 1 to show reset
#     print(clock.tick())
