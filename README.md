# Музыкальный бот для Discord
Внимание! Это моя первая попытка написания бота для discord, бот немного сырой и могут присутствовать баги


<div align="center">
<img src=https://user-images.githubusercontent.com/58953935/160655855-861d8fc7-c94f-481f-93ad-35c301727fa7.png>
<p>Главное меню</p>
</div>

# Возможности
Бот умеет воспроизводить youtube ссылки, поддерживат как плей листы так и стримы. Так же есть возможность запуска локальных файлов расположенных в папке "Исполнители".

Усть возможность добовлять играющие композиции в избранное (Персонально для каждого) и воспроизводить (как ссылки так и локальные файлы)
Так же бонусом идет возможность удалять сообщения из чатов

Полный список комманд:

<div align="center">
<img src=https://user-images.githubusercontent.com/58953935/160659255-f778a14f-7d3c-4efa-b6be-c0fba43594a7.png>
<p>Help</p>
</div>

# Запуск
Для запуска потребуется Python 3.8 и выше, а так же потребуется установить FFmpeg.
После необходимо вписать в поле Tocken и FFmpeg_path токен вашего бота и полный путь к exe файлу FFmpeg а так же создать папку "Плейлисты" для поддержки персональных плей листов

Для работы локальных файлов необходимо создать папку "Исполнители", в которой разместить композици следующим образом: 

/Название исполнителя/год альбома - Группа - Название альбома/Номер трека. Название трека.mp3

При запуске бот автоматически проиндексирует все папки

После запуска бота необходимо указать канал бота, сделать это можно коммандой !Ch_chenal в нужном текстовом канале.

Рекомендую использовать пустой чат, поскольку в процессе работы будет удалятся все сообщения не написанные ботом.
