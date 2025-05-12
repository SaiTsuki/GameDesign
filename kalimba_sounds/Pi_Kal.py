import pygame
import time
import decimal
import os
import random

# --- ОБЩИЕ МУЗЫКАЛЬНЫЕ НАСТРОЙКИ (как в предыдущем скрипте) ---
KALIMBA_NOTES_COUNT = 17
SOUND_FILES_DIR = "kalimba_sounds"
AUDIO_FILE_EXTENSION = ".ogg" # или .wav

USE_OCTAVE_PREFERENCE = True
OCTAVE_RANGES_DEF = {
    '1st': (0, 6), '2nd': (7, 13), '3rd': (14, 16)
}
OCTAVE_PROBABILITIES_DEF = {
    '1st': 3, '2nd': 6, '3rd': 1
}
OCTAVE_CHOICE_REST_TRIGGER_DIGIT = '9' # Цифра Пи для выбора октавы, которая вызовет паузу

USE_MUSICAL_DURATIONS = True
BASE_NOTE_DURATION = 0.30
MUSICAL_DURATION_MULTIPLIERS = [0.5, 0.5, 0.75, 1.0, 1.0, 1.0, 1.5, 2.0, 0.25, 1.0]

USE_DOUBLE_DIGITS_FOR_NOTE_RAW = False # True: 00-99 для "сырого" значения ноты, False: 0-9
LEGACY_REST_TRIGGER_FIRST_DIGIT = '0' # Для паузы, если USE_OCTAVE_PREFERENCE = False

# --- НАСТРОЙКИ ЭВОЛЮЦИОННОГО АЛГОРИТМА ---
POPULATION_SIZE = 6       # Сколько последовательностей в одном поколении (не делайте слишком большим!)
SEQUENCE_LENGTH = 16       # Длина каждой музыкальной последовательности (n нот/пауз)
NUM_GENERATIONS = 10      # Сколько поколений будем "эволюционировать"
MUTATION_RATE_EVENT = 0.15 # Вероятность мутации для каждого события в последовательности
MUTATION_RATE_PARAM = 0.5 # Если событие мутирует, вероятность изменения каждого его параметра
CROSSOVER_RATE = 0.7      # Вероятность скрещивания двух родителей

# --- Глобальные переменные для управления числом Пи ---
PI_DIGITS_GLOBAL = ""
PI_IDX_GLOBAL = 0
INITIAL_PI_BUFFER = 5000 # Начальное количество знаков Пи для загрузки

# --- Вспомогательные структуры и функции ---
octave_preference_data_g = None # Глобальные данные по октавам для генерации

