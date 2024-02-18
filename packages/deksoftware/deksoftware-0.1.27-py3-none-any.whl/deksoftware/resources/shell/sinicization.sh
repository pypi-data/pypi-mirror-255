#!/bin/bash

if hash apt-get 2>/dev/null; then
  sed -i "s@http://.*archive.ubuntu.com@http://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list
  sed -i "s@http://.*security.ubuntu.com@http://mirrors.tuna.tsinghua.edu.cn@g" /etc/apt/sources.list
fi

if hash yarn 2>/dev/null; then
  yarn config set registry https://repo.huaweicloud.com/repository/npm/
  yarn cache clean -f

  yarn config set disturl https://repo.huaweicloud.com/nodejs

  yarn config set sass_binary_site https://repo.huaweicloud.com/node-sass

  yarn config set phantomjs_cdnurl https://repo.huaweicloud.com/phantomjs
  yarn config set chromedriver_cdnurl https://repo.huaweicloud.com/chromedriver
  yarn config set operadriver_cdnurl https://repo.huaweicloud.com/operadriver

  yarn config set electron_mirror https://repo.huaweicloud.com/electron/
  yarn config set python_mirror https://repo.huaweicloud.com/python

  yarn config set sqlite3_binary_host_mirror https://foxgis.oss-cn-shanghai.aliyuncs.com/
  yarn config set profiler_binary_host_mirror https://npm.taobao.org/mirrors/node-inspector/
fi

PYPI_INDEX_HOST=mirrors.jlu.edu.cn
PYPI_INDEX=https://$PYPI_INDEX_HOST/pypi/simple

if hash pip3 2>/dev/null; then
mkdir -p /root/.config/pip
cat <<EOF | tee /root/.config/pip/pip.conf
[global]
index-url = $PYPI_INDEX
trusted-host = $PYPI_INDEX_HOST
timeout = 120
EOF
fi

if hash pdm 2>/dev/null; then
  pdm config pypi.url $PYPI_INDEX
fi

if hash docker 2>/dev/null; then
mkdir -p /etc/docker
cat <<EOF | tee /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://dockerproxy.com",
    "https://docker.nju.edu.cn",
    "https://docker.mirrors.sjtug.sjtu.edu.cn",
    "https:docker.m.daocloud.io",
    "https://registry-1.docker.io"
  ]
}
EOF
systemctl daemon-reload && systemctl restart docker
fi

# https://zhuanlan.zhihu.com/p/655419673
# https://github.com/ciiiii/cloudflare-docker-proxy
if hash containerd 2>/dev/null; then
mkdir -p /etc/containerd
cat <<EOF | tee /etc/containerd/config.toml
version = 2

[plugins]
  [plugins."io.containerd.grpc.v1.cri"]
    [plugins."io.containerd.grpc.v1.cri".registry]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
        [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
          endpoint = ["https://dockerproxy.com","https://docker.nju.edu.cn","https://docker.mirrors.sjtug.sjtu.edu.cn","https://docker.m.daocloud.io","https://registry-1.docker.io"]
EOF
systemctl daemon-reload && systemctl restart containerd
fi

if hash gem 2>/dev/null; then
  gem sources --add https://gems.ruby-china.com/ --remove https://rubygems.org/
fi

if [ -f "/usr/share/zoneinfo/Asia/Shanghai" ]; then
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
fi
