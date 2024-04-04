# For port forward
```bash
chmod 755 port_forward.sh; chown root:root port_forward.sh
echo -e "%libvirt ALL = (root) NOPASSWD: /opt/project/port_forward.sh" > /etc/sudoers.d/project
```

# For python deps
```bash
sudo dnf install -y python3-paramiko python3-flask python3-gunicorn
```

# To run (alexey user):
```bash
gunicorn -w 1 'app:app'
```

# For firewall
```bash
firewall-cmd --add-port=8000/tcp
firewall-cmd --add-port=8000/tcp --permanent
```

# Systemd unit
```s
[Unit]
Description=RedOS testing
After=network.target

[Service]
Type=notify
User=alexey
WorkingDirectory=/opt/project
ExecStart=/usr/bin/gunicorn -w 1 -b 0.0.0.0:8000 app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```