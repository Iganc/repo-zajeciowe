import os
import shutil
from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from git import Repo
from models import db, Repository, User
from flask import send_file

repos_bp = Blueprint('repos', __name__)

@repos_bp.route('/')
@login_required
def index():
    repos = Repository.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', repos=repos)

@repos_bp.route('/repo/<int:repo_id>')
@login_required
def view_repo(repo_id):
    repo_data = Repository.query.get_or_404(repo_id)
    if repo_data.user_id != current_user.id:
        abort(403)

    sub_path = request.args.get('path', '')
    path = repo_data.get_absolute_path
    files = []
    breadcrumbs = []

    try:
        git_repo = Repo(path)
        if git_repo.heads:
            root_tree = git_repo.head.commit.tree
            current_tree = root_tree
            
            if sub_path:
                try:
                    current_tree = root_tree[sub_path]
                except KeyError:
                    abort(404) 

            for item in current_tree:
                item_rel_path = os.path.join(sub_path, item.name).replace("\\", "/")
                files.append({
                    "name": item.name,
                    "type": "folder" if item.type == "tree" else "file",
                    "size": item.size if item.type == "blob" else "-",
                    "path": item_rel_path
                })
            
            path_parts = sub_path.split('/') if sub_path else []
            curr_build = ""
            for part in path_parts:
                curr_build = os.path.join(curr_build, part).replace("\\", "/")
                breadcrumbs.append({"name": part, "path": curr_build})

    except Exception as e:
        print(f"Błąd odczytu Gita: {e}")

    return render_template('repo_view.html', 
                           repo=repo_data, 
                           files=files, 
                           current_path=sub_path, 
                           breadcrumbs=breadcrumbs)

@repos_bp.route('/create_repo', methods=['POST'])
@login_required
def create_repo():
    repo_name = request.form.get('repo_name')
    if not repo_name:
        flash('Nazwa repozytorium jest wymagana!', 'warning')
        return redirect(url_for('repos.index'))

    folder_name = f"{current_user.username}_{repo_name.replace(' ', '_').lower()}"
    base_path = os.path.join(os.getcwd(), 'repos')
    repo_path = os.path.join(base_path, folder_name)

    if not os.path.exists(base_path):
        os.makedirs(base_path)

    if os.path.exists(repo_path):
        flash('Masz już folder o takiej nazwie!', 'danger')
        return redirect(url_for('repos.index'))

    try:
        os.makedirs(repo_path)
        Repo.init(repo_path)

        new_repo = Repository(
            name=repo_name, 
            folder_name=folder_name, 
            user_id=current_user.id 
        )
        db.session.add(new_repo)
        db.session.commit()
        flash('Repozytorium utworzone pomyślnie!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Błąd inicjalizacji: {str(e)}', 'danger')

    return redirect(url_for('repos.index'))

@repos_bp.route('/upload/<int:repo_id>', methods=['POST'])
@login_required
def upload_file(repo_id):
    repo_data = Repository.query.get_or_404(repo_id)
    current_subpath = request.args.get('path', '')
    
    uploaded_files = request.files.getlist('files')
    repo_path = repo_data.get_absolute_path
    git_repo = Repo(repo_path)
    saved_filenames = []

    for file in uploaded_files:
        if file:
            filename = secure_filename(file.filename)
            target_dir = os.path.join(repo_path, current_subpath)
            file_path = os.path.join(target_dir, filename)
            
            file.save(file_path)
            saved_filenames.append(os.path.join(current_subpath, filename).replace("\\", "/"))

    if saved_filenames:
        git_repo.index.add(saved_filenames)
        git_repo.index.commit(f"Dodano pliki do {current_subpath or 'root'}")
        flash(f'Wgrano {len(saved_filenames)} plików.', 'success')
        
    return redirect(url_for('repos.view_repo', repo_id=repo_id, path=current_subpath))

