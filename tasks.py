import base64

def file_to_base64(path: str):
    file_text = open(path, 'rb')
    file_read = file_text.read()
    return base64.b64encode(file_read).decode('ascii')

class task:
    def __init__(
        self,
        name: str = "Empty task",
        text: str = "May be HTML code",
        id: str = "empty_task",
        flag_code: str = "flag",
        is_auto=False,
        ci_add: str = "",
        check_cmd: str = "exit 0"
    ):
        self.name = name
        self.text = text
        self.id = id
        # Note: default flag looks like `RED_flag_OS`
        self.flag_code = f"RED_{flag_code}_OS".upper() if not is_auto else None
        self.is_auto = is_auto
        self.ci_add = ci_add
        self.check_cmd = check_cmd
    def check_flag(self, flag: str):
        if self.is_auto:
            raise ValueError("It is auto task. Flag check is not supported")
        return flag.upper() == self.flag_code

f0_ssh_ci="""write_files:
- content: |
    RED_portalgun_OS
  path: /home/{USERNAME}/flag.txt
"""

f1_ext4_ci=f"""write_files:
- encoding: b64
  content: {file_to_base64('files/f1_ext4.img')}
  path: /home/{{USERNAME}}/image.img
  permissions: '0777'
"""

f2_kmsg_ci=f"""bootcmd:
 - [ bash, -c, 'echo "Your flag is: RED_openrc_OS" > /dev/kmsg' ]
"""

f3_jpg_ci=f"""write_files:
- encoding: b64
  content: {file_to_base64('files/f3_img.jpg')}
  path: /home/{{USERNAME}}/flag.jpg
  permissions: '0777'
"""

f4_broken_img_ci=f"""write_files:
- encoding: b64
  content: {file_to_base64('files/f4_broken_image.img')}
  path: /home/{{USERNAME}}/image.img
  permissions: '0777'
"""

f5_nodejs_ci=f"""write_files:
- encoding: b64
  content: {file_to_base64('files/f5_code.js')}
  path: /home/{{USERNAME}}/code.js
  permissions: '0777'
"""

f6_find_ci=f"""write_files:
- content: |
    RED_hatsune_OS
  path: /var/lib/xfsdump/inventory/flag.txt
"""

f7_cross_arch_ci=f"""write_files:
- encoding: b64
  content: {file_to_base64('files/f7_binary.out')}
  path: /home/{{USERNAME}}/f7_binary.out
  permissions: '0777'
"""

f8_rpm_ci=f"""write_files:
- encoding: b64
  content: {file_to_base64('files/f8_pkg.rpm')}
  path: /home/{{USERNAME}}/empty-pkg-1-1.x86_64.rpm
  permissions: '0777'
"""

a3_tar_ci="""write_files:
- content: |
    https://www.youtube.com/watch?v=o-YBDTqX_ZU
  path: /mnt/files/cool_video.txt
- content: |
    XD
    https://support.microsoft.com/en-us/topic/how-to-remove-linux-and-install-windows-on-your-computer-f489c550-f8ec-b458-0a64-c3a8d60d3497
    https://www.geeksforgeeks.org/uninstall-linux-completely-from-a-pc-with-windows/
  path: /mnt/files/instructions.txt
"""

div_b_p="<div><b>{B_PART}</b>: <p>{P_PART}</p></div>"


