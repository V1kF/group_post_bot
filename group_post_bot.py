import requests
import json
import random
import re
import os

GROUP_ID='айди вашей группы'
USER_TOKEN_ALL='пользовательский токен'
USER_TOKEN_VIDEO='токен с правами на видео'
GROUP_TOKEN='токен группы'

# функция,отвечающая за отправку сообщений
def msg(peer_ids, key_message, message, keyboard='', attachment=None):

    random_id = random.getrandbits(64)

    answer_str = requests.post('https://api.vk.com/method/messages.send',
                               data={'peer_ids': peer_ids,
                                     'random_id': random_id,
                                     'access_token': GROUP_TOKEN,
                                     key_message: message, 'keyboard': keyboard, 'attachment': attachment,
                                     'v': '5.130'})
    answer_str = answer_str.text
    answer = json.loads(answer_str)
    return answer

def receive():  # функция для замены значений в запросе сообщений

    global server
    global key
    global ts

    # запрос на получение данных для запроса сообщений(key,ts,server)
    session_str = requests.get(
        f'https://api.vk.com/method/groups.getLongPollServer?group_id={GROUP_ID}&access_token={GROUP_TOKEN}&v=5.130')
    session_str = session_str.text
    session = json.loads(session_str)

    # переменные для замены значений в запросе сообщений
    server = session['response']['server']
    key = session['response']['key']
    ts = session['response']['ts']

def btn(type, payload, label, color):#функция для создания кнопок
    d = {
        "action": {
            "type": type,
            "payload": payload,
            "label": label
        },
        "color": color
    }
    return d

def make_post(owner_id, count, filter='all', extended='0', ):
    answer_str = requests.post('https://api.vk.com/method/wall.get',
                               data={'owner_id': '-' + f'{owner_id}',
                                     'access_token': USER_TOKEN_ALL,
                                     'count': count, 'filter': filter, 'extended': extended, 'v': '5.130'})
    answer_str = answer_str.text
    answer = json.loads(answer_str)
    return answer

def preparing_posts():
    pass
# данные о админах сообщества
admins = {}
# ---------------------------------------------
# запрос на получение данных для запроса сообщений(key,ts,server)
session_str = requests.get(
    f'https://api.vk.com/method/groups.getLongPollServer?group_id={GROUP_ID}&access_token={GROUP_TOKEN}&v=5.130')
session_str = session_str.text
session = json.loads(session_str)

# переменные для замены значений в запросе сообщений
server = session['response']['server']
key = session['response']['key']
ts = session['response']['ts']

