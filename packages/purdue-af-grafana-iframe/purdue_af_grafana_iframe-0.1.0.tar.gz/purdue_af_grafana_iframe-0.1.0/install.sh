sudo pip uninstall jupyterlab_iframe_launcher
sudo pip install -e "."
sudo jupyter labextension develop . --overwrite
sudo jlpm build
