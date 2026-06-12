# Candidate Claim Registry Review

This worksheet is a human review queue, not an automatically approved claim registry.
For each candidate, confirm the exact source file, source fields, expected rendered text,
tier, interpretation boundary, and whether the sentence should be registered at all.

## Review Rules

- Core: primary outcome, main model estimate, key denominator, or mandatory interpretation boundary.
- Supporting: sensitivity analysis, secondary estimate, or derived traceability check.
- Background: numeric literature, guideline, or context statement that needs citation but is not a study result.
- Do not register a claim until the exact source artifact and interpretation boundary are known.

Candidate file: `harness/claims/nhanes_candidate_claims.json`
Machine-readable decisions: `harness/claims/nhanes_candidate_claim_decisions.json`
Total candidates: `40`
Needs human review: `28`

## Decision Workflow

1. Keep a candidate as `pending` until a human reviewer confirms source artifact, source fields, tier, and interpretation boundary.
2. Change the decision to `register`, `reject`, `defer`, or `merge` in the machine-readable decisions file.
3. Run `python3 harness/scripts/apply_claim_review_decisions.py` to produce registry additions for approved `register` decisions.
4. Copy approved additions into the claim registry only after a second review of source traceability.

## Registry Drafts

### nhanes-candidate-001

- Suggested tier: `core`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> This study estimated the weighted prevalence of HbA1c-defined undiagnosed diabetes among self-reported non-diabetic U.S. adults and examined demographic, anthropometric, cardiometabolic, and lifestyle correlates using National Health and Nutrition Examination Survey (NHANES) 2017-2018 data.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-001",
  "tier": "core",
  "type": "numeric-claim",
  "expectedText": "This study estimated the weighted prevalence of HbA1c-defined undiagnosed diabetes among self-reported non-diabetic U.S. adults and examined demographic, anthropometric, cardiometabolic, and lifestyle correlates using National Health and Nutrition Examination Survey (NHANES) 2017-2018 data.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-002

- Suggested tier: `core`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> This cross-sectional study used public-use NHANES 2017-2018 interview, examination, and laboratory files.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-002",
  "tier": "core",
  "type": "numeric-claim",
  "expectedText": "This cross-sectional study used public-use NHANES 2017-2018 interview, examination, and laboratory files.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-003

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> Adults aged 20 years or older who self-reported no prior diabetes diagnosis and had available HbA1c data were included.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-003",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "Adults aged 20 years or older who self-reported no prior diabetes diagnosis and had available HbA1c data were included.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-006

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> A fasting-subsample sensitivity definition used HbA1c >=6.5% or fasting plasma glucose >=126 mg/dL.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-006",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "A fasting-subsample sensitivity definition used HbA1c >=6.5% or fasting plasma glucose >=126 mg/dL.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-007

- Suggested tier: `core`
- Type: `sample-size`
- Interpretation boundary needed: `True`

Sentence:

> The final analytic sample included 4,004 self-reported non-diabetic adults with available HbA1c data after excluding pregnant participants.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-007",
  "tier": "core",
  "type": "sample-size",
  "expectedText": "The final analytic sample included 4,004 self-reported non-diabetic adults with available HbA1c data after excluding pregnant participants.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-014

- Suggested tier: `core`
- Type: `prevalence-or-percentage`
- Interpretation boundary needed: `True`

Sentence:

> Among self-reported non-diabetic U.S. adults in NHANES 2017-2018, HbA1c-defined undiagnosed diabetes was present in approximately 2% of the weighted population and was patterned by obesity, waist circumference, non-HDL cholesterol, and race/ethnicity.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-014",
  "tier": "core",
  "type": "prevalence-or-percentage",
  "expectedText": "Among self-reported non-diabetic U.S. adults in NHANES 2017-2018, HbA1c-defined undiagnosed diabetes was present in approximately 2% of the weighted population and was patterned by obesity, waist circumference, non-HDL cholesterol, and race/ethnicity.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-017

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> Self-reported diabetes status is useful in population surveys, but it cannot fully capture glycemic abnormalities in people who have not been tested, have not received results, or do not recall a prior diagnosis.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-017",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "Self-reported diabetes status is useful in population surveys, but it cannot fully capture glycemic abnormalities in people who have not been tested, have not received results, or do not recall a prior diagnosis.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-019

- Suggested tier: `core`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> The National Institute of Diabetes and Digestive and Kidney Diseases similarly emphasizes that abnormal A1C results used for diagnosis usually require confirmation with a second measurement [6].

Draft registry object:

