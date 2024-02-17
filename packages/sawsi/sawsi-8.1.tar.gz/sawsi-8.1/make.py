import click
import os
import shutil
from pathlib import Path

# 현재 파일의 Path 객체
current_file_path = Path(__file__)

# boilerplate 파일이 위치한 디렉토리
boilerplate_dir = current_file_path.parent / 'boilerplate'


@click.group()
def cli():
    pass


@cli.command()
@click.argument('app_name')
def startapp(app_name):
    # 현재 작업 디렉토리를 기준으로 앱 디렉토리 생성
    project_path = Path(os.getcwd())
    project_path.mkdir(parents=True, exist_ok=True)

    # 기본 파일 구조 생성
    create_base_dir(app_name, project_path)

    # 앱 구조 생성
    create_app_dir(app_name, project_path)

    click.echo(f"App {app_name} has been created in {project_path}")


def create_base_dir(app_name, project_path):
    target_files = ['api.py', 'errs.py']
    for target_file in target_files:
        source_file = boilerplate_dir / target_file
        copy_without_overwrite(source_file, project_path)
        click.echo(f"Copied {target_file} to {project_path}")


def create_app_dir(app_name, project_path):
    source_dir = boilerplate_dir / 'app'
    destination_dir = project_path / app_name

    # 대상 디렉토리가 이미 존재하는 경우에도 복사를 수행
    try:
        shutil.copytree(source_dir, destination_dir, dirs_exist_ok=False)
    except Exception as ex:
        print(ex)
    # {{app}} 수정
    replace_app(destination_dir / 'controller' / 'sample_login.py', app_name)
    replace_app(destination_dir / 'dao' / 'sample_user_dao.py', app_name)
    replace_app(destination_dir / 'view_model' / 'sample_user_vm.py', app_name)


def replace_app(target_file, app_name):
    rfp = open(target_file, 'r')
    text = rfp.read()
    text = text.replace('{{app}}', app_name)
    rfp.close()

    wfp = open(target_file, 'w+')
    wfp.write(text)


def copy_without_overwrite(source, destination):
    """
    shutil.copy와 유사하게 파일을 복사하지만, 대상 파일이 이미 존재하는 경우 복사를 수행하지 않습니다.

    :param source: 복사할 소스 파일의 경로입니다.
    :param destination: 파일을 복사할 대상 경로입니다. 파일 이름을 포함할 수도 있고, 디렉토리만을 지정할 수도 있습니다.
    :return: 복사가 성공적으로 수행되었으면 True를, 이미 파일이 존재하여 복사하지 않았으면 False를 반환합니다.
    """
    # destination이 디렉토리인 경우, 동일한 파일 이름으로 설정
    if os.path.isdir(destination):
        destination = os.path.join(destination, os.path.basename(source))

    # 대상 파일이 이미 존재하는지 확인
    if os.path.exists(destination):
        print(f'Copy skipped: {destination} already exists.')
        return False
    else:
        shutil.copy(source, destination)
        print(f'File copied to {destination}')
        return True



if __name__ == '__main__':
    cli()