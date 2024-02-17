import os
from pathlib import Path

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

BASE_DIR = Path(__file__).resolve().parent.parent
template_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
template_dir = os.path.join(template_dir, 'spark_webdat_tools', 'src', 'templates')
app = Flask(__name__, template_folder=template_dir)


def run_server():
    app.debug = False
    app.run(host='0.0.0.0')


def get_configurate_git():
    from git import Actor
    author = Actor("jonathan quiza", "jonathan.quiza@bbva.com")
    committer = Actor("jonathan", "jonathan.quiza@bbva.com")
    return author, committer


def get_shutil_copy_files(folder_files, directory_move):
    import shutil
    import sys
    is_windows = sys.platform.startswith('win')

    for files_dir in os.listdir(folder_files):
        file_dir = os.path.join(folder_files, files_dir)
        if os.path.isdir(file_dir):
            directory_move_subdir = os.path.join(directory_move, files_dir)
            for files_subdir in os.listdir(file_dir):
                file_subdir = os.path.join(folder_files, files_dir, files_subdir)
                if is_windows:
                    directory_move_subdir = directory_move_subdir.replace("\\", "/")
                    file_subdir = file_subdir.replace("\\", "/")
                os.makedirs(directory_move_subdir, exist_ok=True)
                shutil.copy(file_subdir, directory_move_subdir)
        else:
            shutil.copy(file_dir, directory_move)


url_clone_repo = "/repository_kirby/clone_repo"
url_branch_dq360 = "/repository_kirby/configurate_branch_dq360"
url_branch_jon_runner = "/repository_kirby/configurate_branch_jon_runner"
url_branch_kirby_m360 = "/repository_kirby/configurate_branch_kirby_m360"
url_branch_validate_m360 = "/repository_kirby/configurate_branch_validate_m360"
url_branch_master = "/repository_kirby/configurate_branch_master"
url_branch_master_filename = "/repository_kirby/configurate_branch_master_filename"
url_bitbucket_repository = "/repository_kirby/configurate_bitbucket_repository"
url_branch_merge_repository_master = "/repository_kirby/configurate_branch_merge_repository_master"


@app.route('/repository_kirby', methods=['GET'])
def repository_kirby():
    branches = {
        "url_clone_repo": url_clone_repo,
        "url_branch_dq360": url_branch_dq360,
        "url_branch_jon_runner": url_branch_jon_runner,
        "url_branch_kirby_m360": url_branch_kirby_m360,
        "url_branch_validate_m360": url_branch_validate_m360,
        "url_branch_master": url_branch_master,
        "url_branch_master_filename": url_branch_master_filename,
        "url_bitbucket_repository": url_bitbucket_repository,
        "url_branch_merge_repository_master": url_branch_merge_repository_master
    }
    return render_template('page/repository_kirby.html', branches=branches)


@app.route('/repository_kirby/clone_repo', methods=['POST'])
def repository_kirby_clone_repo():
    import sys
    import shutil
    from git import Repo
    is_windows = sys.platform.startswith('win')

    if request.method == 'POST':
        folder_path = request.form.get("name_folder_path")
        ssh_git = request.form.get("name_ssh_git")

        if is_windows:
            folder_path = folder_path.replace("\\", "/")
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        os.mkdir(folder_path)
        Repo.clone_from(ssh_git, folder_path, progress=None)
        return jsonify({"data": "1.Repository Clone was successfully created"})
    else:
        return jsonify({"data": "1.Not a valid request method for this route"})


