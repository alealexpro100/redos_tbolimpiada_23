window.addEventListener("load", (event) => {

  // ---- For draggable windows ----

  // https://www.w3schools.com/howto/howto_js_draggable.asp
  function dragElement(elmnt) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    if (elmnt.firstElementChild.firstElementChild && elmnt.firstElementChild.classList.contains('title-bar')) {
      /* if present, the header is where you move the DIV from:*/
      elmnt.firstElementChild.onmousedown = dragMouseDown;
    } else {
      /* otherwise, move the DIV from anywhere inside the DIV:*/
      elmnt.onmousedown = dragMouseDown;
    }

    function dragMouseDown(e) {
      e.preventDefault();
      // get the mouse cursor position at startup:
      pos3 = e.clientX;
      pos4 = e.clientY;
      document.onmouseup = closeDragElement;
      // call a function whenever the cursor moves:
      document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
      e = e || window.event;
      e.preventDefault();
      // calculate the new cursor position:
      pos1 = pos3 - e.clientX;
      pos2 = pos4 - e.clientY;
      pos3 = e.clientX;
      pos4 = e.clientY;
      // set the element's new position:
      elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
      elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
      /* stop moving when mouse button is released:*/
      document.onmouseup = null;
      document.onmousemove = null;
    }
  }

  const containers = document.querySelectorAll(".window");
  //console.log(containers);
  containers.forEach((container) => {
    dragElement(container);
  });

  // ---- For tabs ----

  // Tabs
  function tabHandler(e, tabButtons) {
    e.preventDefault();
    const tabContainer = e.target.parentElement.parentElement;
    const targetId = e.target.getAttribute("aria-controls");
    tabButtons.forEach((_tabButton) =>
      _tabButton.setAttribute("aria-selected", false)
    );
    e.target.setAttribute("aria-selected", true);
    e.target.focus();
    tabContainer
      .querySelectorAll("[role=tabpanel]")
      .forEach((tabPanel) => tabPanel.setAttribute("hidden", true));
    tabContainer
      .querySelector(`[role=tabpanel]#${targetId}`)
      .removeAttribute("hidden");
  }

  // Tabs > Sample Tabs
  const tabList_Flag = document.querySelector("[aria-label='Flag-check tasks']");
  const tabButtons_Flag = tabList_Flag.querySelectorAll("[role=tab]");
  tabButtons_Flag.forEach((tabButton) =>
    tabButton.addEventListener("mousedown", (evt) => {
      tabHandler(evt, tabButtons_Flag)
    }));
  tabButtons_Flag.forEach((tabButton) =>
    tabButton.addEventListener("focus", (evt) => {
      tabHandler(evt, tabButtons_Flag)
    }));

  // Tabs > Sample Tabs
  const tabList_AutoCheck = document.querySelector("[aria-label='Auto-check tasks']");
  const tabButtons_AutoCheck = tabList_AutoCheck.querySelectorAll("[role=tab]");
  tabButtons_AutoCheck.forEach((tabButton) =>
    tabButton.addEventListener("mousedown", (evt) => {
      tabHandler(evt, tabButtons_AutoCheck)
    }));
  tabButtons_AutoCheck.forEach((tabButton) =>
    tabButton.addEventListener("focus", (evt) => {
      tabHandler(evt, tabButtons_AutoCheck)
    }));

  // Copy code
  async function copyToClipboard(textToCopy) {
    // Navigator clipboard api needs a secure context (https)
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(textToCopy);
    } else {
      // Use the 'out of viewport hidden text area' trick
      const textArea = document.createElement("textarea");
      textArea.value = textToCopy;

      // Move textarea out of the viewport so it's not visible
      textArea.style.position = "absolute";
      textArea.style.left = "-999999px";

      document.body.prepend(textArea);
      textArea.select();

      try {
        document.execCommand('copy');
      } catch (error) {
        console.error(error);
      } finally {
        textArea.remove();
      }
    }
  }

  document.querySelectorAll(".copy").forEach((input_el) => {
    input_el.addEventListener("click", (e) => {
      const val = input_el.value;
      if (val != "" && val != "Скопировано") {
        copyToClipboard(input_el.value).then(() => {
          const prevtext = input_el.value;
          input_el.value = "Скопировано";
          setTimeout(() => (input_el.value = prevtext), 5000);
        });
      }
    });
  });

  // Actual work

  async function request_post(url, data) {
    var response;
    await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    }).then(response => response.json())
      .then(data => {
        response = data;
        console.log('Success:', data);
      })
      .catch((error) => {
        response = null;
        console.error('Error:', error);
      });
    return response;
  }

  async function request_get(url) {
    var response;
    await fetch(url, {
      method: 'GET',
    }).then(response => response.json())
      .then(data => {
        response = data;
        console.log('Success:', data);
      })
      .catch((error) => {
        response = null;
        console.error('Error:', error);
      });
    return response;
  }

  var task_changed = false;

  async function wait_until_ready(task_id) {
    var resp;
    const prog_bar = document.querySelector("#progress_" + task_id);
    document.querySelector("#log_" + task_id).textContent = "Идёт подготовка виртуальной машины..."
    while (task_changed) {
      await new Promise(r => setTimeout(r, 5000));
      resp = await request_get('/task_ready');
      console.log(resp);
      if (resp == null || resp.msg == true) {
        break
      }
    }
    if (resp == null) {
      prog_bar.style.width = '100%';
      prog_bar.parentElement.classList.remove('paused');
      prog_bar.parentElement.classList.add('error');
    } else {
      if (resp.msg == true) {
        prog_bar.parentElement.classList.remove('error');
        prog_bar.parentElement.classList.add('paused');
        prog_bar.style.width = '50%';
        document.querySelector("#check_" + task_id).disabled = false;
        document.querySelector("#log_" + task_id).textContent = "Виртуальная машина готова!"
      }
    }
  }

  document.querySelectorAll(".start_button").forEach((button_el) => {
    button_el.addEventListener("click", async (e) => {
      task_changed = true;
      var task_id = button_el.id.replace("start_", "");
      var prog_bar = document.querySelector("#progress_" + task_id);
      prog_bar.style.width = '10%';
      document.querySelector("#log_" + task_id).textContent = "Идёт получение данных для SSH подключения..."
      var is_flag = button_el.parentElement.parentElement.parentElement.querySelector('menu').attributes['aria-label'].value == 'Flag-check tasks';
      var data = {
        id: task_id,
        type: is_flag ? 'flag' : 'auto'
      }
      response = await request_post('/start_task', data);
      if (response != null) {
        document.querySelector("#ssh_cmd_" + task_id).value = response.ssh_command;
        document.querySelector("#ssh_pass_" + task_id).value = response.password;
        prog_bar.parentElement.classList.remove('error');
        prog_bar.parentElement.classList.add('paused');
        prog_bar.style.width = '30%';
        wait_until_ready(task_id);
      } else {
        prog_bar.style.width = '100%';
        document.querySelector("#log_" + task_id).textContent = "Ошибка соединения с сервером!"
      }
    });
  });

  document.querySelectorAll(".check_button").forEach((button_el) => {
    button_el.addEventListener("click", async (e) => {
      var task_id = button_el.id.replace("check_", "");
      var is_flag = button_el.parentElement.parentElement.parentElement.querySelector('menu').attributes['aria-label'].value == 'Flag-check tasks';
      var data = {
        id: task_id,
        type: 'auto'
      }
      if (is_flag) {
        data['type'] = 'flag';
        data['flag'] = document.querySelector("#flag_" + task_id).value;
      }
      response = await request_post('/check_task', data);
      console.log(response);
      prog_bar = document.querySelector("#progress_" + task_id);
      if (response != null) {
        if (response.status == 'correct') {
          prog_bar.style.width = '100%';
          prog_bar.parentElement.classList.remove('paused');
          prog_bar.parentElement.classList.remove('animate');
          document.querySelector("#start_" + task_id).disabled = true;
          document.querySelector("#ssh_cmd_" + task_id).disabled = true;
          document.querySelector("#ssh_pass_" + task_id).disabled = true;
          if (is_flag) {
            document.querySelector("#flag_" + task_id).disabled = true;
          }
          document.querySelector("#check_" + task_id).disabled = true;
          if (is_flag) {
            document.querySelector("#log_" + task_id).textContent = "Правильно!"
          } else {
            document.querySelector("#log_" + task_id).textContent = response.msg.join("");
          }
        } else if (response.status == 'incorrect') {
          if (is_flag) {
            document.querySelector("#log_" + task_id).textContent = "Не правильно."
          } else {
            document.querySelector("#log_" + task_id).textContent = response.msg.join("");
          }
        }
      } else {
        prog_bar.style.width = '100%';
        prog_bar.parentElement.classList.remove('paused');
        prog_bar.parentElement.classList.add('error');
        document.querySelector("#log_" + task_id).textContent = "Ошибка соединения с сервером!"
      }
    });
  });
});