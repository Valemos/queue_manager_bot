
admin_help = '''
/new_queue          - создать новую очередь без перемешивания
/new_random_queue   - создать новую случайную очередь
/edit_queue         - меню редактирования очереди

/edit_registered    - меню редактирования зарегистированных
/admin              - добавить нового админа
/del_admin          - удалить админа

/setup_subject      - установить параметры выбора тем
/allow_choose       - начать выбор тем в общем чате
/stop_choose        - закончить выбор тем в общем чате 
                        (получить таблицу можно 
                        через команду /get_choice_table)
/get_choice_table   - получить ексель таблицу с данными'''

permission_denied = 'Нет разрешения'
code_not_valid = 'Внутренняя ошибка: Уровень доступа имеет неверный формат'
not_owner = 'Не владелец'
enter_students_list = 'Введите новый список студентов\nон должен состоять из строк с именами студентов'
set_registered_students = 'Введите новый список студентов он должен состоять из строк\n'\
                          'в формате: имя_студента-telegram_id'
del_registered_students = 'Чтобы удалить несколько пользователей, введите их позиции в списке через пробел'
get_user_message = 'Перешлите сообщение пользователя, которого необходимо добавить'
queue_finished = 'Очередь завершена'
unknown_user = 'Неизвестный пользователь. Вы не можете использовать данную команду ' \
               '(возможно в вашем аккаунте ID закрыт для просмотра)'
all_known_users = 'Все известные пользователи:\n{0}'
queue_commands = 'когда сдашь\n' \
                 '/i_finished\n' \
                 'чтобы выйти из очереди\n' \
                 '/remove_me\n' \
                 'чтобы попасть в конец очереди\n' \
                 '/add_me'
error_in_values = 'Ошибка в значениях'
was_not_forwarded = 'Сообщение ни от кого не переслано, или закрыт для просмотра ID пользователя'
user_register_successfull = 'Пользователь зарегистрирован'
queue_not_exists_create_new = 'Очереди нет.\nХотите создать новую?'
create_new_queue = 'Удалить предыдущую очередь и создать новую?'
title_edit_queue = 'Редактирование очереди'
title_edit_registered = 'Редактирование пользователей'
queue_not_exists = 'Очереди нет.'
first_user_added = 'Первый владелец добавлен - {0}'
already_requested_send_message = 'Уже запрошено, пришлите сообщение нового владельца'
admins_added = 'Администраторы добавлены'
bot_already_running = 'Бот уже запущен.'
bot_stopped = 'Бот остановлен, и больше не принимает команд'
your_turn_not_now = '{0}, вы не сдаете сейчас.'
you_deleted = 'Вы удалены из очереди'
you_not_found = 'Вы не найдены в очереди'
you_added_to_queue = 'Вы записаны в очередь'
send_student_number_and_new_position = 'Пришлите номер студента в очереди и через пробел номер новой позиции'
users_deleted = 'Пользователи удалены'
error_in_this_values = 'Ошибка возникла в этих значениях:\n{0}'
send_student_numbers_with_space = 'Пришлите номер студентов в очереди через пробел'
not_index_from_queue = 'Не номер из очереди. Отмена операции'
student_added_to_end = 'Студент добавлен в конец'
send_student_number = 'Пришлите номер одного студента в очереди'
queue_deleted = 'Очередь удалена'
position_set = 'Позиция установлена'
send_new_position = 'Пришлите номер новой позциции'
students_set = 'Студенты установлены'
student_set = 'Студент установлен'
students_moved = 'Студенты перемещены'
student_moved = 'Студент перемещен'
send_student_name_to_end = 'Пришлите имя нового студента, он будет добавлен в конец очереди'
admin_set = 'Администратор установлен'
admin_deleted = 'Администратор удален'
users_added = 'Пользователи добавлены'
enter_new_list_in_order = 'Введите список новых имен для всех пользователей в порядке их расположения ' \
                          '(каждое имя с новой строки)'
send_two_positions_students_space = 'Пришлите номера двух студентов через пробел'
names_more_than_users = 'Количество введенных имен больше количества пользователей'
random_queue_created_from_registered = 'Очередь создана из списка известных студентов'
send_choice_numbers = 'Присылайте выбранные номера тем, возможно выбрать до 5 тем, ' \
                      'пишите через пробел в порядке приоритетности, \n' \
                      'чтобы остановить набор тем, администратор пиши\n/stop_choose'
send_choice_file_name = 'Пришлите имя файла с темами'
send_subject_name_without_spaces = 'Пришлите название файла с темами без пробелов'
send_number_range = 'Пришлите интервал целых чисел\nв формате <минимум>-<максимум>'
number_range_incorrect = 'Интервал целых чисел имеет неверный формат'
number_interval_set = 'Интервал установлен'
set_repeatable_limit = 'Пришлите максимальное число людей, которые могут выбрать одну тему ' \
                       '(\"0\" будет означать выбор по умолчанию)'
value_incorrect = 'Данное значение - не целое число, повторите попытку'
value_set = 'Значение установлено.'
finished_choice_manager_creation = 'Задание параметров завершено, с этого момента возможен выбор тем, ' \
                                   'напишите в общем чате /allow_pick_subjects'
choices_collection_stopped = 'Выбор тем завершен'
show_choices = 'Выбранные темы:\n{0}'
get_choices_excel_file = 'Файл со всеми выбранными темами'
