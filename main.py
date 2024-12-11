class Controller:
    def __init__(self, elevs):
        self.elevs = elevs  

    def elv_choose(self, pickup_floor):
        # Выбираем свободный ближайший лифт 


        elevs_distances = [
            (self.elevs[0], abs(self.elevs[0].current_floor - pickup_floor)),
            (self.elevs[1], abs(self.elevs[1].current_floor - pickup_floor))
        ]

        # Фильтруем занятые и выбираем ближайший свободный если есть
        free_elevs = [elev for elev, distance in elevs_distances if not elev.is_busy()]
        nearest_elv = min(free_elevs, key=lambda elev: abs(elev.current_floor - pickup_floor), default=None)
        nearest_elv and nearest_elv.set_busy(True)

        return nearest_elv
    def request(self, pickup_floor, target_floor):
        chosen_elv = self.elv_choose(pickup_floor)
        self.move_elv(chosen_elv, pickup_floor)

        chosen_elv.open_doors()
        chosen_elv.close_doors()

        self.move_elv(chosen_elv, target_floor)

        chosen_elv.open_doors()
        chosen_elv.close_doors()

        return chosen_elv.movement_count, chosen_elv



    def move_elv(self, elevator, target_floor):
        elevator.set_target(target_floor)
        elevator.execute_movement()

class Elev:
    def __init__(self, current_floor, floor_dispatcher):
        self.current_floor = current_floor
        self.floor_dispatcher = floor_dispatcher  
        self.movement_count = 0
        self.command_log = []
        self.busy = False
        self.direction = None
        self.target_floor = None
        
        self.movement_actions = {
            'up': self.move_up,
            'down': self.move_down
        }

    def set_target(self, target_floor):
        # Задаем нужный этаж, проверяем с помощью FloorDispatcher, потом расчитываем направление 
        self.target_floor = self.floor_dispatcher.get_floor(target_floor)  # Проверка допустимости этажа
        self.direction = 'up' if self.current_floor < self.target_floor else 'down'

    def move_up(self):
        next_floor = self.current_floor + 1
        self.current_floor = self.floor_dispatcher.get_floor(next_floor)  # Проверка через диспетчер
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
        # Исполняем команду движения в направлении до нужного этажа
        while self.current_floor != self.target_floor:
            self.movement_actions[self.direction]()

    def get_commands(self):
        return "\n".join(self.command_log)

    def is_busy(self):
        return self.busy

    def set_busy(self, state):
        self.busy = state





class House:
    def __init__(self, num_floors, elevs_positions):
        self.num_floors = num_floors
        self.floor_dispatcher = FloorDispatcher(num_floors)  # Создаем диспетчер этажей
        self.elevs = [Elev(pos, self.floor_dispatcher) for pos in elevs_positions]
        self.controller = Controller(self.elevs)

    def process_request(self, pickup_floor, target_floor):
        moves, elevator = self.controller.request(pickup_floor, target_floor)
        return moves, elevator


class InvalidFloorError(Exception):
    pass


class FloorDispatcher:
    def __init__(self, max_floor):
        self.valid_floors = {i: i for i in range(1, max_floor + 1)}

    def get_floor(self, floor):
        # Возвращает этаж или выбрасывает исключение
        try:
            return self.valid_floors[floor]  
        except KeyError:
            raise InvalidFloorError(f"Этаж {floor} недопустим.")



if __name__ == "__main__":
    max_floor = 10
    elevs_positions = [2, 6]  
    
    building = House(max_floor, elevs_positions)
    
    queries = [(3, 10), (8, 4)] 
    for idx, elevator in enumerate(building.elevs):
        pickup_floor, target_floor = queries[idx]
        moves, chosen_elv = building.process_request(pickup_floor, target_floor)
        print(f"Лифт совершил {moves} команд перемещения до открытия дверей на {target_floor} этаже")
        print(f"Начальная позиция лифта {idx + 1}: {elevs_positions[idx]} этаж")
        print(f"История команд лифта {idx + 1}:")
        print(elevator.get_commands())
        print()
