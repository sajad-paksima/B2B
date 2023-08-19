import multiprocessing
import requests
import time

token1 = "8yhzP83fAnHNfj49V5Toqqq5K46kKblNL78SKLveU8EJTMU2"
token2 = "6TWNQivV9SjIy9m7LO6Bi6Y11VyG7gPxdm4gYyR1nGhNtDGk"
username1 = "Mohammad"
username2 = "Zahra"

def register_two_user(username1, username2):
    global token1, token2
    response1 = requests.post("http://localhost:8000/accounts/register/", {
        "username": username1,
        "password": "1234"
    })
    token1 = response1.json()["token"]
    response2 = requests.post("http://localhost:8000/accounts/register/", {
        "username": username2,
        "password": "1234"
    })
    token2 = response2.json()["token"]
    # token1 = Token.objects.get(user=User.objects.get(username=username1)).token
    # token2 = Token.objects.get(user=User.objects.get(username=username2)).token

# def delete_users(username1, username2):
#     User.objects.get(username=username1).delete()
#     User.objects.get(username=username2).delete()

def submit_charge(amount, receiver):
    requests.post("http://localhost:8000/submit/charge/", {
        "token": "test",
        "amount": amount,
        "receiver": receiver
    })

def submit_sell(token, amount, phone_number):
    requests.post("http://localhost:8000/submit/sell/", {
        "token": token,
        "amount": amount,
        "phone_number": phone_number
    })

def parallel_test(size):
    charge_processes = []
    sell_processes = []

    charge_processes.append(multiprocessing.Process(target=submit_charge, args=("2000", username1)))
    charge_processes.append(multiprocessing.Process(target=submit_charge, args=("1500", username2)))

    for _ in range(size):
        sell_processes.append(multiprocessing.Process(target=submit_sell, args=(token1, "100", "09123456789")))
        sell_processes.append(multiprocessing.Process(target=submit_sell, args=(token2, "70", "09198765432")))

    for process in charge_processes:
        process.start()
    for process in charge_processes:
        process.join()

    for process in sell_processes:
        process.start()
    for process in sell_processes:
        process.join()

def find_avg_response_time(size):
    low_trafic_process = multiprocessing.Process(target=submit_sell, args=(token1, "200", "09158749614"))
    start_time = time.time()
    low_trafic_process.start()
    low_trafic_process.join()
    end_time = time.time()
    print(f'Response time for low trafic (1 request(s) per second) is {round((end_time - start_time) * 1000)} ms.')
    high_trafic_processes = []
    for _ in range(size):
        high_trafic_processes.append(multiprocessing.Process(target=submit_sell, args=(token1, "10", "09133458796")))
    start_time = time.time()
    for process in high_trafic_processes:
        process.start()
    for process in high_trafic_processes:
        process.join()
    end_time = time.time()
    print(f'Response time for high trafic ({size} requests per second) is {round((end_time - start_time) * 1000)} ms.')
    print(f'Amortized response time for high trafic ({size} requests per second) is'
          f' {round((end_time - start_time) * 1000 / size)} ms.')

if __name__ == "__main__":
    # register_two_user(username1, username2)
    # parallel_test(10)
    find_avg_response_time(50)