# coding=utf-8
import requests
import time
import os
from threading import Thread, current_thread
from Queue import Queue


theard_count = 25


domain_file = "domains.txt"
domain_temp = "temp"


def check_url(host):
    url = 'http://' + host

    try:
        requests.get(url, timeout=5)
    except Exception:
        return False
    else:
        return True


def run(queue, result_queue):
    # Цикл продолжается пока очередь задач не станет пустой
    while not queue.empty():
        # получаем первую задачу из очереди
        host = queue.get_nowait()
        print '{} checking in thread {}'.format(host, current_thread())
        # проверяем URL
        status = check_url(host)
        # сохраняем результат для дальнейшей обработки
        result_queue.put_nowait((status, host))
        # сообщаем о выполнении полученной задачи
        queue.task_done()
        print '{} finished in thread {}. Result={}'.format(host, current_thread(), status)

    print '{} closing'.format(current_thread())


# MAIN
def main():
    start_time = time.time()

    # Для получения задач и выдачи результата используем очереди
    queue = Queue()
    result_queue = Queue()

    fr_success = os.path.join(domain_temp, "req-good.txt")
    fr_errors  = os.path.join(domain_temp, "req-error.txt")

    # Сначала загружаем все URL из файла в очередь задач
    with open(domain_file) as f:
        for line in f:
            queue.put(line.strip())

    # Затем запускаем необходимое количество потоков
    for i in range(theard_count):
        thread = Thread(target=run, args=(queue, result_queue))
        thread.daemon = True
        thread.start()

    # И ждем, когда задачи будут выполнены    
    queue.join()


    

    # После чего пишем результаты в файлы
    with open(fr_success, 'w') as fs, open(fr_errors, 'w') as fe:
        while not result_queue.empty():
            status, host = result_queue.get_nowait()

            if status:
                f = fs
            else:
                f = fe

            f.write(host)
            f.write('\n')

    print time.time() - start_time

if __name__ == '__main__':
    main()