def get_pi_digits_string(num_digits):
    """Возвращает строку цифр Пи. Для ЭА нужна возможность получать много цифр."""
    global PI_DIGITS_GLOBAL, PI_IDX_GLOBAL
    
    # Эта реализация использует заранее заданную строку.
    # Для длительной работы ЭА может потребоваться более продвинутый источник Пи.
    predefined_pi = "141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844609550582231725359408128481117450284102701938521105559644622948954930381964428810975665933446128475648233786783165271201909145648566923460348610454326648213393607260249141273724587006606315588174881520920962829254091715364367892590360011330530548820466521384146951941511609433057270365759591953092186117381932611793105118548074462379962749567351885752724891227938183011949129833673362440656643086021394946395224737190702179860943702770539217176293176752384674818467669405132000568127145263560827785771342757789609173637178721468440901224953430146549585371050792279689258923542019956112129021960864034418159813629774771309960518707211349999998372978049951059731732816096318595024459455346908302642522308253344685035261931188171010003137838752886587533208381420617177669147303598253490428755468731159562863882353787593751957781857780532171226806613001927876611195909216420198938095257201065485863278865936153381827968230301952035301852968995773622599413891249721775283479131515574857242454150695950829533116861727855889075098381754637464939319255060400927701671139009848824012858361603563707660104710181942955596198946767837449448255379774726847104047534646208046684259069491293313677028989152104752162056966024058038150193511253382430035587640247496473263914199272604269922796782354781636009341721641219924586315030286182974555706749838505494588586926995690927210797509302955321165344987202755960236480665499119881834797753566369807426542527862551818417574672890977772793800081647060016145249192173217214772350141441973568548161361157352552133475741849468438523323907394143334547762416862518983569485562099219222184272550254256887671790494601653466804988627232791786085784383827967976681454100953883786360950680064225125205117392984896084128488626945604241965285022210661186306744278622039194945047123713786960956364371917287467764657573962413890865832645995813390478027590099465764078951269468398352595709825822620522489407726719478268482601476990902640136394437455305068203496252451749399651431429809190659250937221696461515709858387410597885959772975498930161753928468138268683868942774155991855925245953959431049972524680845987273644695848653836736222626099124608051243884390451244136549762780797715691435997700129616089441694868555848406353422072225828488648158456028506016842739452267467678895252138522549954666727823986456596116354886230577456498035593634568174324112515076069479451096596094025228879710893145669136867228748940560101503308617928680920874760917824938589009714909675985261365549781893129784821682998948722658804857564014270477555132379641451523746234364542858444795265867821051141354735739523113427166102135969536231442952484937187110145765403590279934403742007310578539062198387447808478489683321445713868751943506430218453191048481005370614680674919278191197939952061419663428754440643745123718192179998391015919561814675142691239748940907186494231961567945208095146550225231603881930142093762137855956638937787083039069792077346722182562599661501421503068038447734549202605414665925201497442850732518666002132434088190710486331734649651453905796268561005508106658796998163574736384052571459102897064140110971206280439039759515677157700420337869936007230558763176359421873125147120532928191826186125867321579198414848829164470609575270695722091756711672291098169091528017350671274858322287183520935396572512108357915136988209144421006751033467110314126711136990865851639831501970165151168517143765761835155650884909989859982387345528331635507647918535893226185489632132933089857064204675259070915481416549859461637180270981994309924488957571282890592323326097299712084433573265489382391193259746366730583604142813883032038249037589852437441702913276561809377344403070746921120191302033038019762110110044929321516084244485963766983895228684783123552658213144957685726243344189303968642624341077322697802807318915441101044682325271620105265227211166039666557309254711055785376346682065310989652691862056476931257058635662018558100729360659876486117910453348850346113657686753249441668039626579787718556084552965412665408530614344431858676975145661406800700237877659134401712749470420562230538994561314071127000407854733269939081454664645880797270826683063432858785698305235808933065757406795457163775254202114955761581400250126228594130216471550979259230990796547376125517656751357517829666454779174501129961489030463994713296210734043751895735961458901938971311179042978285647503203198691514028708085990480109412147221317947647772622414254854540332157185306142288137585043063321751829798662237172159160771669254748738986654949450114654062843366393790039769265672146385306736096571209180763832716641627488880078692560290228472104031721186082041900042296617119637792133757511495950156604963186294726547364252308177036751590673502350728354056704038674351362222477158915049530984448933309634087807693259939780541934144737744184263129860809988868741326047291" # Добавьте больше цифр при необходимости
    
    if not PI_DIGITS_GLOBAL or len(PI_DIGITS_GLOBAL) < num_digits:
        print(f"INFO: Загружаем {max(num_digits, INITIAL_PI_BUFFER)} знаков Пи.")
        decimal.getcontext().prec = max(num_digits, INITIAL_PI_BUFFER) + 5
        # В Python decimal нет встроенной Pi, используем предзаданную
        PI_DIGITS_GLOBAL = predefined_pi 
        PI_IDX_GLOBAL = 0 # Сбрасываем индекс при новой загрузке
        if len(PI_DIGITS_GLOBAL) < num_digits:
            print(f"ВНИМАНИЕ: Доступно только {len(PI_DIGITS_GLOBAL)} знаков Пи, запрошено {num_digits}.")
            return PI_DIGITS_GLOBAL

    # Эта функция теперь больше для инициализации глобальной переменной
    # и возврата начального среза, если нужно
    return PI_DIGITS_GLOBAL[:num_digits]


