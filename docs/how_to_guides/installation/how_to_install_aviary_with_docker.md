## How to install aviary with Docker

<span class="aviary-skill-level">Skill level: Beginner</span>

!!! abstract "TL;DR"
    Use `docker pull ghcr.io/geospaitial-lab/aviary` to install aviary’s CLI.

Docker offers a simple way to use aviary’s CLI in a containerized environment.
This approach is ideal for users who want to run the pipelines
on systems where installing software directly is not feasible or in distributed environments
where the use of containers is necessary.

### Install Docker

First, make sure Docker is installed on your system.

Download Docker from the
[official Docker website :material-arrow-top-right:][official Docker website].
If you need help, you can refer to the
[official Docker installation guide :material-arrow-top-right:][official Docker installation guide].

  [official Docker website]: https://www.docker.com
  [official Docker installation guide]: https://docs.docker.com/get-docker

### Install aviary

Install aviary using Docker.

```
docker pull ghcr.io/geospaitial-lab/aviary
```

We recommend shortening the image name by tagging it with a custom name – in this case, `aviary`.

```
docker tag ghcr.io/geospaitial-lab/aviary aviary
```

### Verify the installation

To verify that aviary was installed successfully, you can check the version.

```
docker run --rm aviary --version
```

This shows the version of aviary.
