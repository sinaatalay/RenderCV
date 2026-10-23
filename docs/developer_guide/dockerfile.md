---
toc_depth: 2
---

# Dockerfile

Running RenderCV normally requires installing Python, the application, and its dependencies. [Docker](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/) lets us package that environment so users can run it without installing those components individually on their computer.

An **image** is the packaged filesystem and instructions for starting the application. A **container** is a running instance of that image, with its own filesystem view and processes. The **Dockerfile** is the recipe used to build the image. Users need Docker installed to run it; a container does not eliminate that requirement.

## Run RenderCV in a container

The image includes Python, RenderCV, fonts, and its built-in Typst packages. The container needs access to your CV and somewhere to write the result. A **bind mount** makes a directory on your computer available inside it.

From the directory containing `Your_Name_CV.yaml`, run this command in a macOS or Linux shell:

```bash
docker run --rm -v "$PWD":/work \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -w /work \
  ghcr.io/rendercv/rendercv render Your_Name_CV.yaml
```

The options connect the packaged environment to your files:

- `-v "$PWD":/work` makes the current directory available at `/work` inside the container. Changes there also appear on your computer.
- `-w /work` runs the command from that directory.
- `--user` supplies your user and group IDs, the numbers the operating system uses for file ownership. This avoids creating output owned by another account on Linux. `HOME=/tmp` gives that account a writable home directory inside the container.
- `--rm` removes the container after the command finishes. Files in the mounted directory remain.

`ghcr.io/rendercv/rendercv` names the image. Docker downloads it if it is missing locally. Everything after that name is passed to RenderCV. Replace `render Your_Name_CV.yaml` with `new "Your Name"` to create a sample input. The PDF is written under `rendercv_output/` in the mounted directory.

## How the image is built

The repository's [`Dockerfile`](https://github.com/rendercv/rendercv/blob/main/Dockerfile) uses a **multi-stage build**: one environment prepares the application, and a second contains what is needed to run it.

The builder installs dependencies from `uv.lock`, downloads the built-in Typst packages, and installs RenderCV and its fonts from this repository. The runtime stage copies the installed environment and starts `rendercv` as its command. Both stages use Python 3.15 on Debian trixie.

Docker caches build steps whose inputs have not changed. Installing external dependencies before copying the source lets an ordinary code edit reuse that installation. `.dockerignore` excludes local environments and build outputs from the files sent to Docker, avoiding unnecessary copies and rebuilds. See [uv's Docker guide](https://docs.astral.sh/uv/guides/integration/docker/) for the build pattern.

## Build and verify offline

From the repository root:

```bash
docker build -t rendercv:local .
mkdir -p docker-smoke
docker run --rm --network none -v "$PWD/docker-smoke":/work \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -w /work \
  rendercv:local new "Offline Test"
docker run --rm --network none -v "$PWD/docker-smoke":/work \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -w /work \
  rendercv:local render Offline_Test_CV.yaml
```

`-t` names the image; `.` gives Docker the repository directory as its build input. Building needs network access to fetch base images and dependencies. The two runs disable networking with `--network none` and use fresh containers without mounted font or Typst caches. A successful render therefore checks that the image contains its built-in rendering dependencies. The PDF appears under `docker-smoke/rendercv_output`.

Remote photos and new package imports in custom Typst code still need network access. The [test workflow](github_workflows.md#tests) runs this offline check on Ubuntu.

## File ownership with Podman

The image's `rendercv` account uses user and group IDs `1000:1000`. Docker users with those host IDs can omit `--user`. Other IDs need the override above.

Podman is another tool for running container images. In **rootless** mode, it runs without administrator privileges and maps container accounts to host accounts. Matching the numeric IDs alone is insufficient. Use `keep-id` to map your account to the image's user:

```bash
podman run --rm --network none --user rendercv \
  --userns=keep-id:uid=1000,gid=1000 \
  -v "$PWD":/work:Z -w /work \
  ghcr.io/rendercv/rendercv render Your_Name_CV.yaml
```

The `:Z` suffix sets the mount's private security label on systems using SELinux. See Podman's [`--userns` documentation](https://docs.podman.io/en/latest/markdown/podman-run.1.html#userns-mode) for the mapping rules; making the host directory writable by everyone is unnecessary.

## Publishing

A **registry** stores images for download. The release workflow builds RenderCV's image and publishes it to GitHub Container Registry (GHCR) at `ghcr.io/rendercv/rendercv`. See [GitHub Workflows](github_workflows.md#releases) for the release sequence.
