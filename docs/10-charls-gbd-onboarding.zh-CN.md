# CHARLS 与 GBD 接入指南

本项目已经支持 NHANES 完整示例，并为 CHARLS 与 GBD 提供了合规接入脚手架。

## 原则

1. 不把受限原始数据提交到 GitHub。
2. 所有原始数据放入 `.gitignore` 保护目录。
3. 每个研究项目必须先完成 S0/S1/S2，再执行分析和写作。
4. 任何正文结论都必须能追溯到结果文件、变量映射和 claim registry。

## CHARLS

适用场景：

- 中国中老年人群慢病、功能、衰弱、认知、养老、医疗利用、社会经济因素研究。
- 纵向队列分析、单波次横断面分析、轨迹/转归分析。

推荐原始数据位置：

```text
data/charls/raw/<wave-or-release>/
```

初始化项目：

```bash
python3 harness/scripts/init_public_database_project.py charls charls-aging-template \
  --title "CHARLS aging public-database manuscript template" \
  --research-question "To be refined after CHARLS wave access and variable mapping."
```

下一步必须人工填写：

- `examples/charls-aging-template/project_manifest.json`
- `examples/charls-aging-template/charls_file_manifest.csv`
- `examples/charls-aging-template/charls_wave_map.csv`
- `examples/charls-aging-template/variable_map.csv`
- `examples/charls-aging-template/charls_design_gate.json`
- `examples/charls-aging-template/charls_codebook_extract.csv`
- `examples/charls-aging-template/charls_s1_s2_design_review.md`
- `examples/charls-aging-template/charls_variable_mapping_decisions.json`
- `examples/charls-aging-template/checkpoints/stage-S0-intake.md`
- `examples/charls-aging-template/checkpoints/stage-S1-research-question.md`
- `examples/charls-aging-template/checkpoints/stage-S2-method-plan.md`

`charls_file_manifest.csv` 只记录本地文件清单和访问状态，不提交原始数据。
当 `project_manifest.json` 中的 `rawFilesDownloaded` 仍为 `false` 时，
validator 只检查清单结构、必需波次和路径边界；当设为 `true` 后，必需行
必须指向 `data/charls/raw/` 下真实存在的本地文件。

CHARLS 本地受限数据 dry-run：

```bash
python3 harness/validators/validate_charls_local_dry_run.py
```

默认模式不会读取 `.dta`、`.sav`、`.sas7bdat`、CSV 或压缩包内容，只验证：

- `project_manifest.json` 是否声明 CHARLS、本地原始数据目录和禁止入库策略；
- `charls_file_manifest.csv` 是否包含必需列、至少两个纵向必需波次、路径边界和合法访问状态；
- `charls_wave_map.csv` 是否把波次标记为 baseline/follow-up、说明时间锚点、文件标签、linkage key 状态、权重决策和 attrition 角色；
- `variable_map.csv` 是否包含 respondent/person ID、wave、baseline/follow-up wave、age、sex、exposure、outcome、attrition status；
- required 变量是否填写语义字段：`semantic_status`、`construct`、`measurement_domain`、`measurement_type`、`wave_role`、`time_anchor`、`coding_decision`、`missingness_decision`、`interpretation_boundary`；
- 已标记为 `downloaded_local` 的文件是否存在，若填写 `checksum_sha256` 是否匹配；
- `data/charls/raw/` 下是否误提交受限原始数据。

准备进入真实分析前运行严格模式：

```bash
python3 harness/validators/validate_charls_local_dry_run.py --require-local-data
```

严格模式会要求最小纵向分析所需的本地文件已经就绪；当前模板在未下载数据时应返回
`awaiting-local-data`，而不是被解释为完整 CHARLS 分析实例。

`variable_map.csv` 必须至少明确 respondent/person ID、wave、baseline wave、
follow-up wave、age、sex、primary exposure、primary outcome、attrition status。
在仅有脚手架时，`source_variable` 可以暂时保留为 `TBD_after_codebook_review`，
但 `semantic_status` 应为 `planned`，并且必须先写清构念、时间定位、编码决策、
缺失处理和解释边界。准备进入真实分析前，required 变量必须从 `planned` 升级为
`mapped` 或 `derived`，并替换为真实 CHARLS codebook 变量名。

`charls_wave_map.csv` 是波次语义层，不替代 `charls_file_manifest.csv`。前者说明
2011、2013 等波次在研究设计中的 baseline/follow-up 角色、时间锚点、权重决策和
attrition 角色；后者说明本地文件路径、下载状态和 checksum。两者必须一致。
纵向研究不能因为有先后波次就自动写成因果结论，必须在 S2 说明时序、样本流失、
缺失、权重和波次链接策略。

CHARLS S1/S2 研究设计门禁：

```bash
python3 harness/validators/validate_charls_design_gate.py
```

`charls_design_gate.json` 把 `variable_map.csv` 和 `charls_wave_map.csv` 继续接到
研究问题、估计目标、暴露/结局时间顺序、attrition plan、weight decision 和
claim-language boundary。默认模式允许 scaffold 通过，但会返回
`s1-s2-design-pending`，提示哪些 S1/S2 决策尚未关闭。它检查：