def ensure_pi_digits(needed_count=10):
    """Убеждается, что есть достаточно цифр Пи, при необходимости "догружает"."""
    global PI_DIGITS_GLOBAL, PI_IDX_GLOBAL
    if PI_IDX_GLOBAL + needed_count >= len(PI_DIGITS_GLOBAL):
        print("INFO: Закончились цифры Пи, пытаемся 'догрузить' (в данной реализации это перезапуск).")
        # В этой простой реализации мы просто "перезапускаем" указатель на начало строки Пи.
        # Для реального бесконечного потока нужен другой механизм.
        PI_IDX_GLOBAL = 0
        if PI_IDX_GLOBAL + needed_count >= len(PI_DIGITS_GLOBAL):
            print("КРИТИЧЕСКАЯ ОШИБКА: Недостаточно знаков Пи даже после сброса. Увеличьте строку predefined_pi.")
            # Можно выбросить исключение или вернуть флаг ошибки
            return False 
    return True

def consume_pi_digits(count):
    """Безопасно извлекает 'count' цифр Пи и сдвигает глобальный индекс."""
    global PI_DIGITS_GLOBAL, PI_IDX_GLOBAL
    if not ensure_pi_digits(count):
        # Если не удалось обеспечить достаточно цифр, возвращаем строку из '0'
        # Это предотвратит падение, но может повлиять на генерацию.
        print(f"ПРЕДУПРЕЖДЕНИЕ: Не удалось получить {count} цифр Пи, используем нули.")
        return "0" * count 
    
    digits = PI_DIGITS_GLOBAL[PI_IDX_GLOBAL : PI_IDX_GLOBAL + count]
    PI_IDX_GLOBAL += count
    return digits

def prepare_octave_data_ea(ranges_def, probs_def, total_notes):
    # Аналогично prepare_octave_data из предыдущего скрипта
    octaves = []
    valid_octave_names = [
        name for name, (start, end) in ranges_def.items()
        if 0 <= start <= end < total_notes and probs_def.get(name, 0) > 0
    ]
    if not valid_octave_names: return None
    current_total_prob_units = sum(probs_def[name] for name in valid_octave_names)
    if current_total_prob_units == 0: return None
    
    cumulative_prob = 0
    for name in valid_octave_names:
        start, end = ranges_def[name]
        prob = probs_def[name]
        cumulative_prob += prob
        octaves.append({
            'name': name, 'range': (start, end), 'num_notes': end - start + 1,
            'cumulative_threshold': (cumulative_prob / current_total_prob_units)
        })
    octaves.sort(key=lambda x: x['cumulative_threshold'])
    return octaves

def load_kalimba_sounds_ea(sound_dir, num_notes, file_extension):
    # Аналогично load_kalimba_sounds
    sounds = []
    if not os.path.isdir(sound_dir):
        print(f"ОШИБКА: Папка со звуками '{sound_dir}' не найдена.")
        return None
    for i in range(num_notes):
        file_path = os.path.join(sound_dir, f"{i}{file_extension}")
        if os.path.exists(file_path):
            try: sounds.append(pygame.mixer.Sound(file_path))
            except pygame.error as e:
                print(f"Ошибка загрузки файла {file_path}: {e}"); sounds.append(None)
        else: sounds.append(None) # Меньше логов при инициализации
    if not any(sounds): print("ОШИБКА: Ни один звуковой файл не был успешно загружен."); return None
    return sounds

