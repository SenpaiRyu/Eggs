# Ton-Nft-Sniper
___
Необходимо скачать Python, при установке везде ставить галочки где видите PATH
https://www.python.org/downloads/

Ознакомьтесь с кодом в main.py, прочитайте комментарии что там есть, они помогут вам заранее понять, что не так

Контракт вашего кошелька должен быть wallet_v4r2, проверить это можно на https://tonviewer.com

Создайте новый кошелек и закиньте туда бабосики, не используйте свой мейн!!!! 

1. Запустить install.bat он установит необходимые либы 
2. В файле config.py установить свои данные
3. Запустить скрипт через start.bat(Если таким образом у вас не запускается скрипт, тогда вам нужно открыть папку со скриптом в cmd/powershell терминале и прописать python main.py)


Кошелек для доната: youarenoteligible.ton

Относительно этого момента на 14 строке. Перед каждым запуском скрипта, нужно ввести туда 2 последних адреса контракта продажи, иначе он пустит две транзы в холостую, на кошели откуда уже купили нфт, тем самым -0.02 тона
```python
# Самая важная часть, которая все еще работает колхозно, адреса что тут находятся это два последних адреса контракта продажи, если не хотите в пустую тратить бабки на комсу при каждом старте софта, то найдите по адресу EQBmSy9SfRj44LZPi84NyvI4seJlZYSz33MM0rl78DnkCb2Z последние два кошеля с контрактом продажи и напишите их тут
processed_addresses = {
    "EQAk5i9ti7_mUU1QLqUU8TBkZqpivzNwQXMXIfBge5c7QRZD",
    "EQDbMFUDqzo_5ZgaWivQRKoxIuaZpzTL5Qtz1OCCYaXDJP_4"
}
```
