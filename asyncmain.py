import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import lxml
from time import sleep
import time
from random import randint
from selenium import webdriver
import csv
from multiprocessing import Pool

# domen = "https://www.olx.ua/dom-i-sad/"
domen = input("Введите URL: ")
cat_name_list = domen.split("/")
cat_name = cat_name_list[(len(cat_name_list))-2]
if not os.path.exists("data"):
    os.mkdir("data")
data_folder_path = 'data/' + cat_name


# Сортировка списка
def sort_key_digit_getter(row):
    raw_digit, *_ = row.split("_")
    return int(raw_digit)


# Получаем HTML всех страниц
def get_data():
    useragent = UserAgent()
    headers = {"user-agent": useragent.Chrome}
    # Вставляем url нужного раздела

    req = requests.get(url=domen, headers=headers)
    src = req.text

    if not os.path.exists(data_folder_path):
        os.mkdir(data_folder_path)
        print(f"Директория для \"{cat_name}\" успешно создана!")

    # Получаем главный html (Закомментируй)
    with open(f"{data_folder_path}/{cat_name}.html", "w", encoding="UTF-8") as file:
        file.write(src)
        print(f"HTML файл категории \"{cat_name}\" успешно сохранен!")
        sleep(randint(3,6))

    try:
        # Открываем главный html
        with open(f"{data_folder_path}/{cat_name}.html", "r", encoding="UTF-8") as file:
            src = file.read()
            print(f"HTML файл категории \"{cat_name}\" считан, начинаю работу!")
        soup = BeautifulSoup(src, "lxml")

        pages_num = soup.find("a", {"data-cy":"page-link-last"}).text.strip()
        print(f"Количество страниц с объявлениями = {pages_num}")
        # sleep(randint(1,3))
        pages_num = int(pages_num)

        if not os.path.exists(f"{data_folder_path}/pages"):
            os.mkdir(f"{data_folder_path}/pages")
            print(f"Директория для страниц поиска успешно создана!")

        # Сохраняем HTML страниц поиска в цикле
        for page in range(1,pages_num+1):
            headers = {"user-agent": useragent.Chrome}
            req = requests.get(url=(f"{domen}?page={page}"), headers=headers)
            src = req.text


            # Сохраняем HTML страницы (закомментрируй)
            with open(f"{data_folder_path}/pages/{page}_page.html", "w", encoding="UTF-8") as file:
                file.write(src)
                print(f"HTML cтраница №{page} категории \"{cat_name}\" успешно сохранена!")
                sleep(randint(3, 6))
                print(26*"-")
        print(f"- - - Успешно сохранено {pages_num} страниц - - -")

    except Exception as ex:
        print("Ошибка:")
        print(ex)

# Создаем CVS файл
def create_csv():
    with open(f"{data_folder_path}/{cat_name}.csv", "w", newline='', encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                "Имя",
                "Телефон",
                "Заголовок",
                "Цена",
                "Описание",
                "Категория",
                "Адрес",
                "Ссылка на фото",
                "Детали",
                "Добавлено:",
                "Ссылка на обьявление",
                "Ссылка на продавца"

            )
        )

def get_txt():
    # Упорядоченный список листов с объявлениями
    html_files_list = os.listdir(data_folder_path+"/pages")
    html_files_list = sorted(html_files_list, key=sort_key_digit_getter)

    try:
        # Цикл добавления ссылок на все товары со всех страниц данной категории
        list = []
        for html in html_files_list:
            print(f"- - - Открываем лист объявлений {html} - - -")
            with open(f"{data_folder_path}/pages/{html}", "r", encoding="UTF-8") as file:
                src = file.read()
            soup = BeautifulSoup(src, "lxml")
            tags_list = soup.findAll("tr",class_="wrap")
            for tag in tags_list:
                href = tag.find("a", {"data-cy":"listing-ad-title"}).get("href")
                list.append(href)
            print(f"Ссылки из листа объявлений {html} собраны")

        # Запись в TXT
        with open(f"{data_folder_path}/list.txt", "w", encoding="UTF-8") as file:
            for i in list:
                file.write(i+"\n")
        print("TXT файл со ссылками успешно записан")

    except Exception as ex:
        print("Ошибка:")
        print(ex)


