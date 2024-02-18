# skills_network_authoring_jupyterlab_extension

[![Github Actions Status](https://github.com/ibm-skills-network/skills-network-authoring-jupyterlab-extension/actions/workflows/build.yml/badge.svg)](https://github.com/ibm-skills-network/skills-network-authoring-jupyterlab-extension/actions/workflows/build.yml)

JupterLab/JupyerLite extension for Skills Network Authoring

If you are an author start [here](#to-use-the-extension-as-an-author)

If you are a contributor start [here](#to-contribute-to-the-extension)

## Requirements

- JupyterLab >= 4.0.0

## To Use the Extension as an Author

### Install

To install the extension, execute:

```bash
pip install skills_network_authoring_jupyterlab_extension
```

After installing, enable the extension:

```bash
jupyter server extension enable skills_network_authoring_jupyterlab_extension
```

### Launch JupyterLab

To launch Jupyter Lab visit [http://localhost:8888/](http://localhost:8888/)

### Uninstall

To remove the extension, execute:

```bash
pip uninstall skills_network_authoring_jupyterlab_extension
```

### Edit a Lab via Token

![](/static/extension_demo.gif)

### Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## To Contribute to the Extension

### Before Getting Started

Check the JupyterLab version in staging and production and download the correct JupyterLab extension.

To check the version go to [Menu Bar]([https://jupyterlab.readthedocs.io/en/stable/user/interface.html#menu-bar]) -> Help -> About JupyterLab

```
pip install jupyterlab==<version>
```

### Development Install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the skills-network-authoring-jupyterlab-extension directory
cd skills-network-authoring-jupyterlab-extension
# Install package in development mode
pip install -e "."
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Server extension must be manually installed in develop mode
jupyter server extension enable skills_network_authoring_jupyterlab_extension
# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Launch JupyterLab

To launch Jupyter Lab visit [http://localhost:8888/](http://localhost:8888/)

### Hard Reset

Sometimes you want to hard reset and remove all build files. To clean up all the development files before rebuilding the package:

```bash
jlpm clean:all
```

```bash
git clean -dfX
```

### Development Uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable skills_network_authoring_jupyterlab_extension
pip uninstall skills_network_authoring_jupyterlab_extension
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `skills_network_authoring_jupyterlab_extension` within that folder.

### Edit a Lab via Token

Demo [Here](#edit-a-lab-via-token)

#### Get a Token

1. Go to Author Workbench production [site](https://author.skills.network/)
2. Select `Labs` on the left panel screen
3. Select `JupyterLab` Tool Type
4. Select `Edit` on the desired lab
5. Pick the "On Your Computer" tab of the pop-up
6. Copy the displayed token

Public instructions of the above (with images) [here](https://author.skills.network/docs/labs/edit-jupyterlab-instructions-computer/#editing-using-a-local-installation-of-jupyterlab)

### Packaging the Extension

See [RELEASE](RELEASE.md)