tasks_list_flag = [
    task(
        name="SSH",
        text=div_b_p.format(B_PART='Описание', P_PART='SSH - своеобразный портал на удалённую машину. Почему-бы его не попробовать?')
            + div_b_p.format(B_PART='Задание', P_PART='Подключиться к SSH и просмотреть файл <i>flag.txt</i>.'),
        id="f0_ssh",
        flag_code="portalgun",
        is_auto=False,
        ci_add=f0_ssh_ci
    ),
    task(
        name="ext4",
        text=div_b_p.format(B_PART='Описание', P_PART='Ваш друг сделал бэкап раздела с флешки через dd. Внутри него есть файл <i>flag.txt</i> с флагом.')
            + div_b_p.format(B_PART='Задание', P_PART='Подключиться к SSH и получить флаг.'),
        id="f1_ext4",
        flag_code="sanabi",
        is_auto=False,
        ci_add=f1_ext4_ci
    ),
    task(
        name="kmsg",
        text=div_b_p.format(B_PART='Описание', P_PART='Логи всегда нужно уметь читать. Это касается и логов ядра.')
            + div_b_p.format(B_PART='Задание', P_PART='Подключиться к SSH и получить флаг из логов ядра.'),
        id="f2_kmsg",
        flag_code="openrc",
        is_auto=False,
        ci_add=f2_kmsg_ci
    ),
    task(
        name="JPG",
        text=div_b_p.format(B_PART='Описание', P_PART='По SSH можно получать файлы с сервера. Это не так быстро, но работает.')
            + div_b_p.format(B_PART='Задание', P_PART='Подключиться к SSH и получить любым удобным способом флаг из изображения <i>flag.jpg</i>.'),
        id="f3_jpg",
        flag_code="starcraft",
        is_auto=False,
        ci_add=f3_jpg_ci
    ),
    task(
        name="testdisk",
        text=div_b_p.format(B_PART='Описание', P_PART='Кто-то то ли созла, то ли случайно повредил MBR запись в образе диска. А там на разделе есть файл с флагом.')
            + div_b_p.format(B_PART='Задание', P_PART='Подключиться к SSH и получить любым удобным способом флаг из образа диска <i>image.img</i>.'),
        id="f4_broken_img",
        flag_code="rifle",
        is_auto=False,
        ci_add=f4_broken_img_ci
    ),
    task(
        name="nodejs",
        text=div_b_p.format(B_PART='Описание', P_PART='Вам дали загадочный (нет) JS-файл. Код прошёл обфускацию.')
            + div_b_p.format(B_PART='Задание', P_PART='Подключиться к SSH и получить флаг путём запуска JS-файла в виртуальной машине.'),
        id="f5_nodejs",
        flag_code="obfuscator",
        is_auto=False,
        ci_add=f5_nodejs_ci
    ),
    task(
        name="find",
        text=div_b_p.format(B_PART='Описание', P_PART='Использование <i>find</i> в Linux является классикой жанра.')
            + div_b_p.format(B_PART='Задание', P_PART='Подключиться к SSH и получить флаг путём поиска файла <i>flag.txt</i> в папке /var.'),
        id="f6_nodejs",
        flag_code="hatsune",
        is_auto=False,
        ci_add=f6_find_ci
    ),
    task(
        name="cross arch",
        text=div_b_p.format(B_PART='Описание', P_PART='Вам дали статический бинарник, который выводит флаг. В RedOS есть возможность запуска бинарных файлов с другой архитектуры.')
            + div_b_p.format(B_PART='Задание', P_PART='Подключиться к SSH и получить флаг путём запуска файла <i>f7_binary.out</i>.'),
        id="f7_cross_arch",
        flag_code="devops",
        is_auto=False,
        ci_add=f7_cross_arch_ci
    ),
    task(
        name="RPM",
        text=div_b_p.format(B_PART='Описание', P_PART='В RedOS используется пакетный менеджер RPM. В файлах его пакетов обычно есть описание.')
            + div_b_p.format(B_PART='Задание', P_PART='Подключиться к SSH и получить флаг из пакета <i>empty-pkg-1-1.x86_64.rpm</i>.'),
        id="f8_rpm",
        flag_code="singularity",
        is_auto=False,
        ci_add=f8_rpm_ci
    )
]

