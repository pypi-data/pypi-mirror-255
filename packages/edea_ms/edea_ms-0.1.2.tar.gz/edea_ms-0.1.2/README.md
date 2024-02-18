# EDeA Measurement Server

edea-ms provides an API and user interface for planning, executing and analyzing measurement data for electronics engineering purposes. It allows engineering teams or collaborating individuals to automate tests and share results in a unified way, be it for board bringup, silicon evaluation or other test and measurement tasks.

This project is based on the original EDeA Project proposal and takes further inspiration from the [TestOps Manifesto by Keysight](https://www.keysight.com/us/en/assets/7018-06546/white-papers/5992-3771.pdf).

## Current Status

We're using and developing this at Fully Automated for our OSHW and consulting projects. It's in a usable state, but currently only used internally. If you intend to use this, please contact us so we can understand the usecase of other engineering teams better.

## Running it

To make it as easy as possible to use, we've published a package on pypi which can just be installed like this:

```sh
pip install edea_ms
# or with optional dependencies for rendering charts server-side
pip install "edea_ms[optional]"
```

And it can be run locally like this:

```sh
python -m edea_ms --local
```

This starts a webserver which is only reachable on the local machine without any user authentication to keep it simple for single user installs or just trying it out. To set up authentication to collaborate with others in a team see the docs on [Authentication](https://edea-dev.gitlab.io/edea-ms/authentication.html).

### Development

To run the server from the repository, it needs both the backend and the frontend like this:

```sh
# run the server
pdm run uvicorn edea_ms.main:app --reload

# run the frontend
npm run dev
```

## Building the package

In case you want to bundle a modified frontend into your own package, simply run:

```sh
npm run build # this will compile the frontend to static files
pdm build # to build the final wheel with the frontend embedded in it
```

## Measurement Client

See the [EDeA TMC](https://gitlab.com/edea-dev/edea-tmc) project for a library with which one can write test programs with.

## Licenses

The server code is licensed under the [EUPL-1.2 license](LICENSE.txt) and the frontend code is licensed under the [MIT license](LICENSE.frontend.txt).
Images and artwork are licensed under CC BY-ND 4.0.

Linking the server code (e.g. using it as a library) is allowed under the EUPL-1.2, even for commercial use. Modifications should be shared but the server code is structured in a way that it can easily be integrated in other systems (internal or otherwise) without modifying the core.

If you want to host a modified frontend internally or externally, please replace the logos so that it's clear that it is a modified distribution.
