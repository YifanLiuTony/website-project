# Sunfly 项目 Codex 提示词

你正在维护 Sunfly 建材营销网站。当前仓库文件是事实来源，修改前先检查相关代码。

## 必须遵守

1. 每次修改前先运行 `git fetch origin` 和 `git status --short --branch`；如果远程有更新，先同步再编辑。
2. `zkya/` 是另一个项目，严禁修改、删除、格式化、生成、暂存或提交其中任何文件，搜索和批量操作也必须排除它。
3. 保留用户已有及无关改动，只处理当前任务范围。
4. 用户明确要求提交或推送时，只提交本次任务改动，并直接推送到 `origin/main`。

## 项目要点

- 网站主要使用静态 HTML、CSS 和 JavaScript。
- 核心文件：`index.html`、`js/main.js`、`js/translations.js`。
- 公开品牌必须是 Sunfly，不得显示 Parete 品牌。
- 不得在公开页面展示价格、MOQ、包装、生产、交付、付款或供应条款。
- 网站支持英文、繁体中文/香港和简体中文；可见文字修改必须检查三种语言。
- 公司电话：`+852 2388 6056`，链接：`tel:+85223886056`。
- 公司邮箱：`info@sunfly.hk`。

## 产品页流程

- 产品源数据：`parete-scrape/products.json`。
- 源图片：`parete-scrape/images/`。
- 生成器：`tools/build_products.py`。
- 生成页面：`products/`；镜像图片：`assets/products/`。
- 修改产品页时先改源数据或生成器，再重新生成，不要只改生成后的 HTML。
- 图片清理先改 `parete-scrape/images/`，再同步到 `assets/products/`。
- 生成器缺少依赖时运行 `python -m pip install opencc`。
- 构建时使用当前仓库路径：

```powershell
python tools/build_products.py --site-root <repo-root> --skip-images
```

## 验证

- 页面布局改动要在浏览器检查桌面和手机尺寸。
- 产品生成器改动要运行对应构建。
- 提交前检查旧值残留，并运行 `git diff --check`。
- 无法验证时，明确说明阻碍和下一步检查方法。


## 公司名称（用户于2026年9月5日确认）
- 正式中文名：香港沈飛材料科技有限公司
- 正式英文名：SUNFLY MATERIALS TECHNOLOGY (HONG KONG) CO., LIMITED
- 简体页面显示：香港沈飞材料科技有限公司
- 公司介绍、页脚及结构化公司资料使用上述对应名称。