# --- Генерация одного музыкального события (нота/пауза) на основе Пи ---
def generate_pi_event():
    """Генерирует одно событие (ноту или паузу) используя глобальные настройки и Пи."""
    global octave_preference_data_g # Используем глобально инициализированные данные

    is_rest = False
    note_index = -1
    # Длительность по умолчанию (если что-то пойдет не так с Пи)
    current_duration = BASE_NOTE_DURATION * random.choice(MUSICAL_DURATION_MULTIPLIERS) \
                       if USE_MUSICAL_DURATIONS else BASE_NOTE_DURATION

    try:
        # 1. ОПРЕДЕЛЕНИЕ НОТЫ (или паузы)
        if USE_OCTAVE_PREFERENCE and octave_preference_data_g:
            octave_choice_digit_str = consume_pi_digits(1)
            if OCTAVE_CHOICE_REST_TRIGGER_DIGIT and octave_choice_digit_str == OCTAVE_CHOICE_REST_TRIGGER_DIGIT:
                is_rest = True
            else:
                octave_choice_val = int(octave_choice_digit_str) / 10.0
                chosen_octave = next((od for od in octave_preference_data_g if octave_choice_val < od['cumulative_threshold']), octave_preference_data_g[-1])
                
                note_digits_count = 2 if USE_DOUBLE_DIGITS_FOR_NOTE_RAW else 1
                note_val_pi_str = consume_pi_digits(note_digits_count)
                raw_note_val = int(note_val_pi_str)
                
                note_index_in_octave = raw_note_val % chosen_octave['num_notes']
                note_index = chosen_octave['range'][0] + note_index_in_octave
        else: # Стандартный выбор ноты
            first_digit_for_note_str = consume_pi_digits(1)
            if first_digit_for_note_str == LEGACY_REST_TRIGGER_FIRST_DIGIT:
                is_rest = True
            else:
                # Если не пауза по первой цифре, то эта цифра (или следующая пара) определяет ноту
                if USE_DOUBLE_DIGITS_FOR_NOTE_RAW:
                    # Если первая цифра была не для паузы, а для ноты, и нужны две, берем еще одну
                    note_val_pi_str = first_digit_for_note_str + consume_pi_digits(1)
                else:
                    note_val_pi_str = first_digit_for_note_str
                
                raw_note_val = int(note_val_pi_str)
                note_index = raw_note_val % KALIMBA_NOTES_COUNT

        # 2. ОПРЕДЕЛЕНИЕ ДЛИТЕЛЬНОСТИ
        duration_digit_str = consume_pi_digits(1)
        duration_choice_digit = int(duration_digit_str)
        if USE_MUSICAL_DURATIONS:
            duration_multiplier = MUSICAL_DURATION_MULTIPLIERS[duration_choice_digit % len(MUSICAL_DURATION_MULTIPLIERS)]
            current_duration = BASE_NOTE_DURATION * duration_multiplier
        else: # Старый способ (можно удалить, если не нужен)
            duration_multiplier = 0.5 + (duration_choice_digit / 9.0)
            current_duration = BASE_NOTE_DURATION * duration_multiplier

    except (ValueError, IndexError) as e:
        # Ошибка при парсинге Пи или доступе к данным - делаем паузу
        print(f"Предупреждение: Ошибка при генерации события из Пи ({e}), создана пауза.")
        is_rest = True
        current_duration = BASE_NOTE_DURATION # Безопасная длительность для паузы

    if is_rest:
        return {'type': 'rest', 'duration': current_duration}
    elif note_index != -1:
        return {'type': 'note', 'pitch': note_index, 'duration': current_duration}
    else: # Если что-то совсем пошло не так
        return {'type': 'rest', 'duration': BASE_NOTE_DURATION}


# --- Функции Эволюционного Алгоритма ---
def create_individual():
    """Создает одну музыкальную последовательность (индивида)."""
    return [generate_pi_event() for _ in range(SEQUENCE_LENGTH)]

def create_initial_population():
    """Создает начальную популяцию индивидов."""
    get_pi_digits_string(INITIAL_PI_BUFFER) # Инициализация/проверка глобального буфера Пи
    return [create_individual() for _ in range(POPULATION_SIZE)]

def play_sequence_ea(sequence, kalimba_sounds, seq_id):
    """Воспроизводит последовательность и выводит информацию."""
    print(f"\n--- Прослушивание последовательности #{seq_id + 1} ---")
    for i, event in enumerate(sequence):
        print(f"  Событие {i+1}: ", end="")
        if event['type'] == 'note':
            print(f"Нота {event['pitch']}, Длит: {event['duration']:.2f}с")
            if 0 <= event['pitch'] < len(kalimba_sounds) and kalimba_sounds[event['pitch']]:
                kalimba_sounds[event['pitch']].play()
                time.sleep(event['duration'])
            else: # Если звук для ноты не найден
                time.sleep(event['duration']) # Пауза вместо отсутствующей ноты
        elif event['type'] == 'rest':
            print(f"Пауза, Длит: {event['duration']:.2f}с")
            time.sleep(event['duration'])
    pygame.mixer.stop() # Остановить все звуки перед следующей оценкой

