
## Мини-сервис обработки видео

Загрузка видео доступна по ссылке на youtube и с локальной машины. В качестве имитации деятельности используются команды: 

convert(ffmpeg -y -i "{video_file}" "{output_file}")  
create_clip(ffmpeg -y -i "{video_file}" -ss 00:00:00 -to 00:00:05 -c copy "{output_file}")  
resize(ffmpeg -y -i "{video_file}" -vf scale=1280:720 "{output_file}")  
compress(ffmpeg -y -i "{video_file}" -vcodec libx264 -crf 28 "{output_file}")  

## Запуск

docker compose up --build

## API Reference

#### Отправить видео используя ссылку на youtube

```http
  POST /upload_url
```

| Параметр | Тип     | Описание                |
| :-------- | :------- | :------------------------- |
| `source` | `string` | **Required**. Ссылка на видео |
| `command` | `string` | **Required**. Одна из перечисленных команд |

Вернется id таска


```http
  POST /upload_file
```

| Параметр | Тип     | Описание                |
| :-------- | :------- | :------------------------- |
| `file` | `string` | **Required**. Путь к файлу |
| `command` | `string` | **Required**. Одна из перечисленных команд |

Вернется id таска

#### Получить информацию о задаче

```http
  GET /status/{task_id}
```

| Параметр | Тип     | Описание                |
| :-------- | :------- | :-------------------------------- |
| `task_id`      | `string` | **Required** |

Вернется статус задачи, в случае ее завершения также вернется название обработанного видео

#### Скачать обработанный файл

```http
  GET /download/{filename}
```

| Параметр | Тип     | Описание                |
| :-------- | :------- | :-------------------------------- |
| `filename`      | `string` | **Required** |




## Дополнительная информация

За распределение задач отвечает связка redis+celery, для бэка использован flask. Видео и их обработанные варианты удаляются после запроса на скачивание пользователем. Если запроса не было - воркер из задачи на очистку по расписанию их уберет.


