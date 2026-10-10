# 共享组件验收

[English](README.md) | 简体中文

两个 OctoScript 应用使用同一组固定版本的 Rust WebAssembly 组件。组件文件只保存
一份，但每个应用拥有独立的计数器实例和私有笔记。另一个组件通过真正的宿主调用
`runtime.describe` API。所有输入均为测试数据，不需要个人账号、API 密钥、模型
或单独保管的发布者签名密钥。

这是一套验收样例，不是通用笔记编辑器。`SOURCE.json` 记录上游源码和验证工具的
精确版本；`guest/` 包含 Rust 源码及依赖锁定文件，Markdown 渲染由
`pulldown-cmark` 完成。

## 发布与审核

工作流使用 Rust 1.97.1 编译两个组件，从文件中提取 WIT 导入、导出及 BLAKE3
摘要，再把精确摘要写入两个应用的清单。四份 GitHub Actions 来源证明绑定不可变
标签、仓库数字身份、工作流、提交和对象字节。固定版本的 App Hub CLI 验证真实
证明后，才生成发布文件。

推送标签前，必须使用实际模板在隐藏的原生 Makepad 窗口中截图并审核
`templates/first.png`、`templates/second.png`。没有截图，准备步骤会停止；不能
使用不相关的截图。初始标签是 `v0.1.0`，后续发布必须使用新版本，不修改历史文件。

发布文件包含两组 `*.component.json` / `*.wasm` 和两个
`*.bundle.pack.json`。提交 App Hub issue 时提供仓库、不可变标签和提交，以及
发布文件。组件依赖必须结合经过验证的目录检查；发布者回执不代表目录发布或
运行验收已经完成。

App Hub 管理员审核全部文件，基于当前可信目录准备同时包含组件和应用的候选，
再通过现有目录工作流执行 `dry_run: true`。得到的真实签名目录可以放在隔离的
本地镜像中安装，不必把测试应用加入公开商店。演练仍要求候选提交已审核并进入
App Hub main，而且通过受保护的管理员环境。假证明或测试验证器不能替代来源
证明和管理员目录证明。

## 运行验收

使用支持 `wasm-shared-components-v1` 的干净构建和全新的应用数据目录，通过
正常商店从验证过的本地镜像安装两个应用。生产流程验收不能切换到旧密钥目录。

1. 分别调用两个应用的 `first.inspect` / `second.inspect`，检查原始宿主响应。
2. 每个应用初次返回计数 1、2，再次返回 3、4；另一个应用的计数不受影响。
3. 初次 `before_write` 因文件尚不存在而失败；`read_back` 包含该应用自己的名称。
4. Markdown 渲染正确；`wasm.functions` 列出 `md.*` 和 `bridge.call` 及精确组件信息。
5. `bridge.call` 经正常宿主分发调用 `runtime.describe`，返回已实现 API 的描述。
6. 两个应用共享 `.components` 中的只读文件，每个摘要仅一份。

先在隐藏的 Makepad 窗口验证桌面端，最后测试指定 Android 手机。使用全新的
`dev.makepad.octosense.hostapilab.*` 包和合成测试数据，不能替换用户的 Home。
OctoSense 现有 `wasm-phone-smoke` 只验证核心模块 ABI，不能单独证明本共享组件
发布流程。

准备源码不等于完成发布、目录证明、截图或运行验收。需要另行记录实测结果，以及
源码、运行时、APK 和发布文件的摘要。
