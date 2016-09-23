#!/bin/bash
# Run the tests locally using the qgis testing environment docker

xhost +

PLUGIN_NAME="lessons"

docker rm -f qgis-testing-environment

# replace release with master or master_2 if you wish to test on master or master_2
docker pull elpaso/qgis-testing-environment:release
docker tag elpaso/qgis-testing-environment:release qgis-testing-environment

docker run -d  --name qgis-testing-environment  -e DISPLAY=:99 -v /tmp/.X11-unix:/tmp/.X11-unix -v `pwd`:/tests_directory qgis-testing-environment


docker exec -it qgis-testing-environment sh -c "qgis_setup.sh $PLUGIN_NAME"

# Install the plugin
docker exec -it qgis-testing-environment sh -c "easy_install --upgrade pip"
docker exec -it qgis-testing-environment sh -c "pip install paver"
docker exec -it qgis-testing-environment sh -c "cd /tests_directory && paver setup"
docker exec -it qgis-testing-environment sh -c "mkdir -p /root/.qgis2/python/plugins/"
docker exec -it qgis-testing-environment sh -c "ln -s /tests_directory/$PLUGIN_NAME /root/.qgis2/python/plugins/$PLUGIN_NAME"


# run the tests
docker exec -it qgis-testing-environment sh -c "DISPLAY=unix:0 qgis_testrunner.sh $PLUGIN_NAME.tests.unit_tests"
