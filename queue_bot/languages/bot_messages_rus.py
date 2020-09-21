
admin_help = '''
/new_queue          - создать новую очередь без перемешивания
/new_random_queue   - создать новую случайную очередь
/edit_queue         - меню редактирования очереди
/select_queue       - выбор очереди из списка
/delete_queue       - удаление очереди из списка

/edit_registered    - меню редактирования зарегистированных
/admin              - добавить нового админа
/del_admin          - удалить админа

/setup_subject      - установить параметры выбора тем
/allow_choose       - начать выбор тем в общем чате
/stop_choose        - закончить выбор тем в общем чате 
                        (получить таблицу можно 
                        через команду /get_choice_table)
/get_choice_table   - получить ексель таблицу с данными'''


# name must be specified with \n
# to mimic telegram trimming first characters if they are \n
queue_format = '''{name}Сдает:
{current}
Следующий:
{next}

Оставшиеся:
{other}

когда сдашь
/i_finished
чтобы выйти из очереди
/remove_me
чтобы попасть в конец очереди
/add_me'''


queue_simple_format = '{name}:\n{students}'


permission_denied = 'Нет разрешения'
code_not_valid = 'Внутренняя ошибка: Уровень доступа имеет неверный формат'
not_owner = 'Не владелец'
enter_students_list = 'Введите новый список студентов\nон должен состоять из строк с именами студентов'
set_registered_students = 'Введите новый список студентов он должен состоять из строк\n'\
                          'в формате: имя_студента-telegram_id'
del_registered_students = 'Чтобы удалить несколько пользователей, введите их позиции в списке через пробел'
get_user_message = 'Перешлите сообщение пользователя, которого необходимо добавить'
queue_finished = 'Очередь завершена'
unknown_user = 'Неизвестный пользователь. Вы не можете использовать данную команду\n' \
               '(возможно в вашем аккаунте ID закрыт для просмотра)'
all_known_users = 'Все известные пользователи:\n{0}'
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
send_choice_numbers = 'Присылайте выбранные номера тем в формате\n' \
                      '/ch <номер1> <номер2> ... <номер5>\n' \
                      '(через пробел в порядке приоритетности)'
send_choice_file_name = 'Пришлите имя файла с темами'
send_subject_name_without_spaces = 'Пришлите название файла с темами без пробелов'
send_number_range = 'Пришлите интервал целых чисел\nв формате <минимум>-<максимум>'
number_range_incorrect = 'Интервал целых чисел имеет неверный формат'
number_interval_set = 'Интервал установлен'
set_repeatable_limit = 'Пришлите максимальное число людей, которые могут выбрать одну тему ' \
                       '(\"0\" будет означать выбор по умолчанию)'
int_value_incorrect = 'Данное значение - не целое число, повторите попытку'
value_set = 'Значение установлено.'
finished_choice_manager_creation = 'Задание параметров завершено, с этого момента возможен выбор тем, ' \
                                   'напишите в общем чате /allow_choose'
choices_collection_stopped = 'Выбор тем завершен'
choices_collection_not_started = 'Выбор тем еще не был начат(контактируйте с админом, чтобы начать его)'
show_choices = 'Выбранные темы:\n{0}\n\nДоступные темы:\n{1}'
your_choice = 'Ваша тема - {0}'
choices_not_made = 'Еще не были выбраны'
not_available = 'Нет доступных'
get_choices_excel_file = 'Файл со всеми выбранными темами'
your_choice_deleted = 'Ваша запись удалена'
cannot_choose_any_subject = 'Не удалось выбрать ни одной темы'
set_new_choice_file = 'Установите новый файл для сохранения тем\n' \
                      '(в личном чате бота /admin_help)'
copy_queue = 'Чтобы скопировать очередь, вставьте текст сообщения в команду /new_queue'
enter_queue_name = 'Введите имя для очереди. Оно будет отображено на сообщении с очередью.\n' \
                   'Имя не должно содержать пробелов, разрешается \'_\'\n' \
                   '(это имя также используется для создания файла для хранения)'
name_incorrect = 'Имя в неверном формате.'
queue_set = 'Очередь установлена'
queue_limit_reached = 'Больше очередей установить нельзя, удалите некоторые из них'
queue_removed = 'Очередь \'{0}\' удалена'
queue_not_found = 'Очередь не найдена'
title_select_queue = 'Выбор очереди'
