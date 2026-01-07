@echo off
mkdir scripts 2>NUL
move /Y check_social_app.py scripts\
move /Y inspect_db.py scripts\
move /Y reset_admin_password.py scripts\
move /Y verify_db.py scripts\
move /Y verify_pkg.py scripts\
move /Y verify_resume_field.py scripts\
move /Y verify_setup.py scripts\
del /F /Q views.py
del /F /Q sample_python_resume.txt
del /F /Q build.sh
echo Cleanup completed.
