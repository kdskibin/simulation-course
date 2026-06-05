import heapq
import random
import math
from dataclasses import dataclass, field
from typing import Optional, Any

class EventType:
    ARRIVAL = 0
    DEPARTURE = 1
    IMPATIENT = 2

@dataclass(order=True)
class Event:
    time: float
    type: int = field(compare=True)
    agent_id: int = field(compare=False)
    agent_ref: Any = field(compare=False, repr=False)

class Request:
    """Агент-заявка"""
    def __init__(self, req_id: int, arrival_time: float, service_time: float,
                 max_wait_time: float, is_vip: bool = False):
        self.id = req_id
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.max_wait_time = max_wait_time
        self.is_vip = is_vip
        self.state = "created"
        self.server_id = None

    def on_arrival(self, system, current_time: float):
        self.state = "arrived"
        prefix = "VIP " if self.is_vip else ""
        system.log(f"t={current_time:.2f} | {prefix}Заявка #{self.id}: прибытие")
        system.stats['total_arrivals'] += 1

        free_server = system.get_free_server()
        if free_server:
            self.start_service(free_server, system, current_time)
        else:
            if system.queue_length < system.max_queue_size:
                if self.is_vip:
                    # VIP вставляется в конец VIP-секции (перед обычными заявками)
                    insert_pos = system.vip_count
                    system.queue.insert(insert_pos, self)
                    self.state = "waiting"
                    system.log(f"t={current_time:.2f} | VIP Заявка #{self.id}: в очередь (VIP секция, позиция {system.vip_count})")
                else:
                    system.queue.append(self)
                    self.state = "waiting"
                    system.log(f"t={current_time:.2f} | Заявка #{self.id}: в очередь (позиция {system.vip_count + system.regular_count})")
                imp_time = current_time + self.max_wait_time
                if imp_time <= system.duration:
                    system.schedule_event(imp_time, EventType.IMPATIENT, self.id, self)
            elif self.is_vip:
                # VIP-заявка: выбиваем первую обычную заявку из очереди
                if system.regular_count > 0:
                    bumped = system.queue.pop(system.vip_count)
                    bumped.state = "refused"
                    system.stats['total_refused'] += 1
                    system.log(f"t={current_time:.2f} | Заявка #{bumped.id}: выбита из очереди VIP-заявкой #{self.id}")

                    # Переносим VIP в конец VIP-секции
                    insert_pos = system.vip_count
                    system.queue.insert(insert_pos, self)
                    self.state = "waiting"
                    system.log(f"t={current_time:.2f} | VIP Заявка #{self.id}: в очередь (выбила заявку #{bumped.id})")
                    imp_time = current_time + self.max_wait_time
                    if imp_time <= system.duration:
                        system.schedule_event(imp_time, EventType.IMPATIENT, self.id, self)
                else:
                    self.state = "refused"
                    system.stats['total_refused'] += 1
                    system.log(f"t={current_time:.2f} | VIP Заявка #{self.id}: ОТКАЗ (очередь полна VIP-заявками)")
            else:
                self.state = "refused"
                system.stats['total_refused'] += 1
                system.log(f"t={current_time:.2f} | Заявка #{self.id}: ОТКАЗ (очередь полна)")

    def start_service(self, server, system, current_time: float):
        self.state = "serving"
        self.server_id = server.id
        wait_time = current_time - self.arrival_time
        system.stats['total_wait_time'] += wait_time
        system.stats['total_served'] += 1
        system.stats['total_service_time'] += self.service_time
        
        server.on_start_service(self, system, current_time)
        system.log(f"t={current_time:.2f} | Заявка #{self.id}: сервер #{server.id}, ждал {wait_time:.2f}, обслуживание {self.service_time:.2f}")
        
        dep_time = current_time + self.service_time
        if dep_time <= system.duration:
            system.schedule_event(dep_time, EventType.DEPARTURE, self.id, self)

    def on_impatient(self, system, current_time: float):
        if self.state == "waiting":
            if self.is_vip:
                # удаляем последнюю VIP-заявку
                system.queue.pop(system.vip_count - 1)
            else:
                # Обычная: удаляем из секции обычных (начинается с индекса vip_count)
                system.queue.pop(system.vip_count)
            self.state = "impatient"
            system.stats['total_impatient'] += 1
            waited = current_time - self.arrival_time
            prefix = "VIP " if self.is_vip else ""
            system.log(f"t={current_time:.2f} | {prefix}Заявка #{self.id}: ушла (нетерпеливость), ждала {waited:.2f}")

    def on_departure(self, system, current_time: float):
        self.state = "served"
        server = system.get_server_by_id(self.server_id)
        if server:
            server.on_finish_service(system, current_time)
        system.log(f"t={current_time:.2f} | Заявка #{self.id}: завершение обслуживания на сервере #{self.server_id}")