def get_list():
    # Преобразуем из TXT обратно в list
    list = []
    with open(f"{data_folder_path}/list.txt", "r", encoding="UTF-8") as file:
        for line in file:
            list.append(line.strip())
    print(f"Всего ссылок на товары - {len(list)}")
    return list

def get_selenium_data(link):

    if not os.path.exists(f"{data_folder_path}/obyavlenie"):
        os.mkdir(f"{data_folder_path}/obyavlenie")
        print(f"Директория obyavlenie успешно создана!")


    link = link.split(".html")[0]
    link = link+".html"
    html_name = link.split("/")[-1]


    useragent = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={useragent.random}")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--headless")
    options.add_argument("--window-size=1280,1024")

    driver = webdriver.Chrome(options=options)

    try:
        print(f"Работаю с объявлением:")
        print(link)
        driver.get(link)
        sleep(randint(3,5))
        try:
            print("Попытка получить номер телефона")
            login_button = driver.find_element_by_xpath("/html/body/div[1]/section/div[3]/div/div[1]/div[2]/div/div[3]/ul/li[2]/div/strong").click()
            print("Номер телефона успешно получен")
        except Exception as ex:
            print(26*"- ")
            print(f"Ошибка в объявлении ищу по ВТОРОМУ пути")
            try:
                # sleep(randint(2, 4))
                login_button = driver.find_element_by_xpath(
                    "/html/body/div[1]/section/div[3]/div/div[1]/div[2]/div/div[4]/ul/li[2]/div").click()
                print("Номер телефона успешно получен")
                # sleep(randint(2, 4))
            except Exception as ex:
                print(f"Ошибка в объявлении ищу по ТРЕТЬЕМУ пути")
                try:
                    # sleep(randint(2, 4))
                    login_button = driver.find_element_by_xpath(
                        "/html/body/div[1]/section/div[3]/div/div[2]/div[2]/div/div[3]/ul/li[2]/div/strong").click()
                    print("Номер телефона успешно получен")
                except Exception as ex:
                    print(f"Ошибка в объявлении ищу по ЧЕТВЕРТОМУ пути")
                    try:
                        # sleep(randint(2, 4))
                        login_button = driver.find_element_by_xpath(
                            "/html/body/div[1]/section/div[3]/div/div[2]/div[2]/div/div[3]/ul/li[2]/div/span").click()
                        print("Номер телефона успешно получен")
                    except Exception as ex:
                        # print(ex)
                        print(f"Ошибка в объявлении ищу по ПЯТОМУ пути")
                        try:
                            # sleep(randint(2, 4))
                            login_button = driver.find_element_by_xpath(
                                "/html/body/div[1]/section/div[3]/div/div[2]/div[2]/div/div[3]/ul/li[2]").click()
                            print("Номер телефона успешно получен")
                        except Exception as ex:
                            print(f"Ошибка в объявлении ищу по ШЕСТОМУ пути")
                            try:
                                # sleep(randint(2, 4))
                                login_button = driver.find_element_by_xpath(
                                    "/html/body/div[1]/section/div[3]/div/div[2]/div[2]/div/div[3]/ul/li[2]/div").click()
                                print("Номер телефона успешно получен")
                            except Exception as ex:
                                print(f"Ошибка в объявлении ищу по CЕДЬМОМУ пути")
                                try:
                                    # sleep(randint(2, 4))
                                    login_button = driver.find_element_by_xpath(
                                        "/html/body/div[1]/section/div[3]/div/div[2]/div[2]/div/div[3]/ul/li[2]/div/i").click()
                                    print("Номер телефона успешно получен")
                                except Exception as ex:
                                    print(f"Ошибка в объявлении ищу по ВОСЬМОМУ пути")
                                    try:
                                        # sleep(randint(2, 4))
                                        login_button = driver.find_element_by_xpath(
                                            "/html/body/div[1]/section/div[3]/div/div[1]/div[2]/div/div[3]/ul/li[2]/div").click()
                                        print("Номер телефона успешно получен")
                                    except Exception as ex:
                                        print(f"Ошибка в объявлении ищу по ДЕВЯТОМУ пути")
                                        try:
                                            # sleep(randint(2, 4))
                                            login_button = driver.find_element_by_xpath(
                                                "/html/body/div[1]/section/div[3]/div/div[1]/div[2]/div/div[4]/ul/li[2]/div/strong").click()
                                            print("Номер телефона успешно получен")
                                        except Exception as ex:
                                            print(ex)

        sleep(randint(1,2))
        with open(f"{data_folder_path}/obyavlenie/{html_name}", "w") as file:
            file.write(driver.page_source)
        print(f"HTML объявления успешно сохранен")


        driver.close()
        driver.quit()
    except Exception as ex:
        print(ex)
        driver.close()
        driver.quit()


