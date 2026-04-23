# Build TL-WR703N OpenWrt

面向 `TP-Link TL-WR703N` 硬改 `8M Flash + 64M RAM` 的 OpenWrt 云编译仓库。

## 当前核实结果

截至 `2026-04-23`，以下上游当前源码分支都还能找到 `wr703n` 设备定义：

- `OpenWrt`：`master`、`openwrt-24.10`
- `ImmortalWrt`：`master`、`openwrt-24.10`
- `LEDE`：`master`

`Kwrt` 当前 GitHub 仓库不是完整 OpenWrt 源码树，更像编译入口/聚合仓，不适合作为本仓库的上游源码基线。

本仓库最终选择：

- 上游：`OpenWrt openwrt-24.10`
- 机型：`ath79/tiny -> tplink_tl-wr703n`
- 硬改补丁：`8M flash + 64M RAM`
- 插件源：`https://github.com/EasyTier/luci-app-easytier`

## 关于 EasyTier

固件保持原版设备默认包，不内置 `luci-app-easytier`，也不为了塞插件去裁剪原版 profile。

工作流会额外编译这些模块包并上传到 Release：

- `luci-light`
- `luci-app-easytier`
- `easytier`
- `wget-ssl`
- `unzip`

同时会自动把这些包的依赖闭包一起收集上传，方便后续离线安装。

## 仓库内容

- [`.config`](./.config)
- [`patches/openwrt/0001-ath79-wr703n-8m64m.patch`](./patches/openwrt/0001-ath79-wr703n-8m64m.patch)
- [`.github/workflows/build.yml`](./.github/workflows/build.yml)
- [`scripts/collect_release_ipks.py`](./scripts/collect_release_ipks.py)

## 产物

工作流会把以下内容上传到 GitHub Release：

- `wr703n` 固件
- `luci-light`、`luci-app-easytier`、`easytier` 及依赖 `ipk`
- 本地生成并提交的 `.config`
