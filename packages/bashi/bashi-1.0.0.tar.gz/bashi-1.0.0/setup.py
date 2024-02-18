from setuptools import setup, find_packages
import os , requests 
import subprocess



class PypiPublisher : 
    def __init__(self, start_version = "1.0.0") : 
        self.start_version = start_version
        self.name = os.path.basename(os.getcwd())
        print(f"Project name : {self.name}")
        self.version , self.new_version = self.get_versions()
        print(f"Project version : {self.version} -> {self.new_version }")
        #######
        author= subprocess.check_output(['git', 'config', 'user.name']).decode().strip()  if not os.environ.get("GITLAB_USER_NAME",None ) else os.environ.get("GITLAB_USER_NAME",None )  
        #######
        author_email= subprocess.check_output(['git', 'config', 'user.email']).decode().strip() if not  os.environ.get("GITLAB_USER_EMAIL", None ) else os.environ.get("GITLAB_USER_EMAIL", None ) 
        ######
        url  = subprocess.check_output(['git', 'remote', 'get-url', 'origin']).decode().strip() if not os.environ.get("CI_PROJECT_URL",None ) else os.environ.get("CI_PROJECT_URL",None )
        setup(
            name= os.path.basename(os.getcwd()),
            version=self.version,
            packages=find_packages(),
            author= author  ,
            author_email=author_email   ,
            description=f'Python Package made by Mhadhbi Issam . ',
            long_description=open("README.md").read(),
            long_description_content_type="text/markdown",
            url= url    ,
            install_requires=["colorama"]  ,
            classifiers=[
                'Programming Language :: Python :: 3',
                'License :: OSI Approved :: MIT License',
                'Operating System :: OS Independent',
            ],
        )
    def get_versions(self) : 
        response = requests.get(f"https://pypi.org/pypi/{self.name}/json")
        version = self.start_version
        if response.status_code == 200 : 
            version  = response.json()["info"]["version"]

        new_version = self.upgrade_version(version)
        return version , new_version

    def upgrade_version(self,version) : 
        major , minor , patch = map(int, version.split('.'))
        newversion = str(patch + 10 * minor + 100 * major + 1)
        a , b , c =  newversion[:-2]  , newversion[-2] , newversion[-1]
        return ".".join([str(i) for i in [newversion[:-2]  , newversion[-2] , newversion[-1]]])


if __name__ == '__main__':
    PypiPublisher()