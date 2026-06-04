import argparse
import logging
import math
import random

parser = argparse.ArgumentParser(description="Парсер лаб09")

parser.add_argument("lambda_val", help="Интенсивность входящего потока заявок", default=0.8, type=float)
parser.add_argument("mu_val", help="Интенсивность обработки заявок", default=1.0, type=float)
parser.add_argument("logging_step", help="Шаг визуализации", default=100.0, type=float)
parser.add_argument("N", help="Количество заявок", type=int, default=1000)


def check_args_correctness(lambda_val: float, mu_val: float, logging_step: float, N: int):
    if (lambda_val <= 0) or (mu_val <= 0) or (N <= 0):
        logging.error(f"Параметры должны быть неотрицательны")
        raise ValueError(f"Параметры должны быть неотрицательны")

def shiny_output(emp_p0: float, emp_p1: float):
    print(f"{'-'*60}")
    print(f"Эмперические вероятности:")
    print(f"Сервер свободен: {emp_p0}")
    print(f"Сервер занят: {emp_p1}")

def simulate(lambda_val: float, mu_val: float, logging_step: float, N: int):
    rho = lambda_val / mu_val

    theo_p0 = 1.0 / (1.0 + rho) # сервер свободен
    theo_p1 = rho / (1.0 + rho) # сервер занят
    print(f"Теоретические значения:\nвероятность отказа = {theo_p1}\nВероятность обслуживания: {theo_p0}")

    accepted = 0
    refused = 0
    current_time = 0.0
    server_free_at = 0.0
    next_logging_timestamp = logging_step
    for query_n in range(N):
        req_arrival = -math.log(max(random.random(), 1e-10)) / lambda_val
        current_time += req_arrival
        if current_time >= server_free_at:
            accepted += 1
            service_time = -math.log(max(random.random(), 1e-10)) / mu_val
            server_free_at = current_time + service_time
        else:
            refused += 1
        if current_time >= next_logging_timestamp:
            print(f"Текущее время моделирования: {current_time} у.е, Обработано заявок: {query_n}")
            shiny_output(accepted/query_n, refused/query_n)
            next_logging_timestamp += logging_step

    total_time = current_time # время прихода последней заявки

    # Эмпирические вероятности
    emp_p0 = accepted / N
    emp_p1 = refused / N

    return (emp_p0, emp_p1, total_time)

if __name__ == "__main__":
    args = parser.parse_args()
    lambda_val = args.lambda_val
    mu_val = args.mu_val
    logging_step = args.logging_step
    N = args.N
    check_args_correctness(lambda_val, mu_val, logging_step, N)
    print(f"Начало имитационного моделирования...")
    final_p0, final_p1, modelling_time = simulate(lambda_val, mu_val, logging_step, N)
    print(f"{'='*60}")
    print(f"Время моделирования: {modelling_time}")
    print(f"Эмперические вероятности:")
    print(f"Сервер свободен: {final_p0}")
    print(f"Сервер занят: {final_p1}")