tasks_list_auto = [
    task(
        name="htop",
        text=div_b_p.format(B_PART='Описание', P_PART='В RedOS есть консольный диспетчер задач. Его стоит посмотреть!')
            + div_b_p.format(B_PART='Задание', P_PART='Поставить и запустить <i>htop</i>.'),
        id="a0_htop",
        is_auto=True,
        ci_add='',
        # To check use: dnf install -y htop; htop
        check_cmd='if [[ -n $(rpm -qa | grep htop) ]]; then echo "+ Пакет htop установлен"; else echo "- Пакет htop не установлен"; exit 1; fi;' +
            'if pgrep -f htop &>/dev/null; then echo "+ Процесс htop обнаружен"; else echo "- Процесс htop не обнаружен"; exit 1; fi;'
    ),
    task(
        name="NGINX",
        text=div_b_p.format(B_PART='Описание', P_PART='NGINX сейчас практически везде. А ещё его легко развернуть.')
            + div_b_p.format(B_PART='Задание', P_PART='Нужно установить и запустить nginx.'),
        id="a1_nginx",
        is_auto=True,
        ci_add='',
        # To check use: dnf install -y nginx; systemctl start nginx
        check_cmd='if [[ -n $(rpm -qa | grep nginx) ]]; then echo "+ Пакет nginx установлен"; else echo "- Пакет nginx не установлен"; exit 1; fi;' +
        'if systemctl is-active nginx &>/dev/null; then echo "+ Сервис nginx запущен"; else echo "- Сервис nginx не запущен"; exit 1; fi;'
    ),
    task(
        name="loop0",
        text=div_b_p.format(B_PART='Описание', P_PART='Виртуальные машины хранят данные в образах дисков. И совершенно не обязательно их виртуальный размер равен реальному.')
            + div_b_p.format(B_PART='Задание', P_PART='Нужно создать raw-диск размером 2G (но не занимать эти 2G) по пути <i>/mnt/image.img</i>, подключить его к системе, сделать разметку, и создать раздел с ext4.'),
        id="a2_loop0",
        is_auto=True,
        ci_add='',
        # To check use: truncate -s 2G; /mnt/image.img; losetup -Pf /mnt/image.img; echo -e "label: dos\n ,,L" | sfdisk /dev/loop0; mkfs.ext4 /dev/loop0p1;
        check_cmd='if [[ -f /mnt/image.img ]]; then echo "+ Файл диска есть"; else echo "- Нет файла диска"; exit 1; fi;' +
            'if [[ $(du /mnt/image.img | awk "{{print \$1;}}") -lt 100000 ]]; then echo "+ Диск создан корректно"; else echo "- Диск создан через dd"; exit 1; fi;' +
            'if [[ $(ls -l /mnt/image.img | awk "{{print \$5;}}") == 2147483648 ]]; then echo "+ Размер диска корректен"; else echo "- Размер диска некорректен"; exit 1; fi;' +
            'losetup -D; losetup -Pf /mnt/image.img;' +
            'if [[ -e /dev/loop0p1 ]]; then echo "+ Раздел существует"; else echo "- Раздел не существует"; exit 1; fi;' +
            'if [[ $(blkid -o value -s TYPE /dev/loop0p1) == "ext4" ]]; then echo "+ Файловая система обнаружена"; else echo "- Файловая система не обнаружена"; exit 1; fi;' +
            'losetup -D;'
    ),
    task(
        name="TAR",
        text=div_b_p.format(B_PART='Описание', P_PART='Самый популярный файл архива в linux - tar.gz. Его скорость работы и умеренная эффективность сделали его таким популярным.')
            + div_b_p.format(B_PART='Задание', P_PART='Нужно создать архив <i>/mnt/backup.tar.gz</i> с данными из папки <i>/mnt/files</i>. Обратите внимание, что вложенных папок в архиве быть не должно.'),
        id="a3_tar",
        is_auto=True,
        ci_add=a3_tar_ci,
        # To check use: (cd /mnt/files; tar czv -C /mnt/files -f /mnt/backup.tar.gz .)
        check_cmd='if [[ -f /mnt/backup.tar.gz ]]; then echo "+ Файл архива существует"; else echo "- Файл архива не существует"; exit 1; fi;' +
            'if tar -ztvf /mnt/backup.tar.gz &>/dev/null; then echo "+ Архив не повреждён"; else echo "- Архив повреждён"; exit 1; fi;' +
            'if [[ $(tar -ztvf /mnt/backup.tar.gz | awk "{{print \$6;}}" | sed "s|/\\$||") == $(cd /mnt/files; find .) ]]; then echo "+ Список файлов совпадает"; else echo "- Список файлов не совпадает"; exit 1; fi;'
    ),
    task(
        name="X SSH",
        text=div_b_p.format(B_PART='Описание', P_PART='Раннее (возможно и сейчас) был распространён сценарий использования сетевой прозрачности X11. В RedOS используется X.org, а не Wayland, в котором данной функции нет.')
            + div_b_p.format(B_PART='Задание', P_PART='Нужно установить и запустить firefox через подключение по SSH.'),
        id="a4_x_ssh",
        is_auto=True,
        ci_add='',
        # To check use: dnf install firefox; firefox # (use -Y when connecting SSH)
        check_cmd='if [[ -n $(rpm -qa | grep firefox) ]]; then echo "+ Пакет firefox установлен"; else echo "- Пакет firefox не установлен"; exit 1; fi;' +
            'if pgrep -f firefox &>/dev/null; then echo "+ Процесс firefox обнаружен"; else echo "- Процесс firefox не обнаружен"; exit 1; fi;' +
            'if ! systemctl is-active graphical.target &>/dev/null; then echo "+ Target графики выключен"; else echo "- Target графики включен"; exit 1; fi;'
    ),
    task(
        name="nologin",
        text=div_b_p.format(B_PART='Описание', P_PART='Для безопасности иногда создают пользователя без возможности использования SHELL-а. Это делается довольно просто.')
            + div_b_p.format(B_PART='Задание', P_PART='Нужно создать пользователя <i>tester</i>, у которого будет выключен логин.'),
        id="a5_nologin",
        is_auto=True,
        ci_add='',
        # To check use: useradd -s /sbin/nologin tester
        check_cmd='if id tester &>/dev/null; then echo "+ Пользователь tester существует"; else echo "- Пользователь tester не существует"; exit 1; fi;' +
            'if ! sudo bash -c "su -l tester -c echo"; then echo "+ Логин tester-а заблокирован"; else echo "- Логин tester-а разблокирован"; exit 1; fi;'
    ),
    task(
        name="SUID",
        text=div_b_p.format(B_PART='Описание', P_PART='В случаях, когда нужно запускать файл от имени другого пользователя используют SUID. Хорошо про это написано <a href="https://www.redhat.com/sysadmin/suid-sgid-sticky-bit">здесь</a>.')
            + div_b_p.format(B_PART='Задание', P_PART='Нужно создать файл <i>/mnt/test</i> и установить ему права доступа <i>-rwSrw-rw-</i>.'),
        id="a6_suid",
        is_auto=True,
        ci_add='',
        # To check use: touch /mnt/test; chmod 4666 /mnt/test
        check_cmd='if [[ -f /mnt/test ]]; then echo "+ Файл существует"; else echo "- Файл не существует"; exit 1; fi;' +
            'if [[ $(ls -l /mnt/test | awk "{{print \$1;}}") == "-rwSrw-rw-." ]]; then echo "+ Права корректные"; else echo "- Права некорректные"; exit 1; fi;'
    ),
    task(
        name="cmdline",
        text=div_b_p.format(B_PART='Описание', P_PART='Иногда бывают ситуации, когда нужно загрузить ОС без настройки экрана. Так, например, на китайских платах X99 без параметра <i>nomodeset</i> ядро не загрузится, а зависнет.')
            + div_b_p.format(B_PART='Задание', P_PART='Нужно добавить параметр загрузки ядра <i>nomodeset</i> и перезагрузить ВМ с добавленным параметром.'),
        id="a7_cmdline",
        is_auto=True,
        ci_add='',
        # To check use: touch /mnt/test; chmod 4666 /mnt/test
        check_cmd='if [[ -n $(cat /proc/cmdline | grep nomodeset) ]]; then echo "+ Параметр в cmdline обнаружен"; else echo "- Параметр в cmdline не обнаружен"; exit 1; fi;'
    ),
    task(
        name="DNS",
        text=div_b_p.format(B_PART='Описание', P_PART='Есть достаточно интересный вид DNS под названием <a href="https://www.opennic.org/">opennic</a>. Он не так популярен, но тем не менее, его можно счатать "слоем" интернета.')
            + div_b_p.format(B_PART='Задание', P_PART='Установить DNS от opennic в ВМ так, чтобы работал доступ к его сайтам.'),
        id="a8_dns",
        is_auto=True,
        ci_add='',
        # To check use: touch /mnt/test; chmod 4666 /mnt/test
        check_cmd='if curl --head --fail "http://www.opennic.chan/" &>/dev/null; then echo "+ Сайты opennic доступны"; else echo "- Сайты opennic недоступны"; exit 1; fi;'
    ),
]