@app.route('/repository_kirby/configurate_branch_dq360', methods=['POST'])
def repository_kirby_configurate_branch_dq360():
    from git import Repo
    import sys
    import os
    from spark_webdat_tools.src.main import BASE_DIR

    if request.method == 'POST':
        author, committer = get_configurate_git()
        is_windows = sys.platform.startswith('win')
        current_folder_path = request.form.get("name_folder_path")
        path_static_branch_skynet = os.path.join("src", "static", "repository_examples", "branchs_skynet")
        folder_path_dqa_360 = os.path.join(BASE_DIR, path_static_branch_skynet, "dq-m360")

        if is_windows:
            current_folder_path = current_folder_path.replace("\\", "/")
            folder_path_dqa_360 = folder_path_dqa_360.replace("\\", "/")

        repo = Repo(current_folder_path)
        repo.git.execute("git fetch origin --recurse-submodules=no --progress --prune")
        repo = Repo(current_folder_path)
        repo.git.checkout('develop')
        new_branch_name = 'dq-m360'
        repo.git.checkout('-b', new_branch_name)
        get_shutil_copy_files(folder_path_dqa_360, current_folder_path)
        repo.git.execute("git add --all")
        repo.index.commit("Initial", author=author, committer=committer)
        repo.git.push('origin', '-u', new_branch_name)

        return jsonify({"data": f"2.Repository {new_branch_name} was successfully created"})
    else:
        return jsonify({"data": "2.Not a valid request method for this route"})


@app.route('/repository_kirby/configurate_branch_jon_runner', methods=['POST'])
def repository_kirby_configurate_branch_jon_runner():
    from git import Repo
    import sys
    import os
    from spark_webdat_tools.src.main import BASE_DIR

    if request.method == 'POST':
        author, committer = get_configurate_git()
        is_windows = sys.platform.startswith('win')
        current_folder_path = request.form.get("name_folder_path")
        path_static_branch_skynet = os.path.join("src", "static", "repository_examples", "branchs_skynet")
        folder_path_jon_runner = os.path.join(BASE_DIR, path_static_branch_skynet, "job-runner")

        if is_windows:
            current_folder_path = current_folder_path.replace("\\", "/")
            folder_path_jon_runner = folder_path_jon_runner.replace("\\", "/")

        repo = Repo(current_folder_path)
        repo.git.execute("git fetch origin --recurse-submodules=no --progress --prune")
        repo.git.checkout('develop')
        new_branch_name = 'job-runner'
        repo.git.checkout('-b', new_branch_name)
        get_shutil_copy_files(folder_path_jon_runner, current_folder_path)
        repo.git.execute("git add --all")
        repo.index.commit("Initial", author=author, committer=committer)
        repo.git.push('origin', '-u', new_branch_name)

        return jsonify({"data": f"3.Repository {new_branch_name} was successfully created"})
    else:
        return jsonify({"data": "3.Not a valid request method for this route"})


@app.route('/repository_kirby/configurate_branch_kirby_m360', methods=['POST'])
def repository_kirby_configurate_branch_kirby_m360():
    from git import Repo
    import sys
    import os
    from spark_webdat_tools.src.main import BASE_DIR

    if request.method == 'POST':
        author, committer = get_configurate_git()
        is_windows = sys.platform.startswith('win')
        current_folder_path = request.form.get("name_folder_path")
        path_static_branch_skynet = os.path.join("src", "static", "repository_examples", "branchs_skynet")
        folder_path_kirby_m360 = os.path.join(BASE_DIR, path_static_branch_skynet, "kirby-m360")

        if is_windows:
            current_folder_path = current_folder_path.replace("\\", "/")
            folder_path_kirby_m360 = folder_path_kirby_m360.replace("\\", "/")

        repo = Repo(current_folder_path)
        repo.git.execute("git fetch origin --recurse-submodules=no --progress --prune")
        repo.git.checkout('develop')
        new_branch_name = 'kirby_m360'
        repo.git.checkout('-b', new_branch_name)
        get_shutil_copy_files(folder_path_kirby_m360, current_folder_path)
        repo.git.execute("git add --all")
        repo.index.commit("Initial", author=author, committer=committer)
        repo.git.push('origin', '-u', new_branch_name)

        return jsonify({"data": f"4.Repository {new_branch_name} was successfully created"})
    else:
        return jsonify({"data": "4.Not a valid request method for this route"})