while True:

    # запрос на получение событий,которые приходят боту
    receiving_messages_str = requests.get(f'{server}?act=a_check&key={key}&wait=25&mode=2&ts={ts}')
    receiving_messages_str = receiving_messages_str.text
    receiving_messages = json.loads(receiving_messages_str)
    #print(receiving_messages)

    if receiving_messages.get('ts') != None and receiving_messages.get('updates') != None:

        ts = receiving_messages['ts']  # добавляем постоянную замену ts,ибо с каждым новым сообщением его надо менять

        for event in receiving_messages['updates']:  # обход внутренностей updates,дабы обнаружить какие типы сообщений пришли

            # обработка событый
            if event.get('type') == 'message_new':

                from_id = event["object"]["message"]["from_id"]

                text = event['object']['message']['text']

                print('Новое сообщение: ' + text)

                # поиск id человека
                if admins.get(from_id)==None:# если человек с таким id не найден

                    answer_str = requests.post('https://api.vk.com/method/groups.getMembers',
                                               data={'group_id': GROUP_ID,
                                                     'filter': 'managers',
                                                     'access_token': GROUP_TOKEN,
                                                     'v': '5.130'})
                    answer_str = answer_str.text
                    answer = json.loads(answer_str)
                    print(answer)

                    for manager in answer['response']['items']:

                        if from_id == manager['id'] and (manager['role']=='administrator' or manager['role']=='creator'):  # проверка на то,является ли человек администратором

                            # добавление id в словарь
                            admins[from_id]={}

                if admins.get(from_id)!=None: #если человек является администратором сообщества

                    if admins[from_id].get('menu')!=None:

                        menu=admins[from_id]['menu']

                        if menu== 1:

                            if re.fullmatch(r".+vk\.com/([a-zA-Z0-9._-]+)", text):

                                result = re.findall(r'vk\.com/([a-zA-Z0-9._-]+)',  text)

                                if re.fullmatch(r"club([a-zA-Z0-9._-]+)", result[0]):

                                    result_2 = re.findall(r'club([a-zA-Z0-9._-]+)', text)

                                    admins[from_id]['owner_id']=result_2[0]

                                    msg(from_id, 'message', 'Славненько🍃')

                                elif re.fullmatch(r"public([a-zA-Z0-9._-]+)", result[0]):

                                    result_3 = re.findall(r'public([a-zA-Z0-9._-]+)', text)

                                    admins[from_id]['owner_id']=result_3[0]

                                    msg(from_id, 'message', 'Славненько🍃')

                                elif re.fullmatch(r"event([a-zA-Z0-9._-]+)", result[0]):

                                    result_4 = re.findall(r'event([a-zA-Z0-9._-]+)', text)

                                    admins[from_id]['owner_id']=result_4[0]

                                    msg(from_id, 'message', 'Славненько🍃')

                                else:
                                    answer_str = requests.post('https://api.vk.com/method/groups.getById',#получение айди группы,если domain не стандартный
                                                               data={'group_ids': result[0],
                                                                     'access_token': USER_TOKEN_ALL,
                                                                     'v': '5.130'})
                                    answer_str = answer_str.text
                                    answer = json.loads(answer_str)


                                    admins[from_id]['owner_id']=answer['response'][0]['id']

                                    msg(from_id, 'message', 'Славненько🍃')

                            elif text != '|1|' and text != '|2|' and text != '|3|' and \
                                    text != '/хочу посты':

                                msg(from_id, 'message', 'Вы ввели не ссылку')

                        if menu == 2:
                            if str.isdigit(text):
                                if int(text) > 0 and int(text) <= 20:

                                    admins[from_id]['count_post'] = int(text)

                                    msg(from_id, 'message', 'Славненько🍃')

                                if int(text) > 20:

                                    msg(from_id, 'message', 'Вы ввели слишком большое число')

                                if int(text) <= 0:

                                    msg(from_id, 'message', 'Вы ввели слишком маленькое число')

                            elif text != '|1|' and text != '|2|' and text != '|3|':

                                msg(from_id, 'message', 'Это не число😞')

                    if text == '/хочу посты':
                        a = {
                            "one_time": False,
                            "buttons": [[]]
                        }

                        a['buttons'][0].append(btn("text", '{\"command\": \"1\"}', "|1|", 'primary'))
                        a['buttons'][0].append(btn("text", '{\"command\": \"2\"}', "|2|", 'primary'))
                        a['buttons'][0].append(btn("text", '{\"command\": \"3\"}', "|3|", 'primary'))

                        a = json.dumps(a)  # делаем json,ибо keyboard принимает ток его

                        msg(from_id, 'message',
                            '1)Введите ссылку на группу,из которой хотите получить посты)🍃'
                            '\n2)Укажите количество нужных постов🙌🏻\n3)Хочу посты🙏🏻',a)

                if event['object']['message'].get('payload') != None: # проверяем есть ли ключ payload(нажата ли кнопка)

                    payload_str = event['object']['message']['payload']

                    payload = json.loads(payload_str)

                    if payload["command"]=="1":  # кнопка "Ввод группы"
                        print(admins)

                        admins[from_id]['menu']=1

                        msg(from_id, 'message','Введите ссылку на группу)')

                    if payload["command"]=="2":  # кнопка "Укажите кол-во постов"

                        admins[from_id]['menu']=2

                        msg(from_id, 'message','Укажите количество нужных постов🙌🏻')

                    if payload["command"]=="3":  # кнопка "Хочу посты"

                        admins[from_id]['menu']=3

                        if admins[from_id].get('count_post')!=None and admins[from_id].get('owner_id')!=None:

                            dataPosts = make_post(admins[from_id]['owner_id'],admins[from_id]['count_post'])

                            if dataPosts.get('response'):

                                items = dataPosts['response']['items']

                                url = ''
                                mp4 = 0
                                media_del = []

                                for item in items:  # перебираем посты/репосты

                                    id = item['id']

                                    owner_id = item['owner_id']

                                    text = item['text']

                                    if item.get('attachments'):  # пост

                                        print('post')

                                        for attachment in item['attachments']:  # перебираем содержимое

                                            if attachment['type'] == "photo":  # перебираем фотки

                                                media_id = attachment['photo']['id']

                                                access_key = attachment['photo']['access_key']

                                                url = url + 'photo' + str(owner_id) + '_' + str(
                                                    media_id) + '_' + str(
                                                    access_key) + ','

                                            elif attachment['type'] == "doc":# перебираем гифки

                                                media_id = attachment['doc']['id']

                                                media_del.append(media_id)

                                                access_key = attachment['doc']['access_key']

                                                if not os.path.exists(f'{id}/'):

                                                    os.makedirs(f'{id}/')

                                                send = requests.get(attachment['doc']['url'], stream=True)

                                                with open(f'{id}/{media_id}.gif', 'ab') as file:

                                                    for chunk in send.iter_content(1024000):
                                                        file.write(chunk)

                                                upload_url = requests.post(
                                                    'https://api.vk.com/method/docs.getUploadServer',
                                                    data={'group_id': GROUP_ID,
                                                          'access_token': USER_TOKEN_ALL,
                                                          'v': '5.131'})

                                                upload_url = upload_url.text

                                                upload_url = json.loads(upload_url)

                                                request = requests.post(upload_url['response']['upload_url'],
                                                                        files={'file': open(
                                                                            f'{id}/{media_id}.gif', 'rb')})
                                                request = request.text

                                                request = json.loads(request)

                                                save = requests.post(
                                                    'https://api.vk.com/method/docs.save',
                                                    data={'file': request['file'],
                                                          'access_token': USER_TOKEN_ALL,
                                                          'v': '5.131'})

                                                save = save.text

                                                save = json.loads(save)

                                                url = url + 'doc' + str(
                                                    save['response']['doc']['owner_id']) + '_' + str(
                                                    save['response']['doc']['id']) + ','

                                            elif attachment['type'] == "audio":# перебираем аудио

                                                media_id = attachment['audio']['id']

                                                if attachment['audio'].get('owner_id'):

                                                    url = url + 'audio' + str(attachment['audio']['owner_id']) + '_' \
                                                          + str(attachment['audio']['id']) + '_' + str(access_key) + ','

                                                else:
                                                    url = url + 'audio' + str(owner_id) + '_' + str(
                                                        media_id) + '_' + str(access_key) + ','



                                            elif attachment['type'] == "video":# перебираем видео

                                                media_id = attachment['video']['id']

                                                media_del.append(media_id)

                                                access_key = attachment['video']['access_key']

                                                if attachment['video'].get('owner_id'):

                                                    answer_str = requests.post(
                                                        'https://api.vk.com/method/video.get',
                                                        data={'videos': str(attachment['video']['owner_id']) + '_' + str(
                                                            media_id) + '_' + access_key,
                                                              'access_token': USER_TOKEN_VIDEO,
                                                              'v': '5.131'})

                                                    answer_str = answer_str.text

                                                    answer = json.loads(answer_str)

                                                else:
                                                    answer_str = requests.post(
                                                        'https://api.vk.com/method/video.get',
                                                        data={'videos': str(owner_id) + '_' + str(media_id) + '_' + access_key,
                                                              'access_token': USER_TOKEN_VIDEO,
                                                              'v': '5.131'})

                                                    answer_str = answer_str.text

                                                    answer = json.loads(answer_str)

                                                files = answer['response']['items'][0]['files']

                                                if files.get('external') == None:  # если видео из вк

                                                    for key in files:

                                                        if re.fullmatch(r"mp4_(\d+)", key):

                                                            result = re.findall(r'mp4_(\d+)', str(key))

                                                            if int(result[0]) > int(mp4):

                                                                mp4 = result[0]

                                                                url_mp4 = files[f'mp4_{mp4}']

                                                            mp4 = 0

                                                    if not os.path.exists(f'{id}/'):

                                                        os.makedirs(f'{id}/')

                                                    send = requests.get(url_mp4, stream=True)

                                                    with open(f'{id}/{media_id}.mp4', 'ab') as file:

                                                        for chunk in send.iter_content(1024000):

                                                            file.write(chunk)

                                                    upload_url = requests.post(
                                                        'https://api.vk.com/method/video.save',
                                                        data={'group_id': GROUP_ID,
                                                              'wallpost': '0',
                                                              'access_token': USER_TOKEN_VIDEO,
                                                              'v': '5.131'})

                                                    upload_url = upload_url.text

                                                    upload_url = json.loads(upload_url)
                                                    #print(upload_url)
                                                    request = requests.post(upload_url['response']['upload_url'],
                                                                            files={'file': open(
                                                                                f'{id}/{media_id}.mp4',
                                                                                'rb')})
                                                    request = request.text

                                                    request = json.loads(request)

                                                    url = url + 'video' + str(request['owner_id']) + '_' + str(
                                                        request['video_id']) + ','
                                                    print(url)

                                                else:  # если видео с внешнего видеохостинга

                                                    answer_str = requests.post(
                                                        'https://api.vk.com/method/video.save',
                                                        data={'link': files['external'],
                                                              'group_id': GROUP_ID,
                                                              'wallpost': '0',
                                                              'access_token': USER_TOKEN_VIDEO,
                                                              'v': '5.131'})
                                                    answer_str = answer_str.text
                                                    answer = json.loads(answer_str)

                                                    upload_url = requests.get(answer['response']['upload_url'])
                                                    upload_url = upload_url.text
                                                    upload_url = json.loads(upload_url)

                                                    url = url + 'video' + str(
                                                        upload_url['owner_id']) + '_' + str(
                                                        upload_url['video_id']) + ','

                                    else:  # репост
                                        print('repost')
                                        for repost in item['copy_history']:  # перебираем посты из репоста
                                            id = repost['id']
                                            owner_id = repost['owner_id']
                                            text = repost['text']

                                            for attachment in repost['attachments']:  # перебираем содержимое репоста

                                                if attachment['type'] == "photo":  # перебираем фотки

                                                    media_id = attachment['photo']['id']

                                                    access_key = attachment['photo']['access_key']

                                                    url = url + 'photo' + str(owner_id) + '_' + str(
                                                        media_id) + '_' + str(
                                                        access_key) + ','

                                                elif attachment['type'] == "doc":# перебираем гифки

                                                    media_id = attachment['doc']['id']

                                                    media_del.append(media_id)

                                                    access_key = attachment['doc']['access_key']

                                                    if not os.path.exists(f'{id}/'):

                                                        os.makedirs(f'{id}/')

                                                    send = requests.get(attachment['doc']['url'], stream=True)

                                                    with open(f'{id}/{media_id}.gif', 'ab') as file:

                                                        for chunk in send.iter_content(1024000):
                                                            file.write(chunk)

                                                    upload_url = requests.post(
                                                        'https://api.vk.com/method/docs.getUploadServer',
                                                        data={'group_id': GROUP_ID,
                                                              'access_token': USER_TOKEN_ALL,
                                                              'v': '5.131'})
                                                    upload_url = upload_url.text
                                                    upload_url = json.loads(upload_url)
                                                    print(upload_url)

                                                    request = requests.post(upload_url['response']['upload_url'],
                                                                            files={'file': open(
                                                                                f'{id}/{media_id}.gif',
                                                                                'rb')})
                                                    request = request.text
                                                    request = json.loads(request)
                                                    print(request)

                                                    save = requests.post(
                                                        'https://api.vk.com/method/docs.save',
                                                        data={'file': request['file'],
                                                              'access_token': USER_TOKEN_ALL,
                                                              'v': '5.131'})
                                                    save = save.text
                                                    save = json.loads(save)
                                                    print(save)

                                                    url = url + 'doc' + str(
                                                        save['response']['doc']['owner_id']) + '_' + str(
                                                        save['response']['doc']['id']) + ','
                                                    print(url)

                                                elif attachment['type'] == "audio":  # перебираем аудио

                                                    media_id = attachment['audio']['id']

                                                    if attachment['audio'].get('owner_id'):
                                                        url = url + 'audio' + str(
                                                            attachment['audio']['owner_id']) + '_' + str(
                                                            attachment['audio']['id']) + '_' + str(access_key) + ','
                                                        print(url)
                                                    else:
                                                        url = url + 'audio' + str(owner_id) + '_' + str(
                                                            media_id) + '_' + str(access_key) + ','

                                                    # print(url)

                                                elif attachment['type'] == "video":  # перебираем видеозаписи

                                                    media_id = attachment['video']['id']

                                                    media_del.append(media_id)

                                                    access_key = attachment['video']['access_key']

                                                    if attachment['video'].get('owner_id'):

                                                        answer_str = requests.post(
                                                            'https://api.vk.com/method/video.get',
                                                            data={'videos': str(
                                                                attachment['video']['owner_id']) + '_' + str(
                                                                media_id) + '_' + access_key,
                                                                  'access_token': USER_TOKEN_VIDEO,
                                                                  'v': '5.131'})

                                                        answer_str = answer_str.text

                                                        answer = json.loads(answer_str)

                                                    else:
                                                        answer_str = requests.post(
                                                            'https://api.vk.com/method/video.get',
                                                            data={'videos': str(owner_id) + '_' + str(
                                                                media_id) + '_' + access_key,
                                                                  'access_token': USER_TOKEN_VIDEO,
                                                                  'v': '5.131'})
                                                        answer_str = answer_str.text
                                                        answer = json.loads(answer_str)

                                                    files = answer['response']['items'][0]['files']

                                                    if files.get('external') == None:  # если видео из вк

                                                        for key in files:

                                                            if re.fullmatch(r"mp4_(\d+)", key):

                                                                result = re.findall(r'mp4_(\d+)', str(key))

                                                                if int(result[0]) > int(mp4):

                                                                    mp4 = result[0]

                                                                    url_mp4 = files[f'mp4_{mp4}']

                                                                mp4 = 0

                                                        if not os.path.exists(f'{id}/'):

                                                            os.makedirs(f'{id}/')

                                                        send = requests.get(url_mp4, stream=True)

                                                        with open(f'{id}/{media_id}.mp4', 'ab') as file:

                                                            for chunk in send.iter_content(10240000):
                                                                file.write(chunk)

                                                        upload_url = requests.post(
                                                            'https://api.vk.com/method/video.save',
                                                            data={'group_id': GROUP_ID,
                                                                  'wallpost': '0',
                                                                  'access_token': USER_TOKEN_VIDEO,
                                                                  'v': '5.131'})

                                                        upload_url = upload_url.text

                                                        upload_url = json.loads(upload_url)

                                                        request = requests.post(
                                                            upload_url['response']['upload_url'], files={
                                                                'file': open(f'{id}/{media_id}.mp4',
                                                                             'rb')})
                                                        request = request.text
                                                        request = json.loads(request)

                                                        url = url + 'video' + str(
                                                            requests['response']['owner_id']) + '_' + str(
                                                            requests['response']['video_id']) + ','

                                                    else:  # если видео с внешнего видеохостинга

                                                        answer_str = requests.post(
                                                            'https://api.vk.com/method/video.save',
                                                            data={'link': files['external'],
                                                                  'group_id': GROUP_ID,
                                                                  'wallpost': '0',
                                                                  'access_token': GROUP_TOKEN,
                                                                  'v': '5.131'})
                                                        answer_str = answer_str.text
                                                        answer = json.loads(answer_str)

                                                        upload_url = requests.get(answer['response']['upload_url'])

                                                        upload_url = upload_url.text

                                                        upload_url = json.loads(upload_url)

                                                        url = url + 'video' + str(
                                                            upload_url['response']['owner_id']) + '_' + str(
                                                            upload_url['response']['video_id']) + ','

                                    msg(event["object"]["message"]["from_id"], 'message', text, None, url)

                                    answer_str = requests.post('https://api.vk.com/method/wall.post',
                                                               data={'owner_id': '-'+GROUP_ID,
                                                                     'from_group': '1',
                                                                     'message': text,
                                                                     'attachments': url,
                                                                     'access_token': USER_TOKEN_ALL,
                                                                     'v': '5.131'})
                                    answer_str = answer_str.text
                                    answer = json.loads(answer_str)

                                    msg(event["object"]["message"]["from_id"], 'message', 'Выполнено🧤(на стене)')
                                    print(media_del)

                                    if os.path.exists(f'{id}'):#удаление медиа
                                        while not media_del==[]:
                                            for media in media_del:

                                                os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)),f'{id}/{media}.mp4'))

                                                media_del.remove(media)

                                        os.removedirs(f'{id}')



                                    url = ''



                        else:

                            msg(event["object"]["message"]["from_id"], 'message', 'Вы не указали нужные данные')

    if receiving_messages.get('failed') != None:  # проверка на содержимое ответа от запроса сообщений

        if receiving_messages['failed'] == 1:
            receive()

        if receiving_messages['failed'] == 2:
            receive()

        if receiving_messages['failed'] == 3:
            receive()