def get_fitness_from_user(seq_id):
    """Получает оценку от пользователя."""
    while True:
        try:
            rating = input(f"Оцените последовательность #{seq_id + 1} (1-плохо, 5-отлично, 0-пропустить): ")
            rating = int(rating)
            if 0 <= rating <= 5:
                return rating
            print("Неверная оценка. Введите число от 0 до 5.")
        except ValueError:
            print("Неверный ввод. Введите число.")

def selection(population, fitness_scores):
    """Турнирный отбор двух родителей."""
    parents = []
    for _ in range(2): # Выбираем двух родителей
        tournament_size = min(3, len(population)) # Размер турнира
        if tournament_size == 0: # Если популяция пуста (не должно быть)
            return random.choice(population) if population else None, random.choice(population) if population else None
        
        contender_indices = random.sample(range(len(population)), tournament_size)
        winner_idx = max(contender_indices, key=lambda idx: fitness_scores[idx])
        parents.append(population[winner_idx])
    return parents[0], parents[1]

def crossover(parent1, parent2):
    """Одноточечное скрещивание."""
    if random.random() > CROSSOVER_RATE or len(parent1) <= 1:
        return parent1[:], parent2[:] # Возвращаем копии родителей
    
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate_event(event):
    """Мутация одного события."""
    mutated_event = event.copy()
    
    # Шанс изменить тип события (нота <-> пауза)
    if random.random() < MUTATION_RATE_PARAM / 2: # Делим вероятность, т.к. несколько типов мутаций
        if mutated_event['type'] == 'note':
            mutated_event['type'] = 'rest'
            if 'pitch' in mutated_event: del mutated_event['pitch']
        else:
            mutated_event['type'] = 'note'
            mutated_event['pitch'] = random.randint(0, KALIMBA_NOTES_COUNT - 1) # Случайная нота
    
    # Шанс изменить высоту ноты (если это нота)
    if mutated_event['type'] == 'note' and random.random() < MUTATION_RATE_PARAM:
        mutated_event['pitch'] = random.randint(0, KALIMBA_NOTES_COUNT - 1) # Новая случайная нота

    # Шанс изменить длительность
    if random.random() < MUTATION_RATE_PARAM:
        if USE_MUSICAL_DURATIONS:
            new_multiplier = random.choice(MUSICAL_DURATION_MULTIPLIERS)
            mutated_event['duration'] = BASE_NOTE_DURATION * new_multiplier
        else:
            mutated_event['duration'] = max(0.1, mutated_event['duration'] * random.uniform(0.7, 1.3))
            
    return mutated_event

def mutate(individual):
    """Мутация индивида (последовательности)."""
    mutated_individual = []
    for event in individual:
        if random.random() < MUTATION_RATE_EVENT:
            mutated_individual.append(mutate_event(event))
        else:
            mutated_individual.append(event.copy()) # Важно копировать, чтобы не менять оригинал
    return mutated_individual