@repos_bp.route('/create_folder/<int:repo_id>', methods=['POST'])
@login_required
def create_folder(repo_id):
    repo_data = Repository.query.get_or_404(repo_id)
    current_subpath = request.args.get('path', '')
    new_folder_name = request.form.get('folder_name')
    
    if new_folder_name:
        new_folder_name = secure_filename(new_folder_name)
        repo_path = repo_data.get_absolute_path
        target_path = os.path.join(repo_path, current_subpath, new_folder_name)
        
        if not os.path.exists(target_path):
            os.makedirs(target_path)
            keep_file = os.path.join(target_path, '.gitkeep')
            with open(keep_file, 'w') as f:
                f.write('')
            
            rel_keep = os.path.join(current_subpath, new_folder_name, '.gitkeep').replace("\\", "/")
            git_repo = Repo(repo_path)
            git_repo.index.add([rel_keep])
            git_repo.index.commit(f"Utworzono folder: {new_folder_name}")
            flash(f'Utworzono folder {new_folder_name}', 'success')
            
    return redirect(url_for('repos.view_repo', repo_id=repo_id, path=current_subpath))

@repos_bp.route('/rename_repo/<int:repo_id>', methods=['POST'])
@login_required
def rename_repo(repo_id):
    repo = Repository.query.get_or_404(repo_id)
    if repo.user_id != current_user.id:
        abort(403)
        
    new_name = request.form.get('new_name')
    if new_name:
        repo.name = new_name
        db.session.commit()
        flash('Nazwa została zmieniona.', 'success')
    return redirect(url_for('repos.index'))

@repos_bp.route('/delete_repo/<int:repo_id>', methods=['POST'])
@login_required
def delete_repo(repo_id):
    repo = Repository.query.get_or_404(repo_id)
    if repo.user_id != current_user.id:
        abort(403)
        
    repo_path = repo.get_absolute_path
    try:
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            
        db.session.delete(repo)
        db.session.commit()
        flash(f'Repozytorium {repo.name} zostało usunięte.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Błąd usuwania: {str(e)}', 'danger')
        
    return redirect(url_for('repos.index'))

@repos_bp.route('/repo/<int:repo_id>/history')
@login_required
def repo_history(repo_id):
    repo_data = Repository.query.get_or_404(repo_id)
    if repo_data.user_id != current_user.id:
        abort(403)
        
    path = repo_data.get_absolute_path
    commits = []
    
    try:
        git_repo = Repo(path)
        for commit in git_repo.iter_commits(max_count=50):
            commits.append({
                "hash": commit.hexsha[:7],
                "message": commit.message,
                "author": commit.author.name,
                "date": commit.authored_datetime.strftime("%Y-%m-%d %H:%M:%S")
            })
    except Exception as e:
        flash(f"Błąd historii: {str(e)}", "danger")

    return render_template('repo_history.html', repo=repo_data, commits=commits)

@repos_bp.route('/upload_folder/<int:repo_id>', methods=['POST'])
@login_required
def upload_folder(repo_id):
    repo_data = Repository.query.get_or_404(repo_id)
    uploaded_files = request.files.getlist('files')
    repo_path = repo_data.get_absolute_path
    
    saved_paths = []
    for file in uploaded_files:
        if file:
            rel_path = file.filename 
            full_path = os.path.join(repo_path, rel_path)
            
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            file.save(full_path)
            saved_paths.append(rel_path)

    if saved_paths:
        git_repo = Repo(repo_path)
        git_repo.index.add(saved_paths)
        git_repo.index.commit(f"Wgrano folder z {len(saved_paths)} plikami")
        flash('Folder wgrany pomyślnie.', 'success')

    return redirect(url_for('repos.view_repo', repo_id=repo_id))

@repos_bp.route('/repo/<int:repo_id>/download')
@login_required
def download_repo(repo_id):
    repo_data = Repository.query.get_or_404(repo_id)
    if repo_data.user_id != current_user.id:
        abort(403)
        
    path = repo_data.get_absolute_path
    zip_name = f"{repo_data.folder_name}_backup"
    zip_path = os.path.join(os.getcwd(), zip_name)
    
    shutil.make_archive(zip_path, 'zip', path)
    
    return send_file(f"{zip_path}.zip", as_attachment=True, download_name=f"{repo_data.name}.zip")