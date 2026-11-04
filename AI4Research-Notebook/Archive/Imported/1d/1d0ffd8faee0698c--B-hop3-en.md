<!-- source: C:\Users\mukch\projects\work\deepseek-harness\README.zh.md -->
<!-- lines: 1-96 (whole file) -->
<!-- commit: c291e7961a515f6d7af9304e7fd1d257929aef26 -->

<translation>
# DeepSeek Harness

[English](README.md) | Chinese

DeepSeek Harness (`dsh`) is an open-source agent framework developed by [DeepSeek AI](https://deepseek.com).

Its architecture is based on the **everything is a plugin** philosophy, and is driven by [Cordis](https://github.com/cordiverse/cordis); for design details, see the paper [_A Programming Paradigm for Spatiotemporal Composability_](https://arxiv.org/abs/2608.25512).

Documentation: [https://deepseek-harness.github.io/deepseek-harness/](https://deepseek-harness.github.io/deepseek-harness/)

## Developer Preview

DeepSeek Harness is currently in the _developer preview_ stage and is iterating rapidly. **Breaking changes will occur in the future.**

Before running this project, please read the [security notice](SAFETY.zh.md).

<a id="run"></a>

## Running

### Running via `npm`

Install `Node.js`, then run:

```sh
npx @deepseek-ai/dsh web
```

By default, this command starts the web interface at `http://127.0.0.1:3080`; when started locally, it also opens that page in the default browser. When started via SSH, only the host URL is printed, because the local forwarding address is occupied by the SSH client or editor. You can pass `--no-open` to run only the server without opening the browser. For details, see the [web interface guide](docs/user/guide/index.zh.md).

<a id="run-from-source"></a>

### Running from Source

To run from the repository source:

```sh
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install
pnpm run build
pnpm dsh web
```

`pnpm run build` is used to prepare the repository's build artifacts. `pnpm dsh web` uses these already-built artifacts directly; it does not rebuild them.

## Community and Support

- Submit feedback or bug reports via [GitHub Discussions](https://github.com/deepseek-ai/deepseek-harness/discussions).
- Add the [`dsh-plugin`](https://github.com/topics/dsh-plugin) topic to your plugin repository so it can be discovered.
- You are welcome to join the DeepSeek Harness WeCom group: scan the QR code to add the WeCom assistant, and fill out the group entry questionnaire; once done, the assistant will invite you to join the group chat.

<table>
  <thead>
    <tr>
      <th align="center">WeCom Assistant</th>
      <th align="center">Group Entry Questionnaire</th>
      <th align="center">WeChat Official Account</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><img src="https://cdn.deepseek.com/harness/readme/community-wecom-assistant.png" alt="DeepSeek Harness WeCom Assistant QR code" width="180" height="180"></td>
      <td align="center"><a href="https://trtgsjkv6r.feishu.cn/share/base/form/shrcnIt5twSVdLGD52KJBckGCgg"><img src="https://cdn.deepseek.com/harness/readme/community-wecom-survey.png" alt="DeepSeek Harness Group Entry Questionnaire QR code" width="180" height="180"></a></td>
      <td align="center"><img src="https://cdn.deepseek.com/harness/readme/community-wechat-official-account.png" alt="DeepSeek Harness Team WeChat Official Account QR code" width="180" height="180"></td>
    </tr>
  </tbody>
</table>

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.zh.md).

## Development

Please first read the [development guide](docs/development.zh.md) and the [architecture documentation](docs/architecture.zh.md).

For agents: please follow [AGENTS.md](AGENTS.md).

## Citation

```bibtex
@misc{deepseek-harness2026,
  title={DeepSeek Harness: Everything is a Plugin},
  author={DeepSeek-AI},
  year={2026},
  publisher={GitHub},
  howpublished={\url{https://github.com/deepseek-ai/deepseek-harness}},
}
```

## License

[MIT](LICENSE)

For information about third-party dependencies and their licenses, see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
</translation>
