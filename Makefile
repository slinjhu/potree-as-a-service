NAME = potree-aas
CONTAINER=${NAME}-container
GCP=ml-slin

# A list of pairs <host_absolute_path:container_absolute_path> (separated by space) that the dev container will bind.
DOCKER_PARAM =  \
  -v ${PWD}/src:/src \
  -w /src \
  --privileged

build-dev:
	docker build . --tag ${NAME} --target dev


dev: build-dev
	docker container rm -f ${CONTAINER} || true
	docker run -it --publish 5000:80 ${DOCKER_PARAM} ${NAME}

build-release:
	sudo git clean -Xfd
	docker build . --tag ${NAME}-release --target prod

deploy: build-release
	docker container rm -f ${CONTAINER} || true
	docker run --name ${CONTAINER} -d -p 5000:80 --env "DEPLOY_ENV=local" ${NAME}-release
	docker logs --follow ${CONTAINER}

release: build-release
	DEST=gcr.io/${GCP}/${NAME}; \
	VERSION=$$(git rev-list --count master); \
        docker tag ${NAME}-release $$DEST:$$VERSION ; \
        docker push $$DEST:$$VERSION ; \
        echo ">>> Released version: $$VERSION"
