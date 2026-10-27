# 配套技能上游与按需安装

本页连接本主技能使用的专业能力与其真实公开上游，供其他使用者按任务安装。**不捆绑第三方代码，不自动安装，不把来源核查当作运行验证。** 2026-10-27按下列固定提交读取上游README、技能入口及许可；安装时还要核上游当前说明、目标客户端和本机条件。

## 先按任务选，再决定安装

从[能力导航](tool-routing.md)选当前需要的能力，优先使用已经可用且合适的工具。只有缺能力且任务需要时，确认目标位置、版本、许可、依赖与权限再安装；不要为了使用主技能整套装齐。

仓库链接用于找上游，**固定提交链接用于定位本文依据**，不是“永远锁旧版”的建议。上游默认安装命令可能跟随当前分支或标签，不等于安装下列固定提交；需要复现时检出明确提交，按上游说明放置对应技能目录及其必要配套文件，并记录实际版本。新版本先在隔离环境检查兼容性，不静默覆盖已有技能或共享依赖。

## 16个专业技能

| 本项目识别名 | 什么时候需要 | 上游仓库与固定技能目录 | 许可与依赖提示 |
| --- | --- | --- | --- |
| `cad` | 参数化实体、导出STEP/STL与保存后量测 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/2f793659fb7bab537e2f00836e06448fc4087cb2/skills/cad) | MIT；固定入口使用uv、Python 3.13、cadgen 0.7.26 |
| `bambu-labs` | 交接Bambu打印应用，由用户选机并开始 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/bambu-labs) | MIT；Bambu Connect/Studio，平台支持以当前上游为准 |
| `dfam-check` | 壁厚、悬垂、支撑与朝向分析 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/dfam-check) | MIT；Python及本技能requirements；抽样/漏测不等于合格 |
| `dfm` | CNC、钣金、注塑可制造性评审 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/dfm) | MIT；测量脚本另需Python依赖，评审不必都运行脚本 |
| `dxf` | 二维轮廓、模板与DXF导出 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/dxf) | MIT；uv、Python 3.13、cadgen 0.7.20；快照另需浏览器 |
| `engineering-drawing` | 真实几何的投影、尺寸与工程图PDF | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/engineering-drawing) | MIT；uv、Python 3.13、cadgen 0.7.20；PDF需matplotlib |
| `gcode` | OrcaSlicer切片及预设选择 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/gcode) | MIT；OrcaSlicer，预设辅助脚本用Python 3；不连接打印机 |
| `sdf` | SDFormat模型/世界与仿真交接 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/sdf) | MIT；cadgen 0.7.20路线，模拟器另核；不是signed-distance-field |
| `sendcutsend` | 指定SendCutSend服务的上传前评审 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/sendcutsend) | MIT；几何工具按需；检查不授权上传、报价或下单 |
| `srdf` | MoveIt规划语义、分组和碰撞配置 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/srdf) | MIT；需真实URDF；cadgen 0.7.20，MoveIt运行另核 |
| `step-parts` | 查找可采购标准件并下载STEP | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/step-parts) | MIT；在线api.step.parts，核查询外传与下载范围 |
| `urdf` | 机器人结构、关节、惯量和网格引用 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) · [固定目录](https://github.com/earthtojake/text-to-cad/tree/b48ff49e00968ac07af08572b0595483dae07c85/skills/urdf) | MIT；cadgen 0.7.20，check_urdf等工具按环境核验 |
| `answer-me-with-html` | 按需HTML讲解与复杂方案评审 | [QingYunA/answer-me-with-html](https://github.com/QingYunA/answer-me-with-html) · [固定目录](https://github.com/QingYunA/answer-me-with-html/tree/533c39fd47d814a6bee3d9c1df388345f4e4c858/skills/answer-me-with-html) | MIT；Node.js 20+；基础HTML不要求视频依赖 |
| `bambu-studio-ai` | 本地Bambu预设查询与CLI切片等 | [heyixuan2/bambu-studio-ai](https://github.com/heyixuan2/bambu-studio-ai) · [固定目录](https://github.com/heyixuan2/bambu-studio-ai/tree/cdc26987d5bf1052a055d9403e3cb9630959dd08) | 自有代码MIT，部分派生数据AGPL-3.0；Python 3.10+、Bambu Studio |
| `flowful-cad` | 指定Flowful CadQuery/GridfinityBin等 | [flowful-ai/cad-skill](https://github.com/flowful-ai/cad-skill) · [固定目录](https://github.com/flowful-ai/cad-skill/tree/fe4215970d39f388ff1afc411fac49a9c5f79756) | 上游名parametric-3d-printing；PolyForm Noncommercial 1.0.0；Python 3.10–3.12及依赖 |
| `openscad` | OpenSCAD参数化源、导出与STL重建 | [andreahaku/openscad_claude_skill](https://github.com/andreahaku/openscad_claude_skill) · [固定目录](https://github.com/andreahaku/openscad_claude_skill/tree/3483e23dd4c5b41144ba69dac13d7b56ecdf0c0c) | README声明MIT，根目录缺独立LICENSE正文；OpenSCAD CLI/Bash，重建另需Python包 |

固定目录都包含 `SKILL.md`；路径为 `skills/<技能名>` 的项目不把整个仓库根目录误当单个技能。`flowful-cad` 是本地识别别名，上游实际技能名为 **`parametric-3d-printing`**；按实际发现的名字和入口读取，不必为了名字一致改写上游或假定两份技能已安装。

### 一：text-to-cad 的 CAD 与11个配套入口

- [CAD版本README](https://github.com/earthtojake/text-to-cad/blob/2f793659fb7bab537e2f00836e06448fc4087cb2/README.md) · [配套版本README](https://github.com/earthtojake/text-to-cad/blob/b48ff49e00968ac07af08572b0595483dae07c85/README.md) · [许可](https://github.com/earthtojake/text-to-cad/blob/b48ff49e00968ac07af08572b0595483dae07c85/LICENSE)。
- 上游文档提供 `npx skills add earthtojake/text-to-cad#latest` 及多个客户端的插件安装方式；这是上游安装入口说明，**本页未执行，也不保证只装一项或复现固定版本**。按上游安装器实际选项选择所需技能，不编造未核实的选择参数。
- 本页CAD来源的 `cadgen==0.7.26` 与配套入口中部分使用的 `cadgen==0.7.20` **不是已验证同一运行栈**。分别核uv、Python、CAD依赖及导出/渲染工具；技能文件可发现不代表这些运行条件已满足。
- `bambu-labs` 的应用交接不等于自动开始打印；`gcode` 切片不连接打印机。机器人相关静态文件验证不等于Gazebo/MoveIt/实体执行通过。

### 二：HTML表达

[answer-me-with-html固定README](https://github.com/QingYunA/answer-me-with-html/blob/533c39fd47d814a6bee3d9c1df388345f4e4c858/README.md) · [MIT许可](https://github.com/QingYunA/answer-me-with-html/blob/533c39fd47d814a6bee3d9c1df388345f4e4c858/LICENSE)。上游提供 `npx skills add QingYunA/answer-me-with-html`、Claude插件及手动放置 `skills/answer-me-with-html` 的方式。需Node.js 20+，已打包的基础CLI不需要额外 `npm install`；MP4等扩展功能另查依赖。按需使用，不启用常驻HTML输出或自动服务。

### 三：Bambu Studio能力

[bambu-studio-ai固定README](https://github.com/heyixuan2/bambu-studio-ai/blob/cdc26987d5bf1052a055d9403e3cb9630959dd08/README.md) · [MIT许可](https://github.com/heyixuan2/bambu-studio-ai/blob/cdc26987d5bf1052a055d9403e3cb9630959dd08/LICENSE) · [第三方通知](https://github.com/heyixuan2/bambu-studio-ai/blob/cdc26987d5bf1052a055d9403e3cb9630959dd08/THIRD_PARTY_NOTICES.md)。上游提供 `npx skills add heyixuan2/bambu-studio-ai` 或将根目录作为技能包克隆；Python 3.10+及requirements用于脚本，切片需实际Bambu Studio。

上游还包含生成、渲染、修复、分色、联网和设备相关入口；**本主技能的现有集成不等于这些功能全部经过验证或授权**。Blender、AI provider和打印机连接按选择的功能逐项核验；部分Bambu Studio派生数据保留AGPL-3.0，不能整仓概称MIT。

### 四：Flowful / CadQuery

[Flowful固定README](https://github.com/flowful-ai/cad-skill/blob/fe4215970d39f388ff1afc411fac49a9c5f79756/README.md) · [许可](https://github.com/flowful-ai/cad-skill/blob/fe4215970d39f388ff1afc411fac49a9c5f79756/LICENSE)。上游示例把仓库根目录克隆为 `~/.claude/skills/parametric-3d-printing`；这是其客户端示例，不是所有CLI的通用安装路径。需要Python 3.10–3.12、独立环境及requirements中的CadQuery等依赖。

**PolyForm Noncommercial 1.0.0包含非商业限制**，采用前核完整许可与实际用途。用户明确选择该工具包或其特定API时再使用，不因普通CAD/Gridfinity任务自动替换已有路线。

### 五：OpenSCAD

[OpenSCAD固定README](https://github.com/andreahaku/openscad_claude_skill/blob/3483e23dd4c5b41144ba69dac13d7b56ecdf0c0c/README.md)。上游示例克隆到 `~/.claude/skills/openscad`，或克隆后建立符号链接；其他客户端按其发现机制安置。需可调用的OpenSCAD CLI与Bash；Reconstruct/Replicate另需trimesh、numpy、scipy、rtree、shapely等Python依赖。

固定README写有 `License: MIT`，但该提交根目录没有独立LICENSE正文；本页准确保留这一证据状态，复制或再分发前向上游确认完整许可与署名要求，不能从公开可读推导无限制授权。

## 项目管理与Jev：另外核实当前入口

`linear-flow`、`linear-cli`、`jev-sidekick` 和 `jev_evaluate` 是可选协作入口，不属于上表16个项目专业技能的捆绑内容。

- `linear-flow`：本次未能公开访问候选 `Loveacup/linear-flow`（404不能区分不存在或私有），因此不提供虚构下载地址。已具备它的环境可读取；没有它仍可按[项目管理与本地后备](project-organization.md#项目管理接入与本地后备)推进，不因此安装未知同名包。
- Linear操作可参考已知公开的 [schpet/linear-cli](https://github.com/schpet/linear-cli) 及 [Linear官方API](https://linear.app/developers/graphql)。操作工具与协作方法不是同一个skill；安装命令、认证及写入范围由所选入口核验，本次不代安装或提供凭据。
- `jev-sidekick`/`jev_evaluate`：没有已核实的独立公共安装源，不编造仓库。Jev产品及API见 [TypeSafe官方文档](https://docs.typesafe.ai/)，本文的有界工具契约是当前集成方式，不等于每个客户端自带。没有封装时由主模型继续，新增API集成、服务费用或数据外传另行确认。

## 安装后验证与升级

核对实际skill名、目录、提交/版本和许可；再验证客户端能发现、依赖可执行、一个与任务相关的最小产物可生成且能独立读回。高风险动作如模型上传、安装额外服务、购买或打印另核授权，不靠安装成功推导权限。

本地适配可能改过名字、触发条件、路径、版本锁定、遥测/更新、viewer或设备动作。本目录不分发这些本机适配，也不声称上游原样安装带有同样保护。需要上游代码时直接在其许可下按所选入口取得；更新后重核受影响能力、记录不兼容项，并保留原版本回退位置。

发现上游链接、许可、接口或行为变化，按[每次使用的知识循环](closeout.md)查重记录。通用问题写回主技能；上游自身缺陷保留准确来源与版本；未经真实运行不要标记为已集成通过。