```json
{
  "id": "nhanes-reviewed-019",
  "tier": "core",
  "type": "numeric-claim",
  "expectedText": "The National Institute of Diabetes and Digestive and Kidney Diseases similarly emphasizes that abnormal A1C results used for diagnosis usually require confirmation with a second measurement [6].",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-021

- Suggested tier: `core`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> NHANES provides demographic data, anthropometry, blood pressure, health questionnaires, and laboratory measures, including glycohemoglobin and fasting glucose in the 2017-2018 cycle.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-021",
  "tier": "core",
  "type": "numeric-claim",
  "expectedText": "NHANES provides demographic data, anthropometry, blood pressure, health questionnaires, and laboratory measures, including glycohemoglobin and fasting glucose in the 2017-2018 cycle.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-022

- Suggested tier: `core`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> NHANES analytic guidelines and weighting tutorials emphasize that weights account for unequal selection probabilities, oversampling, non-response, and post-stratification adjustment [1,2].

Draft registry object:

```json
{
  "id": "nhanes-reviewed-022",
  "tier": "core",
  "type": "numeric-claim",
  "expectedText": "NHANES analytic guidelines and weighting tutorials emphasize that weights account for unequal selection probabilities, oversampling, non-response, and post-stratification adjustment [1,2].",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-023

- Suggested tier: `core`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> Prior NHANES-based studies have examined diabetes prevalence trends, undiagnosed diabetes definitions, population screening patterns, and discrepancies between HbA1c-based and glucose-based glycemic classification [9-13].

Draft registry object:

```json
{
  "id": "nhanes-reviewed-023",
  "tier": "core",
  "type": "numeric-claim",
  "expectedText": "Prior NHANES-based studies have examined diabetes prevalence trends, undiagnosed diabetes definitions, population screening patterns, and discrepancies between HbA1c-based and glucose-based glycemic classification [9-13].",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-024

- Suggested tier: `core`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> These studies provide important background but leave room for narrower analyses focused on the profile of people who self-report no diabetes diagnosis while meeting laboratory criteria for diabetes-range HbA1c.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-024",
  "tier": "core",
  "type": "numeric-claim",
  "expectedText": "These studies provide important background but leave room for narrower analyses focused on the profile of people who self-report no diabetes diagnosis while meeting laboratory criteria for diabetes-range HbA1c.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-025

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> This framing is especially relevant for public health and primary care because variables such as waist circumference, blood pressure, and lipid measures are widely available or relatively inexpensive compared with advanced metabolic testing.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-025",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "This framing is especially relevant for public health and primary care because variables such as waist circumference, blood pressure, and lipid measures are widely available or relatively inexpensive compared with advanced metabolic testing.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-026

- Suggested tier: `supporting`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> Central adiposity is closely related to insulin resistance and adverse cardiometabolic risk profiles, and NHANES-based studies have examined waist circumference and other body shape indices in relation to glycemic outcomes [14].

Draft registry object:

```json
{
  "id": "nhanes-reviewed-026",
  "tier": "supporting",
  "type": "numeric-claim",
  "expectedText": "Central adiposity is closely related to insulin resistance and adverse cardiometabolic risk profiles, and NHANES-based studies have examined waist circumference and other body shape indices in relation to glycemic outcomes [14].",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-027

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> Recent NHANES and cohort studies have reported associations between non-HDL cholesterol, non-HDL-to-HDL cholesterol ratio, and diabetes or incident diabetes risk [15-17].

Draft registry object:

```json
{
  "id": "nhanes-reviewed-027",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "Recent NHANES and cohort studies have reported associations between non-HDL cholesterol, non-HDL-to-HDL cholesterol ratio, and diabetes or incident diabetes risk [15-17].",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-028

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> Participants with undiagnosed diabetes may have altered lifestyle behaviors, unmeasured comorbidities, or differential health awareness.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-028",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "Participants with undiagnosed diabetes may have altered lifestyle behaviors, unmeasured comorbidities, or differential health awareness.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-029

- Suggested tier: `core`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> The objective of this study was to estimate the weighted prevalence of HbA1c-defined undiagnosed diabetes among self-reported non-diabetic U.S. adults and to examine its demographic, anthropometric, cardiometabolic, and lifestyle correlates using NHANES 2017-2018 data.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-029",
  "tier": "core",
  "type": "numeric-claim",
  "expectedText": "The objective of this study was to estimate the weighted prevalence of HbA1c-defined undiagnosed diabetes among self-reported non-diabetic U.S. adults and to examine its demographic, anthropometric, cardiometabolic, and lifestyle correlates using NHANES 2017-2018 data.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-030

- Suggested tier: `core`
- Type: `sample-size`
- Interpretation boundary needed: `True`

Sentence:

> The study further evaluated HbA1c-defined prediabetes and a fasting-subsample sensitivity definition that incorporated fasting plasma glucose.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-030",
  "tier": "core",
  "type": "sample-size",
  "expectedText": "The study further evaluated HbA1c-defined prediabetes and a fasting-subsample sensitivity definition that incorporated fasting plasma glucose.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-031

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> First, the denominator is not the general adult population or adults with diagnosed diabetes, but adults who report no diabetes diagnosis.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-031",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "First, the denominator is not the general adult population or adults with diagnosed diabetes, but adults who report no diabetes diagnosis.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-032

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> This restriction better matches the practical screening problem: clinicians and public health programs often need to decide which apparently non-diabetic adults may warrant laboratory testing or closer follow-up.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-032",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "This restriction better matches the practical screening problem: clinicians and public health programs often need to decide which apparently non-diabetic adults may warrant laboratory testing or closer follow-up.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-033

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> The analysis can identify associations that may guide future screening research, but it cannot determine whether modifying waist circumference, lipid levels, or physical activity would reduce undiagnosed diabetes in the observed population.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-033",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "The analysis can identify associations that may guide future screening research, but it cannot determine whether modifying waist circumference, lipid levels, or physical activity would reduce undiagnosed diabetes in the observed population.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-034

- Suggested tier: `supporting`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> This cross-sectional study used publicly available NHANES 2017-2018 data.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-034",
  "tier": "supporting",
  "type": "numeric-claim",
  "expectedText": "This cross-sectional study used publicly available NHANES 2017-2018 data.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-035

- Suggested tier: `core`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> The 2017-2018 cycle included demographic, examination, questionnaire, and laboratory components.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-035",
  "tier": "core",
  "type": "numeric-claim",
  "expectedText": "The 2017-2018 cycle included demographic, examination, questionnaire, and laboratory components.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-036

- Suggested tier: `supporting`
- Type: `numeric-claim`
- Interpretation boundary needed: `True`

Sentence:

> The present analysis used 12 NHANES files: demographic data (`DEMO_J`), body measures (`BMX_J`), blood pressure examination data (`BPX_J`), diabetes questionnaire data (`DIQ_J`), glycohemoglobin (`GHB_J`), fasting plasma glucose (`GLU_J`), blood pressure and cholesterol questionnaire data (`BPQ_J`), total cholesterol (`TCHOL_J`), HDL cholesterol (`HDL_J`), physical activity questionnaire data (`PAQ_J`), smoking questionnaire data (`SMQ_J`), and sleep questionnaire data (`SLQ_J`).

Draft registry object:

```json
{
  "id": "nhanes-reviewed-036",
  "tier": "supporting",
  "type": "numeric-claim",
  "expectedText": "The present analysis used 12 NHANES files: demographic data (`DEMO_J`), body measures (`BMX_J`), blood pressure examination data (`BPX_J`), diabetes questionnaire data (`DIQ_J`), glycohemoglobin (`GHB_J`), fasting plasma glucose (`GLU_J`), blood pressure and cholesterol questionnaire data (`BPQ_J`), total cholesterol (`TCHOL_J`), HDL cholesterol (`HDL_J`), physical activity questionnaire data (`PAQ_J`), smoking questionnaire data (`SMQ_J`), and sleep questionnaire data (`SLQ_J`).",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-037

- Suggested tier: `core`
- Type: `prevalence-or-percentage`
- Interpretation boundary needed: `True`

Sentence:

> Glycohemoglobin was identified using the NHANES variable `LBXGH`, documented as glycohemoglobin (%) in the 2017-2018 laboratory documentation [3,4].

Draft registry object:

```json
{
  "id": "nhanes-reviewed-037",
  "tier": "core",
  "type": "prevalence-or-percentage",
  "expectedText": "Glycohemoglobin was identified using the NHANES variable `LBXGH`, documented as glycohemoglobin (%) in the 2017-2018 laboratory documentation [3,4].",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-038

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> The analytic population was restricted to adults aged 20 years or older.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-038",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "The analytic population was restricted to adults aged 20 years or older.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-039

- Suggested tier: `core`
- Type: `sample-size`
- Interpretation boundary needed: `True`

Sentence:

> Participants were eligible for the primary analysis if they self-reported no prior diabetes diagnosis and had available HbA1c data.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-039",
  "tier": "core",
  "type": "sample-size",
  "expectedText": "Participants were eligible for the primary analysis if they self-reported no prior diabetes diagnosis and had available HbA1c data.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```

### nhanes-candidate-040

- Suggested tier: `core`
- Type: `model-estimate`
- Interpretation boundary needed: `True`

Sentence:

> Diabetes self-report was derived from the NHANES diabetes questionnaire item asking whether a doctor or health professional had ever told the participant that they had diabetes.

Draft registry object:

```json
{
  "id": "nhanes-reviewed-040",
  "tier": "core",
  "type": "model-estimate",
  "expectedText": "Diabetes self-report was derived from the NHANES diabetes questionnaire item asking whether a doctor or health professional had ever told the participant that they had diabetes.",
  "sourceFile": "TODO",
  "sourceFields": [
    "TODO"
  ],
  "interpretationBoundary": "TODO"
}
```