@app.route('/repository_kirby/configurate_branch_validate_m360', methods=['POST'])
def repository_kirby_configurate_branch_validate_m360():
    from git import Repo
    import sys
    import os
    from spark_webdat_tools.src.main import BASE_DIR

    if request.method == 'POST':
        author, committer = get_configurate_git()
        is_windows = sys.platform.startswith('win')
        current_folder_path = request.form.get("name_folder_path")
        path_static_branch_skynet = os.path.join("src", "static", "repository_examples", "branchs_skynet")
        folder_path_validate_m360 = os.path.join(BASE_DIR, path_static_branch_skynet, "validate-m360")

        if is_windows:
            current_folder_path = current_folder_path.replace("\\", "/")
            folder_path_validate_m360 = folder_path_validate_m360.replace("\\", "/")

        repo = Repo(current_folder_path)
        repo.git.execute("git fetch origin --recurse-submodules=no --progress --prune")
        repo.git.checkout('develop')
        new_branch_name = 'validate_m360'
        repo.git.checkout('-b', new_branch_name)
        get_shutil_copy_files(folder_path_validate_m360, current_folder_path)
        repo.git.execute("git add --all")
        repo.index.commit("Initial", author=author, committer=committer)
        repo.git.push('origin', '-u', new_branch_name)

        return jsonify({"data": f"5.Repository {new_branch_name} was successfully created"})
    else:
        return jsonify({"data": "5.Not a valid request method for this route"})


@app.route('/repository_kirby/configurate_branch_master', methods=['POST'])
def repository_kirby_configurate_branch_master():
    from git import Repo
    import sys
    import os
    from spark_webdat_tools.src.main import BASE_DIR

    if request.method == 'POST':
        author, committer = get_configurate_git()
        is_windows = sys.platform.startswith('win')
        current_folder_path = request.form.get("name_folder_path")
        path_static_branch_skynet = os.path.join("src", "static", "repository_examples", "branchs_skynet")
        folder_path_master = os.path.join(BASE_DIR, path_static_branch_skynet, "master")

        if is_windows:
            current_folder_path = current_folder_path.replace("\\", "/")
            folder_path_master = folder_path_master.replace("\\", "/")

        repo = Repo(current_folder_path)
        repo.git.execute("git fetch origin --recurse-submodules=no --progress --prune")
        repo.git.checkout('develop')
        new_branch_name = 'repository'
        repo.git.checkout('-b', new_branch_name)
        get_shutil_copy_files(folder_path_master, current_folder_path)
        repo.git.execute("git add --all")
        repo.index.commit("Initial", author=author, committer=committer)
        repo.git.push('origin', '-u', new_branch_name)

        return jsonify({"data": f"6.Repository {new_branch_name} was successfully created"})
    else:
        return jsonify({"data": "6.Not a valid request method for this route"})


