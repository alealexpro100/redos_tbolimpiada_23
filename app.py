import os
import random
import socket
from threading import Thread
from flask import Flask, abort, render_template, send_file, request, g, send_from_directory
from flask import request
from tasks import task, tasks_list_flag, tasks_list_auto
from vm_work import (
    CHECKER_NAME,
    CHECKER_PASSWORD,
    DEFAULT_USER_DATA,
    USERS_USER,
    qemu_vm,
)

import secrets
import string
import paramiko

# Global object with task data
task_on = {"task": None, "task_type": None}


class TaskVM:
    def __init__(self, task_obj: task):
        self.vm_obj = qemu_vm()
        self.task_obj = task_obj
        self.username = None
        self.password = None
        self.port = None
        self.start()

    def start(self):
        alphabet = string.ascii_letters + string.digits
        self.username = ("".join(secrets.choice(alphabet) for _ in range(4))).lower()
        self.password = "".join(secrets.choice(alphabet) for _ in range(8))
        ci_user_data = (
            DEFAULT_USER_DATA
            + USERS_USER.format(USERNAME=self.username, PASSWORD=self.password)
            + self.task_obj.ci_add.format(
                USERNAME=self.username, PASSWORD=self.password
            )
        )
        print(ci_user_data)
        self.vm_obj.gen_ci(user_data=ci_user_data)
        self.vm_obj.snapshot_restore()
        self.vm_obj.power_on()
        self.port = random.randint(128, 512)
        self.port_forward_task = Thread(
            target=self.vm_obj.port_forward, daemon=True, kwargs={"port_ext": self.port}
        )
        self.port_forward_task.start()

    def is_ready(self):
        # TODO: check also by trying to connect using ssh
        return not self.port_forward_task.is_alive()

    def auto_check(self) -> str:
        username = CHECKER_NAME
        password = CHECKER_PASSWORD
        self.vm_obj.do_paramiko_ssh(username=username, password=password, cmd=f"echo 'set -e; {self.task_obj.check_cmd.format(USERNAME=self.username, PASSWORD=self.password)}' > /tmp/for_check.sh;")
        ssh_stdin, ssh_stdout, ssh_stderr = self.vm_obj.do_paramiko_ssh(
            username=username, password=password,
            cmd=f"sudo bash /tmp/for_check.sh; exit_code=$?; sudo rm -rf /tmp/for_check.sh; exit $exit_code"
        )
        ssh_stdout.channel.set_combine_stderr(True)
        msg = ssh_stdout.readlines()
        exit_code = ssh_stdout.channel.recv_exit_status()
        return [(exit_code == 0), msg]

    def __del__(self):
        self.vm_obj.port_forward(port_ext=self.port, remove=True)
        self.vm_obj.power_off()


app = Flask(__name__)


@app.route("/")
def index_page():
    return render_template(
        "index.html", tasks_list_flag=tasks_list_flag, tasks_list_auto=tasks_list_auto
    )

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/start_task", methods=["POST"])
def task_start():
    try:
        task_id = request.json["id"]
        task_type = request.json["type"]
    except Exception as e:
        abort(500)
    if task_type == "flag":
        task = next((x for x in tasks_list_flag if x.id == task_id), None)
    elif task_type == "auto":
        task = next((x for x in tasks_list_auto if x.id == task_id), None)
    else:
        abort(500)
    task_on["task_type"] = task_type
    task_on["task"] = TaskVM(task)
    # https://stackoverflow.com/a/1267524
    # Bacause of lo!
    hostname = (
        (
            [
                ip
                for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                if not ip.startswith("127.")
            ]
            or [
                [
                    (s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close())
                    for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
                ][0][1]
            ]
        )
        + ["no IP found"]
    )[0]
    return {
        "ssh_command": f"ssh -o \"UserKnownHostsFile /dev/null\" -p {task_on['task'].port} {task_on['task'].username}@{hostname}",
        "password": task_on["task"].password,
    }


@app.route("/task_ready", methods=["GET"])
def task_ready():
    if task_on["task"] is None:
        return {"msg": "No running task."}
    return {"msg": task_on["task"].is_ready()}


@app.route("/check_task", methods=["POST"])
def task_check():
    if task_on["task"] is None:
        return {"msg": "No running task."}
    if task_on["task_type"] == "flag":
        try:
            flag = request.json["flag"]
        except Exception as e:
            abort(500)
        if task_on["task"].task_obj.check_flag(flag):
            task_on["task"] = None
            return {"status": "correct"}
        else:
            return {"status": "incorrect"}
    elif task_on["task_type"] == "auto":
        res = task_on["task"].auto_check()
        if res[0]:
            task_on["task"] = None
            return {"status": "correct", "msg": res[1]}
        else:
            return {"status": "incorrect", "msg": res[1]}
    else:
        abort(500)


if __name__ == "__main__":
    app.run(debug=True)
