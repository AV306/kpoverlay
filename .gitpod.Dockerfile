FROM gitpod/workspace-full-vnc

SHELL ["/bin/bash", "-c"]
RUN sudo apt update && sudo apt upgrade -y && sudo apt autoremove

RUN source /etc/lsb-release