def parce_and_csv():

    folder_name = f"{data_folder_path}/obyavlenie"
    # print(folder_name)
    nazvaniya = os.listdir(folder_name)
    nazvaniya = sorted(nazvaniya)

    n = 1
    try:

        for html in nazvaniya:
            print(f"Работаю с обьявлением №:{n}")
            with open(f"{folder_name}/{html}", "r", encoding="UTF-8") as file:
                src = file.read()
            soup = BeautifulSoup(src, "lxml")

            try:
                cathegory = soup.find("td",class_="middle").text.strip().replace("\n\n\n","").replace("\n"," - ")
                # print(cathegory)
            except:
                cathegory = "-"


            try:
                user_name = soup.find("div",class_="offer-user__actions").find("h4").text.strip()
                # print(user_name)
            except:
                user_name = "-"


            try:
                phones = soup.find("strong",class_="xx-large").text
                # print(phones)
            except:
                phones = "-"


            try:
                adres = soup.find("div", class_="offer-user__address").text.strip()
                # print(adres)
            except:
                adres = "-"


            try:
                price = soup.find("div", class_="pricelabel").text.strip()
                # print(price)
            except:
                price = "-"


            try:
                head = soup.find("div",class_="offer-titlebox").find("h1").text.strip()
                # print(head)
            except:
                head = "-"

            try:
                descript = soup.find("div",id="textContent").text.strip()
                # print(descript)
            except:
                descript = "-"

            try:
                photo_href = soup.find("div",id="descImage").find("img").get("src")
                # print(photo_href)
            except:
                photo_href = "-"

            try:
                detals = soup.find("ul",class_="offer-details").text.strip().replace("\n\n\n\n","")
                # print(detals)
            except:
                detals = "-"

            try:
                user_href = soup.find("div",class_="offer-user__actions").find("h4").find("a").get("href")
                # print(user_href)
            except:
                user_href = "-"

            try:

                link = "https://www.olx.ua/obyavlenie/" + html
                print(link)
            except:
                link = "-"

            try:
                date = soup.find("li",class_="offer-bottombar__item").find("strong").text.strip()
                # print(date)
            except:
                date = "-"

            with open(f"{data_folder_path}/{cat_name}.csv", "a", newline='', encoding="UTF-8") as file:
                writer = csv.writer(file)
                writer.writerow(
                    (
                        user_name,
                        phones,
                        head,
                        price,
                        descript,
                        cathegory,
                        adres,
                        photo_href,
                        detals,
                        date,
                        link,
                        user_href
                    )
                )

            print(f"Объявление №:{n} успешно добавлено в csv таблицу, осталось {len(nazvaniya) - n}")
            n += 1


    except Exception as ex:
        print(ex)





def main():
    start_time = time.time()
    get_data()
    get_txt()
    p = Pool(processes=4)
    p.map(get_selenium_data, get_list())
    create_csv()
    parce_and_csv()
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
    main()
