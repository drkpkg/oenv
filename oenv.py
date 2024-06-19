import os, sys, argparse

"""
Oenv is a Odoo environment manager. It allows you to create, delete, list and switch between Odoo environments.

Usage:
    oenv create 10.0 -p /path/to/odoo/v10
    oenv delete 10.0
    oenv list
    oenv switch 10.0
    oenv current
"""

class Oenv:
    def __init__(self):
        self.odoo_envs = {}
        self.current_env = None

    def create(self, name, path, version='17.0'):
        self.odoo_envs[name] = path
        self.switch(name)
        self._setup_pyenv()
        self._setup_odoo(version, path)
        self._setup_odoo_requirements(path)
        self._setup_postgres_docker_compose()
        self._setup_odoo_config(path)

    def delete(self, name):
        if name in self.odoo_envs:
            del self.odoo_envs[name]
        if name == self.current_env:
            self.current_env = None

    def list(self):
        for name, path in self.odoo_envs.items():
            print(name, path)

    def switch(self, name):
        if name in self.odoo_envs:
            self.current_env = name
        else:
            print("Environment not found")

    def current(self):
        if self.current_env:
            print(self.current_env)
        else:
            print("No environment selected")

    def _setup_odoo(self, version, path):
        url = f"https://github.com/odoo/odoo/archive/refs/heads/{version}.zip"
        # every version is decompressed with the name odoo-{version}, normalizing it to odoo
        os.system(f"wget {url} -O /tmp/odoo.zip")
        os.system(f"unzip /tmp/odoo.zip -d {path}")
        os.system(f"mv {path}/odoo-{version} {path}/odoo")

    def _setup_postgres_docker_compose(self):
        with open("docker-compose.yml", "w") as f:
            f.write("""
                    services:
                        db:
                            image: postgres:lastest
                            environment:
                            POSTGRES_DB: odoo
                            POSTGRES_USER: odoo
                            POSTGRES_PASSWORD: odoo
                        """)
        os.system("docker-compose up -d")
    
    def _setup_odoo_requirements(self, path):
        os.system(f"pip install -r {path}/requirements.txt")
    
    def _setup_odoo_config(self, path):
        os.system(f"cp {path}/odoo.conf {path}/odoo.conf.example")
        os.system(f"cp {path}/odoo.conf {path}/odoo.conf")
        os.system(f"sed -i 's/db_user = .*/db_user = odoo/' {path}/odoo.conf")
        os.system(f"sed -i 's/db_password = .*/db_password = odoo/' {path}/odoo.conf")
        os.system(f"sed -i 's/admin_passwd = .*/admin_passwd = odoo/' {path}/odoo.conf")
        os.system(f"sed -i 's/; dbfilter = .*/dbfilter = odoo/' {path}/odoo.conf")
        os.system(f"sed -i 's/; db_host = .*/db_host = db/' {path}/odoo.conf")
        os.system(f"sed -i 's/; db_port = .*/db_port = 5432/' {path}/odoo.conf")
    
    def _setup_pyenv(self):
        if os.system("pyenv --version") != 0:
           os.system("echo 'Pyenv is not installed, please install it'")
        else: 
            os.system("curl https://pyenv.run | bash")
            os.system("echo 'export PATH=\"$HOME/.pyenv/bin:$PATH\"' >> ~/.bashrc")
            os.system("echo 'eval \"$(pyenv init -)\"' >> ~/.bashrc")
            os.system("echo 'eval \"$(pyenv virtualenv-init -)\"' >> ~/.bashrc")
            os.system("source ~/.bashrc")

def main():
    parser = argparse.ArgumentParser(description='Odoo environment manager')
    parser.add_argument('command', help='Command to execute')
    parser.add_argument('env', nargs='?', help='Environment name')
    parser.add_argument('-p', '--path', help='Path to Odoo installation')

    args = parser.parse_args()
    oenv = Oenv()

    if args.command == 'create':
        oenv.create(args.env, args.path)
    elif args.command == 'delete':
        oenv.delete(args.env)
    elif args.command == 'list':
        oenv.list()
    elif args.command == 'switch':
        oenv.switch(args.env)
    elif args.command == 'current':
        oenv.current()

if __name__ == '__main__':
    main()