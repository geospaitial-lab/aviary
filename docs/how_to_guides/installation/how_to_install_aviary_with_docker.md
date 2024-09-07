## How to install aviary with Docker

Follow along this step-by-step guide to install aviary using Docker.

Note that with Docker, you can use only the [**command-line interface (CLI)**](../../cli_reference/index.md)
of aviary.<br />
If you want to use the [Python API](../../api_reference/index.md)
to build a custom pipeline, you need to install the package locally.
Have a look at the [how-to guide](how_to_install_aviary_with_pip.md) for further information.

### Step 1: Install Docker

First, make sure you have Docker installed.

If you don't have Docker installed, you can download the latest version from the
[official Docker website](https://www.docker.com).
If you need help installing Docker, you can refer to the
[official Docker installation guide](https://docs.docker.com/get-docker).

---

### Step 2: Download the Docker image

Download the Docker image by launching your command-line interface and run the following command:

```
docker pull ghcr.io/geospaitial-lab/aviary
```

We recommend to shorten the image name by tagging it with a custom name (in this case, `aviary`).
To do so, run the command below:

```
docker tag ghcr.io/geospaitial-lab/aviary aviary
```

---

### Step 3: Verify the download

To verify that the Docker image was downloaded successfully, you can run the following command:

```
docker run --rm aviary --version
```
