Kapellmeister management server
===============================

Manage agents, store running parameters and latest image versions


Description
===============================

Kapellmeister server has 2 endpoints which serve agents  and receive updates after your gitlab CI pipeline was started.
Agents using  their endpoint for requesting new images and run parameters, and has token which have read access.
When you run your gitlab CI pipeline endpoint for pipelines receiving new image version and container run parameters  and store at sqlite db. Every 5 minutes (by default) agents requesting updates

Quick start
===============================

Generate your secret key and type at  env.list
```angular2html
SECRET_KEY="YOUR_SECRET_KEY"  #  50 chars recommended
```
Define username and password for your super user at docker-entrypoint.sh

```angular2html
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('YOUR_USERNAME', 'username@yourdomain.com', 'PASSWORD')" | python manage.py shell
```
Starting server
===============================

We're ready to go, lets start Kapellmeister management server with docker
```angular2html
docker run -it  -p 0.0.0.0:8000:8000  --env-file env.list kapellmeister_server
```
Create read only  username  with default permissions, then move to tokens and add  token for created user.
This token you could already use for your kapellmeister agent.

Here is an example how to run kapellmeister agent with it read only users token
```angular2html
docker run -d
--name kapellmeister-agent \ 
-v /var/run/docker.sock:/var/run/docker.sock \
--restart unless-stopped 
-e KAPELLMEISTER_URL: http://domain.name/api/v1
-e KAPELLMEISTER_KEY: TOKEN_FROM_READ_ONLY_USER 
-e KAPELLMEISTER_PROJECT: project_name 
-e KAPELLMEISTER_CHANNEL: branch_name 
belichberghub/kapellmeister-agent
```
Create username with with staff permissions and add token. Then you could use this token for your gitlab CI
```angular2html
- envsubst < kapellmeister.yaml | curl --header "Authorization: Token ${KAPELLMEISTER_KEY}" --header "Content-Type: application/yaml" -X POST --data-binary @- --url $KAPELLMEISTER_PATH

```





