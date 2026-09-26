# 阶段 1 · 第 2 课：CSS 基础与 Flexbox

目标：给主页加上样式表，掌握盒模型、选择器、Flex 布局。时长约 2 小时。

---

## 1. CSS 三种引入方式

| 方式    | 写法                                    | 用不用    |
| ----- | ------------------------------------- | ------ |
| 外部文件  | `<link rel="stylesheet" href="style.css" />` | ✅ 项目唯一选择 |
| 内部样式  | `<style>` 写在 head                      | 仅单页临时 demo |
| 行内样式  | `<p style="color:red">`                | ❌ 难维护，禁止 |

理由：HTML 管结构、CSS 管外观，分离后才能改一处换全站。

---

## 2. 盒模型（必须刻进脑子）

每个元素都是一个盒子，由内到外：`content → padding → border → margin`

```css
*, *::before, *::after { box-sizing: border-box; }   /* 几乎每个项目的第一行 */
```

| 值             | 含义                            |
| ------------- | ----------------------------- |
| `content-box` | 默认值：设 width=200，实际宽度还要加 padding+border |
| `border-box`  | width=200 就是最终宽度，padding 往内挤  |

不写 `border-box` 的后果：加了 padding 就撑破布局，这是新手布局错乱的第一原因。

---

## 3. 选择器与优先级

| 选择器            | 示例                   | 说明       |
| -------------- | -------------------- | -------- |
| 元素             | `p { }`              | 所有 `<p>` |
| 类              | `.section { }`       | 最常用     |
| id             | `#about { }`         | 唯一元素    |
| 后代             | `.site-nav a { }`    | 导航里的链接  |
| 伪类             | `a:hover { }`        | 鼠标悬停状态  |

冲突时优先级：`!important` > 行内 > id > 类 > 元素 > 继承。
**不要靠 `!important` 解决冲突** —— 写更具体的选择器才是正解。

---

## 4. 单位

| 单位    | 含义                            | 用途       |
| ----- | ----------------------------- | -------- |
| `px`  | 固定像素                          | 边框、小间距   |
| `rem` | 相对根字号（1rem=16px）              | 字号、大间距   |
| `%`   | 相对父元素                         | 宽度自适应    |
| `vh`  | 视口高度的 1%                      | 整屏区块     |
| `fr`  | Grid 剩余空间份额（第 3 课）             | 栅格       |

---

## 5. Flexbox（重点）

给**父元素**加 `display: flex`，它就变成弹性容器，子元素自动排成一行。

容器属性：

| 属性                | 作用                          |
| ----------------- | --------------------------- |
| `display: flex`   | 开启弹性布局                      |
| `flex-direction`  | `row`（默认横排）/ `column`（竖排）   |
| `justify-content` | **主轴**对齐：`center` / `space-between` / `flex-start` |
| `align-items`     | **交叉轴**对齐：`center` / `stretch` / `flex-start` |
| `gap`             | 子元素间距（比 margin 干净得多）         |
| `flex-wrap`       | `wrap` 允许换行（做响应式常用）          |

子项属性：`flex: 1` = 占满剩余空间；`flex: 0 0 200px` = 固定 200px 不伸缩。

记忆口诀：**横向看 justify，纵向看 align**。`flex-direction: column` 时两者含义对调。

居中三连：

```css
display: flex;
justify-content: center;   /* 水平居中 */
align-items: center;       /* 垂直居中 */
```

---

## 6. CSS 变量

```css
:root { --color-accent: #0969da; }   /* 定义 */
a { color: var(--color-accent); }     /* 使用 */
```

改一次换全站配色。项目的配色、间距、圆角都应该收敛到变量里。

---

## 7. 本次改动对照

| 文件改动                                            | 效果              |
| ----------------------------------------------- | --------------- |
| `<link rel="stylesheet" href="style.css" />`    | HTML 与 CSS 建立连接 |
| `:root` 定义配色/间距/圆角变量                            | 全站统一，改一处生效      |
| `*{box-sizing:border-box}`                       | 消除 padding 撑破布局 |
| `.container { max-width:760px; margin:0 auto }`  | 内容居中并限宽（阅读更舒适）  |
| `.site-nav ul { display:flex; gap:24px }`        | 导航由竖排变横排        |
| `.section { padding/border/radius }`             | 区块卡片化           |
| `table { border-collapse:collapse }`             | 去掉表格双线          |

---

## 8. 调试方法

| 方法                     | 用途                     |
| ---------------------- | ---------------------- |
| F12 → 元素面板              | 点任意元素看它命中了哪条 CSS      |
| F12 → 勾选/取消样式           | 实时试效果                |
| `border: 1px solid red` | "边框大法"：看不清盒子边界时临时加边框 |
| 改了没生效                  | 先 Ctrl+F5，再看选择器有没有命中  |

---

## 9. 作业

1. 把 `--color-accent` 换成你自己喜欢的颜色，观察全站链接与 hover 一起变化（体验变量的价值）。
2. 给页脚加 `display:flex; justify-content:space-between`，做「左边版权 + 右边 GitHub 链接」的两端对齐。
3. 去掉 `box-sizing: border-box` 看布局怎么崩，再加回来 —— **亲手体验一次比看十遍记得牢**。

下一课：Grid 布局 + 响应式（媒体查询），让页面在手机上也能看，然后部署上线。
