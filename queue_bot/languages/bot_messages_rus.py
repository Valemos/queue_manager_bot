# name must be specified with \n
# to mimic telegram trimming first characters if they are \n
queue_format = '''{name}Сдает:
{current}
Следующие:
{next}

{other}

когда сдашь
/i_finished
чтобы выйти из очереди
/remove_me
чтобы попасть в конец очереди
/add_me'''

copy_queue_format = '/new_queue {name}\n{students}'

unknown_command = 'Неизвестная команда'

queue_simple_format = '{name}:\n{students}'
default_queue_name = 'Без_имени'
permission_denied = 'Нет разрешения'
code_not_valid = 'Внутренняя ошибка: Уровень доступа имеет неверный формат'
not_owner = 'Не владелец'
enter_students_list = 'Введите новый список студентов\nон должен состоять из строк с именами студентов ' \
                      'не более 60 символов каждое'
set_registered_students = 'Введите новый список студентов он должен состоять из строк\n' \
                          'в формате: имя_студента-telegram_id'
del_registered_students = 'Чтобы удалить несколько пользователей, введите их позиции в списке через пробел'
get_user_message = 'Перешлите сообщение пользователя, которого необходимо добавить'
was_not_forwarded = 'Сообщение ни от кого не переслано, или закрыт для просмотра ID пользователя'
queue_finished_select_other = '{0}\n\n' \
                              'В очереди никого нет\n' \
                              'добавьтесь /add_me\n' \
                              'или выберите очередь /select_queue'
queue_finished = 'Очередь завершена'
all_known_users = 'Все известные пользователи:\n{0}'
error_in_values = 'Ошибка в значениях'
user_register_successful = 'Пользователь зарегистрирован'
queue_not_exists_create_new = 'Очереди нет.\nХотите создать новую?'
select_queue_or_create_new = 'Выберите очередь командой /select_queue'
create_new_queue = 'Cоздать новую очередь?'
title_edit_queue = 'Редактирование очереди'
title_edit_registered = 'Редактирование пользователей'
queue_not_selected = 'Очередь не выбрана'
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
student_added_to_end = 'Студент {0} добавлен в конец'
send_student_number = 'Пришлите номер одного студента в очереди'
position_set = 'Позиция установлена'
send_new_position = 'Пришлите номер новой позциции'
enter_student_name = 'Введите имя студента'
students_set = 'Студенты установлены'
student_set = 'Студент установлен'
students_moved = 'Студенты перемещены'
student_moved = 'Студент перемещен'
students_swapped = 'Студенты {0} и {1} поменялись'
send_student_name_to_end = 'Пришлите имя нового студента, он будет добавлен в конец очереди'
admin_set = 'Администратор установлен'
admin_deleted = 'Администратор удален'
users_added = 'Пользователи добавлены'
enter_new_list_in_order = 'Введите список новых имен для всех пользователей в порядке их расположения ' \
                          '(каждое имя с новой строки и не более 40 символов)'
send_two_positions_students_space = 'Пришлите номера двух студентов через пробел'
names_more_than_users = 'Количество введенных имен больше количества пользователей'
random_queue_created_from_registered = 'Очередь создана из списка известных студентов'

send_choice_numbers = \
    '''Присылайте выбранные номера тем в формате
/ch <номер1> <номер2> ... <номер5>
(через пробел в порядке приоритетности)'''

send_choice_file_name = 'Пришлите имя файла с темами'
send_subject_name_without_spaces = 'Пришлите название файла с темами без пробелов'
send_number_range = 'Пришлите интервал целых чисел\nв формате <минимум>-<максимум> (края включены)'
number_range_incorrect = 'Интервал целых чисел имеет неверный формат'
number_interval_set = 'Интервал установлен'
set_repeatable_limit = 'Пришлите максимальное число людей, которые могут выбрать одну тему ' \
                       '(\"0\" будет означать выбор по умолчанию)'
int_value_incorrect = 'Данное значение - не целое число, повторите попытку'
value_set = 'Значение установлено.'
finished_choice_manager_creation = 'Задание параметров завершено, с этого момента возможен выбор тем, ' \
                                   'напишите в общем чате /start_choose'
choices_collection_stopped = 'Выбор тем завершен'
choices_collection_not_started = 'Выбор тем еще не был начат(контактируйте с админом, чтобы начать его)'
show_choices = 'Выбранные темы:\n{0}\n\nДоступные темы:\n{1}'
your_choice = 'Ваша тема - {0}'
choices_not_made = 'Еще не были выбраны'
not_available = 'Нет доступных'
get_choices_excel_file = 'Файл со всеми выбранными темами'
your_choice_deleted = 'Ваша запись удалена'
cannot_choose_any_subject = 'Все выбранные темы заняты'
set_new_choice_file = 'Установите новый файл для сохранения тем\n' \
                      '(в личном чате бота /admin_help)'
copy_queue = 'Чтобы скопировать очередь,\nвставьте текст предыдущего сообщения'
enter_queue_name = 'Введите имя для очереди.\n' \
                   'Имя не должно содержать пробелов (разрешается \'_\'),\n' \
                   'Должно быть в одной строке, длиной не больше 40 знаков'
name_incorrect = 'Имя в неверном формате.'
name_set = 'Имя установлено'
queue_set = 'Очередь установлена'
queue_set_format = 'Очередь \'{0}\' установлена'
queue_rename_send_new_name = 'Пришлите новое имя для очереди \"{0}\"'
queue_limit_reached = 'Больше очередей установить нельзя, удалите некоторые из них'
queue_removed = 'Очередь \'{0}\' удалена'
queue_not_found = 'Очередь не найдена'
title_select_queue = 'Выбор очереди'
select_student = 'Выберите студента'
select_students = 'Выберите студентов'
selected_object = 'Выбрано: {0}'
selected_position = 'Выбрана позиция: {0}'
selected_position_not_exists = 'Эта позиция уже не существует'
command_for_private_chat = 'Используйте команду в приватном чате'
student_moved_to_position = 'Студент {0} поставлен на позицию {1}'
queues_saved_to_cloud = 'Все очереди перемещены на GoogleDrive'