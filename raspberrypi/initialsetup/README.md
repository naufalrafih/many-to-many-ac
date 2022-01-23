Software yang harus ada pada Raspberry Pi (Server Institusi & Cert Center):

| Komponen | Fungsi | Install status |
| -------- | ------ | ------ |
| Python 3.7 | Main programming language | By default |
| Pip3 | Python package installer | By default |
| Pipenv | Pip + virtual environment | Manual |
| Git | Version control | Manual |
| Zerotier | Virtual network | Manual |
| SSH Key | Untuk kredensial GitHub | Manual
| SQLite | Sebagai DB engine | Manual

NOTE:
* Library-library pada program/script Python diinstall melalui Pipenv.
* Public SSH key perlu ditambahkan manual ke GitHub repository.
* Cara initial setup adalah meng-copy script-script di folder ini secara manual dan me-run setup.sh.