@app.route('/repository_kirby/configurate_branch_master_filename', methods=['POST'])
def repository_kirby_configurate_branch_master_filename():
    from git import Repo
    import sys
    import os

    if request.method == 'POST':
        author, committer = get_configurate_git()
        is_windows = sys.platform.startswith('win')
        current_folder_path = str(request.form.get("name_folder_path")).strip()
        current_repo_name = str(request.form.get("name_repo_name")).strip()
        current_uuaa_name = str(request.form.get("name_uuaa_name")).strip()

        file_pom_externo = os.path.join(current_folder_path, "pom.xml")
        file_projectinfo_externo = os.path.join(current_folder_path, "project-info.json")
        file_pom_interno = os.path.join(current_folder_path, "skynet", "pom.xml")

        if is_windows:
            current_folder_path = current_folder_path.replace("\\", "/")
            file_pom_externo = file_pom_externo.replace("\\", "/")
            file_projectinfo_externo = file_projectinfo_externo.replace("\\", "/")
            file_pom_interno = file_pom_interno.replace("\\", "/")

        print(file_pom_externo)
        print(file_projectinfo_externo)
        print(file_pom_interno)
        repo = Repo(current_folder_path)
        repo.git.execute("git fetch origin --recurse-submodules=no --progress --prune")
        repo.git.checkout('develop')
        repo.git.checkout('repository')

        with open(file_pom_externo) as f:
            ch = f.read()
            text = str(ch).replace("peinqtesting", current_repo_name)
            text = str(text).replace("pdit", str(current_uuaa_name).lower())
            with open(file_pom_externo, 'w') as file:
                file.write(text)

        with open(file_projectinfo_externo) as f:
            ch = f.read()
            text = str(ch).replace("PDIT", str(current_uuaa_name).upper())
            with open(file_projectinfo_externo, 'w') as file:
                file.write(text)

        with open(file_pom_interno) as f:
            ch = f.read()
            text = str(ch).replace("peinqtesting", current_repo_name)
            text = str(text).replace("pdit", str(current_uuaa_name).lower())
            with open(file_pom_interno, 'w') as file:
                file.write(text)

        new_branch_name = 'repository'
        repo.git.execute("git add --all")
        repo.index.commit("Initial", author=author, committer=committer)
        repo.git.push('origin', '-u', new_branch_name)

        return jsonify({"data": f"7.Repository {new_branch_name} was successfully update files"})
    else:
        return jsonify({"data": "7.Not a valid request method for this route"})


@app.route('/repository_kirby/configurate_bitbucket_repository', methods=['POST'])
def repository_kirby_configurate_bitbucket_repository():
    from spark_webdat_tools.functions.jira import Jira

    if request.method == 'POST':
        token = str(request.form.get("name_token_name")).strip()
        proxy = str(request.form.get("name_proxy_name")).strip()
        current_repo_name = str(request.form.get("name_ssh_git")).strip()
        current_repo_name_split = current_repo_name.split("/")

        project_name = current_repo_name_split[3]
        repo_name = str(current_repo_name_split[4]).split(".")[0]

        if str(proxy).lower() in ("false", None):
            proxy = False
        else:
            proxy = True

        jira = Jira(username="jonathan.quiza", token=token, proxy=proxy)
        jira.post_projects_repo_permissions_groups(project_name=project_name, repo_name=repo_name)
        jira.post_projects_repo_branch_permissions_key(project_name=project_name, repo_name=repo_name)
        jira.post_projects_repo_reviewers_key(project_name=project_name, repo_name=repo_name)

        return jsonify({"data": f"8.Bitbucket configurate was successfully"})
    else:
        return jsonify({"data": "8.Not a valid request method for this route"})


@app.route('/repository_kirby/configurate_branch_merge_repository_master', methods=['POST'])
def repository_kirby_configurate_branch_merge_repository_master():
    from git import Repo
    import sys

    if request.method == 'POST':
        author, committer = get_configurate_git()
        is_windows = sys.platform.startswith('win')
        current_folder_path = str(request.form.get("name_folder_path")).strip()

        if is_windows:
            current_folder_path = current_folder_path.replace("\\", "/")

        repo = Repo(current_folder_path)
        repo.git.execute("git fetch origin --recurse-submodules=no --progress --prune")
        repo.git.checkout('develop')

        new_branch_name = 'master'
        repo.git.checkout(new_branch_name)
        repo.git.merge("repository")
        repo.git.execute("git add --all")
        repo.index.commit("Initial", author=author, committer=committer)
        repo.git.push('origin', '-u', new_branch_name)

        return jsonify({"data": f"9.Branch {new_branch_name} was successfully update files"})
    else:
        return jsonify({"data": "9.Not a valid request method for this route"})


@app.route('/repository_smartcleaner', methods=['POST', 'GET'])
def repository_smartcleaner():
    return render_template('page/repository_smartcleaner.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    print("I am running")
    return render_template('layout.html')
