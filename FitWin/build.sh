set -o errexit

pip install -r ../requirements.txt

python manage.py collectstatic --no-input
python manage.py makemigrations announcements
python manage.py makemigrations authentication
python manage.py makemigrations chat
python manage.py makemigrations landingPage
python manage.py makemigrations payment
python manage.py makemigrations searching
python manage.py makemigrations users
python manage.py makemigrations
python manage.py migrate