class ServerAgent:
    """Агент-сервер (канал обслуживания)"""
    def __init__(self, server_id: int):
        self.id = server_id
        self.is_busy = False
        self.current_request = None
        self.free_at = 0.0

    def on_start_service(self, request, system, current_time: float):
        self.is_busy = True
        self.current_request = request
        self.free_at = current_time + request.service_time

    def on_finish_service(self, system, current_time: float):
        self.is_busy = False
        self.current_request = None
        if system.queue:
            next_req = system.queue.pop(0)
            next_req.start_service(self, system, current_time)


class QueueingSystem:
    """Среда, координатор событий и сборщик статистики"""
    def __init__(self, num_servers: int, max_queue_size: int, arrival_rate: float,
                 service_rate: float, max_patience: float, duration: float,
                 vip_prob: float = 0.0):
        self.num_servers = num_servers
        self.max_queue_size = max_queue_size
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.max_patience = max_patience
        self.duration = duration
        self.vip_prob = vip_prob

        self.servers = [ServerAgent(i+1) for i in range(num_servers)]
        self.queue = []

        self.event_queue = []
        self.current_time = 0.0

        self.stats = {
            'total_arrivals': 0, 'total_served': 0, 'total_refused': 0,
            'total_impatient': 0, 'total_wait_time': 0.0, 'total_service_time': 0.0
        }
        self.log_entries = []

        self.time_points = []
        self.busy_servers_series = []
        self.queue_length_series = []

        self.request_counter = 0

    @property
    def vip_count(self):
        """Количество VIP-заявок в очереди (индексы 0..vip_count-1)"""
        count = 0
        for item in self.queue:
            if item.is_vip:
                count += 1
            else:
                break
        return count

    @property
    def regular_count(self):
        """Количество обычных заявок в очереди"""
        return len(self.queue) - self.vip_count

    @property
    def queue_length(self):
        """Общая длина очереди"""
        return len(self.queue)
        
    def log(self, message: str):
        self.log_entries.append(message)
        
    def schedule_event(self, time: float, event_type: int, agent_id: int, agent_ref: Any):
        heapq.heappush(self.event_queue, Event(time, event_type, agent_id, agent_ref))
        
    def get_free_server(self) -> Optional[ServerAgent]:
        for s in self.servers:
            if not s.is_busy: return s
        return None
        
    def get_server_by_id(self, server_id: int) -> Optional[ServerAgent]:
        for s in self.servers:
            if s.id == server_id: return s
        return None
        
    def run(self):
        snapshot_interval = self.duration / 500 if self.duration > 0 else 1
        next_snapshot_time = 0.0
        
        # Генерация первого прибытия
        self.request_counter += 1
        inter_arrival = -math.log(max(random.random(), 1e-10)) / self.arrival_rate
        arrival_time = self.current_time + inter_arrival
        service_time = -math.log(max(random.random(), 1e-10)) / self.service_rate
        is_vip = random.random() < self.vip_prob
        req = Request(self.request_counter, arrival_time, service_time, self.max_patience, is_vip=is_vip)
        self.schedule_event(arrival_time, EventType.ARRIVAL, req.id, req)
        
        while self.event_queue and self.current_time <= self.duration:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            
            if self.current_time > self.duration: break
                
            # Снимки состояния для графиков
            while next_snapshot_time <= self.current_time and next_snapshot_time <= self.duration:
                self.time_points.append(next_snapshot_time)
                self.busy_servers_series.append(sum(1 for s in self.servers if s.is_busy))
                self.queue_length_series.append(len(self.queue))
                next_snapshot_time += snapshot_interval
                
            # Делегирование события соответствующему агенту
            if event.type == EventType.ARRIVAL:
                event.agent_ref.on_arrival(self, self.current_time)
                if self.current_time < self.duration:
                    self.request_counter += 1
                    inter_arrival = -math.log(max(random.random(), 1e-10)) / self.arrival_rate
                    next_time = self.current_time + inter_arrival
                    service_time = -math.log(max(random.random(), 1e-10)) / self.service_rate
                    next_req = Request(self.request_counter, next_time, service_time, self.max_patience, is_vip=(random.random() < self.vip_prob))
                    self.schedule_event(next_time, EventType.ARRIVAL, next_req.id, next_req)
                    
            elif event.type == EventType.DEPARTURE:
                event.agent_ref.on_departure(self, self.current_time)
                
            elif event.type == EventType.IMPATIENT:
                event.agent_ref.on_impatient(self, self.current_time)
                
        # Финальный снимок
        if next_snapshot_time <= self.duration:
             self.time_points.append(self.duration)
             self.busy_servers_series.append(sum(1 for s in self.servers if s.is_busy))
             self.queue_length_series.append(len(self.queue))