class Controller:
    def __init__(self, elevs):
        self.elevs = elevs
        self.pending_requests = []

    def elv_choose(self, pickup_floor):
        elevs_distances = [
            (elev, abs(elev.current_floor - pickup_floor)) for elev in self.elevs
        ]

        free_elevs = filter(lambda elev_dist: not elev_dist[0].is_busy(), elevs_distances)
        nearest_elv = min(free_elevs, key=lambda elev_dist: elev_dist[1], default=None)

        nearest_elv and nearest_elv[0].set_busy(True)

        return nearest_elv[0] if nearest_elv else None

    def request(self, pickup_floor, target_floor):
        chosen_elv = self.elv_choose(pickup_floor)
        
        (lambda: chosen_elv.add_request(pickup_floor, target_floor), 
         lambda: self.pending_requests.append((pickup_floor, target_floor)))[chosen_elv is None]()

    def process_pending_requests(self):
        list(map(lambda elev: self.pending_requests and not elev.is_busy() and elev.add_request(*self.pending_requests.pop(0)), self.elevs))

class Elev:
    def __init__(self, current_floor, floor_dispatcher):
        self.current_floor = current_floor
        self.floor_dispatcher = floor_dispatcher
        self.movement_count = 0
        self.command_log = []
        self.busy = False
        self.requests = []
        self.direction = None
        self.target_floor = None

    def add_request(self, pickup_floor, target_floor):
        self.requests.append((pickup_floor, target_floor))
        self.process_requests()

    def set_target(self, target_floor):
        self.target_floor = self.floor_dispatcher.get_floor(target_floor)
        self.direction = ('up', 'down')[self.current_floor > self.target_floor]

    def move_up(self):
        next_floor = self.current_floor + 1
        self.current_floor = self.floor_dispatcher.get_floor(next_floor)
        self.movement_count += 1
        self.command_log.append(f"Подъем на {self.current_floor} этаж")

    def move_down(self):
        next_floor = self.current_floor - 1
        self.current_floor = self.floor_dispatcher.get_floor(next_floor)
        self.movement_count += 1
        self.command_log.append(f"Спуск на {self.current_floor} этаж")

    def open_doors(self):
        self.command_log.append(f"Открыть двери на {self.current_floor} этаже")

    def close_doors(self):
        self.command_log.append("Закрыть двери")

    def execute_movement(self):
        while self.current_floor != self.target_floor:
            self.movement_actions()[self.direction]()

    def process_requests(self):
        self.set_busy(True)
        while self.requests:
            pickup_floor, target_floor = self.requests.pop(0)
            self.set_target(pickup_floor)
            self.execute_movement()
            self.open_doors()
            self.close_doors()

            self.set_target(target_floor)
            self.execute_movement()
            self.open_doors()
            self.close_doors()
        self.set_busy(False)

    def movement_actions(self):
        return {'up': self.move_up, 'down': self.move_down}

    def get_commands(self):
        return "\n".join(self.command_log)

    def is_busy(self):
        return self.busy

    def set_busy(self, state):
        self.busy = state

class House:
    def __init__(self, num_floors, elevs_positions):
        self.num_floors = num_floors
        self.floor_dispatcher = FloorDispatcher(num_floors)
        self.elevs = [Elev(pos, self.floor_dispatcher) for pos in elevs_positions]
        self.controller = Controller(self.elevs)

    def process_request(self, pickup_floor, target_floor):
        self.controller.request(pickup_floor, target_floor)
        self.controller.process_pending_requests()

class InvalidFloorError(Exception):
    pass

class FloorDispatcher:
    def __init__(self, max_floor):
        self.valid_floors = {i: i for i in range(1, max_floor + 1)}

    def get_floor(self, floor):
        return self.valid_floors.get(floor) or self._invalid_floor(floor)

    def _invalid_floor(self, floor):
        raise InvalidFloorError(f"Этаж {floor} недопустим.")

if __name__ == "__main__":
    max_floor = 10
    elevs_positions = [2, 6]  

    building = House(max_floor, elevs_positions)

    queries = [(3, 10), (8, 4), (2, 5), (7, 1), (1, 9)]  
    for pickup_floor, target_floor in queries:
        building.process_request(pickup_floor, target_floor)

    for idx, elevator in enumerate(building.elevs):
        print(f"История команд лифта {idx + 1}:")
        print(elevator.get_commands())
        print()
