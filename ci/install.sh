#!/bin/env bash

if [[ "${UNITTEST_WITH_K8S}" == "true" ]]; then
  sudo apt-get -y update;
  sudo apt-get install  -y conntrack;
  curl -Lo kubectl https://storage.googleapis.com/kubernetes-release/release/v1.7.0/bin/linux/amd64/kubectl;
  chmod +x kubectl;
  sudo mv kubectl /usr/local/bin/;
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip";
  unzip awscliv2.zip;
  sudo ./aws/install;
  aws eks --region eu-central-1 update-kubeconfig --name xcube-webapis-stage --alias xcube-webapis-stage;
  kubectl config use-context xcube-webapis-stage;
fi;
