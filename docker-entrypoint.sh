#!/bin/bash

python manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@yourdomain.com', 'password')" | python manage.py shell
python manage.py runserver 0.0.0.0:8000