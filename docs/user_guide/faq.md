# Frequently Asked Questions (FAQ)

## How to use it with JSON Resume?

You can use [jsonresume-to-rendercv](https://github.com/guruor/jsonresume-to-rendercv) to convert your JSON Resume file to a RenderCV input file.

## How to use it with Docker?

If you have Docker installed, you can use RenderCV without installing anything else. Run the command below to open a Docker container with RenderCV installed.

```bash
docker run -it -v ./rendercv:/rendercv docker.io/rendercv/rendercv:latest
```

Then, you can use RenderCV CLI as if it were installed on your machine. The files will be saved in the `rendercv` directory.