- 研究问题中的 exposure/outcome 是否存在于变量语义表；
- baseline/follow-up 波次是否存在于波次语义表，且角色正确；
- exposure 是否定位在 baseline，outcome 是否定位在 follow-up；
- attrition status 和 sample weight 是否连接到 S2 处理计划；
- 是否存在 `no-causal-language` 边界，防止把观察性关联写成因果结论。

准备进入真实 CHARLS 分析前运行严格模式：

```bash
python3 harness/validators/validate_charls_design_gate.py --require-ready
```

严格模式要求 `charls_design_gate.json` 的 `status` 为 `ready-for-analysis`，
研究问题和 estimand 不再是占位文本，exposure/outcome/attrition 已经映射到真实
CHARLS source variables 或明确 derived variables，且 weight decision 不再是
`pending_weight_decision`。未满足这些条件时，即使本地文件存在，也不应进入真实分析或
撰写结果性结论。

CHARLS S1/S2 项目实例化助手：

```bash
python3 harness/scripts/prepare_charls_design_gate_instance.py
python3 harness/scripts/prepare_charls_design_gate_instance.py --dry-run
```

`charls_codebook_extract.csv` 是从官方 CHARLS questionnaire/codebook 中摘录的
变量级元数据表，只能包含变量名、标签、模块、波次、构念关键词、测量域、测量类型、
可承担的分析角色等 codebook 级信息，不得包含任何 respondent-level 原始数据。

默认命令会生成 `charls_s1_s2_design_review.md`，把 S1/S2 design gate 的目标变量
逐个连接到 codebook extract 中的候选 source variables，并标注仍需人工确认的动作。
该 worksheet 不会自动修改 `variable_map.csv`，也不会把 `charls_design_gate.json`
改为 `ready-for-analysis`。CI 使用 `--dry-run`，只检查实例化助手可运行且输入结构可读。

CHARLS codebook extract 到 variable map 的人工决策闭环：

```bash
python3 harness/scripts/apply_charls_variable_mapping_decisions.py --dry-run
python3 harness/scripts/apply_charls_variable_mapping_decisions.py
python3 harness/scripts/apply_charls_variable_mapping_decisions.py --require-reviewed --update-variable-map
```

`charls_variable_mapping_decisions.json` 记录人工复核后的变量映射决定。允许的状态包括
`pending`、`map_source`、`derive`、`defer` 和 `reject_candidate`。默认 scaffold 中
所有核心变量保持 `pending`，因此普通 dry-run 可以通过，但 `--require-reviewed` 会阻断。

普通运行会生成 `variable_map.review_draft.csv`，供人工比较和复核；它不会覆盖
`variable_map.csv`。只有在所有必需变量完成审核、且明确传入
`--require-reviewed --update-variable-map` 时，脚本才允许更新正式变量语义表。正式更新前
必须确认 source variable、wave/file、coding decision、missingness decision 和
interpretation boundary 均来自官方 CHARLS 文档。

CHARLS 重点风险：

- 波次链接和样本流失。
- 权重使用和目标总体定义。
- 生物标志物、问卷变量、随访变量版本差异。
- 数据使用条款和引用要求。

## GBD

适用场景：

- 疾病负担趋势分析。
- 国家/地区比较。
- 年龄、性别、病因、风险因素分层。
- DALYs、Deaths、YLLs、YLDs、Prevalence、Incidence 等指标分析。

推荐原始导出位置：

```text
data/gbd/raw/<gbd-release>/
```

初始化项目：

```bash
python3 harness/scripts/init_public_database_project.py gbd gbd-burden-template \
  --title "GBD burden public-database manuscript template" \
  --research-question "To be refined after GBD query export and metric selection."
```

下一步必须人工填写：

- `examples/gbd-burden-template/project_manifest.json`
- `examples/gbd-burden-template/gbd_query_manifest.csv`
- `examples/gbd-burden-template/checkpoints/stage-S0-intake.md`
- `examples/gbd-burden-template/checkpoints/stage-S1-research-question.md`
- `examples/gbd-burden-template/checkpoints/stage-S2-method-plan.md`

GBD 重点风险：

- GBD release 版本必须记录。
- measure、metric、cause、location、age、sex、year 必须与导出文件一致。
- rate、count、percent 不能混写。
- uncertainty interval 必须保留并解释。
- 不能把 GBD 描述性趋势写成个体层面因果结论。

## 验证

运行全部本地验证：

```bash
python3 harness/scripts/run_all_validations.py
```

验证单个项目壳：

```bash
python3 harness/validators/validate_project_scaffold.py examples/charls-aging-template
python3 harness/validators/validate_charls_design_gate.py
python3 harness/scripts/prepare_charls_design_gate_instance.py --dry-run
python3 harness/scripts/apply_charls_variable_mapping_decisions.py --dry-run
python3 harness/validators/validate_charls_local_dry_run.py
python3 harness/validators/validate_project_scaffold.py examples/gbd-burden-template
```