# --- Основной цикл Эволюционного Алгоритма ---
def run_evolution():
    global octave_preference_data_g

    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()

    kalimba_sounds = load_kalimba_sounds_ea(SOUND_FILES_DIR, KALIMBA_NOTES_COUNT, AUDIO_FILE_EXTENSION)
    if not kalimba_sounds:
        print("Не удалось загрузить звуки. Выход.")
        pygame.quit()
        return

    # Инициализация данных для генерации на основе Пи
    if USE_OCTAVE_PREFERENCE:
        octave_preference_data_g = prepare_octave_data_ea(OCTAVE_RANGES_DEF, OCTAVE_PROBABILITIES_DEF, KALIMBA_NOTES_COUNT)
        if not octave_preference_data_g:
            print("Предупреждение: Не удалось подготовить данные по октавам. Предпочтения октав не будут использованы.")
            # Можно установить USE_OCTAVE_PREFERENCE в False или обработать иначе

    population = create_initial_population()
    best_overall_individual = None
    best_overall_fitness = -1

    print("\n--- Начало Эволюции Музыки из Числа Пи ---")
    print(f"Параметры: Популяция={POPULATION_SIZE}, Длина={SEQUENCE_LENGTH}, Поколений={NUM_GENERATIONS}")

    for gen in range(NUM_GENERATIONS):
        print(f"\n===== Поколение {gen + 1}/{NUM_GENERATIONS} =====")
        
        fitness_scores = []
        current_gen_best_fitness = -1
        current_gen_best_individual = None

        for i, individual in enumerate(population):
            play_sequence_ea(individual, kalimba_sounds, i)
            fitness = get_fitness_from_user(i)
            fitness_scores.append(fitness)

            if fitness > current_gen_best_fitness:
                current_gen_best_fitness = fitness
                current_gen_best_individual = individual[:]
            
            if fitness > best_overall_fitness:
                best_overall_fitness = fitness
                best_overall_individual = individual[:]
                print(f"*** Найдена новая лучшая последовательность (Поколение {gen+1}, Оценка: {fitness})! ***")

        if not any(s > 0 for s in fitness_scores): # Если все оценки 0 (пропуск)
            print("Все последовательности в этом поколении были пропущены. Генерация новой случайной популяции.")
            population = create_initial_population()
            continue


        print(f"\nЛучшая оценка в поколении {gen + 1}: {current_gen_best_fitness}")
        if best_overall_individual:
             print(f"Лучшая оценка за все время: {best_overall_fitness}")


        new_population = []
        # Элитизм: сохраняем лучшего из текущего поколения, если он есть и оценен
        if current_gen_best_individual and current_gen_best_fitness > 0:
            new_population.append(current_gen_best_individual)
        
        # Заполняем остальную часть новой популяции
        while len(new_population) < POPULATION_SIZE:
            if not population or not any(s > 0 for s in fitness_scores): # Если отбирать не из кого
                print("Нет кандидатов для отбора, добавляем случайного индивида.")
                new_population.append(create_individual())
                if len(new_population) >= POPULATION_SIZE: break
                new_population.append(create_individual()) # Добавляем парами, если нужно
                continue

            parent1, parent2 = selection(population, fitness_scores)
            
            # Проверка, что родители были выбраны
            if parent1 is None or parent2 is None:
                print("Не удалось выбрать родителей, добавляем случайных индивидов.")
                new_population.append(create_individual())
                if len(new_population) < POPULATION_SIZE:
                    new_population.append(create_individual())
                continue


            child1, child2 = crossover(parent1, parent2)
            
            new_population.append(mutate(child1))
            if len(new_population) < POPULATION_SIZE:
                new_population.append(mutate(child2))
        
        population = new_population[:POPULATION_SIZE] # Убедимся, что размер популяции не превышен

        if gen < NUM_GENERATIONS -1:
            cont = input("Нажмите Enter для следующего поколения, 's' чтобы остановить и сохранить лучшую: ")
            if cont.lower() == 's':
                break
    
    print("\n--- Эволюция Завершена ---")
    if best_overall_individual:
        print(f"Финальная лучшая последовательность (Оценка: {best_overall_fitness}):")
        play_sequence_ea(best_overall_individual, kalimba_sounds, -1) # -1 как флаг финального прослушивания
        # Здесь можно добавить сохранение `best_overall_individual` в файл
    else:
        print("Не было найдено 'лучшей' последовательности.")

    pygame.mixer.quit()
    pygame.quit()


if __name__ == "__main__":
    # Проверка наличия папки и файлов
    if not os.path.exists(SOUND_FILES_DIR):
        os.makedirs(SOUND_FILES_DIR)
        print(f"Создана папка '{SOUND_FILES_DIR}'. Поместите туда звуки калимбы (0{AUDIO_FILE_EXTENSION} ...).")
    
    run_evolution()