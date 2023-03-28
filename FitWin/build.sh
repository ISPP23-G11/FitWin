set -o errexit

pip install -r ../requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py flush
python manage.py loaddata data.json
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@fitwin.com', '12complexpassword34')" | python manage.py shell
