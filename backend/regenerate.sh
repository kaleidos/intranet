dropdb intranet
createdb intranet
python manage.py syncdb
python manage.py migrate
python manage.py sample_data
echo "DELETE FROM auth_permission;" | python manage.py dbshell
echo "DELETE FROM django_content_type;" | python manage.py dbshell

