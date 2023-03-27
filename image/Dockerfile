FROM registry.access.redhat.com/ubi8/ubi:latest
LABEL maintainer="mstoklus@redhat.com"

ENV PATH=$PATH:/usr/local/bin
WORKDIR /home/migration

RUN set -o pipefail && \
    INSTALL_PKGS="unzip rsync" && \
    yum install -y --setopt=tsflags=nodocs $INSTALL_PKGS && \
    curl -Ls https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-linux.tar.gz | tar -zx && \
    mv oc /usr/local/bin && \
    curl -Lo /usr/local/bin/yq https://github.com/mikefarah/yq/releases/download/v4.23.1/yq_linux_amd64 && \
    chmod +x /usr/local/bin/yq && \
    curl -Lo /usr/local/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && \
    chmod +x /usr/local/bin/jq && \
    curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip && \
    unzip awscliv2.zip && \
    ./aws/install -b /usr/local/bin && \
    chmod +x /usr/local/bin/aws

RUN chgrp -R 0 /home/migration && \
    chmod -R g=u /home/migration 

CMD /bin/bash