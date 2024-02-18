# This is replaced during release process.
__version_suffix__ = '186'

APP_NAME = "zalando-kubectl"

KUBECTL_VERSION = "v1.25.16"
KUBECTL_SHA512 = {
    "linux": "887be87d9565ccabde80b92988318ee940d3732e07ebc028a57dda61289fa576760806bc8796fa7a8c41509f8379d3491c30dd2c5a13dca7a56d1fc4ece2aa1e",
    "darwin": "3ed350e314cc287afa5f985b2f350948c6a2b38250d6cda78d5638833f3d2c20ed434a6eef014d1ce8bed9b3fe6f5be1e6a3f0d9b1fb20ba195f5b686b6610a3",
}
STERN_VERSION = "1.26.0"
STERN_SHA256 = {
    "linux": "de79474d9197582e38da0dccc8cd14af23d6b52b72bee06b62943c19ab95125e",
    "darwin": "f89631ea73659e1db4e9d8ef94c58cd2c4e92d595e5d2b7be9184f86e755ee95",
}
KUBELOGIN_VERSION = "v1.28.0"
KUBELOGIN_SHA256 = {
    "linux": "83282148fcc70ee32b46edb600c7e4232cbad02a56de6dc17e43e843fa55e89e",
    "darwin": "8169c6e85174a910f256cf21f08c4243a4fb54cd03a44e61b45129457219e646",
}
ZALANDO_AWS_CLI_VERSION = "0.4.3"
ZALANDO_AWS_CLI_SHA256 = {
    "linux": "bf0c32087985629c8694f4153230cbb7d627ae1794a942752f5cd1d76e118bf4",
    "darwin": "725d7262fb6c8e8705e1c3b59b53ccd78a59e9361711dc584b401d88cfd3fa69",
}

APP_VERSION = KUBECTL_VERSION + "." + __version_suffix__
