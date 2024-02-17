import docker


class DockerClient:
    @property
    def Client(self):
        return self.__client

    @property
    def SharedHostDir(self):
        return self.__shared_host_dir

    def __init__(self, shared_host_dir="/shared_host", **kwargs):
        # import docker
        self.__client = docker.from_env()
        self.__shared_host_dir = shared_host_dir

    # get full image name
    def get_image_name(self, name, version="", **kwargs):
        if not version:
            version = "latest"
        return f"{name}:{version}"

    # get all images
    def get_images(self, **kwargs):
        return self.Client.images.list()

    # check whether image exists
    def has_image(self, name, version="", **kwargs):
        image_name = self.get_image_name(name, version=version, **kwargs)
        images = self.Client.images.list()
        for image in images:
            for tag in image.tags:
                if image_name in tag:
                    return True
        return False

    # pull image
    def pull_image(self, name, version="", **kwargs):
        if not self.has_image(name, version=version):
            image_name = self.get_image_name(name, version=version, **kwargs)
            self.Client.images.pull(image_name)

    # run container
    def run_container(self, image, cmd, host_dir="", stream_logs=False, **kwargs):
        if host_dir:
            volumes = [f"{host_dir}:{self.SharedHostDir}"]
            container = self.Client.containers.run(
                image, cmd, detach=True, remove=True, volumes=volumes
            )
        else:
            container = self.Client.containers.run(image, cmd, remove=True, detach=True)

        # get logs
        logs = container.logs(stream=True, follow=True)

        # stream logs
        if stream_logs:
            for line in logs:
                print(line.decode("utf-8"))
        return logs
