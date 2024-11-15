# NginxProxyManager-CertsLoader
Загрузка сертификатов с Nginx proxy manager с использованием API. 

# Требования

+ python3
+ pip
+ venv
+ git Опциаонально

# Установка

+ Устанавливаем нужные пакеты (приблизительно так)

```console
sudo apt install git python3.12-venv
```
+ Установка скрипта

```console
git clone https://github.com/fabrikant/NginxProxyManager-CertsLoader.git
cd NginxProxyManager-CertsLoader
chmod +x install.sh
./install.sh
```

# Использование

```console
./load-cert.sh -hp HOST_PORT -u USER -p PASSWORD -d DOMAIN -k KEY -c CERT
```

+ HOST_PORT - адрес и порт админской части Nginx Proxy Manager. Например: 192.168.5.1:81 или localhost:81
+ USER - Пользователь Nginx Proxy Manager (его mail). Можно создать специально для этого пользователя и забрать у него все права кроме промотра сертификатов.
+ PASSWORD - Пароль пользователя
+ DOMAIN - доменное имя для которого качаем сертификат
+ KEY - Путь и имя файла, куда будет сохранен приватный ключ
+ CERT - Путь и имя файла, куда будет сохранен сертификат (fullchain)

# Использование с MAILU

Создать файл **mailu.sh** в каталоге со скриптом и примерно следующим содержимым (заменить параметры своими значениями): 

```console
#!/bin/bash 
SCRIPT_PATH=$(dirname $0)
cd $SCRIPT_PATH
./load-cert.sh -hp HOST_PORT -u USER -p PASSWORD -d DOMAIN -k KEY -c CERT
cd /mailu
docker compose down
docker compose -p mailu up -d
./ 
```

Сделать файл исполняемым 
```console
chmod +x mailu.sh
```

Добавить расписание в **crontab**

```console
sudo crontab -e
```
 И что-нибудь вроде:

```console
 0 1 * * 6 /mailu/NginxProxyManager-CertsLoader/mailu.sh
 ```