<!-- source: C:\Users\mukch\projects\work\deepseek-harness\README.zh.md -->
<!-- lines: 1-96 (whole file) -->
<!-- commit: c291e7961a515f6d7af9304e7fd1d257929aef26 -->

<translation>
# DeepSeek Harness

[English](README.md) | 中文

DeepSeek Harness（`dsh`）是由 [DeepSeek AI](https://deepseek.com) 开发的开源智能体框架。

其架构基于 **万物皆插件（everything is a plugin）** 理念，并由 [Cordis](https://github.com/cordiverse/cordis) 驱动；设计细节参见论文 [_A Programming Paradigm for Spatiotemporal Composability_](https://arxiv.org/abs/2608.25512)。

文档：[https://deepseek-harness.github.io/deepseek-harness/](https://deepseek-harness.github.io/deepseek-harness/)

## 开发者预览

DeepSeek Harness 目前处于 _开发者预览（developer preview）_ 阶段，正在快速迭代。**未来将会出现破坏性变更（breaking changes）。**

在运行本项目之前，请阅读[安全须知](SAFETY.zh.md)。

<a id="run"></a>

## 运行

### 通过 `npm` 运行

安装 `Node.js`，然后运行：

```sh
npx @deepseek-ai/dsh web
```

默认情况下，该命令会在 `http://127.0.0.1:3080` 启动 web 界面；在本地启动时，它还会在默认浏览器中打开该页面。通过 SSH 启动时，只会打印主机 URL，因为本地转发地址已被 SSH 客户端或编辑器占用。你可以传入 `--no-open` 来只运行服务端而不打开浏览器。详情参见[web 界面指南](docs/user/guide/index.zh.md)。

<a id="run-from-source"></a>

### 从源代码运行

要从仓库源代码运行：

```sh
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

`pnpm run build` 用于准备仓库的构建产物。`pnpm dsh web` 会直接使用这些已构建好的产物；它不会重新构建它们。

## 社区与支持

- 通过 [GitHub Discussions](https://github.com/deepseek-ai/deepseek-harness/discussions) 提交反馈或错误报告。
- 将 [`dsh-plugin`](https://github.com/topics/dsh-plugin) 主题添加到你的插件仓库，以便被发现。
- 欢迎加入 DeepSeek Harness 企业微信群：扫描二维码添加企业微信助手，并填写入群问卷；完成后，助手会邀请你加入群聊。

<table>
  <thead>
    <tr>
      <th align="center">企业微信助手</th>
      <th align="center">入群问卷</th>
      <th align="center">微信公众号</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><img src="https://cdn.deepseek.com/harness/readme/community-wecom-assistant.png" alt="DeepSeek Harness 企业微信助手二维码" width="180" height="180"></td>
      <td align="center"><a href="https://trtgsjkv6r.feishu.cn/share/base/form/shrcnIt5twSVdLGD52KJBckGCgg"><img src="https://cdn.deepseek.com/harness/readme/community-wecom-survey.png" alt="DeepSeek Harness 入群问卷二维码" width="180" height="180"></a></td>
      <td align="center"><img src="https://cdn.deepseek.com/harness/readme/community-wechat-official-account.png" alt="DeepSeek Harness 团队微信公众号二维码" width="180" height="180"></td>
    </tr>
  </tbody>
</table>

## 贡献

参见 [CONTRIBUTING.md](CONTRIBUTING.zh.md)。

## 开发

请先阅读[开发指南](docs/development.zh.md)和[架构文档](docs/architecture.zh.md)。

对于智能体：请遵循 [AGENTS.md](AGENTS.md)。

## 引用

```bibtex
@misc{deepseek-harness2026,
  title={DeepSeek Harness: Everything is a Plugin},
  author={DeepSeek-AI},
  year={2026},
  publisher={GitHub},
  howpublished={\url{https://github.com/deepseek-ai/deepseek-harness}},
}
```

## 许可证

[MIT](LICENSE)

有关第三方依赖及其许可证的信息，请参见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
</translation>
