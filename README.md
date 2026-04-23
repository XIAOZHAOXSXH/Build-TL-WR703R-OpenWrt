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

`luci-app-easytier` 已内置进固件。

`EasyTier core` 不直接塞进固件，而是编译成独立 `ipk` 一并上传到 Release。原因很直接：`mips` 版 EasyTier 官方二进制体积过大，`8M flash` 下把 `LuCI + luci-app-easytier + easytier core` 全部打进 squashfs 很容易超出镜像上限。

仓库默认做了两件事：

- 固件内置 `luci-app-easytier`
- 首次启动后把 EasyTier 默认程序路径设为 `/tmp/easytier-core` 和 `/tmp/easytier-web`

这样可以先用 LuCI 插件，后续再把核心程序放到：

- `/tmp`
- U 盘
- extroot
- 或直接安装 Release 里的 `easytier.ipk`

## 仓库内容

- [`.config`](./.config)
- [`patches/openwrt/0001-ath79-wr703n-8m64m-and-basic-profile.patch`](./patches/openwrt/0001-ath79-wr703n-8m64m-and-basic-profile.patch)
- [`files/etc/uci-defaults/99-easytier-tmp-path`](./files/etc/uci-defaults/99-easytier-tmp-path)
- [`.github/workflows/build.yml`](./.github/workflows/build.yml)

## 产物

工作流会把以下内容上传到 GitHub Release：

- `wr703n` 固件
- `luci-app-easytier` / `easytier` 相关 `ipk`
- 本地生成并提交的 `.config`
