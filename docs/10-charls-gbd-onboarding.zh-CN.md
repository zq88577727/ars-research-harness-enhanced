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
- `examples/charls-aging-template/variable_map.csv`
- `examples/charls-aging-template/checkpoints/stage-S0-intake.md`
- `examples/charls-aging-template/checkpoints/stage-S1-research-question.md`
- `examples/charls-aging-template/checkpoints/stage-S2-method-plan.md`

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
python3 harness/validators/validate_project_scaffold.py examples/gbd-burden-template
```

